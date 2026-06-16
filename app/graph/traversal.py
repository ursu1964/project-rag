"""Graph traversal helpers returning structured JSON."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.graph.graphdb_client import sparql_query
from app.graph.sparql_templates import (
    impact_query,
    incoming_relationships_query,
    outgoing_relationships_query,
)
from app.graph.triple_builder import sanitize_entity

_DEFAULT_MAX_DEPTH = 3


def _max_depth() -> int:
    return int(getattr(settings, "graph_max_depth", _DEFAULT_MAX_DEPTH))


def _bounded_depth(depth: int) -> int:
    return max(1, min(int(depth), _max_depth()))


def _bindings(result: dict[str, Any]) -> list[dict[str, Any]]:
    return list(result.get("results", {}).get("bindings", [])) if isinstance(result, dict) else []


def _value(binding: dict[str, Any], key: str) -> Any:
    item = binding.get(key)
    return item.get("value") if isinstance(item, dict) else item


def get_neighbors(entity: str) -> dict[str, Any]:
    normalized = sanitize_entity(entity)
    outgoing = _bindings(sparql_query(outgoing_relationships_query(normalized)))
    incoming = _bindings(sparql_query(incoming_relationships_query(normalized)))
    return {
        "entity": normalized,
        "neighbors": {
            "outgoing": [
                {"predicate": _value(item, "predicate"), "object": _value(item, "object")}
                for item in outgoing
            ],
            "incoming": [
                {"subject": _value(item, "subject"), "predicate": _value(item, "predicate")}
                for item in incoming
            ],
        },
    }


def get_dependencies(entity: str) -> dict[str, Any]:
    normalized = sanitize_entity(entity)
    rows = _bindings(sparql_query(outgoing_relationships_query(normalized)))
    dependencies = [
        {"predicate": _value(item, "predicate"), "target": _value(item, "object")}
        for item in rows
        if str(_value(item, "predicate") or "").endswith("dependsOn")
    ]
    return {"entity": normalized, "dependencies": dependencies}


def get_reverse_dependencies(entity: str) -> dict[str, Any]:
    normalized = sanitize_entity(entity)
    rows = _bindings(sparql_query(incoming_relationships_query(normalized)))
    reverse_dependencies = [
        {"source": _value(item, "subject"), "predicate": _value(item, "predicate")}
        for item in rows
        if str(_value(item, "predicate") or "").endswith("dependsOn")
    ]
    return {"entity": normalized, "reverse_dependencies": reverse_dependencies}


def get_impact_path(entity: str, depth: int = 3) -> dict[str, Any]:
    normalized = sanitize_entity(entity)
    bounded_depth = _bounded_depth(depth)
    rows = _bindings(sparql_query(impact_query(normalized)))
    paths = [
        {
            "impacted": _value(item, "impacted"),
            "predicate": _value(item, "predicate"),
            "path": _value(item, "path"),
        }
        for item in rows
    ]
    return {"entity": normalized, "depth": bounded_depth, "paths": paths}
