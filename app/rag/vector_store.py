"""Vector store facade."""

from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.repositories.chunks_repository import insert_chunk as repository_insert_chunk
from app.repositories.chunks_repository import (
    similarity_search as repository_similarity_search,
)
from app.security.tenant_context import current_tenant_id, with_tenant_metadata
from app.services import qdrant_vector_store

logger = get_logger(__name__)


def _backend() -> str:
    backend = (
        str(getattr(settings, "vector_backend", "pgvector") or "pgvector")
        .lower()
        .strip()
    )
    return backend if backend in {"pgvector", "qdrant", "hybrid"} else "pgvector"


def _qdrant_point_id(document_id: str, chunk_index: int) -> str:
    return f"{document_id}:{chunk_index}"


def _qdrant_result_to_chunk(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload") or {}
    return {
        "id": payload.get("chunk_id") or row.get("id"),
        "document_id": payload.get("document_id"),
        "chunk_index": payload.get("chunk_index"),
        "content": payload.get("content", ""),
        "metadata": payload.get("metadata") or {},
        "distance": 1.0 - float(row.get("score") or 0.0),
        "score": row.get("score"),
    }


def insert_chunk(
    document_id: str,
    chunk_index: int,
    chunk_text: str,
    embedding: list[float],
    metadata: dict[str, Any] | None = None,
) -> None:
    repository_insert_chunk(document_id, chunk_index, chunk_text, embedding, metadata)
    if _backend() in {"qdrant", "hybrid"}:
        tenant_metadata = with_tenant_metadata(metadata)
        try:
            qdrant_vector_store.upsert(
                [
                    {
                        "id": _qdrant_point_id(document_id, chunk_index),
                        "vector": embedding,
                        "payload": {
                            "document_id": document_id,
                            "chunk_index": chunk_index,
                            "content": chunk_text,
                            "metadata": tenant_metadata,
                            **tenant_metadata,
                        },
                    }
                ],
                vector_size=len(embedding),
            )
        except (
            Exception
        ) as exc:  # pragma: no cover - depends on local Qdrant availability
            logger.warning("Qdrant chunk upsert failed: %s", exc.__class__.__name__)


def similarity_search(
    embedding: list[float],
    top_k: int = 5,
    tenant_id: str | None = None,
    metadata_filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    backend = _backend()
    filters = {**(metadata_filters or {}), "tenant_id": current_tenant_id(tenant_id)}
    if backend in {"qdrant", "hybrid"}:
        try:
            rows = qdrant_vector_store.search(embedding, top_k=top_k, filters=filters)
            if backend == "qdrant" or rows:
                return [_qdrant_result_to_chunk(row) for row in rows]
        except (
            Exception
        ) as exc:  # pragma: no cover - depends on local Qdrant availability
            logger.warning(
                "Qdrant similarity search failed; falling back to pgvector: %s",
                exc.__class__.__name__,
            )
    return repository_similarity_search(
        embedding, top_k, tenant_id=tenant_id, metadata_filters=metadata_filters
    )
