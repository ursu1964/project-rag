"""Governance agent combining constitutional checks and trust scoring.

The governance agent is recommendation-only. It can require human review but
cannot approve or execute actions autonomously.
"""

from __future__ import annotations

from typing import Any

from app.governance.constitutional_engine import evaluate_constitution
from app.governance.trust_agent import calculate_trust_score


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Evaluate governance posture for a proposed decision/recommendation."""
    decision = str(
        state.get("decision")
        or state.get("recommendation")
        or state.get("answer")
        or state.get("objective")
        or ""
    )
    constitutional = evaluate_constitution(decision, context=state)
    trust = calculate_trust_score({**state, "violations": constitutional["violations"]})
    governance = {
        "decision": decision,
        "constitutional": constitutional,
        "trust": trust,
        "allowed": bool(constitutional["allowed"] and trust["trust_score"] >= 0.45),
        "requires_human_review": bool(constitutional["requires_human_review"] or trust["trust_score"] < 0.45),
        "mode": "recommendation_only",
        "execution": "disabled",
    }
    return {**state, "governance": governance}
