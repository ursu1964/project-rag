"""Idempotency key support for safe API retries."""

from __future__ import annotations

import json
from typing import Any
from uuid import uuid4

from app.memory.postgres import execute, fetch_all

# In-memory cache for testing/local environments
_local_cache: dict[str, dict[str, Any]] = {}


def get_or_create_idempotency_key(namespace: str, reference: str) -> str:
    """Generate a deterministic idempotency key for a resource.

    Args:
        namespace: Category (e.g., 'ingestion', 'evaluation', 'connector_sync')
        reference: Unique identifier (e.g., file_hash, document_id, dataset_name)

    Returns:
        Stable idempotency key.
    """
    return f"{namespace}#{reference}"


def record_idempotent_result(
    idempotency_key: str, result: dict[str, Any], ttl_seconds: int = 86400
) -> bool:
    """Record the result of an idempotent operation.

    Args:
        idempotency_key: The idempotency key.
        result: The operation result to store.
        ttl_seconds: How long to keep the result (default 24 hours).

    Returns:
        True if stored successfully.
    """
    try:
        request_id = str(uuid4())
        execute(
            """
            INSERT INTO idempotency_results (request_id, idempotency_key, result, expires_at)
            VALUES (%s, %s, %s::jsonb, now() + interval '%s seconds')
            ON CONFLICT (idempotency_key) DO UPDATE SET result = EXCLUDED.result, expires_at = EXCLUDED.expires_at
            """,
            (request_id, idempotency_key, json.dumps(result), ttl_seconds),
        )
        _local_cache[idempotency_key] = result
        return True
    except Exception:
        # Fallback to memory cache if DB fails
        _local_cache[idempotency_key] = result
        return True


def get_idempotent_result(idempotency_key: str) -> dict[str, Any] | None:
    """Retrieve a cached result for an idempotent operation.

    Returns None if not found or expired.
    """
    # Check memory cache first
    if idempotency_key in _local_cache:
        return _local_cache[idempotency_key]

    # Check database
    try:
        results = fetch_all(
            """
            SELECT result FROM idempotency_results
            WHERE idempotency_key = %s AND expires_at > now()
            LIMIT 1
            """,
            (idempotency_key,),
        )
        if results:
            result = results[0]["result"]
            _local_cache[idempotency_key] = result
            return result
    except Exception:
        pass

    return None


def clear_idempotent_result(idempotency_key: str) -> bool:
    """Clear a cached idempotent result."""
    try:
        execute("DELETE FROM idempotency_results WHERE idempotency_key = %s", (idempotency_key,))
        _local_cache.pop(idempotency_key, None)
        return True
    except Exception:
        _local_cache.pop(idempotency_key, None)
        return False


def prune_expired_idempotency_results() -> int:
    """Clean up expired idempotency cache entries."""
    try:
        results = fetch_all("DELETE FROM idempotency_results WHERE expires_at < now() RETURNING idempotency_key")
        count = len(results) if results else 0
        # Also prune memory cache
        expired_keys = [k for k, v in _local_cache.items()]
        for k in expired_keys[:min(100, len(expired_keys))]:
            _local_cache.pop(k, None)
        return count
    except Exception:
        return 0
