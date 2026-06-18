"""Document persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.core.logging import get_logger
from app.graph.graphdb_client import delete_graph_facts
from app.memory.postgres import fetch_all, get_connection
from app.security.tenant_context import current_tenant_id, with_tenant_metadata

logger = get_logger(__name__)


def document_exists_by_hash(file_hash: str, tenant_id: str | None = None) -> bool:
    rows = fetch_all(
        """
        SELECT id
        FROM documents
        WHERE file_hash = %s
          AND COALESCE(metadata->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (file_hash, current_tenant_id(tenant_id)),
    )
    return bool(rows)


def get_document_by_hash(file_hash: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    rows = fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE file_hash = %s
          AND COALESCE(metadata->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (file_hash, current_tenant_id(tenant_id)),
    )
    return rows[0] if rows else None


def get_document(document_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    rows = fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE id = %s
          AND COALESCE(metadata->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (document_id, current_tenant_id(tenant_id)),
    )
    return rows[0] if rows else None


def create_document(
    source_path: str,
    file_hash: str,
    metadata: dict[str, Any] | None = None,
    tenant_id: str | None = None,
) -> str:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (source, file_hash, metadata)
                VALUES (%s, %s, %s::jsonb)
                RETURNING id
                """,
                (source_path, file_hash, json.dumps(with_tenant_metadata(metadata, tenant_id))),
            )
            row = cursor.fetchone()
        connection.commit()
    return str(row["id"])


def list_documents(tenant_id: str | None = None) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE COALESCE(metadata->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        """,
        (current_tenant_id(tenant_id),),
    )


def delete_document(document_id: str, tenant_id: str | None = None) -> bool:
    """Delete one document and its derived graph facts/chunks.

    GraphDB cleanup is best-effort. PostgreSQL remains the source of truth for
    document lifecycle, so deletion should still complete if GraphDB is offline.
    """
    tenant = current_tenant_id(tenant_id)
    document = get_document(document_id, tenant_id=tenant)
    if document is None:
        return False

    graph_facts = fetch_all(
        """
        SELECT gf.subject, gf.predicate, gf.object
        FROM graph_facts gf
        JOIN documents d ON d.id = gf.source_document_id
        WHERE gf.source_document_id = %s
          AND COALESCE(d.metadata->>'tenant_id', 'local') = %s
        """,
        (document_id, tenant),
    )
    try:
        delete_graph_facts(graph_facts)
    except Exception as exc:  # pragma: no cover - external GraphDB availability varies
        logger.warning("GraphDB cleanup failed for document %s: %s", document_id, exc)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM graph_facts
                WHERE source_document_id = %s
                  AND source_document_id IN (
                    SELECT id FROM documents
                    WHERE id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s
                  )
                """,
                (document_id, document_id, tenant),
            )
            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = %s
                  AND COALESCE(metadata->>'tenant_id', 'local') = %s
                RETURNING id
                """,
                (document_id, tenant),
            )
            row = cursor.fetchone()
        connection.commit()
    return row is not None
