"""Memory API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.memory.memory_store import add_memory, list_recent_memories, search_memory
from app.security.rbac import permission_dependency

router = APIRouter()


class MemoryCreateRequest(BaseModel):
    memory_type: str = Field(min_length=1)
    content: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


@router.get("/memory", dependencies=[Depends(permission_dependency("read"))])
def list_memory(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, Any]]:
    return list_recent_memories(limit)


@router.post("/memory", dependencies=[Depends(permission_dependency("ingest"))])
def create_memory(request: MemoryCreateRequest) -> dict[str, str]:
    memory_id = add_memory(request.memory_type, request.content, request.metadata)
    return {"id": memory_id, "status": "created"}


@router.get("/memory/search", dependencies=[Depends(permission_dependency("read"))])
def search_memory_route(q: str = Query(..., min_length=1), limit: int = Query(default=5, ge=1, le=50)) -> list[dict[str, Any]]:
    return search_memory(q, limit)
