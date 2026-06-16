"""Cognitive workflow API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.workflows.cognitive_workflow import build_workflow

router = APIRouter()


class CognitiveQueryRequest(BaseModel):
    objective: str = Field(min_length=1)


def _format_cognitive_response(state: dict[str, Any]) -> dict[str, Any]:
    plan = state.get("plan") or []
    security = state.get("security") or {}
    blocked = security.get("blocked", True)
    recommendation = "Execution is blocked; review the recommendation plan and request approval." if blocked else "Review the recommendation plan."

    return {
        "objective": state.get("objective"),
        "analysis": state.get("chief_summary") or {},
        "plan": {"steps": plan},
        "security": security,
        "cost": state.get("cost") or {},
        "validation": state.get("validation") or {},
        "recommendation": recommendation,
        "learning": {"lessons_learned": state.get("lessons_learned") or []},
    }


@router.post("/cognitive/query")
def cognitive_query(request: CognitiveQueryRequest) -> dict[str, Any]:
    workflow = build_workflow()
    state = workflow.invoke({"objective": request.objective, "question": request.objective})
    return _format_cognitive_response(state)
