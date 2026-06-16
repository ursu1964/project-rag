"""Route-aware context scoring helpers."""

from __future__ import annotations

ROUTE_WEIGHTS = {
    "graph": {"graph": 0.55, "vector": 0.25, "memory": 0.10, "metadata": 0.10},
    "vector": {"vector": 0.60, "graph": 0.20, "memory": 0.10, "metadata": 0.10},
    "hybrid": {"vector": 0.45, "graph": 0.35, "memory": 0.10, "metadata": 0.10},
}


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_vector_result(distance) -> float:
    """Convert a vector distance to a normalized relevance score."""
    try:
        distance_value = float(distance)
    except (TypeError, ValueError):
        return 0.0
    if distance_value < 0:
        return 0.0
    return _clamp(1.0 / (1.0 + distance_value))


def score_graph_result(result) -> float:
    """Score a GraphDB result by whether it contains bindings/facts."""
    if not result:
        return 0.0
    if isinstance(result, dict):
        bindings = result.get("results", {}).get("bindings")
        if bindings is not None:
            return 1.0 if bindings else 0.0
        if result.get("dependencies") or result.get("reverse_dependencies"):
            return 1.0
    return 0.5


def score_memory_result(result) -> float:
    """Score a memory result by presence of stored content."""
    if not result:
        return 0.0
    if isinstance(result, dict):
        return 1.0 if result.get("value") or result.get("key") else 0.5
    return 1.0


def weighted_score(
    route: str,
    vector_score: float,
    graph_score: float,
    memory_score: float,
    metadata_score: float = 0.0,
) -> float:
    """Calculate route-aware weighted score."""
    weights = ROUTE_WEIGHTS.get(route, ROUTE_WEIGHTS["hybrid"])
    return _clamp(
        _clamp(vector_score) * weights["vector"]
        + _clamp(graph_score) * weights["graph"]
        + _clamp(memory_score) * weights["memory"]
        + _clamp(metadata_score) * weights["metadata"]
    )
