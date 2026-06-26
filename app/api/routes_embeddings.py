"""Embedding API routes."""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import settings
from app.security.rbac import permission_dependency
from app.services.cache import get_json, set_json
from app.tools.ollama_client import create_embedding

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class EmbeddingRequest(BaseModel):
    text: str = Field(min_length=1)


class BatchEmbeddingRequest(BaseModel):
    texts: list[str] = Field(min_length=1)


def _cache_key(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"embedding:{settings.embedding_model}:{digest}"


@router.post("", dependencies=[Depends(permission_dependency("query"))])
def embed(request: EmbeddingRequest) -> dict:
    key = _cache_key(request.text)
    cached = get_json(key)
    if cached is not None:
        return {"model": settings.embedding_model, "dimensions": len(cached), "embedding": cached, "cached": True}
    embedding = create_embedding(request.text)
    set_json(key, embedding, ttl_seconds=settings.embedding_cache_ttl_seconds)
    return {"model": settings.embedding_model, "dimensions": len(embedding), "embedding": embedding, "cached": False}


@router.post("/batch", dependencies=[Depends(permission_dependency("query"))])
def embed_batch(request: BatchEmbeddingRequest) -> dict:
    return {"model": settings.embedding_model, "items": [embed(EmbeddingRequest(text=text)) for text in request.texts]}


@router.get("/models", dependencies=[Depends(permission_dependency("read"))])
def embedding_models() -> dict:
    return {"default": settings.embedding_model, "provider": "ollama", "cache_ttl_seconds": settings.embedding_cache_ttl_seconds}
