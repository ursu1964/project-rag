"""Long-term knowledge memory store."""

from __future__ import annotations

from typing import Any

from app.memory.memory_store import add_memory, search_memory
from app.memory.postgres import execute
from app.graph.triple_builder import sanitize_entity


def store_fact(content: str, metadata: dict[str, Any] | None = None) -> str:
    """Store a long-term knowledge fact separate from conversation memory."""
    return add_memory("knowledge", content, metadata or {})


def search_fact(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search long-term knowledge facts."""
    rows = search_memory(query, limit)
    return [row for row in rows if row.get("memory_type") == "knowledge"]


def link_fact_to_graph_entity(fact_id: str, entity: str, metadata: dict[str, Any] | None = None) -> None:
    """Link a knowledge memory fact to a graph entity using memory metadata."""
    execute(
        """
        UPDATE memory_items
        SET value = jsonb_set(
            jsonb_set(value, '{graph_entity}', to_jsonb(%s::text), true),
            '{link_metadata}', %s::jsonb, true
        ),
        updated_at = now()
        WHERE id = %s AND memory_type = 'knowledge'
        """,
        (sanitize_entity(entity), __import__("json").dumps(metadata or {}), fact_id),
    )
