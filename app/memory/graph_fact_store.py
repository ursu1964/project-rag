"""PostgreSQL graph fact provenance store."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all
from app.security.tenant_context import current_tenant_id, with_tenant_metadata


def store_graph_fact(
    subject: str,
    predicate: str,
    object: str,
    source_document_id: str | None = None,
    source_chunk_id: str | None = None,
    confidence: float = 0.8,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Store one graph fact with optional provenance."""
    tenant_metadata = with_tenant_metadata(metadata)
    execute(
        """
        INSERT INTO graph_facts (
            subject, predicate, object, source_document_id, source_chunk_id, confidence, metadata
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
        """,
        (
            subject,
            predicate,
            object,
            source_document_id,
            source_chunk_id,
            confidence,
            json.dumps(tenant_metadata),
        ),
    )


def list_graph_facts(entity: str, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """List graph facts where entity appears as subject or object."""
    tenant = current_tenant_id(tenant_id)
    return fetch_all(
        """
        SELECT id, subject, predicate, object, source_document_id, source_chunk_id,
               confidence, created_at, metadata
        FROM graph_facts
        WHERE (subject = %s OR object = %s)
          AND COALESCE(metadata->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        """,
        (entity, entity, tenant),
    )


def list_all_graph_facts(limit: int = 1000, tenant_id: str | None = None) -> list[dict[str, Any]]:
    """List recent graph facts for export/visualization."""
    tenant = current_tenant_id(tenant_id)
    return fetch_all(
        """
        SELECT id, subject, predicate, object, source_document_id, source_chunk_id,
               confidence, created_at, metadata
        FROM graph_facts
        WHERE COALESCE(metadata->>'tenant_id', 'local') = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (tenant, limit),
    )


def count_graph_facts_for_document(document_id: str, tenant_id: str | None = None) -> int:
    """Count graph facts associated with a source document."""
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT COUNT(*) AS count
        FROM graph_facts
        WHERE source_document_id = %s
          AND COALESCE(metadata->>'tenant_id', 'local') = %s
        """,
        (document_id, tenant),
    )
    return int(rows[0]["count"]) if rows else 0


def resolve_graph_entity(candidate: str, tenant_id: str | None = None) -> str | None:
    """Return a known graph entity matching a detected query candidate."""
    text = str(candidate or "").strip()
    if not text:
        return None
    tenant = current_tenant_id(tenant_id)
    rows = fetch_all(
        """
        SELECT subject, object
        FROM graph_facts
        WHERE COALESCE(metadata->>'tenant_id', 'local') = %s
          AND (
            lower(subject) = lower(%s)
            OR lower(object) = lower(%s)
            OR subject ILIKE %s
            OR object ILIKE %s
          )
        ORDER BY
          CASE
            WHEN lower(subject) = lower(%s) THEN 0
            WHEN lower(object) = lower(%s) THEN 1
            ELSE 2
          END,
          created_at DESC
        LIMIT 1
        """,
        (tenant, text, text, f"%{text}%", f"%{text}%", text, text),
    )
    if not rows:
        return None
    row = rows[0]
    for key in ("subject", "object"):
        value = str(row.get(key) or "").strip()
        if value and text.lower() in value.lower():
            return value
    return None
