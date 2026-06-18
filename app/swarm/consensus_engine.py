"""Simple non-executing consensus engine for agent recommendations."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _candidate_answer(candidate: dict[str, Any]) -> Any:
    return candidate.get("answer", candidate.get("recommendation", candidate.get("decision")))


def build_consensus(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Select a final recommendation by majority vote with confidence tie-break.

    This engine only aggregates recommendations. It never executes actions.
    """
    if not candidates:
        return {
            "final_recommendation": None,
            "confidence": 0.0,
            "support": 0,
            "dissenting_opinions": [],
            "execution": "disabled",
        }

    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        grouped[_candidate_answer(candidate)].append(candidate)

    def rank(item: tuple[Any, list[dict[str, Any]]]) -> tuple[int, float]:
        _, votes = item
        avg_confidence = sum(float(vote.get("confidence", 0.0)) for vote in votes) / len(votes)
        return (len(votes), avg_confidence)

    final_answer, supporting_votes = max(grouped.items(), key=rank)
    confidence = sum(float(vote.get("confidence", 0.0)) for vote in supporting_votes) / len(supporting_votes)
    dissenting = [candidate for candidate in candidates if _candidate_answer(candidate) != final_answer]

    return {
        "final_recommendation": final_answer,
        "confidence": round(confidence, 6),
        "support": len(supporting_votes),
        "supporting_opinions": supporting_votes,
        "dissenting_opinions": dissenting,
        "candidate_count": len(candidates),
        "execution": "disabled",
    }


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Agent-compatible entrypoint for consensus aggregation."""
    candidates = list(state.get("candidate_answers") or state.get("recommendations") or [])
    return {**state, "consensus": build_consensus(candidates)}
