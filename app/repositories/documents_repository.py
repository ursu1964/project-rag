"""Document persistence repository."""

from __future__ import annotations

import json
from typing import Any

from app.core.logging import get_logger
from app.graph.graphdb_client import delete_graph_facts
from app.memory.postgres import fetch_all, get_connection
from app.security.tenant_context import current_tenant_id, with_tenant_metadata

logger = get_logger(__name__)


def get_document_by_hash(file_hash: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE file_hash = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (file_hash, tenant),
    )
    return rows[0] if rows else None


def get_document(document_id: str, tenant_id: str | None = None) -> dict[str, Any] | None:
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s
        LIMIT 1
        """,
        (document_id, tenant),
    )
    return rows[0] if rows else None


def create_document(source_path: str, file_hash: str, metadata: dict[str, Any] | None = None, tenant_id: str | None = None) -> str:
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
    tenant = current_tenant_id(tenant_id)
    return fetch_all(
        """
        SELECT id, source, file_hash, metadata, created_at, updated_at
        FROM documents
        WHERE COALESCE(metadata->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        """,
        (tenant,),
    )


def delete_document(document_id: str, tenant_id: str | None = None) -> bool:
    tenant = current_tenant_id(tenant_id)
    graph_facts = fetch_all(
        """
        SELECT subject, predicate, object
        FROM graph_facts
        WHERE source_document_id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s
        """,
        (document_id, tenant),
    )
    try:
        delete_graph_facts(graph_facts)
    except Exception as exc:  # pragma: no cover
        logger.warning("GraphDB cleanup failed for document %s: %s", document_id, exc)
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM graph_facts WHERE source_document_id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s", (document_id, tenant))
            cursor.execute("DELETE FROM documents WHERE id = %s AND COALESCE(metadata->>'tenant_id', 'local') = %s RETURNING id", (document_id, tenant))
            row = cursor.fetchone()
        connection.commit()
    return row is not None
