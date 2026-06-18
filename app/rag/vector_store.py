"""pgvector-backed chunk storage and retrieval."""

from __future__ import annotations

from typing import Any

from app.repositories.chunks_repository import insert_chunk as repository_insert_chunk
from app.repositories.chunks_repository import similarity_search as repository_similarity_search
from app.repositories.chunks_repository import vector_literal


def _vector_literal(embedding: list[float]) -> str:
    return vector_literal(embedding)


def insert_chunk(
    document_id: str,
    chunk_index: int,
    chunk_text: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
    tenant_id: str | None = None,
) -> None:
    repository_insert_chunk(document_id, chunk_index, chunk_text, embedding, metadata, tenant_id)


def similarity_search(
    embedding: list[float],
    top_k: int = 5,
    tenant_id: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if tenant_id is None and metadata_filters is None:
        return repository_similarity_search(embedding, top_k)
    return repository_similarity_search(embedding, top_k, tenant_id=tenant_id, metadata_filters=metadata_filters)
