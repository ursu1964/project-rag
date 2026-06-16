"""Document persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import fetch_all, get_connection


def document_exists_by_hash(file_hash: str) -> bool:
    rows = fetch_all("SELECT id FROM documents WHERE file_hash = %s LIMIT 1", (file_hash,))
    return bool(rows)


def create_document(source_path: str, file_hash: str, metadata: dict[str, Any] | None = None) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (source, file_hash, metadata)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (source_path, file_hash, json.dumps(metadata or {})),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def list_documents() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        ORDER BY created_at DESC
        """
    )
