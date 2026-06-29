"""Durable memory store backed by PostgreSQL with local fallback."""

from __future__ import annotations

import uuid
from typing import Any

from psycopg2.extras import Json

from app.core.logging import get_logger
from app.memory.postgres import get_connection

logger = get_logger(__name__)
_FALLBACK_MEMORIES: list[dict[str, Any]] = []


def _row_to_memory(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("value") or {}
    metadata = value.get("metadata") if isinstance(value, dict) else {}
    return {
        "id": str(row.get("id")),
        "memory_type": row.get("memory_type"),
        "content": value.get("content", "") if isinstance(value, dict) else "",
        "metadata": metadata if isinstance(metadata, dict) else {},
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _fallback_add(
    memory_type: str, content: str, metadata: dict[str, Any] | None = None
) -> str:
    memory_id = str(uuid.uuid4())
    _FALLBACK_MEMORIES.append(
        {
            "id": memory_id,
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata or {},
        }
    )
    return memory_id


def add_memory(
    memory_type: str, content: str, metadata: dict[str, Any] | None = None
) -> str:
    """Persist a memory item and return its id."""
    memory_id = str(uuid.uuid4())
    value = {"content": content, "metadata": metadata or {}}
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO memory_items (id, memory_type, key, value)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (memory_id, memory_type, memory_id, Json(value)),
                )
                row = cursor.fetchone()
            connection.commit()
        return str(row["id"] if isinstance(row, dict) else memory_id)
    except (
        Exception
    ) as exc:  # pragma: no cover - fallback path depends on local services
        logger.warning(
            "PostgreSQL memory insert failed; using process-local fallback: %s",
            exc.__class__.__name__,
        )
        return _fallback_add(memory_type, content, metadata)


def list_recent_memories(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent memory items, newest first."""
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, memory_type, key, value, created_at, updated_at
                    FROM memory_items
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (int(limit),),
                )
                rows = cursor.fetchall()
        return [_row_to_memory(dict(row)) for row in rows]
    except (
        Exception
    ) as exc:  # pragma: no cover - fallback path depends on local services
        logger.warning(
            "PostgreSQL memory list failed; using process-local fallback: %s",
            exc.__class__.__name__,
        )
        return list(reversed(_FALLBACK_MEMORIES[-int(limit) :]))


def search_memory(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search memory content with PostgreSQL text matching."""
    pattern = f"%{query}%"
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, memory_type, key, value, created_at, updated_at
                    FROM memory_items
                    WHERE value ->> 'content' ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (pattern, int(limit)),
                )
                rows = cursor.fetchall()
        return [_row_to_memory(dict(row)) for row in rows]
    except (
        Exception
    ) as exc:  # pragma: no cover - fallback path depends on local services
        logger.warning(
            "PostgreSQL memory search failed; using process-local fallback: %s",
            exc.__class__.__name__,
        )
        q = str(query).lower()
        return [
            item
            for item in reversed(_FALLBACK_MEMORIES)
            if q in str(item.get("content", "")).lower()
        ][: int(limit)]
