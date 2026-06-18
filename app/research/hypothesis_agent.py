"""Hypothesis agent.

Creates recommendation-only hypotheses from context. It does not execute
experiments or make autonomous decisions.
"""

from __future__ import annotations

from typing import Any


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Generate a candidate hypothesis from the provided objective/context."""
    objective = str(state.get("objective") or state.get("question") or "")
    hypothesis = {
        "statement": f"Candidate hypothesis for: {objective}" if objective else "Candidate hypothesis requires an objective.",
        "confidence": 0.3,
        "status": "proposed",
        "mode": "recommendation_only",
        "execution": "disabled",
    }
    return {**state, "hypothesis": hypothesis}
