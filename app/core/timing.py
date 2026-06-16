"""Lightweight timing helpers."""

from __future__ import annotations

import time


def now_ms() -> int:
    """Return a monotonic timestamp in milliseconds."""
    return int(time.perf_counter() * 1000)


def elapsed_ms(start_ms: int) -> int:
    """Return elapsed milliseconds since a now_ms() timestamp."""
    return max(0, now_ms() - start_ms)
