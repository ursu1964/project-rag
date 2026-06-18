"""Blast radius agent for bounded graph traversal around an entity."""

from __future__ import annotations

import re
from typing import Any

from app.core.config import settings
from app.graph.traversal import get_neighbors
from app.graph.triple_builder import sanitize_entity

_STOP_WORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "blast",
    "radius",
    "impact",
    "impacted",
    "breaks",
    "fails",
    "if",
    "for",
    "of",
    "the",
    "a",
    "an",
}


def _extract_entity(state: dict[str, Any]) -> str:
    explicit = state.get("entity") or state.get("target_entity")
    if explicit:
        return sanitize_entity(str(explicit))

    question = str(state.get("question") or state.get("objective") or state.get("query") or "")
    patterns = (
        r"\bblast\s+radius\s+(?:for|of)\s+([A-Za-z0-9_.-]+)",
        r"\bwhat\s+breaks\s+if\s+([A-Za-z0-9_.-]+)\s+fails\b",
        r"\bif\s+([A-Za-z0-9_.-]+)\s+fails\b",
    )
    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            return sanitize_entity(match.group(1))

    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_.-]*", question)
    candidates = [token for token in tokens if token.lower() not in _STOP_WORDS]
    return sanitize_entity(candidates[-1] if candidates else question)


def _bounded_depth(state: dict[str, Any]) -> int:
    requested = state.get("graph_depth") or state.get("depth") or settings.graph_max_depth
    return max(1, min(int(requested), int(settings.graph_max_depth)))


def _neighbor_entities(neighbors: dict[str, Any]) -> list[str]:
    values: list[str] = []
    graph_neighbors = neighbors.get("neighbors", {}) if isinstance(neighbors, dict) else {}
    for item in graph_neighbors.get("outgoing", []):
        target = item.get("object")
        if target:
            values.append(str(target).rsplit("/", 1)[-1])
    for item in graph_neighbors.get("incoming", []):
        source = item.get("subject")
        if source:
            values.append(str(source).rsplit("/", 1)[-1])
    return [sanitize_entity(value) for value in values if value]


def _classify(size: int) -> str:
    if size <= 2:
        return "low"
    if size <= 6:
        return "medium"
    return "high"


def run(state: dict) -> dict:
    """Traverse the graph up to configured depth and classify blast radius."""
    entity = _extract_entity(state)
    max_depth = _bounded_depth(state)
    visited: set[str] = {entity}
    frontier: list[str] = [entity]
    edges: list[dict[str, Any]] = []
    warnings: list[str] = []

    for depth in range(1, max_depth + 1):
        next_frontier: list[str] = []
        for current in frontier:
            try:
                neighbors = get_neighbors(current)
            except Exception as exc:  # pragma: no cover - external GraphDB failures vary
                warnings.append(f"neighbor lookup failed for {current}: {exc.__class__.__name__}")
                continue

            for neighbor in _neighbor_entities(neighbors):
                edges.append({"source": current, "target": neighbor, "depth": depth})
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
        if not frontier:
            break

    affected_entities = sorted(visited - {entity})
    blast_radius_size = len(affected_entities)
    blast_radius_context = {
        "entity": entity,
        "depth": max_depth,
        "affected_entities": affected_entities,
        "blast_radius_size": blast_radius_size,
        "classification": _classify(blast_radius_size),
        "edges": edges,
        "warnings": warnings,
    }
    return {**state, "blast_radius_context": blast_radius_context}
