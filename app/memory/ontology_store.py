"""Permanent semantic memory for ontology definitions and versions."""

from __future__ import annotations

from typing import Any

from app.memory.memory_store import add_memory, search_memory
from app.graph.triple_builder import sanitize_entity


def store_entity_definition(entity_type: str, definition: str, metadata: dict[str, Any] | None = None) -> str:
    """Store a permanent entity type definition."""
    return add_memory(
        "ontology",
        f"entity:{sanitize_entity(entity_type)}:{definition}",
        {"kind": "entity_definition", "entity_type": sanitize_entity(entity_type), **(metadata or {})},
    )


def store_relationship_definition(relationship: str, definition: str, metadata: dict[str, Any] | None = None) -> str:
    """Store a permanent relationship definition."""
    return add_memory(
        "ontology",
        f"relationship:{sanitize_entity(relationship)}:{definition}",
        {"kind": "relationship_definition", "relationship": sanitize_entity(relationship), **(metadata or {})},
    )


def store_ontology_version(version: str, notes: str = "", metadata: dict[str, Any] | None = None) -> str:
    """Store ontology version metadata."""
    return add_memory(
        "ontology",
        f"version:{version}:{notes}",
        {"kind": "ontology_version", "version": version, **(metadata or {})},
    )


def search_ontology(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search permanent ontology memory."""
    rows = search_memory(query, limit)
    return [row for row in rows if row.get("memory_type") == "ontology"]
