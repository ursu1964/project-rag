"""Local in-memory cognitive cache with TTL and invalidation."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any

QUESTION = "question"
GRAPH_QUERY = "graph_query"
MODEL_RESPONSE = "model_response"
_CACHE_TYPES = {QUESTION, GRAPH_QUERY, MODEL_RESPONSE}
_DEFAULT_TTL_SECONDS = 300


@dataclass(frozen=True)
class CacheEntry:
    key: str
    cache_type: str
    value: Any
    expires_at: float
    tags: tuple[str, ...]
    created_at: float


_CACHE: dict[str, CacheEntry] = {}


def _stable_key(cache_type: str, key: str) -> str:
    return hashlib.sha256(f"{cache_type}:{key}".encode()).hexdigest()


def _validate_cache_type(cache_type: str) -> str:
    normalized = str(cache_type).lower()
    if normalized not in _CACHE_TYPES:
        raise ValueError(f"Unsupported cache type: {cache_type}")
    return normalized


def set_cache(cache_type: str, key: str, value: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS, tags=None) -> str:
    normalized = _validate_cache_type(cache_type)
    cache_key = _stable_key(normalized, key)
    now = time.time()
    _CACHE[cache_key] = CacheEntry(cache_key, normalized, value, now + max(1, int(ttl_seconds)), tuple(tags or ()), now)
    return cache_key


def get_cache(cache_type: str, key: str) -> Any | None:
    normalized = _validate_cache_type(cache_type)
    cache_key = _stable_key(normalized, key)
    entry = _CACHE.get(cache_key)
    if entry is None:
        return None
    if entry.expires_at < time.time():
        _CACHE.pop(cache_key, None)
        return None
    return entry.value


def cache_question(question: str, answer: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    return set_cache(QUESTION, question, answer, ttl_seconds, tags=("question",))


def get_cached_question(question: str) -> Any | None:
    return get_cache(QUESTION, question)


def cache_graph_query(query: str, result: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    return set_cache(GRAPH_QUERY, query, result, ttl_seconds, tags=("graph",))


def get_cached_graph_query(query: str) -> Any | None:
    return get_cache(GRAPH_QUERY, query)


def cache_model_response(prompt: str, response: Any, ttl_seconds: int = _DEFAULT_TTL_SECONDS) -> str:
    return set_cache(MODEL_RESPONSE, prompt, response, ttl_seconds, tags=("model",))


def get_cached_model_response(prompt: str) -> Any | None:
    return get_cache(MODEL_RESPONSE, prompt)


def invalidate_by_tag(tag: str) -> int:
    keys = [key for key, entry in _CACHE.items() if tag in entry.tags]
    for key in keys:
        _CACHE.pop(key, None)
    return len(keys)


def invalidate_by_document_ingestion() -> int:
    count = len(_CACHE)
    _CACHE.clear()
    return count


def clear_cache() -> None:
    _CACHE.clear()


def cache_stats() -> dict[str, int]:
    now = time.time()
    for key, entry in list(_CACHE.items()):
        if entry.expires_at < now:
            _CACHE.pop(key, None)
    stats = {QUESTION: 0, GRAPH_QUERY: 0, MODEL_RESPONSE: 0, "total": len(_CACHE)}
    for entry in _CACHE.values():
        stats[entry.cache_type] += 1
    return stats
