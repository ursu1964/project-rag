"""Deterministic volatility metric helpers."""

from __future__ import annotations

from typing import Iterable


def calculate_volatility(values: Iterable[float]) -> float:
    """Calculate normalized average absolute change between sequential values."""
    numbers = [float(value) for value in values]
    if len(numbers) < 2:
        return 0.0

    deltas = [abs(numbers[index] - numbers[index - 1]) for index in range(1, len(numbers))]
    average_delta = sum(deltas) / len(deltas)
    scale = max(abs(value) for value in numbers) or 1.0
    return round(min(1.0, average_delta / scale), 6)
