"""Recommendation-only agent for proposing improvements."""

from __future__ import annotations

from typing import Any


def _confidence(item: dict[str, Any]) -> float:
    score = 0.4
    if item.get("evidence_score"):
        score += min(float(item["evidence_score"]), 1.0) * 0.4
    if item.get("evidence_type") == "graph":
        score += 0.1
    return round(min(score, 0.95), 3)


def _recommendation_from_evidence(item: dict[str, Any], index: int) -> dict[str, Any]:
    evidence_type = item.get("evidence_type", "context")
    if evidence_type == "graph":
        title = "Review graph dependency or impact path"
    elif evidence_type == "vector":
        title = "Review supporting document context"
    elif evidence_type == "memory":
        title = "Review relevant project memory"
    else:
        title = "Review retrieved context"

    return {
        "rank": index,
        "title": title,
        "recommendation": "Use this evidence to refine the plan before any human-approved action.",
        "confidence": _confidence(item),
        "mode": "recommendation_only",
        "execution_allowed": False,
        "evidence": item,
    }


def run(state: dict) -> dict:
    evidence = state.get("evidence") or []
    recommendations = [
        _recommendation_from_evidence(item, index)
        for index, item in enumerate(evidence, start=1)
        if isinstance(item, dict)
    ]
    if not recommendations:
        recommendations = [
            {
                "rank": 1,
                "title": "Gather more evidence",
                "recommendation": "Retrieve more vector, graph, or memory context before making changes.",
                "confidence": 0.5,
                "mode": "recommendation_only",
                "execution_allowed": False,
                "evidence": {},
            }
        ]

    recommendations.sort(key=lambda item: item["confidence"], reverse=True)
    for index, item in enumerate(recommendations, start=1):
        item["rank"] = index

    return {**state, "recommendations": recommendations}
