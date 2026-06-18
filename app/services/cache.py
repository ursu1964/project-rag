"""Redis-backed cache helpers with safe in-memory fallback."""

from __future__ import annotations

import json
import time
from typing import Any

from app.core.config import settings

try:  # optional in local/unit-test environments
    import redis
except ImportError:  # pragma: no cover
    redis = None

_memory_cache: dict[str, tuple[float, Any]] = {}


def _client():
    if redis is None or not settings.redis_url:
        return None
    try:
        return redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        return None


def get_json(key: str) -> Any | None:
    client = _client()
    if client is not None:
        value = client.get(key)
        return json.loads(value) if value else None

    item = _memory_cache.get(key)
    if not item:
        return None
    expires_at, value = item
    if expires_at and expires_at < time.time():
        _memory_cache.pop(key, None)
        return None
    return value


def set_json(key: str, value: Any, ttl_seconds: int = 300) -> None:
    client = _client()
    if client is not None:
        client.setex(key, ttl_seconds, json.dumps(value, default=str))
        return
    _memory_cache[key] = (time.time() + ttl_seconds if ttl_seconds else 0, value)


def delete_prefix(prefix: str) -> int:
    client = _client()
    deleted = 0
    if client is not None:
        for key in client.scan_iter(f"{prefix}*"):
            deleted += int(client.delete(key))
        return deleted
    for key in list(_memory_cache):
        if key.startswith(prefix):
            _memory_cache.pop(key, None)
            deleted += 1
    return deleted


def increment_window_counter(key: str, ttl_seconds: int) -> int | None:
    """Increment a Redis counter for a fixed window.

    Returns None when Redis is unavailable so callers can use their own local
    fallback without making request handling depend on Redis availability.
    """
    client = _client()
    if client is None:
        return None
    try:
        value = int(client.incr(key))
        if value == 1:
            client.expire(key, ttl_seconds)
        return value
    except Exception:
        return None
