"""Deterministic lexical reranker."""

from __future__ import annotations

import re
from typing import Any


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z0-9_]+", text) if len(token) > 2}


def _item_text(item: dict[str, Any]) -> str:
    return " ".join(str(item.get(key) or "") for key in ("content", "chunk_text", "subject", "predicate", "object", "fact_text", "value"))


def _score(question_tokens: set[str], item: dict[str, Any]) -> float:
    item_tokens = _tokens(_item_text(item))
    if not question_tokens or not item_tokens:
        return 0.0
    return round(len(question_tokens & item_tokens) / len(question_tokens), 6)


def rerank_context(question: str, vector_context: list[dict[str, Any]], graph_context: list[dict[str, Any]]) -> dict[str, Any]:
    q_tokens = _tokens(question)
    vector = [{**item, "rerank_score": _score(q_tokens, item)} for item in vector_context]
    graph = [{**item, "rerank_score": _score(q_tokens, item)} for item in graph_context]
    vector.sort(key=lambda item: item.get("rerank_score", 0.0), reverse=True)
    graph.sort(key=lambda item: item.get("rerank_score", 0.0), reverse=True)
    return {"vector": vector, "graph": graph, "explanation": "deterministic_token_overlap"}
