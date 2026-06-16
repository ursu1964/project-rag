from __future__ import annotations

"""pgvector-backed chunk storage and retrieval."""

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
) -> None:
    repository_insert_chunk(document_id, chunk_index, chunk_text, embedding, metadata)


def similarity_search(embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
    return repository_similarity_search(embedding, top_k)
