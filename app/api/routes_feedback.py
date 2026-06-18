"""User feedback routes for answer quality audit."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.metrics import REQUEST_COUNTER
from app.repositories.workflow_repository import store_workflow_feedback

router = APIRouter()


class FeedbackRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    helpful: bool | None = None
    comment: str = Field(default="", max_length=2000)


@router.post("/feedback/{workflow_id}")
def submit_feedback(workflow_id: str, request: FeedbackRequest) -> dict[str, Any]:
    """Attach user feedback to a workflow output and evaluation trend table."""
    REQUEST_COUNTER.labels("/feedback/{workflow_id}").inc()
    feedback = {
        "rating": request.rating,
        "helpful": request.helpful,
        "comment": request.comment,
    }
    result = store_workflow_feedback(workflow_id, feedback)
    if result is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": "stored", "workflow_id": workflow_id, "feedback": result}
