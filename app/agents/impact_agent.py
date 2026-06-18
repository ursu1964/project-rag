"""Impact agent for graph-based direct and indirect dependency impact."""

from __future__ import annotations

import re
from typing import Any

from app.graph.impact_analysis import calculate_direct_impact, calculate_indirect_impact
from app.graph.triple_builder import sanitize_entity

_STOP_WORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "does",
    "do",
    "depend",
    "depends",
    "break",
    "breaks",
    "fail",
    "fails",
    "impact",
    "impacts",
    "affected",
    "entities",
    "if",
    "on",
    "by",
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
        r"\bwhat\s+breaks\s+if\s+([A-Za-z0-9_.-]+)\s+fails\b",
        r"\bwhat\s+depends\s+on\s+([A-Za-z0-9_.-]+)",
        r"\bimpact\s+of\s+([A-Za-z0-9_.-]+)",
        r"\bif\s+([A-Za-z0-9_.-]+)\s+fails\b",
    )
    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            return sanitize_entity(match.group(1))

    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_.-]*", question)
    candidates = [token for token in tokens if token.lower() not in _STOP_WORDS]
    return sanitize_entity(candidates[-1] if candidates else question)


def _entity_from_item(item: dict[str, Any]) -> str | None:
    for key in ("source", "impacted", "target", "object", "subject", "entity"):
        value = item.get(key)
        if value:
            return str(value)
    return None


def _dedupe_entities(items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    entities: list[str] = []
    for item in items:
        entity = _entity_from_item(item)
        if entity and entity not in seen:
            seen.add(entity)
            entities.append(entity)
    return entities


def run(state: dict) -> dict:
    """Return direct, indirect, and deduplicated affected entities for a graph entity."""
    entity = _extract_entity(state)
    try:
        direct_impact = calculate_direct_impact(entity)
        indirect_impact = calculate_indirect_impact(entity)
        affected_entities = _dedupe_entities([*direct_impact, *indirect_impact])
        impact_context = {
            "entity": entity,
            "direct_impact": direct_impact,
            "indirect_impact": indirect_impact,
            "affected_entities": affected_entities,
            "affected_count": len(affected_entities),
            "warnings": [],
        }
    except Exception as exc:  # pragma: no cover - external GraphDB failures vary
        impact_context = {
            "entity": entity,
            "direct_impact": [],
            "indirect_impact": [],
            "affected_entities": [],
            "affected_count": 0,
            "warnings": [f"impact analysis failed: {exc.__class__.__name__}"],
        }

    return {**state, "impact_context": impact_context}
