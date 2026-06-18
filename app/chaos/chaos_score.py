"""Deterministic chaos score aggregation."""

from __future__ import annotations

from typing import Mapping


def calculate_chaos_score(metrics: Mapping[str, float]) -> float:
    """Combine entropy, volatility, instability, complexity, and risk into one score."""
    entropy = min(1.0, float(metrics.get("entropy", 0.0)) / 4.0)
    volatility = min(1.0, float(metrics.get("volatility", 0.0)))
    instability = min(1.0, float(metrics.get("instability", 0.0)))
    complexity = min(1.0, float(metrics.get("complexity_score", metrics.get("complexity", 0.0))))
    risk = min(1.0, float(metrics.get("risk_score", 0.0)))

    score = (
        entropy * 0.25
        + volatility * 0.25
        + instability * 0.20
        + complexity * 0.20
        + risk * 0.10
    )
    return round(min(1.0, score), 6)
