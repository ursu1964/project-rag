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
            "PROJECTRAG_CLOUD_CONNECTORS_ENABLED is true. Ensure credentials, tenant, and audit controls are ready before use.",
            stacklevel=2,
        )

    auth_mode = str(getattr(config, "auth_mode", "local") or "local").strip().lower()
    if auth_mode not in {"local", "oidc"}:
        raise RuntimeError("AUTH_MODE must be either 'local' or 'oidc'")

    oidc_issuer = str(getattr(config, "oidc_issuer", "") or "").strip()
    if oidc_issuer:
        _require_url("OIDC_ISSUER", oidc_issuer)

    app_env = str(getattr(config, "app_env", "local") or "local").strip().lower()
    if app_env != "local":
        _validate_production_startup_guard(config=config, auth_mode=auth_mode, app_env=app_env)

    auth_required = bool(getattr(config, "auth_required", False))

    # Production hardening: non-local environments must have auth and RBAC enforced.
    app_env = str(getattr(config, "app_env", "local") or "local").strip().lower()
    if app_env != "local":
        if not auth_required:
            raise RuntimeError(
                "AUTH_REQUIRED must be true in non-local environments (APP_ENV != 'local'). "
                "Set PROJECTRAG_AUTH_REQUIRED=true."
            )
        enforce_rbac = bool(getattr(config, "enforce_rbac", False))
        if not enforce_rbac:
            raise RuntimeError(
                "ENFORCE_RBAC must be true in non-local environments (APP_ENV != 'local'). "
                "Set PROJECTRAG_ENFORCE_RBAC=true."
            )
        # When auth_mode=local in prod, a hashed API key is required.
        if auth_mode == "local":
            api_key_hash = str(getattr(config, "api_key_hash", "") or "").strip()
            plaintext_api_key = str(getattr(config, "api_key", "") or "").strip()
            if not api_key_hash and not plaintext_api_key:
                raise RuntimeError(
                    "API_KEY_HASH (or API_KEY for backward compat) must be set in non-local environments "
                    "when AUTH_MODE=local. Set PROJECTRAG_API_KEY_HASH to a bcrypt hash "
                    "or PROJECTRAG_API_KEY to a strong secret."
                )
            # Warn if using plaintext api_key (deprecated)
            if plaintext_api_key and not api_key_hash:
                import warnings
                warnings.warn(
                    "Using plaintext PROJECTRAG_API_KEY is deprecated. "
                    "Set PROJECTRAG_API_KEY_HASH to a bcrypt hash instead. "
                    "See docs/security.md for migration guide.",
                    DeprecationWarning,
                    stacklevel=2,
                )
        # Prevent deployment with default Postgres credentials.
        pg_password = str(getattr(config, "postgres_password", "") or "").strip()
        if pg_password in {"projectrag_password", "password", "postgres", "secret", "changeme"}:
            raise RuntimeError(
                "POSTGRES_PASSWORD must not use a default/well-known value in non-local environments."
            )


def _validate_production_startup_guard(config, auth_mode: str, app_env: str) -> None:
    """Validate that at least one valid authentication method is configured in non-local environments.

    This guard ensures the application refuses to start in production without proper auth configuration,
    preventing accidental deployments with authentication gaps.

    Valid authentication methods:
    - OIDC: auth_mode='oidc' with issuer and audience configured
    - API Key: auth_mode='local' with api_key_hash or api_key configured
    """
    if app_env == "local":
        return

    api_key_hash = str(getattr(config, "api_key_hash", "") or "").strip()
    plaintext_api_key = str(getattr(config, "api_key", "") or "").strip()
    oidc_issuer = str(getattr(config, "oidc_issuer", "") or "").strip()
    oidc_audience = str(getattr(config, "oidc_audience", "") or "").strip()

    has_api_key = bool(api_key_hash or plaintext_api_key)
    has_oidc = bool(auth_mode == "oidc" and oidc_issuer and oidc_audience)

    if not has_api_key and not has_oidc:
        raise RuntimeError(
            f"APPLICATION STARTUP BLOCKED: No valid authentication method configured for {app_env} environment.\n\n"
            "Configure at least one valid authentication method before starting:\n\n"
            "Option 1: API Key\n"
            "  - Set PROJECTRAG_API_KEY_HASH to a bcrypt hash (preferred), or\n"
            "  - Set PROJECTRAG_API_KEY to a strong secret (deprecated fallback)\n"
            "  - Helper: python -c \"from app.security.api_key_manager import hash_api_key; print(hash_api_key('your-key'))\"\n\n"
            "Option 2: OIDC/JWT\n"
            "  - Set PROJECTRAG_AUTH_MODE=oidc\n"
            "  - Set PROJECTRAG_OIDC_ISSUER to your provider URL\n"
            "  - Set PROJECTRAG_OIDC_AUDIENCE to your API audience\n"
            "  - Optional: PROJECTRAG_OIDC_JWKS_URL for a non-standard JWKS endpoint\n\n"
            "Local development only:\n"
            "  - Set APP_ENV=local to allow startup without auth\n\n"
            "Missing variables: PROJECTRAG_API_KEY_HASH, PROJECTRAG_API_KEY, PROJECTRAG_AUTH_MODE, "
            "PROJECTRAG_OIDC_ISSUER, PROJECTRAG_OIDC_AUDIENCE, PROJECTRAG_OIDC_JWKS_URL"
        )
