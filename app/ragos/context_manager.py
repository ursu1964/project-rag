"""Local context manager for bounded prompt context assembly."""

from __future__ import annotations

from typing import Any


def assemble_context(*contexts: dict[str, Any], max_items: int = 20) -> dict[str, Any]:
    """Merge context dictionaries and bound list sizes."""
    merged: dict[str, Any] = {}
    for context in contexts:
        for key, value in context.items():
            if isinstance(value, list):
                merged.setdefault(key, [])
                merged[key].extend(value)
                merged[key] = merged[key][:max_items]
            elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
    return {"context": merged, "max_items": max_items, "execution": "assembly_only"}


def summarize_context(context: dict[str, Any]) -> dict[str, Any]:
    """Return lightweight metadata about assembled context."""
    return {
        "keys": sorted(context.keys()),
        "list_counts": {key: len(value) for key, value in context.items() if isinstance(value, list)},
    }
