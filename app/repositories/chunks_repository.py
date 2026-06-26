"""Chunk and vector persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all
from app.security.tenant_context import current_tenant_id, with_tenant_metadata


def vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in embedding) + "]"


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
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT chunk_index
        FROM chunks
        WHERE document_id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s
        ORDER BY chunk_index
        """,
        (document_id, tenant),
    )
    return [int(row["chunk_index"]) for row in rows]


def similarity_search(
    embedding: list[float],
    top_k: int = 5,
    tenant_id: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    tenant = current_tenant_id(tenant_id)
    vector = vector_literal(embedding)
    params: list[Any] = [vector, vector, tenant]
    filters = ""
    for key, value in (metadata_filters or {}).items():
        if key == "tenant_id":
            continue
        filters += " AND metadata->>%s = %s"
        params.extend([str(key), str(value)])
    params.append(int(top_k))
    return fetch_all(
        f"""
        SELECT id, document_id, chunk_index, content, metadata,
               embedding <-> %s::vector AS distance
        FROM chunks
        WHERE embedding IS NOT NULL AND COALESCE(metadata->>'tenant_id', 'local') = %s
        {filters}
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """.replace("WHERE embedding IS NOT NULL AND COALESCE(metadata->>'tenant_id', 'local') = %s", "WHERE embedding IS NOT NULL AND COALESCE(metadata->>'tenant_id', 'local') = %s"),
        tuple([params[0], params[2], *params[3:-1], params[1], params[-1]]),
    )
