"""Risk classification for proposed DevOps actions."""

from __future__ import annotations

from typing import Any

from app.tools.safety import classify_question_risk

_DESTRUCTIVE_TERMS = (
    "delete",
    "destroy",
    "terminate",
    "remove",
    "shutdown",
    "reboot",
    "drop database",
    "modify firewall",
    "change route",
    "apply terraform",
    "execute",
)


def is_destructive(action: str | dict[str, Any]) -> bool:
    """Return True when an action contains destructive terms."""
    text = _action_text(action).lower()
    return any(term in text for term in _DESTRUCTIVE_TERMS)


def _action_text(action: str | dict[str, Any]) -> str:
    if isinstance(action, dict):
        return " ".join(str(value) for value in action.values() if value is not None)
    return str(action)


def classify_action_risk(action: str | dict[str, Any]) -> dict[str, Any]:
    """Classify a planned action and flag destructive actions as blocked."""
    text = _action_text(action)
    risk = classify_question_risk(text)
    destructive = is_destructive(text)
    if destructive:
        return {
            "risk_level": "high",
            "requires_human_approval": True,
            "blocked": True,
            "reason": "Destructive action blocked by ProjectRAG safety policy.",
        }
    return {
        "risk_level": risk["risk_level"],
        "requires_human_approval": bool(risk["requires_human_approval"]),
        "blocked": False,
        "reason": risk["reason"],
    }
