"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_env: str = Field(
        default="local", validation_alias=AliasChoices("AIOS_APP_ENV", "APP_ENV")
    )
    app_host: str = Field(
        default="0.0.0.0", validation_alias=AliasChoices("AIOS_APP_HOST", "APP_HOST")
    )
    app_port: int = Field(
        default=8000, validation_alias=AliasChoices("AIOS_APP_PORT", "APP_PORT")
    )
    log_level: str = Field(
        default="INFO", validation_alias=AliasChoices("AIOS_LOG_LEVEL", "LOG_LEVEL")
    )

    postgres_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("AIOS_POSTGRES_HOST", "POSTGRES_HOST"),
    )
    postgres_port: int = Field(
        default=5432,
        validation_alias=AliasChoices("AIOS_POSTGRES_PORT", "POSTGRES_PORT"),
    )
    postgres_db: str = Field(
        default="projectrag",
        validation_alias=AliasChoices("AIOS_POSTGRES_DB", "POSTGRES_DB"),
    )
    postgres_user: str = Field(
        default="projectrag",
        validation_alias=AliasChoices("AIOS_POSTGRES_USER", "POSTGRES_USER"),
    )
    postgres_password: str = Field(
        default="projectrag_password",
        validation_alias=AliasChoices("AIOS_POSTGRES_PASSWORD", "POSTGRES_PASSWORD"),
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias=AliasChoices("AIOS_REDIS_URL", "REDIS_URL"),
    )

    qdrant_url: str = Field(
        default="http://localhost:6333",
        validation_alias=AliasChoices("AIOS_QDRANT_URL", "QDRANT_URL"),
    )
    qdrant_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("AIOS_QDRANT_API_KEY", "QDRANT_API_KEY"),
    )
    qdrant_collection: str = Field(
        default="projectrag_chunks",
        validation_alias=AliasChoices("AIOS_QDRANT_COLLECTION", "QDRANT_COLLECTION"),
    )
    vector_backend: str = Field(
        default="pgvector",
        validation_alias=AliasChoices("AIOS_VECTOR_BACKEND", "VECTOR_BACKEND"),
    )

    graphdb_url: str = Field(
        default="http://localhost:7200",
        validation_alias=AliasChoices("AIOS_GRAPHDB_URL", "GRAPHDB_URL"),
    )
    graphdb_repository: str = Field(
        default="projectrag",
        validation_alias=AliasChoices("AIOS_GRAPHDB_REPOSITORY", "GRAPHDB_REPOSITORY"),
    )
    graphdb_ensure_repository_on_startup: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "AIOS_GRAPHDB_ENSURE_REPOSITORY_ON_STARTUP",
            "GRAPHDB_ENSURE_REPOSITORY_ON_STARTUP",
        ),
    )

    ollama_url: str = Field(
        default="http://localhost:11434",
        validation_alias=AliasChoices("AIOS_OLLAMA_URL", "OLLAMA_URL"),
    )
    ollama_model: str = Field(
        default="llama3.1:8b",
        validation_alias=AliasChoices("AIOS_OLLAMA_MODEL", "OLLAMA_MODEL"),
    )
    embedding_model: str = Field(
        default="nomic-embed-text",
        validation_alias=AliasChoices("AIOS_EMBEDDING_MODEL", "EMBEDDING_MODEL"),
    )

    chunk_size: int = Field(
        default=1000, validation_alias=AliasChoices("AIOS_CHUNK_SIZE", "CHUNK_SIZE")
    )
    chunk_overlap: int = Field(
        default=150,
        validation_alias=AliasChoices("AIOS_CHUNK_OVERLAP", "CHUNK_OVERLAP"),
    )
    top_k: int = Field(default=5, validation_alias=AliasChoices("AIOS_TOP_K", "TOP_K"))
    max_upload_size_bytes: int = Field(
        default=5 * 1024 * 1024,
        validation_alias=AliasChoices(
            "AIOS_MAX_UPLOAD_SIZE_BYTES", "MAX_UPLOAD_SIZE_BYTES"
        ),
    )
    max_upload_files_per_request: int = Field(
        default=1,
        validation_alias=AliasChoices(
            "AIOS_MAX_UPLOAD_FILES_PER_REQUEST", "MAX_UPLOAD_FILES_PER_REQUEST"
        ),
    )
    ingest_max_files_per_run: int = Field(
        default=200,
        validation_alias=AliasChoices(
            "AIOS_INGEST_MAX_FILES_PER_RUN", "INGEST_MAX_FILES_PER_RUN"
        ),
    )
    use_llm_router: bool = Field(
        default=False,
        validation_alias=AliasChoices("AIOS_USE_LLM_ROUTER", "USE_LLM_ROUTER"),
    )
    use_llm_judge: bool = Field(
        default=False,
        validation_alias=AliasChoices("AIOS_USE_LLM_JUDGE", "USE_LLM_JUDGE"),
    )
    enable_claude_provider: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "AIOS_ENABLE_CLAUDE_PROVIDER", "ENABLE_CLAUDE_PROVIDER"
        ),
    )
    claude_model: str = Field(
        default="claude-3-5-sonnet",
        validation_alias=AliasChoices("AIOS_CLAUDE_MODEL", "CLAUDE_MODEL"),
    )
    graph_max_depth: int = Field(
        default=3,
        validation_alias=AliasChoices("AIOS_GRAPH_MAX_DEPTH", "GRAPH_MAX_DEPTH"),
    )

    api_key: str = Field(
        default="",
        validation_alias=AliasChoices("AIOS_API_KEY", "PROJECTRAG_API_KEY", "API_KEY"),
    )
    api_key_hash: str = Field(
        default="",
        validation_alias=AliasChoices(
            "AIOS_API_KEY_HASH", "PROJECTRAG_API_KEY_HASH", "API_KEY_HASH"
        ),
    )
    rate_limit_per_minute: int = Field(
        default=0,
        validation_alias=AliasChoices(
            "AIOS_RATE_LIMIT_PER_MINUTE",
            "PROJECTRAG_RATE_LIMIT_PER_MINUTE",
            "RATE_LIMIT_PER_MINUTE",
        ),
    )
    # Per-endpoint rate limits (JSON string: {"POST /ingest": 5, "POST /query": 10})
    rate_limit_per_endpoint: str = Field(
        default="{}",
        validation_alias=AliasChoices(
            "AIOS_RATE_LIMIT_PER_ENDPOINT",
            "PROJECTRAG_RATE_LIMIT_PER_ENDPOINT",
            "RATE_LIMIT_PER_ENDPOINT",
        ),
    )
    request_audit_enabled: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "AIOS_REQUEST_AUDIT_ENABLED",
            "PROJECTRAG_REQUEST_AUDIT_ENABLED",
            "REQUEST_AUDIT_ENABLED",
        ),
    )
    enforce_rbac: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "AIOS_ENFORCE_RBAC", "PROJECTRAG_ENFORCE_RBAC", "ENFORCE_RBAC"
        ),
    )
    auth_required: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "AIOS_AUTH_REQUIRED", "PROJECTRAG_AUTH_REQUIRED", "AUTH_REQUIRED"
        ),
    )
    auth_mode: str = Field(
        default="local",
        validation_alias=AliasChoices(
            "AIOS_AUTH_MODE", "PROJECTRAG_AUTH_MODE", "AUTH_MODE"
        ),
    )  # local | oidc
    tenant_header_name: str = "x-projectrag-tenant-id"
    cors_allow_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501,http://127.0.0.1:8501"
    )
    oidc_issuer: str = Field(
        default="",
        validation_alias=AliasChoices(
            "AIOS_OIDC_ISSUER", "PROJECTRAG_OIDC_ISSUER", "OIDC_ISSUER"
        ),
    )
    oidc_audience: str = Field(
        default="",
        validation_alias=AliasChoices(
            "AIOS_OIDC_AUDIENCE", "PROJECTRAG_OIDC_AUDIENCE", "OIDC_AUDIENCE"
        ),
    )
    oidc_jwks_url: str = Field(
        default="",
        validation_alias=AliasChoices(
            "AIOS_OIDC_JWKS_URL", "PROJECTRAG_OIDC_JWKS_URL", "OIDC_JWKS_URL"
        ),
    )
    auth_required_environments: str = (
        "production"  # comma-separated list of envs requiring auth
    )

    enable_cloud_connectors: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "AIOS_CLOUD_CONNECTORS_ENABLED",
            "AIOS_ENABLE_CLOUD_CONNECTORS",
            "PROJECTRAG_CLOUD_CONNECTORS_ENABLED",
            "PROJECTRAG_ENABLE_CLOUD_CONNECTORS",
            "ENABLE_CLOUD_CONNECTORS",
        ),
    )
    embedding_cache_ttl_seconds: int = Field(
        default=86400,
        validation_alias=AliasChoices(
            "AIOS_EMBEDDING_CACHE_TTL_SECONDS", "EMBEDDING_CACHE_TTL_SECONDS"
        ),
    )
    otel_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("AIOS_OTEL_ENABLED", "OTEL_ENABLED"),
    )
    otel_service_name: str = Field(
        default="projectrag-api",
        validation_alias=AliasChoices("AIOS_OTEL_SERVICE_NAME", "OTEL_SERVICE_NAME"),
    )
    otel_exporter_otlp_endpoint: str = Field(
        default="http://otel-collector:4318/v1/traces",
        validation_alias=AliasChoices(
            "AIOS_OTEL_EXPORTER_OTLP_ENDPOINT", "OTEL_EXPORTER_OTLP_ENDPOINT"
        ),
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
