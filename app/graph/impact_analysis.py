"""Impact analysis helpers built on graph traversal."""

from __future__ import annotations

from typing import Any

from app.graph.traversal import get_impact_path, get_reverse_dependencies
from app.graph.triple_builder import sanitize_entity


def calculate_direct_impact(entity: str) -> list[dict[str, Any]]:
    """Return entities with direct reverse dependency impact."""
    result = get_reverse_dependencies(entity)
    return list(result.get("reverse_dependencies", []))


def calculate_indirect_impact(entity: str) -> list[dict[str, Any]]:
    """Return indirect impact paths for an entity."""
    result = get_impact_path(entity)
    return list(result.get("paths", []))


def _risk_score(direct_count: int, indirect_count: int) -> float:
    return min(1.0, round((direct_count * 0.25) + (indirect_count * 0.1), 3))


def build_impact_report(entity: str) -> dict[str, Any]:
    """Build a structured impact report for a graph entity."""
    normalized = sanitize_entity(entity)
    direct = calculate_direct_impact(normalized)
    indirect = calculate_indirect_impact(normalized)
    risk_score = _risk_score(len(direct), len(indirect))
    explanation = (
        f"{normalized} has {len(direct)} direct impacted dependencies and "
        f"{len(indirect)} indirect impact paths."
    )
    return {
        "direct_dependencies": direct,
        "indirect_dependencies": indirect,
        "risk_score": risk_score,
        "explanation": explanation,
    }
