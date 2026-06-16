"""Chunk and vector persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all


def vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def insert_chunk(
    document_id: str,
    chunk_index: int,
    content: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> None:
    execute(
        """
        INSERT INTO chunks (document_id, chunk_index, content, embedding, metadata)
        VALUES (%s, %s, %s, %s::vector, %s::jsonb)
        """,
        (document_id, chunk_index, content, vector_literal(embedding), json.dumps(metadata or {})),
    )


def similarity_search(embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    vector = vector_literal(embedding)
    return fetch_all(
        """
        SELECT id, document_id, chunk_index, content, metadata,
               embedding <-> %s::vector AS distance
        FROM chunks
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """,
        (vector, vector, top_k),
    )
