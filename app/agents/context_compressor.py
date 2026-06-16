"""Context compression agent."""

from __future__ import annotations

_MAX_CHARS = 700


def _shorten(value: str, max_chars: int = _MAX_CHARS) -> str:
    value = value.strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _compress_vector_item(item: dict) -> dict:
    metadata = item.get("metadata") or {}
    return {
        "filename": metadata.get("filename") or metadata.get("source") or item.get("filename"),
        "distance": item.get("distance"),
        "content": _shorten(str(item.get("content") or item.get("chunk_text") or "")),
        "metadata": metadata,
    }


def run(state: dict) -> dict:
    merged = state.get("merged_context") or {}
    vector_context = merged.get("vector") or state.get("vector_context") or []
    graph_context = merged.get("graph") or state.get("graph_context") or {}
    memory_context = merged.get("memory") or state.get("memory_context") or []

    compressed_context = {
        "memory": memory_context,
        "vector": [_compress_vector_item(item) if isinstance(item, dict) else item for item in vector_context],
        "graph_facts": graph_context,
    }

    return {**state, "compressed_context": compressed_context}
