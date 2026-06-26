"""Vector store facade."""

from __future__ import annotations

from typing import Any

from app.repositories.chunks_repository import insert_chunk as repository_insert_chunk
from app.repositories.chunks_repository import similarity_search as repository_similarity_search


def insert_chunk(
    document_id: str,
    chunk_index: int,
    chunk_text: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> None:
    repository_insert_chunk(document_id, chunk_index, chunk_text, embedding, metadata)


def similarity_search(
    embedding: list[float], top_k: int = 5, tenant_id: str | None = None, metadata_filters: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return repository_similarity_search(embedding, top_k, tenant_id=tenant_id, metadata_filters=metadata_filters)
