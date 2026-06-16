"""PostgreSQL graph fact provenance store."""

from __future__ import annotations

import json
from typing import Any

from app.memory.postgres import execute, fetch_all


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
            json.dumps(metadata or {}),
        ),
    )


def list_graph_facts(entity: str) -> list[dict[str, Any]]:
    """List graph facts where entity appears as subject or object."""
    return fetch_all(
        """
        SELECT id, subject, predicate, object, source_document_id, source_chunk_id,
               confidence, created_at, metadata
        FROM graph_facts
        WHERE subject = %s OR object = %s
        ORDER BY created_at DESC
        """,
        (entity, entity),
    )
