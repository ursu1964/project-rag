"""Workflow, agent run, and validation audit routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.metrics import REQUEST_COUNTER
from app.repositories.workflow_repository import (
    get_workflow_run,
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
    return workflow


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
