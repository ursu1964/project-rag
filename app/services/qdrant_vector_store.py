"""Optional Qdrant vector store facade."""

from __future__ import annotations

from typing import Any


def search(embedding: list[float], top_k: int = 5, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return []
