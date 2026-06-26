"""Optional cache service facade."""

from __future__ import annotations

_COUNTERS: dict[str, int] = {}


def increment_window_counter(key: str, ttl_seconds: int = 70) -> int | None:
    """Increment a best-effort local counter.

    Returns None when a distributed cache is unavailable in production designs;
    this local fallback keeps tests and single-process deployments deterministic.
    """
    _COUNTERS[key] = _COUNTERS.get(key, 0) + 1
    return _COUNTERS[key]


def clear_counters() -> None:
    _COUNTERS.clear()

_JSON_CACHE: dict[str, object] = {}


def get_json(key: str):  # noqa: ANN201
    return _JSON_CACHE.get(key)


def set_json(key: str, value, ttl_seconds: int = 300) -> None:  # noqa: ANN001
    _JSON_CACHE[key] = value


def clear_json() -> None:
    _JSON_CACHE.clear()
