"""Plan verifier for ProjectRAG DevOps recommendations."""

from __future__ import annotations

from typing import Any


def verify_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Verify every action has required safety metadata."""
    warnings: list[str] = []
    for index, action in enumerate(plan.get("actions", [])):
        if "risk_level" not in action:
            warnings.append(f"action[{index}] missing risk_level")
        if "rollback_plan" not in action:
            warnings.append(f"action[{index}] missing rollback_plan")
        if action.get("approval", {}).get("execution_allowed"):
            warnings.append(f"action[{index}] unexpectedly allows execution")
        if action.get("blocked") and action.get("risk_level") != "high":
            warnings.append(f"action[{index}] blocked action must be high risk")
    return {
        "passed": not warnings,
        "warnings": warnings,
        "execution_allowed": False,
    }
