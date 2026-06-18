"""Workflow, agent run, and validation audit routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.metrics import REQUEST_COUNTER
from app.core.schemas import QueryRequest
from app.api.routes_query import query as run_query
from app.repositories.workflow_repository import (
    get_workflow_run,
    latest_workflow_checkpoint,
    list_workflow_checkpoints,
    list_agent_runs,
    list_validation_results,
    list_workflow_runs,
)

router = APIRouter()


@router.get("/workflows")
def workflows(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    """List recent workflow runs."""
    REQUEST_COUNTER.labels("/workflows").inc()
    return list_workflow_runs(limit=limit)


@router.get("/workflows/{workflow_id}")
def workflow_detail(workflow_id: str) -> dict:
    """Return one workflow run with related agent runs and validation results."""
    REQUEST_COUNTER.labels("/workflows/{workflow_id}").inc()
    workflow = get_workflow_run(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    workflow["checkpoints"] = list_workflow_checkpoints(workflow_id)
    return workflow


@router.post("/workflows/{workflow_id}/resume")
def workflow_resume_or_replay(
    workflow_id: str,
    replay: bool = Query(default=False),
    debug: bool = Query(default=False),
) -> dict:
    """Resume metadata from latest checkpoint, or replay from checkpoint input.

    - replay=false: return latest checkpoint and suggested resume payload.
    - replay=true: re-run query using original workflow input question.
    """
    REQUEST_COUNTER.labels("/workflows/{workflow_id}/resume").inc()
    workflow = get_workflow_run(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    checkpoint = latest_workflow_checkpoint(workflow_id)
    if checkpoint is None:
        raise HTTPException(status_code=404, detail="No checkpoints found for workflow")

    if not replay:
        return {
            "status": "ok",
            "mode": "resume",
            "workflow_id": workflow_id,
            "latest_checkpoint": checkpoint,
            "resume_payload": {
                "workflow_id": workflow_id,
                "step_name": checkpoint.get("step_name"),
                "state": checkpoint.get("state") or {},
            },
        }

    input_payload = workflow.get("input") if isinstance(workflow.get("input"), dict) else {}
    question = str(input_payload.get("question") or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Workflow input has no question to replay")

    replay_result = run_query(QueryRequest(question=question), debug=debug)
    return {
        "status": "ok",
        "mode": "replay",
        "source_workflow_id": workflow_id,
        "question": question,
        "result": replay_result,
    }


@router.get("/agents/runs")
def agent_runs(
    workflow_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict]:
    """List recent agent runs, optionally filtered by workflow."""
    REQUEST_COUNTER.labels("/agents/runs").inc()
    return list_agent_runs(workflow_id=workflow_id, limit=limit)


@router.get("/validation/results")
def validation_results(
    workflow_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict]:
    """List recent validation results, optionally filtered by workflow."""
    REQUEST_COUNTER.labels("/validation/results").inc()
    return list_validation_results(workflow_id=workflow_id, limit=limit)
