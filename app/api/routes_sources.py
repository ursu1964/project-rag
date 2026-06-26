"""Source catalog routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.core.metrics import REQUEST_COUNTER
from app.rag.source_catalog import build_source_catalog
from app.security.rbac import permission_dependency

router = APIRouter(dependencies=[Depends(permission_dependency("read"))])


@router.get("/sources/catalog")
def source_catalog() -> dict[str, Any]:
    """Return a read-only catalog of local RAG source files."""
    REQUEST_COUNTER.labels("/sources/catalog").inc()
    return build_source_catalog()
