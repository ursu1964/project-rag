"""DevOps action planner that generates safe, non-executable plans only."""

from __future__ import annotations

from typing import Any

from app.devops.approval_gate import gate_plan
from app.devops.risk_classifier import classify_action_risk
from app.devops.rollback_planner import create_rollback_plan
from app.devops.verifier import verify_plan


def _normalize_actions(actions: Any, objective: str) -> list[str]:
    if isinstance(actions, list):
        return [str(action.get("description", action)) if isinstance(action, dict) else str(action) for action in actions]
    if isinstance(actions, str) and actions.strip():
        return [actions.strip()]
    if objective.strip():
        return [f"Review and recommend approach for: {objective.strip()}"]
    return ["Review current infrastructure state and provide recommendation."]


def _planned_action(description: str, index: int) -> dict[str, Any]:
    risk = classify_action_risk(description)
    return {
        "id": f"action-{index + 1}",
        "description": description,
        "type": "recommendation_only",
        "execution": "disabled",
        "risk_level": risk["risk_level"],
        "requires_human_approval": risk["requires_human_approval"],
        "blocked": risk["blocked"],
        "risk_reason": risk["reason"],
        "rollback_plan": create_rollback_plan(description),
    }


def create_action_plan(objective: str, actions: Any = None) -> dict[str, Any]:
    """Create a safe plan. No real execution is ever performed."""
    planned_actions = [
        _planned_action(description, index)
        for index, description in enumerate(_normalize_actions(actions, objective))
    ]
    plan = {
        "objective": objective,
        "mode": "plan_only",
        "execution_allowed": False,
        "actions": planned_actions,
    }
    gated = gate_plan(plan)
    return {**gated, "verification": verify_plan(gated)}


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Agent-compatible entrypoint for action planning."""
    objective = str(state.get("objective") or state.get("question") or "")
    plan = create_action_plan(objective, state.get("actions"))
    return {**state, "action_plan": plan}
