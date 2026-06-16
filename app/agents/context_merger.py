"""Context merge agent."""

from __future__ import annotations

import json
from typing import Any

from app.rag.reranker import rerank_context
from app.rag.scoring import score_graph_result, score_memory_result, score_vector_result, weighted_score

_DEFAULT_TOP_EVIDENCE = 8


def _dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = json.dumps(item, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _flatten_graph_context(graph_context: Any) -> list[dict[str, Any]]:
    if isinstance(graph_context, list):
        return [item for item in graph_context if isinstance(item, dict)]
    if not isinstance(graph_context, dict):
        return []

    facts: list[dict[str, Any]] = []
    for section in ("incoming", "outgoing", "paths"):
        values = graph_context.get(section) or []
        if isinstance(values, list):
            for value in values:
                facts.append({"section": section, **value} if isinstance(value, dict) else {"section": section, "value": value})
    if not facts and graph_context:
        facts.append(graph_context)
    return facts


def _score_vector_items(route: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for item in items:
        vector_score = max(float(item.get("rerank_score", 0.0)), score_vector_result(item.get("distance")))
        score = weighted_score(route, vector_score=vector_score, graph_score=0.0, memory_score=0.0)
        scored.append({**item, "evidence_score": round(score, 6), "evidence_type": "vector"})
    return scored


def _score_graph_items(route: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for item in items:
        graph_score = max(float(item.get("rerank_score", 0.0)), score_graph_result(item))
        score = weighted_score(route, vector_score=0.0, graph_score=graph_score, memory_score=0.0)
        scored.append({**item, "evidence_score": round(score, 6), "evidence_type": "graph"})
    return scored


def _score_memory_items(route: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for item in items:
        score = weighted_score(route, vector_score=0.0, graph_score=0.0, memory_score=score_memory_result(item))
        scored.append({**item, "evidence_score": round(score, 6), "evidence_type": "memory"})
    return scored


def run(state: dict) -> dict:
    question = str(state.get("question") or state.get("query") or "")
    route = str(state.get("route") or "hybrid")
    top_k = int(state.get("evidence_top_k", _DEFAULT_TOP_EVIDENCE))

    memory_context = _dedupe([item for item in (state.get("memory_context") or []) if isinstance(item, dict)])
    vector_context = _dedupe([item for item in (state.get("vector_context") or []) if isinstance(item, dict)])
    graph_facts = _dedupe(_flatten_graph_context(state.get("graph_context") or {}))

    reranked = rerank_context(question, vector_context, graph_facts)
    scored_vector = _score_vector_items(route, reranked["vector"])
    scored_graph = _score_graph_items(route, reranked["graph"])
    scored_memory = _score_memory_items(route, memory_context)

    evidence = sorted(scored_vector + scored_graph + scored_memory, key=lambda item: item["evidence_score"], reverse=True)[:top_k]

    merged_context = {
        "memory": scored_memory[:top_k],
        "vector": scored_vector[:top_k],
        "graph": scored_graph[:top_k],
    }
    evidence_summary = {
        "total_evidence": len(evidence),
        "vector_count": len(scored_vector),
        "graph_count": len(scored_graph),
        "memory_count": len(scored_memory),
        "top_score": evidence[0]["evidence_score"] if evidence else 0.0,
        "rerank_explanation": reranked["explanation"],
    }

    return {**state, "merged_context": merged_context, "evidence": evidence, "evidence_summary": evidence_summary}
