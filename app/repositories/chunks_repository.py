"""Chunk and vector persistence repository."""

from __future__ import annotations

import json
import re
from typing import Any

from app.memory.postgres import execute, fetch_all
from app.security.tenant_context import current_tenant_id, with_tenant_metadata


def vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def insert_chunk(
    document_id: str,
    chunk_index: int,
    content: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
    tenant_id: str | None = None,
) -> None:
    execute(
        """
        INSERT INTO chunks (document_id, chunk_index, content, embedding, metadata)
        VALUES (%s, %s, %s, %s::vector, %s::jsonb)
        """,
        (
            document_id,
            chunk_index,
            content,
            vector_literal(embedding),
            json.dumps(with_tenant_metadata(metadata, tenant_id)),
        ),
    )


def list_chunk_indexes(document_id: str, tenant_id: str | None = None) -> list[int]:
    rows = fetch_all(
        """
        SELECT c.chunk_index
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE c.document_id = %s
          AND COALESCE(c.metadata->>'tenant_id', d.metadata->>'tenant_id', 'local') = %s
        ORDER BY chunk_index
        """,
        (document_id, current_tenant_id(tenant_id)),
    )
    return [int(row["chunk_index"]) for row in rows]


def _normalized_filters(metadata_filters: dict[str, Any] | None) -> list[tuple[str, str]]:
    if not metadata_filters:
        return []
    normalized: list[tuple[str, str]] = []
    for key, value in metadata_filters.items():
        if value is None:
            continue
        key_str = str(key).strip()
        if not key_str or not re.fullmatch(r"[A-Za-z0-9_\-:.]+", key_str):
            continue
        normalized.append((key_str, str(value)))
    return normalized


def similarity_search(
    embedding: list[float],
    top_k: int = 5,
    tenant_id: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    vector = vector_literal(embedding)
    tenant = current_tenant_id(tenant_id)
    filter_items = _normalized_filters(metadata_filters)
    where = ["COALESCE(c.metadata->>'tenant_id', d.metadata->>'tenant_id', 'local') = %s"]
    params: list[Any] = [vector, tenant]

    for key, value in filter_items:
        where.append("((c.metadata->>%s = %s) OR (d.metadata->>%s = %s))")
        params.extend((key, value, key, value))

    params.extend((vector, top_k))
    where_sql = " AND ".join(where)
    return fetch_all(
        f"""
        SELECT c.id, c.document_id, c.chunk_index, c.content, c.metadata,
               c.embedding <-> %s::vector AS distance
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE {where_sql}
        ORDER BY c.embedding <-> %s::vector
        LIMIT %s
        """,
        tuple(params),
    )
