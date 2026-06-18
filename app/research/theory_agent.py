"""Theory agent.

Drafts tentative theories from hypotheses and evidence. Recommendation-only;
no autonomous conclusions are enforced.
"""

from __future__ import annotations

from typing import Any


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Create a tentative theory recommendation from research context."""
    hypothesis = state.get("hypothesis") or {}
    evidence = state.get("evidence_summary") or {}
    theory = {
        "statement": "Tentative theory requires human review.",
        "based_on_hypothesis": hypothesis.get("statement") if isinstance(hypothesis, dict) else hypothesis,
        "evidence_count": evidence.get("count", 0) if isinstance(evidence, dict) else 0,
        "confidence": 0.2,
        "status": "draft",
        "mode": "recommendation_only",
        "execution": "disabled",
    }
    return {**state, "theory": theory}
