"""Operations routes for background job retry visibility and controls."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.metrics import REQUEST_COUNTER
from app.services.background_jobs import list_retry_eta
from app.security.rbac import permission_dependency

router = APIRouter(dependencies=[Depends(permission_dependency("admin"))])


@router.get("/operations/jobs/retry-queue")
def retry_queue(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    """Return retry queue with computed ETA from next_retry_at."""
    REQUEST_COUNTER.labels("/operations/jobs/retry-queue").inc()
    rows = list_retry_eta(limit=limit)
    due_now = sum(1 for row in rows if bool(row.get("due_now")))
    return {
        "status": "ok",
        "total": len(rows),
        "due_now": due_now,
        "jobs": rows,
    }
