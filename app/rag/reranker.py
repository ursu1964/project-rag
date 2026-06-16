"""Deterministic context reranking for MVP retrieval."""

from __future__ import annotations

import re
from typing import Any

_GRAPH_TERMS = {"depend", "depends", "dependency", "dependencies", "connected", "relationship", "graph", "impact", "breaks", "fails"}


def _keywords(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text) if len(token) > 2}


def _route(question: str) -> str:
    words = _keywords(question)
    return "graph" if words & _GRAPH_TERMS else "vector"


def _text_for_item(item: dict[str, Any]) -> str:
    parts = []
    for key in ("content", "text", "chunk_text", "subject", "predicate", "object"):
        if item.get(key) is not None:
            parts.append(str(item[key]))
    if item.get("metadata"):
        parts.append(str(item["metadata"]))
    return " ".join(parts)


def _distance_score(distance: Any) -> float:
    try:
        value = float(distance)
    except (TypeError, ValueError):
        return 0.0
    if value < 0:
        return 0.0
    return 1.0 / (1.0 + value)


def _overlap_score(question_terms: set[str], item: dict[str, Any]) -> float:
    if not question_terms:
        return 0.0
    item_terms = _keywords(_text_for_item(item))
    return len(question_terms & item_terms) / len(question_terms)


def rerank_context(question: str, vector_context: list[dict], graph_context: list[dict]) -> dict:
    """Rerank vector and graph context using deterministic lexical features."""
    question_terms = _keywords(question)
    route = _route(question)
    graph_weight = 1.4 if route == "graph" else 1.0
    vector_weight = 1.2 if route == "vector" else 1.0

    ranked_vector = []
    for item in vector_context:
        score = vector_weight * (_overlap_score(question_terms, item) + _distance_score(item.get("distance")))
        ranked_vector.append({**item, "rerank_score": round(score, 6)})

    ranked_graph = []
    for item in graph_context:
        score = graph_weight * (_overlap_score(question_terms, item) + 0.35)
        ranked_graph.append({**item, "rerank_score": round(score, 6)})

    ranked_vector.sort(key=lambda item: item["rerank_score"], reverse=True)
    ranked_graph.sort(key=lambda item: item["rerank_score"], reverse=True)

    return {
        "vector": ranked_vector,
        "graph": ranked_graph,
        "explanation": f"Deterministic rerank used keyword overlap, vector distance, graph presence bonus, and {route} route awareness.",
    }
