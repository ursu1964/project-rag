"""Approval gate for DevOps action plans."""

from __future__ import annotations

from typing import Any

from app.core.security_modes import get_current_mode


def evaluate_approval(action: dict[str, Any]) -> dict[str, Any]:
    """Return approval requirements; never permit real execution."""
    risk_level = str(action.get("risk_level", "low"))
    blocked = bool(action.get("blocked"))
    requires_approval = blocked or risk_level in {"medium", "high"}
    return {
        "mode": get_current_mode(),
        "approved": False,
        "requires_human_approval": requires_approval,
        "execution_allowed": False,
        "blocked": blocked,
        "reason": "Real execution is disabled; plans are advisory only.",
    }


def gate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Apply approval checks to every planned action."""
    gated_actions = []
    for action in plan.get("actions", []):
        gated_actions.append({**action, "approval": evaluate_approval(action)})
    return {**plan, "actions": gated_actions, "execution_allowed": False}
