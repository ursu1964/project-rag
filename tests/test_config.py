from app.core.config import Settings


def test_settings_defaults_include_env_example_fields():
    settings = Settings()

    assert settings.app_env == "local"
    assert settings.postgres_db == "projectrag"
    assert settings.graphdb_repository == "projectrag"
    assert settings.ollama_url.startswith("http")
    assert settings.chunk_size > settings.chunk_overlap
    assert settings.top_k > 0
