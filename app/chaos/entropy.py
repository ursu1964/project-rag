"""Deterministic entropy metric helpers."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable


def calculate_entropy(values: Iterable[Any]) -> float:
    """Calculate Shannon entropy for a sequence of discrete values."""
    items = list(values)
    if not items:
        return 0.0

    counts = Counter(items)
    total = len(items)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    return round(entropy, 6)
