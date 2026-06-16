"""Simple PostgreSQL-backed memory store."""

from __future__ import annotations

from typing import Any

from app.repositories.memory_repository import (
    add_memory_item,
    list_recent_memory_items,
    search_memory_items,
)

MEMORY_TYPES = {"conversation", "session", "project", "knowledge", "ontology"}


def add_memory(memory_type: str, content: str, metadata: dict[str, Any] | None = None) -> str:
    """Add a memory item and return its id."""
    if memory_type not in MEMORY_TYPES:
        raise ValueError("Unsupported memory type")
    return add_memory_item(memory_type, content[:255], {"content": content, "metadata": metadata or {}})


def search_memory(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search memory by key or JSON value text."""
    return search_memory_items(query, limit)


def list_recent_memories(limit: int = 20) -> list[dict[str, Any]]:
    """List recent memory items."""
    return list_recent_memory_items(limit)
