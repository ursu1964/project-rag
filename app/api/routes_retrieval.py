"""Retrieval API routes."""

from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.metrics import (
    GRAPH_RETRIEVAL_DURATION,
    HYBRID_RETRIEVAL_DURATION,
    REQUEST_COUNTER,
    RETRIEVAL_CACHE_COUNTER,
    VECTOR_RETRIEVAL_DURATION,
)
from app.core.timing import elapsed_ms, now_ms
from app.graph.traversal import get_impact_path
from app.rag.vector_store import similarity_search
from app.security.tenant_context import current_tenant_id
from app.security.rbac import permission_dependency
from app.services.cache import get_json, set_json
from app.services.qdrant_vector_store import search as qdrant_search
from app.tools.ollama_client import create_embedding

router = APIRouter(prefix="/retrieval", tags=["retrieval"], dependencies=[Depends(permission_dependency("query"))])


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: dict = Field(default_factory=dict)


class GraphRetrievalRequest(BaseModel):
    entity: str = Field(min_length=1)
    depth: int = Field(default=1, ge=1, le=5)


def _cache_key(prefix: str, payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def _primary_query_token(query: str) -> str:
    stripped = str(query or "").strip()
    if not stripped:
        return "unknown"
    return stripped.split()[0]


@router.post("/vector")
def vector_retrieval(request: RetrievalRequest) -> dict:
    REQUEST_COUNTER.labels("/retrieval/vector").inc()
    started = now_ms()
    tenant_id = current_tenant_id()
    effective_filters = {**(request.filters or {}), "tenant_id": tenant_id}
    key = _cache_key(
        "retrieval:vector",
        {
            "tenant_id": tenant_id,
            "query": request.query,
            "top_k": request.top_k,
            "filters": effective_filters,
            "embedding_model": settings.embedding_model,
            "qdrant_collection": settings.qdrant_collection,
        },
    )
    cached = get_json(key)
    if cached is not None:
        RETRIEVAL_CACHE_COUNTER.labels("/retrieval/vector", "hit").inc()
        response = {**cached, "cached": True}
        VECTOR_RETRIEVAL_DURATION.observe(elapsed_ms(started))
        return response

    RETRIEVAL_CACHE_COUNTER.labels("/retrieval/vector", "miss").inc()
    embedding = create_embedding(request.query)
    qdrant_results = qdrant_search(embedding, top_k=request.top_k, filters=effective_filters)
    results = qdrant_results or similarity_search(
        embedding,
        top_k=request.top_k,
        tenant_id=tenant_id,
        metadata_filters=effective_filters,
    )
    response = {"backend": "qdrant" if qdrant_results else "pgvector", "results": results, "cached": False}
    set_json(key, response, ttl_seconds=300)
    VECTOR_RETRIEVAL_DURATION.observe(elapsed_ms(started))
    return response


@router.post("/graph")
def graph_retrieval(request: GraphRetrievalRequest) -> dict:
    REQUEST_COUNTER.labels("/retrieval/graph").inc()
    started = now_ms()
    depth = min(request.depth, settings.graph_max_depth)
    key = _cache_key(
        "retrieval:graph",
        {"tenant_id": current_tenant_id(), "entity": request.entity, "depth": depth},
    )
    cached = get_json(key)
    if cached is not None:
        RETRIEVAL_CACHE_COUNTER.labels("/retrieval/graph", "hit").inc()
        response = {**cached, "cached": True}
        GRAPH_RETRIEVAL_DURATION.observe(elapsed_ms(started))
        return response
    RETRIEVAL_CACHE_COUNTER.labels("/retrieval/graph", "miss").inc()
    response = {**get_impact_path(request.entity, depth=depth), "cached": False}
    set_json(key, response, ttl_seconds=120)
    GRAPH_RETRIEVAL_DURATION.observe(elapsed_ms(started))
    return response


@router.post("/hybrid")
def hybrid_retrieval(request: RetrievalRequest) -> dict:
    REQUEST_COUNTER.labels("/retrieval/hybrid").inc()
    started = now_ms()
    vector = vector_retrieval(request)
    graph = graph_retrieval(GraphRetrievalRequest(entity=_primary_query_token(request.query), depth=1))
    HYBRID_RETRIEVAL_DURATION.observe(elapsed_ms(started))
    return {"vector": vector["results"], "graph": graph["paths"]}
