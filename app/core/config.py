"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "projectrag"
    postgres_user: str = "projectrag"
    postgres_password: str = "projectrag_password"

    redis_url: str = "redis://localhost:6379/0"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "projectrag_chunks"

    graphdb_url: str = "http://localhost:7200"
    graphdb_repository: str = "projectrag"
    graphdb_ensure_repository_on_startup: bool = True

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    embedding_model: str = "nomic-embed-text"

    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    max_upload_size_bytes: int = 5 * 1024 * 1024
    max_upload_files_per_request: int = 1
    ingest_max_files_per_run: int = 200
    use_llm_router: bool = False
    use_llm_judge: bool = False
    enable_claude_provider: bool = False
    claude_model: str = "claude-3-5-sonnet"
    graph_max_depth: int = 3

    api_key: str = ""
    api_key_hash: str = ""  # bcrypt hash of api_key for secure storage; used instead of plaintext api_key
    rate_limit_per_minute: int = 0
    # Per-endpoint rate limits (JSON string: {"POST /ingest": 5, "POST /query": 10})
    rate_limit_per_endpoint: str = "{}"
    request_audit_enabled: bool = True
    enforce_rbac: bool = False
    auth_required: bool = False
    auth_mode: str = "local"  # local | oidc
    tenant_header_name: str = "x-projectrag-tenant-id"
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501,http://127.0.0.1:8501"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""  # explicit JWKS URL override; if not set, derived from issuer
    auth_required_environments: str = "production"  # comma-separated list of envs requiring auth

    enable_cloud_connectors: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "PROJECTRAG_CLOUD_CONNECTORS_ENABLED",
            "PROJECTRAG_ENABLE_CLOUD_CONNECTORS",
            "ENABLE_CLOUD_CONNECTORS",
        ),
    )
    embedding_cache_ttl_seconds: int = 86400
    otel_enabled: bool = False
    otel_service_name: str = "projectrag-api"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4318/v1/traces"

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
