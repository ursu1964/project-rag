"""PostgreSQL access helpers."""

from __future__ import annotations

from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings


def get_connection():  # noqa: ANN201
    return psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        connect_timeout=1,
        cursor_factory=RealDictCursor,
    )


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
    return [dict(row) for row in rows]


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
        connection.commit()
