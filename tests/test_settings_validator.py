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
