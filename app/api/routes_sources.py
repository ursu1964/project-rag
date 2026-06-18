"""Source catalog routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.core.metrics import REQUEST_COUNTER
from app.rag.source_catalog import build_source_catalog

router = APIRouter()


@router.get("/sources/catalog")
def source_catalog() -> dict[str, Any]:
    """Return a read-only catalog of local RAG source files."""
    REQUEST_COUNTER.labels("/sources/catalog").inc()
    return build_source_catalog()
