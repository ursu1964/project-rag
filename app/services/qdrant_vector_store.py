"""Qdrant vector index integration with pgvector fallback elsewhere."""

from __future__ import annotations

from typing import Any

from app.core.config import settings

try:  # optional dependency for tests/local fallback
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, PointStruct, VectorParams
except ImportError:  # pragma: no cover
    QdrantClient = None
    Distance = PointStruct = VectorParams = None


def available() -> bool:
    return bool(QdrantClient and settings.qdrant_url)


def _client():
    if not available():
        return None
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


def ensure_collection(vector_size: int) -> bool:
    client = _client()
    if client is None:
        return False
    existing = {collection.name for collection in client.get_collections().collections}
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    return True


def upsert_chunk(
    *,
    chunk_id: str,
    embedding: list[float],
    content: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    client = _client()
    if client is None:
        return False
    ensure_collection(len(embedding))
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[PointStruct(id=chunk_id, vector=embedding, payload={"content": content, "metadata": metadata or {}})],
    )
    return True


def search(embedding: list[float], top_k: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    client = _client()
    if client is None:
        return []
    ensure_collection(len(embedding))
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=embedding,
        limit=max(top_k * 4, top_k),
        query_filter=None,
    )
    items = [
        {
            "id": str(point.id),
            "score": point.score,
            "content": (point.payload or {}).get("content"),
            "metadata": (point.payload or {}).get("metadata") or {},
            "filters": filters or {},
        }
        for point in results
    ]

    normalized_filters = {str(k): str(v) for k, v in (filters or {}).items() if v is not None}
    if not normalized_filters:
        return items[:top_k]

    filtered: list[dict[str, Any]] = []
    for item in items:
        metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
        if all(str(metadata.get(key, "")) == value for key, value in normalized_filters.items()):
            filtered.append(item)
        if len(filtered) >= top_k:
            break
    return filtered
