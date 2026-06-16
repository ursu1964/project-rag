"""Startup settings validation."""

from __future__ import annotations

from urllib.parse import urlparse

from app.core.config import settings


def _require_non_empty(name: str, value: str) -> None:
    if not str(value).strip():
        raise RuntimeError(f"{name} must not be empty")


def _require_url(name: str, value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(f"{name} must be a valid http(s) URL")


def validate_settings(config=settings) -> None:
    """Validate required ProjectRAG settings at startup."""
    _require_non_empty("POSTGRES_HOST", config.postgres_host)
    _require_non_empty("POSTGRES_DB", config.postgres_db)
    _require_url("GRAPHDB_URL", config.graphdb_url)
    _require_url("OLLAMA_URL", config.ollama_url)

    if int(config.top_k) <= 0:
        raise RuntimeError("TOP_K must be greater than 0")
    if int(config.chunk_size) <= 0:
        raise RuntimeError("CHUNK_SIZE must be greater than 0")
    if int(config.chunk_overlap) < 0:
        raise RuntimeError("CHUNK_OVERLAP must be greater than or equal to 0")
    if int(config.chunk_overlap) >= int(config.chunk_size):
        raise RuntimeError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE")
