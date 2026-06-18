"""Fitness scoring for reviewable evolution proposals."""

from __future__ import annotations

from typing import Any, Mapping


def calculate_fitness_score(metrics: Mapping[str, float]) -> dict[str, Any]:
    """Calculate deterministic bounded fitness score from proposal metrics."""
    test_score = min(1.0, max(0.0, float(metrics.get("test_score", 0.0))))
    safety_score = min(1.0, max(0.0, float(metrics.get("safety_score", 0.0))))
    maintainability_score = min(1.0, max(0.0, float(metrics.get("maintainability_score", 0.0))))
    complexity_penalty = min(1.0, max(0.0, float(metrics.get("complexity_penalty", 0.0))))

    score = round(
        max(
            0.0,
            min(
                1.0,
                (test_score * 0.35)
                + (safety_score * 0.35)
                + (maintainability_score * 0.2)
                - (complexity_penalty * 0.1),
            ),
        ),
        6,
    )
    return {
        "fitness_score": score,
        "passed": score >= 0.7 and safety_score >= 0.8,
        "metrics": dict(metrics),
        "requires_human_review": True,
        "execution": "disabled",
    }


def rank_proposals(proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank proposal dictionaries by embedded or calculated fitness score."""
    def score(proposal: dict[str, Any]) -> float:
        if "fitness_score" in proposal:
            return float(proposal["fitness_score"])
        return float(calculate_fitness_score(proposal.get("metrics", {}))["fitness_score"])

    return sorted(proposals, key=score, reverse=True)
