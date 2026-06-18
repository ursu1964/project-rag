"""Constitutional governance engine for ProjectRAG.

The engine evaluates recommendations against default constitutional rules. It is
advisory and does not execute or approve actions autonomously.
"""

from __future__ import annotations

from typing import Any

DEFAULT_CONSTITUTION = [
    "protect availability",
    "protect security",
    "protect recoverability",
    "protect explainability",
    "protect human authority",
    "protect knowledge integrity",
]

_RULE_KEYWORDS = {
    "protect availability": ("shutdown", "outage", "downtime", "terminate", "reboot"),
    "protect security": ("secret", "credential", "public", "firewall", "expose"),
    "protect recoverability": ("delete backup", "remove backup", "no rollback", "irreversible"),
    "protect explainability": ("unexplained", "black box", "no evidence"),
    "protect human authority": ("auto approve", "without approval", "autonomous execute"),
    "protect knowledge integrity": ("fabricate", "ignore evidence", "overwrite facts"),
}


def list_constitution_rules() -> list[str]:
    """Return the default ProjectRAG constitution rules."""
    return list(DEFAULT_CONSTITUTION)


def evaluate_constitution(decision: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Evaluate a decision/recommendation against default constitutional rules."""
    text = f"{decision} {context or {}}".lower()
    violations = []
    for rule, keywords in _RULE_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in text]
        if matched:
            violations.append({"rule": rule, "matched_terms": matched})

    allowed = not violations
    return {
        "allowed": allowed,
        "decision": decision,
        "rules_checked": list_constitution_rules(),
        "violations": violations,
        "requires_human_review": bool(violations),
        "mode": "recommendation_only",
        "execution": "disabled",
    }
