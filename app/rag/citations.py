"""Citation builders for query responses."""

from __future__ import annotations

from typing import Any


def _short_text(value: Any, limit: int = 240) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= limit else f"{text[: limit - 1]}…"


def _graph_value(binding: dict[str, Any], key: str) -> str:
    value = binding.get(key)
    if isinstance(value, dict):
        return str(value.get("value") or "")
    return str(value or "")


def _vector_citations(rows: list[Any]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        source = metadata.get("filename") or metadata.get("source") or row.get("document_id") or "vector"
        citations.append(
            {
                "id": f"V{index}",
                "type": "vector",
                "source": str(source),
                "document_id": row.get("document_id"),
                "chunk_index": row.get("chunk_index"),
                "excerpt": _short_text(row.get("content")),
            }
        )
    return citations


def _memory_citations(rows: list[Any]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        citations.append(
            {
                "id": f"M{index}",
                "type": "memory",
                "source": str(row.get("memory_type") or row.get("key") or "memory"),
                "memory_id": row.get("id"),
                "excerpt": _short_text(row.get("value") or row.get("content") or row),
            }
        )
    return citations


def _graph_citations(graph: Any) -> list[dict[str, Any]]:
    if not isinstance(graph, dict):
        return []
    citations: list[dict[str, Any]] = []
    for section in ("incoming", "outgoing", "paths"):
        rows = graph.get(section) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            index = len(citations) + 1
            subject = _graph_value(row, "subject") or _graph_value(row, "source") or graph.get("entity")
            predicate = _graph_value(row, "predicate") or _graph_value(row, "relationship") or section
            obj = _graph_value(row, "object") or _graph_value(row, "target")
            fact = " ".join(part for part in (subject, predicate, obj) if part)
            citations.append(
                {
                    "id": f"G{index}",
                    "type": "graph",
                    "source": str(graph.get("entity") or "graph"),
                    "section": section,
                    "excerpt": _short_text(fact or row),
                }
            )
    return citations


def build_citations(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    """Build compact citations from vector, graph, and memory evidence."""
    vector = evidence.get("vector") if isinstance(evidence.get("vector"), list) else []
    memory = evidence.get("memory") if isinstance(evidence.get("memory"), list) else []
    graph = evidence.get("graph")
    return [*_vector_citations(vector), *_graph_citations(graph), *_memory_citations(memory)]
