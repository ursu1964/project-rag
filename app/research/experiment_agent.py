"""Experiment agent.

Plans safe experiments only. No autonomous experiment execution is allowed.
"""

from __future__ import annotations

from typing import Any


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Create a recommendation-only experiment plan."""
    hypothesis = state.get("hypothesis") or {}
    statement = hypothesis.get("statement") if isinstance(hypothesis, dict) else str(hypothesis)
    experiment_plan = {
        "hypothesis": statement,
        "steps": [
            "Define measurable success criteria.",
            "Collect read-only evidence from ProjectRAG stores.",
            "Compare evidence against hypothesis.",
            "Record findings for human review.",
        ],
        "status": "planned",
        "mode": "recommendation_only",
        "execution": "disabled",
    }
    return {**state, "experiment_plan": experiment_plan}
