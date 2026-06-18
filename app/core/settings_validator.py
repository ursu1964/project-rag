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
    if int(getattr(config, "max_upload_size_bytes", 0)) <= 0:
        raise RuntimeError("MAX_UPLOAD_SIZE_BYTES must be greater than 0")
    if int(getattr(config, "max_upload_files_per_request", 0)) <= 0:
        raise RuntimeError("MAX_UPLOAD_FILES_PER_REQUEST must be greater than 0")
    if int(getattr(config, "ingest_max_files_per_run", 0)) <= 0:
        raise RuntimeError("INGEST_MAX_FILES_PER_RUN must be greater than 0")

    # Redis URL basic validation (optional but must be valid format when set)
    redis_url = str(getattr(config, "redis_url", "") or "").strip()
    if redis_url and not (redis_url.startswith("redis://") or redis_url.startswith("rediss://")):
        raise RuntimeError("REDIS_URL must start with redis:// or rediss://")

    # Qdrant URL validation when set
    qdrant_url = str(getattr(config, "qdrant_url", "") or "").strip()
    if qdrant_url:
        _require_url("QDRANT_URL", qdrant_url)

    # Cloud connectors: warn at startup if enabled (informational only, not a hard error)
    if getattr(config, "enable_cloud_connectors", False):  # noqa: SIM102
        import warnings
        warnings.warn(
            "ENABLE_CLOUD_CONNECTORS is true. Ensure credentials, tenant, and audit controls are ready before use.",
            stacklevel=2,
        )

    auth_mode = str(getattr(config, "auth_mode", "local") or "local").strip().lower()
    if auth_mode not in {"local", "oidc"}:
        raise RuntimeError("AUTH_MODE must be either 'local' or 'oidc'")

    oidc_issuer = str(getattr(config, "oidc_issuer", "") or "").strip()
    if oidc_issuer:
        _require_url("OIDC_ISSUER", oidc_issuer)

    auth_required = bool(getattr(config, "auth_required", False))
    if auth_required and auth_mode == "oidc" and not oidc_issuer:
        raise RuntimeError("OIDC_ISSUER must be set when AUTH_REQUIRED is true and AUTH_MODE=oidc")
