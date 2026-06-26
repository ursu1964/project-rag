"""RAG query routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.metrics import REQUEST_COUNTER, observe_query_metrics
from app.core.metrics import observe_validation_confidence
from app.core.schemas import QueryRequest
from app.core.timing import elapsed_ms, now_ms
from app.memory.validation_store import store_validation_result
from app.memory.workflow_store import (
    complete_workflow_run,
    create_workflow_run,
    save_workflow_checkpoint,
    store_workflow_output,
)
from app.rag.citations import build_citations
from app.security.audit import record_security_event
from app.security.pii_filter import redact_sensitive_data, redact_sensitive_text
from app.security.prompt_policy import evaluate_prompt_policy
from app.security.rbac import permission_dependency
from app.workflows.rag_workflow import build_workflow

router = APIRouter(dependencies=[Depends(permission_dependency("query"))])

_PROMPT_VERSION = "rag-infra-v1"


def _try_save_checkpoint(
    workflow_id: str,
    step_name: str,
    state: dict,
    status: str = "running",
    error: str | None = None,
) -> None:
    """Best-effort checkpoint persistence to keep request path resilient."""
    try:
        save_workflow_checkpoint(workflow_id, step_name, state, status=status, error=error)
    except Exception:
        # Checkpoint persistence should not break query execution.
        pass


def _query_evidence(state: dict) -> dict:
    merged = state.get("merged_context") if isinstance(state.get("merged_context"), dict) else {}
    return {
        "vector": merged.get("vector") or state.get("vector_context") or [],
        "graph": merged.get("graph") or state.get("graph_context") or [],
        "memory": merged.get("memory") or state.get("memory_context") or [],
    }


def _source_documents(citations: list[dict]) -> list[str]:
    sources: list[str] = []
    for citation in citations:
        source = str(citation.get("source") or "")
        if source and source not in sources:
            sources.append(source)
    return sources


def _provenance(state: dict, evidence: dict, citations: list[dict], workflow_id: str) -> dict:
    metrics = state.get("metrics") or {}
    validation = state.get("validation") or {}
    return {
        "workflow_id": workflow_id,
        "user_question": redact_sensitive_text(state.get("question")),
        "rewritten_query": redact_sensitive_text(state.get("rewritten_query") or state.get("question")),
        "retrieved_chunks": evidence["vector"],
        "source_documents": _source_documents(citations),
        "metadata_filters": state.get("metadata_filters") or [],
        "prompt_version": _PROMPT_VERSION,
        "model_name": settings.ollama_model,
        "embedding_model": settings.embedding_model,
        "generated_answer": redact_sensitive_text(state.get("answer")),
        "citations": citations,
        "confidence_score": validation.get("confidence", 0.0),
        "latency_ms": metrics.get("duration_ms"),
        "token_cost": None,
        "policy_decision": state.get("policy_decision") or {},
        "user_feedback": None,
    }


def _format_query_response(state: dict, workflow_id: str) -> dict:
    evidence = redact_sensitive_data(_query_evidence(state))
    citations = redact_sensitive_data(state.get("citations") or build_citations(evidence))
    provenance = _provenance(state, evidence, citations, workflow_id)
    return {
        "question": redact_sensitive_text(state.get("question")),
        "route": state.get("route"),
        "answer": redact_sensitive_text(state.get("answer")),
        "validation": state.get("validation") or {},
        "evidence": evidence,
        "citations": citations,
        "provenance": provenance,
        "policy_decision": state.get("policy_decision") or {},
        "metrics": {"workflow_id": workflow_id, **(state.get("metrics") or {})},
    }


@router.post("/query", response_model=None)
def query(request: QueryRequest, debug: bool = False) -> dict:
    REQUEST_COUNTER.labels("/query").inc()
    started = now_ms()
    policy_decision = evaluate_prompt_policy(request.question)
    audit_question = redact_sensitive_text(request.question)
    if not policy_decision["allowed"]:
        record_security_event(
            action="query",
            resource="/query",
            decision="deny",
            risk_level=policy_decision.get("risk_level", "high"),
            metadata={"violations": policy_decision.get("violations", []), "question_redacted": audit_question},
        )
        metrics = {"duration_ms": elapsed_ms(started)}
        state = {
            "question": audit_question,
            "route": "blocked_by_policy",
            "answer": "Request blocked by prompt security policy.",
            "validation": {
                "grounded": False,
                "confidence": 0.0,
                "warnings": policy_decision["violations"],
                "requires_human_approval": True,
            },
            "metrics": metrics,
            "citations": [],
            "policy_decision": policy_decision,
        }
        return state if debug else _format_query_response(state, workflow_id="")

    workflow_id = create_workflow_run(audit_question)
    workflow = build_workflow()
    try:
        _try_save_checkpoint(
            workflow_id,
            "workflow_start",
            {"question": audit_question, "debug": debug},
            status="running",
        )
        state = workflow.invoke({"question": request.question, "workflow_id": workflow_id})
        _try_save_checkpoint(
            workflow_id,
            "workflow_invoke",
            {
                "route": state.get("route"),
                "has_answer": bool(state.get("answer")),
                "validation": state.get("validation") or {},
            },
            status="running",
        )
        state["policy_decision"] = policy_decision
        metrics = {**(state.get("metrics") or {}), "duration_ms": elapsed_ms(started)}
        state["workflow_id"] = workflow_id
        state["metrics"] = metrics
        state["citations"] = build_citations(_query_evidence(state))
        observe_query_metrics(metrics)
        response_payload = _format_query_response(state, workflow_id)
        validation = state.get("validation") or {}
        risk_level = "high" if not validation.get("grounded") else "low"
        if "confidence" in validation:
            observe_validation_confidence(float(validation["confidence"]))
        record_security_event(
            action="query",
            resource="/query",
            decision="allow",
            risk_level=risk_level,
            metadata={
                "workflow_id": workflow_id,
                "route": state.get("route"),
                "confidence": validation.get("confidence"),
                "grounded": validation.get("grounded"),
                "duration_ms": metrics.get("duration_ms"),
            },
        )
        if validation:
            store_validation_result(workflow_id, validation)
        store_workflow_output(workflow_id, response_payload)
        _try_save_checkpoint(
            workflow_id,
            "workflow_complete",
            {
                "status": "completed",
                "confidence": validation.get("confidence"),
                "grounded": validation.get("grounded"),
            },
            status="completed",
        )
        complete_workflow_run(workflow_id)
        if debug:
            return state
        return response_payload
    except Exception as exc:
        _try_save_checkpoint(
            workflow_id,
            "workflow_error",
            {"status": "failed"},
            status="failed",
            error=str(exc),
        )
        complete_workflow_run(workflow_id, status="failed")
        raise
