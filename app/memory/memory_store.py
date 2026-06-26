"""Simple memory store."""

from __future__ import annotations

import uuid
from typing import Any

_MEMORIES: list[dict[str, Any]] = []


def add_memory(memory_type: str, content: str, metadata: dict[str, Any] | None = None) -> str:
    memory_id = str(uuid.uuid4())
    _MEMORIES.append({"id": memory_id, "memory_type": memory_type, "content": content, "metadata": metadata or {}})
    return memory_id


def list_recent_memories(limit: int = 20) -> list[dict[str, Any]]:
    return list(reversed(_MEMORIES[-int(limit) :]))


def search_memory(query: str, limit: int = 5) -> list[dict[str, Any]]:
    q = str(query).lower()
    return [item for item in reversed(_MEMORIES) if q in str(item.get("content", "")).lower()][: int(limit)]
