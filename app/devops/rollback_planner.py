"""Rollback plan generation for proposed DevOps actions."""

from __future__ import annotations

from typing import Any


def create_rollback_plan(action: str | dict[str, Any]) -> dict[str, Any]:
    """Create a conservative rollback plan without executing anything."""
    action_text = action.get("description") if isinstance(action, dict) else str(action)
    return {
        "available": True,
        "execution": "disabled",
        "steps": [
            "Capture current state and configuration before any change.",
            "Prepare restore command or manual reversal procedure.",
            "Validate service health after rollback in a staging or maintenance window.",
            f"Rollback target: {action_text}",
        ],
    }
