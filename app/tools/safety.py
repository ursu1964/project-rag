"""Safety helpers for action and question risk classification."""

from __future__ import annotations

_HIGH_RISK_TERMS = (
    "delete",
    "destroy",
    "terminate",
    "remove",
    "shutdown",
    "reboot",
    "modify firewall",
    "change route",
    "drop database",
    "execute",
    "apply terraform",
)

_MEDIUM_RISK_TERMS = (
    "deploy",
    "update",
    "change",
    "create",
    "restart",
    "ingest",
    "upload",
)


def block_execution_by_default() -> bool:
    """ProjectRAG does not execute real actions without an approval mode."""
    return True


def classify_question_risk(question: str) -> dict:
    """Classify question/action risk and approval requirements."""
    normalized = question.lower()
    matched_high = next((term for term in _HIGH_RISK_TERMS if term in normalized), None)
    if matched_high:
        return {
            "risk_level": "high",
            "requires_human_approval": True,
            "reason": f"High-risk action term detected: {matched_high}",
        }

    matched_medium = next((term for term in _MEDIUM_RISK_TERMS if term in normalized), None)
    if matched_medium:
        return {
            "risk_level": "medium",
            "requires_human_approval": True,
            "reason": f"Operational change term detected: {matched_medium}",
        }

    return {
        "risk_level": "low",
        "requires_human_approval": False,
        "reason": "No high-risk action terms detected.",
    }


def require_approval_for_action(question: str) -> bool:
    """Return whether a question/action needs human approval."""
    return block_execution_by_default() or bool(classify_question_risk(question)["requires_human_approval"])
