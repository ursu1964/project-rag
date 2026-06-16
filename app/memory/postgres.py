"""PostgreSQL helpers for ProjectRAG."""

from collections.abc import Sequence
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover - dependency is provided by requirements.txt
    psycopg2 = None
    RealDictCursor = None

from app.core.config import settings


def get_connection():
    """Create a PostgreSQL connection using application settings."""
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed")

    return psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        cursor_factory=RealDictCursor,
    )


def fetch_all(query: str, params: Sequence[Any] = ()) -> list[dict[str, Any]]:
    """Run a query and return all rows as dictionaries."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            return list(cursor.fetchall())


def execute(query: str, params: Sequence[Any] = ()) -> None:
    """Run a write query and commit it."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
        connection.commit()
