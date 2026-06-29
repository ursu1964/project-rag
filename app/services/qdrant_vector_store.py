"""Qdrant vector store facade."""

from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.core.config import settings


def get_client() -> QdrantClient:
    """Return a Qdrant client from application settings."""
    kwargs: dict[str, Any] = {"url": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def ensure_collection(vector_size: int, collection_name: str | None = None) -> str:
    """Create the configured collection if it does not already exist."""
    name = collection_name or settings.qdrant_collection
    client = get_client()
    existing = {collection.name for collection in client.get_collections().collections}
    if name not in existing:
        client.create_collection(
            collection_name=name,
            vectors_config=models.VectorParams(
                size=int(vector_size), distance=models.Distance.COSINE
            ),
        )
    return name


def upsert(
    points: list[dict[str, Any]],
    vector_size: int | None = None,
    collection_name: str | None = None,
) -> None:
    """Upsert points shaped as {id, vector, payload}."""
    if not points:
        return
    first_vector = points[0].get("vector") or []
    size = int(vector_size or len(first_vector))
    name = ensure_collection(size, collection_name=collection_name)
    qdrant_points = [
        models.PointStruct(
            id=point["id"],
            vector=point["vector"],
            payload=point.get("payload") or {},
        )
        for point in points
    ]
    get_client().upsert(collection_name=name, points=qdrant_points)


def _build_filter(filters: dict[str, Any] | None) -> models.Filter | None:
    if not filters:
        return None
    conditions = [
        models.FieldCondition(key=str(key), match=models.MatchValue(value=value))
        for key, value in filters.items()
        if value is not None
    ]
    return models.Filter(must=conditions) if conditions else None


def search(
    embedding: list[float],
    top_k: int = 5,
    filters: dict[str, Any] | None = None,
    collection_name: str | None = None,
) -> list[dict[str, Any]]:
    """Search Qdrant and return normalized result dictionaries."""
    name = collection_name or settings.qdrant_collection
    query_filter = _build_filter(filters)
    client = get_client()
    try:
        results = client.search(
            collection_name=name,
            query_vector=embedding,
            query_filter=query_filter,
            limit=int(top_k),
            with_payload=True,
        )
    except AttributeError:  # qdrant-client >= 1.10 favors query_points
        response = client.query_points(
            collection_name=name,
            query=embedding,
            query_filter=query_filter,
            limit=int(top_k),
            with_payload=True,
        )
        results = response.points
    return [
        {
            "id": str(point.id),
            "score": float(point.score),
            "payload": dict(point.payload or {}),
        }
        for point in results
    ]


def health() -> dict[str, Any]:
    """Return basic Qdrant availability and collection metadata."""
    client = get_client()
    collections = [
        collection.name for collection in client.get_collections().collections
    ]
    return {
        "status": "ok",
        "url": settings.qdrant_url,
        "collection": settings.qdrant_collection,
        "collection_exists": settings.qdrant_collection in collections,
    }
