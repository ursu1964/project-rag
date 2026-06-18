"""Consensus helpers for multiple agent outputs."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def majority_vote(votes: list[dict[str, Any]]) -> dict[str, Any]:
    """Return weighted majority consensus for agent votes.

    Each vote may include: agent_name, answer, confidence, weight.
    """
    if not votes:
        return {"answer": None, "confidence": 0.0, "support": 0, "votes": []}

    weights: dict[Any, float] = defaultdict(float)
    support: dict[Any, int] = defaultdict(int)
    for vote in votes:
        answer = vote.get("answer")
        confidence = float(vote.get("confidence", 1.0))
        weight = float(vote.get("weight", 1.0))
        weights[answer] += max(0.0, confidence * weight)
        support[answer] += 1

    answer = max(weights, key=weights.get)
    total_weight = sum(weights.values()) or 1.0
    return {
        "answer": answer,
        "confidence": round(weights[answer] / total_weight, 6),
        "support": support[answer],
        "votes": votes,
    }


def consensus_from_agent_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Build consensus from result dictionaries containing answer/recommendation fields."""
    votes = []
    for result in results:
        answer = result.get("answer", result.get("recommendation", result.get("decision")))
        votes.append(
            {
                "agent_name": result.get("agent_name"),
                "answer": answer,
                "confidence": result.get("confidence", 1.0),
                "weight": result.get("weight", 1.0),
            }
        )
    return majority_vote(votes)
