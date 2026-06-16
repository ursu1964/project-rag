"""Memory persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import fetch_all, get_connection


def add_memory_item(memory_type: str, key: str, value: dict[str, Any]) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO memory_items (memory_type, key, value)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (memory_type, key, json.dumps(value)),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def search_memory_items(query: str, limit: int = 5) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, memory_type, key, value, created_at, updated_at
        FROM memory_items
        WHERE key ILIKE %s OR value::text ILIKE %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (f"%{query}%", f"%{query}%", limit),
    )


def list_recent_memory_items(limit: int = 20) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, memory_type, key, value, created_at, updated_at
        FROM memory_items
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,),
    )
