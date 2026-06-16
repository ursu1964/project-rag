"""Topology chaos analysis entry points."""

from __future__ import annotations

from typing import Iterable

from app.chaos.metrics import Edge, calculate_complexity_score, calculate_entropy, calculate_instability


def analyze_topology(edges: Iterable[Edge]) -> dict[str, float]:
    """Return deterministic chaos metrics for a topology edge list."""
    edge_list = list(edges)
    return {
        "entropy": calculate_entropy(edge_list),
        "instability": calculate_instability(edge_list),
        "complexity_score": calculate_complexity_score(edge_list),
    }
