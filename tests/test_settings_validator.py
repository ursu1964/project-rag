from types import SimpleNamespace

import pytest

from app.core.settings_validator import validate_settings


def _settings(**overrides):
    values = {
        "postgres_host": "localhost",
        "postgres_db": "projectrag",
        "graphdb_url": "http://localhost:7200",
        "ollama_url": "http://localhost:11434",
        "top_k": 5,
        "chunk_size": 1000,
        "chunk_overlap": 150,
        "max_upload_size_bytes": 1024,
        "max_upload_files_per_request": 1,
        "ingest_max_files_per_run": 100,
        "auth_mode": "local",
        "auth_required": False,
        "oidc_issuer": "",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_validate_settings_accepts_valid_config():
    validate_settings(_settings())


def test_validate_settings_rejects_empty_postgres_host():
    with pytest.raises(RuntimeError, match="POSTGRES_HOST"):
        validate_settings(_settings(postgres_host=""))


def test_validate_settings_rejects_bad_urls():
    with pytest.raises(RuntimeError, match="GRAPHDB_URL"):
        validate_settings(_settings(graphdb_url="localhost:7200"))


def test_validate_settings_rejects_bad_chunk_overlap():
    with pytest.raises(RuntimeError, match="CHUNK_OVERLAP"):
        validate_settings(_settings(chunk_size=100, chunk_overlap=100))


def test_validate_settings_rejects_bad_top_k():
    with pytest.raises(RuntimeError, match="TOP_K"):
        validate_settings(_settings(top_k=0))


def test_validate_settings_rejects_unknown_auth_mode():
    with pytest.raises(RuntimeError, match="AUTH_MODE"):
        validate_settings(_settings(auth_mode="unknown"))


def test_validate_settings_requires_oidc_issuer_when_auth_required():
    with pytest.raises(RuntimeError, match="OIDC_ISSUER"):
        validate_settings(_settings(auth_mode="oidc", auth_required=True, oidc_issuer=""))


def test_validate_settings_rejects_invalid_oidc_issuer_url():
    with pytest.raises(RuntimeError, match="OIDC_ISSUER"):
        validate_settings(_settings(oidc_issuer="issuer.local"))


def test_validate_settings_rejects_non_positive_upload_limit():
    with pytest.raises(RuntimeError, match="MAX_UPLOAD_SIZE_BYTES"):
        validate_settings(_settings(max_upload_size_bytes=0))


def test_validate_settings_rejects_non_positive_ingest_file_limit():
    with pytest.raises(RuntimeError, match="INGEST_MAX_FILES_PER_RUN"):
        validate_settings(_settings(ingest_max_files_per_run=0))
