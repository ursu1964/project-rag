"""Tests for production startup guard.

Tests prove that the application refuses to start in non-local environments
without proper authentication configuration.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.core.settings_validator import validate_settings


class TestProductionStartupGuardLocal:
    """Tests for local environment (auth not required)."""

    def test_local_env_accepts_no_auth_configuration(self):
        """Local environment runs without authentication (by design)."""
        config = MagicMock()
        config.app_env = "local"
        config.postgres_host = "localhost"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://localhost:7200"
        config.ollama_url = "http://localhost:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://localhost:6379/0"
        config.qdrant_url = "http://localhost:6333"
        config.auth_required = False
        config.auth_mode = "local"
        config.api_key_hash = ""
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = False
        config.enable_cloud_connectors = False
        config.postgres_password = "projectrag_password"

        # Should NOT raise - local is allowed without auth
        validate_settings(config)

    def test_local_env_with_api_key_accepted(self):
        """Local environment with API key is still accepted."""
        config = MagicMock()
        config.app_env = "local"
        config.postgres_host = "localhost"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://localhost:7200"
        config.ollama_url = "http://localhost:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://localhost:6379/0"
        config.qdrant_url = "http://localhost:6333"
        config.auth_required = False
        config.auth_mode = "local"
        config.api_key_hash = "$2b$12$hashhash"
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = False
        config.enable_cloud_connectors = False
        config.postgres_password = "projectrag_password"

        # Should NOT raise - local is allowed even with auth
        validate_settings(config)


class TestProductionStartupGuardWithOIDC:
    """Tests for production environment with OIDC configuration."""

    def test_production_accepts_valid_oidc_configuration(self):
        """Production environment accepts valid OIDC configuration."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "oidc"
        config.oidc_issuer = "https://auth.example.com"
        config.oidc_audience = "projectrag-api"
        config.api_key_hash = ""
        config.api_key = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should NOT raise - valid OIDC configuration
        validate_settings(config)

    def test_production_with_oidc_missing_audience_fails(self):
        """Production environment with OIDC but missing audience fails."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "oidc"
        config.oidc_issuer = "https://auth.example.com"
        config.oidc_audience = ""  # Missing!
        config.api_key_hash = ""
        config.api_key = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should raise - no valid auth method is available
        with pytest.raises(RuntimeError, match="No valid authentication method configured"):
            validate_settings(config)

    def test_production_with_oidc_missing_issuer_fails(self):
        """Production environment with OIDC but missing issuer fails at startup guard."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "oidc"
        config.oidc_issuer = ""  # Missing!
        config.oidc_audience = "projectrag-api"
        config.api_key_hash = ""
        config.api_key = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should raise - startup guard detects no valid auth method
        with pytest.raises(RuntimeError, match="No valid authentication method configured"):
            validate_settings(config)


class TestProductionStartupGuardWithAPIKey:
    """Tests for production environment with API key configuration."""

    def test_production_accepts_valid_api_key_hash(self):
        """Production environment accepts bcrypt-hashed API key."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = "$2b$12$hashhash.hashhash.hashhash.hashhash.hashhash"
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should NOT raise - valid API key hash
        validate_settings(config)

    def test_production_accepts_plaintext_api_key_with_deprecation_warning(self):
        """Production accepts plaintext API key (deprecated) with warning."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = ""
        config.api_key = "my-secret-key"
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should NOT raise but emit deprecation warning
        with pytest.warns(DeprecationWarning, match="plaintext PROJECTRAG_API_KEY is deprecated"):
            validate_settings(config)


class TestProductionStartupGuardFailures:
    """Tests that prove the app refuses unsafe production startup."""

    def test_production_rejects_no_auth_configuration(self):
        """Production environment MUST have auth - refuses to start without it."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = ""  # No API key hash
        config.api_key = ""  # No plaintext API key
        config.oidc_issuer = ""  # No OIDC issuer
        config.oidc_audience = ""  # No OIDC audience
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should RAISE - no valid auth method
        with pytest.raises(RuntimeError) as exc_info:
            validate_settings(config)

        error_msg = str(exc_info.value)
        assert "No valid authentication method configured" in error_msg
        assert "APPLICATION STARTUP BLOCKED" in error_msg
        assert "production" in error_msg
        assert "Option 1: API Key" in error_msg
        assert "Option 2: OIDC/JWT" in error_msg
        assert "PROJECTRAG_API_KEY_HASH" in error_msg
        assert "PROJECTRAG_API_KEY" in error_msg
        assert "PROJECTRAG_OIDC_ISSUER" in error_msg
        assert "PROJECTRAG_OIDC_AUDIENCE" in error_msg
        assert "PROJECTRAG_OIDC_JWKS_URL" in error_msg

    def test_production_rejects_partial_oidc_configuration(self):
        """Production rejects incomplete OIDC setup."""
        config = MagicMock()
        config.app_env = "stage"  # Non-local
        config.postgres_host = "db.stage.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.stage.local:7200"
        config.ollama_url = "http://ollama.stage.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.stage.local:6379/0"
        config.qdrant_url = "http://qdrant.stage.local:6333"
        config.auth_required = True
        config.auth_mode = "oidc"
        config.oidc_issuer = "https://auth.example.com"  # Issuer present
        config.oidc_audience = ""  # But audience missing
        config.api_key_hash = ""  # No API key
        config.api_key = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should raise - startup guard blocks unsafe non-local startup
        with pytest.raises(RuntimeError, match="No valid authentication method configured"):
            validate_settings(config)

    def test_production_rejects_empty_whitespace_credentials(self):
        """Production rejects credentials that are empty or just whitespace."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = "   "  # Only whitespace
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should RAISE - whitespace treated as empty
        with pytest.raises(RuntimeError, match="No valid authentication method configured"):
            validate_settings(config)

    def test_dev_environment_rejects_no_auth(self):
        """Development environment also requires auth (not local)."""
        config = MagicMock()
        config.app_env = "dev"  # Not local
        config.postgres_host = "db.dev.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.dev.local:7200"
        config.ollama_url = "http://ollama.dev.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.dev.local:6379/0"
        config.qdrant_url = "http://qdrant.dev.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = ""
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "dev-password-123"

        # Should RAISE - dev is not local
        with pytest.raises(RuntimeError, match="No valid authentication method configured"):
            validate_settings(config)

    def test_startup_guard_lists_all_options_clearly(self):
        """Startup guard error message includes all configuration options."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = ""
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        with pytest.raises(RuntimeError) as exc_info:
            validate_settings(config)

        error_msg = str(exc_info.value)
        # Verify comprehensive error message
        assert "APPLICATION STARTUP BLOCKED" in error_msg
        assert "Option 1: API Key" in error_msg
        assert "Option 2: OIDC/JWT" in error_msg
        assert "PROJECTRAG_API_KEY_HASH" in error_msg
        assert "PROJECTRAG_API_KEY" in error_msg
        assert "Helper: python -c" in error_msg
        assert "PROJECTRAG_AUTH_MODE=oidc" in error_msg
        assert "PROJECTRAG_OIDC_ISSUER" in error_msg
        assert "PROJECTRAG_OIDC_AUDIENCE" in error_msg
        assert "PROJECTRAG_OIDC_JWKS_URL" in error_msg
        assert "APP_ENV=local" in error_msg


class TestProductionStartupGuardEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_both_api_key_and_oidc_configured_allowed(self):
        """Having both API key and OIDC configured is allowed (belt and suspenders)."""
        config = MagicMock()
        config.app_env = "production"
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "oidc"  # OIDC is primary
        config.oidc_issuer = "https://auth.example.com"
        config.oidc_audience = "projectrag-api"
        config.api_key_hash = "$2b$12$hashhash"  # Also has API key
        config.api_key = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should NOT raise - both auth methods available
        validate_settings(config)

    def test_case_insensitive_app_env(self):
        """App environment is case-insensitive."""
        config = MagicMock()
        config.app_env = "PRODUCTION"  # Uppercase
        config.postgres_host = "db.prod.local"
        config.postgres_db = "projectrag"
        config.graphdb_url = "http://graphdb.prod.local:7200"
        config.ollama_url = "http://ollama.prod.local:11434"
        config.top_k = 5
        config.chunk_size = 1000
        config.chunk_overlap = 150
        config.max_upload_size_bytes = 5242880
        config.max_upload_files_per_request = 1
        config.ingest_max_files_per_run = 200
        config.redis_url = "redis://redis.prod.local:6379/0"
        config.qdrant_url = "http://qdrant.prod.local:6333"
        config.auth_required = True
        config.auth_mode = "local"
        config.api_key_hash = "$2b$12$hashhash"
        config.api_key = ""
        config.oidc_issuer = ""
        config.oidc_audience = ""
        config.enforce_rbac = True
        config.enable_cloud_connectors = False
        config.postgres_password = "strong-password-here"

        # Should NOT raise - case is normalized
        validate_settings(config)
