"""Pytest configuration and fixtures for ProjectRAG tests."""

import os

import pytest


_EXTERNAL_MODULES = {
    "tests/test_background_jobs.py",
    "tests/test_eval_runner.py",
}

_EXTERNAL_NAME_FRAGMENTS = (
    "background_job",
    "idempotent",
    "golden_evaluation_with_job",
    "create_golden_evaluation_job",
    "connector_job_creation",
)


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "external_dependency: requires live Docker/PostgreSQL/GraphDB/Ollama services"
    )


@pytest.fixture(scope="session")
def postgres_available():
    """Check if PostgreSQL is available for testing."""
    try:
        import psycopg2

        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "projectrag")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")

        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname=db,
                user=user,
                password=password,
                connect_timeout=1,
            )
            conn.close()
            return True
        except Exception:
            return False
    except ImportError:
        return False


def _is_postgres_reachable() -> bool:
    """One-shot postgres reachability check used at collection time."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "projectrag"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            connect_timeout=1,
        )
        conn.close()
        return True
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    """Skip external_dependency tests when PostgreSQL is not reachable."""
    db_up = _is_postgres_reachable()
    skip_marker = pytest.mark.skip(reason="external_dependency: PostgreSQL not reachable in this environment")
    external_marker = pytest.mark.external_dependency

    for item in items:
        node_path = str(item.fspath).replace("\\", "/")
        in_external_module = any(node_path.endswith(m) for m in _EXTERNAL_MODULES)
        name_matches = any(frag in item.name for frag in _EXTERNAL_NAME_FRAGMENTS)

        if in_external_module or name_matches:
            item.add_marker(external_marker)
            if not db_up:
                item.add_marker(skip_marker)
