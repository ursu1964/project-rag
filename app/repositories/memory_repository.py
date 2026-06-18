"""Memory persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import fetch_all, get_connection
from app.security.tenant_context import current_tenant_id


def add_memory_item(
    memory_type: str,
    key: str,
    value: dict[str, Any],
    tenant_id: str | None = None,
) -> str:
    payload = dict(value or {})
    payload["tenant_id"] = current_tenant_id(tenant_id)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO memory_items (memory_type, key, value)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (memory_type, key, json.dumps(payload)),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def search_memory_items(query: str, limit: int = 5, tenant_id: str | None = None) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, memory_type, key, value, created_at, updated_at
        FROM memory_items
                WHERE COALESCE(value->>'tenant_id', 'local') = %s
                    AND (key ILIKE %s OR value::text ILIKE %s)
        ORDER BY created_at DESC
        LIMIT %s
        """,
                (current_tenant_id(tenant_id), f"%{query}%", f"%{query}%", limit),
    )


def list_recent_memory_items(limit: int = 20, tenant_id: str | None = None) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, memory_type, key, value, created_at, updated_at
        FROM memory_items
        WHERE COALESCE(value->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (current_tenant_id(tenant_id), limit),
    )
