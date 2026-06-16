"""RAG query routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.metrics import REQUEST_COUNTER, observe_query_metrics
from app.core.schemas import QueryRequest, QueryResponse
from app.core.timing import elapsed_ms, now_ms
from app.memory.validation_store import store_validation_result
from app.memory.workflow_store import complete_workflow_run, create_workflow_run
from app.workflows.rag_workflow import build_workflow

router = APIRouter()


def _format_query_response(state: dict, workflow_id: str) -> dict:
    return {
        "question": state.get("question"),
        "route": state.get("route"),
        "answer": state.get("answer"),
        "validation": state.get("validation") or {},
        "evidence": {
            "vector": state.get("vector_context") or [],
            "graph": state.get("graph_context") or [],
            "memory": state.get("memory_context") or [],
        },
        "metrics": {"workflow_id": workflow_id, **(state.get("metrics") or {})},
    }


@router.post("/query", response_model=None)
def query(request: QueryRequest, debug: bool = False) -> dict:
    REQUEST_COUNTER.labels("/query").inc()
    started = now_ms()
    workflow_id = create_workflow_run(request.question)
    workflow = build_workflow()
    try:
        state = workflow.invoke({"question": request.question, "workflow_id": workflow_id})
        metrics = {**(state.get("metrics") or {}), "duration_ms": elapsed_ms(started)}
        state["workflow_id"] = workflow_id
        state["metrics"] = metrics
        observe_query_metrics(metrics)
        if state.get("validation"):
            store_validation_result(workflow_id, state["validation"])
        complete_workflow_run(workflow_id)
        if debug:
            return state
        return _format_query_response(state, workflow_id)
    except Exception:
        complete_workflow_run(workflow_id, status="failed")
        raise
