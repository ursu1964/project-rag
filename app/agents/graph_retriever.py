"""Graph retrieval agent."""

from __future__ import annotations

import re
from typing import Any

from app.core.timing import elapsed_ms, now_ms
from app.graph.graphdb_client import sparql_query
from app.graph.sparql_templates import (
    impact_query,
    incoming_relationships_query,
    outgoing_relationships_query,
    two_hop_dependency_query,
)
from app.graph.triple_builder import sanitize_entity
from app.memory.graph_fact_store import resolve_graph_entity

_STOP_WORDS = {
    "what",
    "which",
    "who",
    "where",
    "when",
    "why",
    "how",
    "does",
    "do",
    "is",
    "are",
    "the",
    "a",
    "an",
    "depend",
    "depends",
    "dependency",
    "dependencies",
    "related",
    "to",
    "on",
    "of",
    "for",
    "breaks",
    "break",
    "if",
    "fails",
    "fail",
}


def _bindings(result: dict[str, Any]) -> list[dict[str, Any]]:
    return list(result.get("results", {}).get("bindings", [])) if isinstance(result, dict) else []


def _binding_value(binding: dict[str, Any], key: str) -> str:
    value = binding.get(key)
    if isinstance(value, dict):
        value = value.get("value")
    text = str(value or "")
    if text.startswith("http://projectrag.local/"):
        return text.rsplit("/", 1)[-1]
    return text.rsplit("#", 1)[-1] if "#" in text else text


def _normalize_bindings(entity: str, section: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        item = {key: _binding_value(row, key) for key in row}
        if section == "outgoing":
            item["subject"] = entity
            item["fact_text"] = " ".join(
                part for part in (entity, item.get("predicate"), item.get("object")) if part
            )
        elif section == "incoming":
            item["object"] = entity
            item["fact_text"] = " ".join(
                part for part in (item.get("subject"), item.get("predicate"), entity) if part
            )
        elif item.get("middle") or item.get("dependency"):
            item["subject"] = entity
            item["predicate"] = "dependsOn"
            item["object"] = item.get("dependency") or item.get("middle")
            item["fact_text"] = " ".join(
                part
                for part in (entity, "dependsOn", item.get("middle"), "dependsOn", item.get("dependency"))
                if part
            )
        else:
            item["object"] = entity
            item["fact_text"] = " ".join(
                part for part in (item.get("impacted"), item.get("predicate"), entity) if part
            )
        normalized.append(item)
    return normalized


def _detect_query_type(question: str) -> str:
    normalized = question.lower()
    if re.search(r"\bwhat\s+breaks\s+if\b", normalized) or "fails" in normalized:
        return "impact"
    if re.search(r"\bwhat\s+depends\s+on\b", normalized):
        return "incoming"
    if re.search(r"\bwhat\s+does\b.+\bdepend\s+on\b", normalized):
        return "outgoing"
    return "both"


def _extract_candidate_entity(question: str) -> str:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", question)
    if quoted:
        return sanitize_entity(quoted.group(1))

    patterns = (
        r"\bwhat\s+depends\s+on\s+([A-Za-z0-9_.-]+)",
        r"\bwhat\s+does\s+([A-Za-z0-9_.-]+)\s+depend\s+on\b",
        r"\bwhat\s+breaks\s+if\s+([A-Za-z0-9_.-]+)\s+fails\b",
        r"\bdependencies\s+of\s+([A-Za-z0-9_.-]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match:
            return sanitize_entity(match.group(1))

    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]*", question)
    candidates = [token for token in tokens if token.lower() not in _STOP_WORDS]
    return sanitize_entity(candidates[-1] if candidates else question)


def run(state: dict) -> dict:
    start_ms = now_ms()
    route = str(state.get("route") or "hybrid")
    if route in {"vector", "action"}:
        metrics = {**(state.get("metrics") or {}), "graph_retrieval_ms": elapsed_ms(start_ms)}
        return {**state, "graph_context": {"incoming": [], "outgoing": [], "paths": []}, "metrics": metrics}

    question = str(state.get("question") or state.get("query") or "")
    entity = _extract_candidate_entity(question)
    try:
        entity = resolve_graph_entity(entity) or entity
    except Exception:
        # GraphDB remains the source for retrieval; PostgreSQL entity lookup is a best-effort precision boost.
        pass
    query_type = _detect_query_type(question)

    incoming: list[dict[str, Any]] = []
    outgoing: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []

    if query_type in {"incoming", "both"}:
        incoming = _bindings(sparql_query(incoming_relationships_query(entity)))
    if query_type in {"outgoing", "both"}:
        outgoing = _bindings(sparql_query(outgoing_relationships_query(entity)))
    if query_type == "impact":
        incoming = _bindings(sparql_query(incoming_relationships_query(entity)))
        paths = _bindings(sparql_query(impact_query(entity)))
    if query_type == "outgoing":
        paths = _bindings(sparql_query(two_hop_dependency_query(entity)))

    incoming = _normalize_bindings(entity, "incoming", incoming)
    outgoing = _normalize_bindings(entity, "outgoing", outgoing)
    paths = _normalize_bindings(entity, "paths", paths)

    graph_context = {
        "entity": entity,
        "query_type": query_type,
        "incoming": incoming,
        "outgoing": outgoing,
        "paths": paths,
    }

    metrics = {**(state.get("metrics") or {}), "graph_retrieval_ms": elapsed_ms(start_ms)}
    return {**state, "graph_entity": entity, "graph_context": graph_context, "metrics": metrics}
