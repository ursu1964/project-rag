"""Local in-memory cognitive cache with TTL and ingestion invalidation.

This cache is intentionally lightweight and single-process. It is suitable for
local MVP use and tests, not distributed deployments.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

QUESTION = "question"
GRAPH_QUERY = "graph_query"
MODEL_RESPONSE = "model_response"
_CACHE_TYPES = {QUESTION, GRAPH_QUERY, MODEL_RESPONSE}


@dataclass(frozen=True)
class CacheEntry:
    key: str
    cache_type: str
    value: Any
    expires_at: float
    tags: tuple[str, ...]
    created_at: float


_CACHE: dict[str, CacheEntry] = {}
_DEFAULT_TTL_SECONDS = 300


def _stable_key(cache_type: str, key: str) -> str:
    raw = f"{cache_type}:{key}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _validate_cache_type(cache_type: str) -> str:
    normalized = str(cache_type).lower()
    if normalized not in _CACHE_TYPES:
        raise ValueError(f"Unsupported cache type: {cache_type}")
    return normalized


def set_cache(
    cache_type: str,
    key: str,
    value: Any,
    ttl_seconds: int = _DEFAULT_TTL_SECONDS,
    tags: list[str] | tuple[str, ...] | None = None,
) -> str:
    """Store a cache entry and return its internal cache key."""
    normalized_type = _validate_cache_type(cache_type)
    now = time.time()
    cache_key = _stable_key(normalized_type, key)
    _CACHE[cache_key] = CacheEntry(
        key=key,
        cache_type=normalized_type,
        value=value,
        expires_at=now + max(1, int(ttl_seconds)),
        tags=tuple(tags or ()),
        created_at=now,
    )
    return cache_key


def get_cache(cache_type: str, key: str) -> Any | None:
    """Return cached value when present and not expired."""
    normalized_type = _validate_cache_type(cache_type)
    cache_key = _stable_key(normalized_type, key)
    entry = _CACHE.get(cache_key)
    if entry is None:
        return None
    if entry.expires_at < time.time():
        _CACHE.pop(cache_key, None)
        return None
    return entry.value


def cache_question(question: str, answer: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    """Cache a repeated question answer."""
    return set_cache(QUESTION, question, answer, ttl_seconds, tags=("question",))


def get_cached_question(question: str) -> Any | None:
    """Return cached answer for a repeated question."""
    return get_cache(QUESTION, question)


def cache_graph_query(query: str, result: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    """Cache a GraphDB query result."""
    return set_cache(GRAPH_QUERY, query, result, ttl_seconds, tags=("graph",))


def get_cached_graph_query(query: str) -> Any | None:
    """Return cached GraphDB query result."""
    return get_cache(GRAPH_QUERY, query)


def cache_model_response(prompt: str, response: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    """Cache an expensive model response."""
    return set_cache(MODEL_RESPONSE, prompt, response, ttl_seconds, tags=("model",))


def get_cached_model_response(prompt: str) -> Any | None:
    """Return cached model response."""
    return get_cache(MODEL_RESPONSE, prompt)


def invalidate_by_tag(tag: str) -> int:
    """Invalidate cache entries with a matching tag."""
    keys = [cache_key for cache_key, entry in _CACHE.items() if tag in entry.tags]
    for cache_key in keys:
        _CACHE.pop(cache_key, None)
    return len(keys)


def invalidate_by_document_ingestion() -> int:
    """Invalidate caches affected by document ingestion.

    Ingestion can change vector, graph, and answer evidence, so all local cache
    entries are invalidated for correctness.
    """
    count = len(_CACHE)
    _CACHE.clear()
    return count


def clear_cache() -> None:
    """Clear all cache entries. Intended for tests and local reset."""
    _CACHE.clear()


def cache_stats() -> dict[str, int]:
    """Return current cache entry counts by type."""
    now = time.time()
    expired = [key for key, entry in _CACHE.items() if entry.expires_at < now]
    for key in expired:
        _CACHE.pop(key, None)
    stats = {QUESTION: 0, GRAPH_QUERY: 0, MODEL_RESPONSE: 0, "total": len(_CACHE)}
    for entry in _CACHE.values():
        stats[entry.cache_type] += 1
    return stats
