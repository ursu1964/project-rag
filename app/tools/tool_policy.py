"""Policy checks for safe internal tool execution."""

from __future__ import annotations

from typing import Any

from app.core.security_modes import READ_ONLY, get_current_mode

LOW = "low"
MEDIUM = "medium"
HIGH = "high"
CRITICAL = "critical"
RISK_CLASSES = {LOW, MEDIUM, HIGH, CRITICAL}


def normalize_risk(risk_class: str) -> str:
    """Normalize and validate a risk class."""
    normalized = str(risk_class or "").lower()
    if normalized not in RISK_CLASSES:
        raise ValueError(f"Unsupported risk class: {risk_class}")
    return normalized


def evaluate_tool_policy(
    risk_class: str,
    *,
    approved: bool = False,
    explicit_approval: bool = False,
    rollback_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a registered tool may run under ProjectRAG policy."""
    risk = normalize_risk(risk_class)
    mode = get_current_mode()

    if risk == CRITICAL:
        return {
            "allowed": False,
            "risk_class": risk,
            "mode": mode,
            "reason": "Critical-risk tools are blocked by default.",
        }

    if risk == LOW:
        return {
            "allowed": mode == READ_ONLY,
            "risk_class": risk,
            "mode": mode,
            "reason": "Low-risk read-only tools may run in READ_ONLY mode."
            if mode == READ_ONLY
            else "Low-risk tools are only enabled in READ_ONLY mode.",
        }

    if risk == MEDIUM:
        return {
            "allowed": bool(approved),
            "risk_class": risk,
            "mode": mode,
            "reason": "Medium-risk tools require approval.",
        }

    has_rollback = bool(rollback_plan and rollback_plan.get("steps"))
    return {
        "allowed": bool(explicit_approval and has_rollback),
        "risk_class": risk,
        "mode": mode,
        "reason": "High-risk tools require explicit approval and a rollback plan.",
    }
