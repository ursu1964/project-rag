"""Safe graph-based failure simulation engine."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.graph.traversal import get_neighbors
from app.graph.triple_builder import sanitize_entity


def _bounded_depth(depth: int | None = None) -> int:
    requested = settings.graph_max_depth if depth is None else depth
    return max(1, min(int(requested), int(settings.graph_max_depth)))


def _node_name(value: Any) -> str | None:
    if not value:
        return None
    return sanitize_entity(str(value).rsplit("/", 1)[-1])


def _neighbors(entity: str) -> list[str]:
    result = get_neighbors(entity)
    graph_neighbors = result.get("neighbors", {}) if isinstance(result, dict) else {}
    nodes: list[str] = []
    for item in graph_neighbors.get("incoming", []):
        node = _node_name(item.get("subject"))
        if node:
            nodes.append(node)
    for item in graph_neighbors.get("outgoing", []):
        node = _node_name(item.get("object"))
        if node:
            nodes.append(node)
    return nodes


def _risk_level(size: int) -> str:
    if size <= 2:
        return "low"
    if size <= 6:
        return "medium"
    return "high"


def simulate_failure(entity: str, depth: int | None = None) -> dict[str, Any]:
    """Simulate failure impact without executing any real actions."""
    normalized = sanitize_entity(entity)
    max_depth = _bounded_depth(depth)
    visited: set[str] = {normalized}
    impacted: list[str] = []
    frontier: list[str] = [normalized]
    traversal: list[dict[str, Any]] = []
    warnings: list[str] = []

    for current_depth in range(1, max_depth + 1):
        next_frontier: list[str] = []
        for current in frontier:
            try:
                neighbors = _neighbors(current)
            except Exception as exc:  # pragma: no cover - external GraphDB failures vary
                warnings.append(f"neighbor lookup failed for {current}: {exc.__class__.__name__}")
                continue
            for node in neighbors:
                traversal.append({"source": current, "target": node, "depth": current_depth})
                if node not in visited:
                    visited.add(node)
                    impacted.append(node)
                    next_frontier.append(node)
        frontier = next_frontier
        if not frontier:
            break

    risk = _risk_level(len(impacted))
    explanation = (
        f"Simulated failure of {normalized} affects {len(impacted)} node(s) "
        f"within depth {max_depth}. Risk is {risk}. No real actions were executed."
    )
    return {
        "entity": normalized,
        "simulation_type": "failure",
        "depth": max_depth,
        "impacted_nodes": impacted,
        "impact_count": len(impacted),
        "risk_level": risk,
        "risk_explanation": explanation,
        "traversal": traversal,
        "execution": "disabled",
        "warnings": warnings,
    }
