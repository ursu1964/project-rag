"""Execution agent placeholder."""

from __future__ import annotations

from app.core.security_modes import can_execute_actions, get_current_mode, require_approval


def run(state: dict) -> dict:
    execution = {
        "status": "execution_disabled",
        "executed": False,
        "mode": get_current_mode(),
        "requires_approval": require_approval(),
        "can_execute_actions": can_execute_actions(),
        "reason": "Real actions are disabled until approval mode exists.",
    }
    return {**state, "execution": execution}
