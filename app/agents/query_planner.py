"""Query planning agent for retrieval strategy selection."""

from __future__ import annotations

from app.core.config import settings

_GRAPH_TERMS = ("depend", "dependency", "graph", "relationship", "impact", "break", "fails", "connected")
_ACTION_TERMS = ("ingest", "upload", "delete", "execute", "create", "update", "run")


def _route(question: str) -> str:
    normalized = question.lower()
    has_graph = any(term in normalized for term in _GRAPH_TERMS)
    has_action = any(term in normalized for term in _ACTION_TERMS)
    if has_action:
        return "action"
    if has_graph and any(term in normalized for term in ("what", "explain", "which", "how")):
        return "hybrid"
    if has_graph:
        return "graph"
    return "vector"


def _graph_depth(question: str, route: str) -> int:
    normalized = question.lower()
    max_depth = int(getattr(settings, "graph_max_depth", 3))
    if route not in {"graph", "hybrid"}:
        return 0
    if "impact" in normalized or "break" in normalized or "fails" in normalized:
        return min(3, max_depth)
    return min(2, max_depth)


def _token_budget(question: str, route: str) -> int:
    base = 1200 if route == "vector" else 1800
    if route == "hybrid":
        base = 2400
    return min(4000, base + len(question.split()) * 20)


def run(state: dict) -> dict:
    question = str(state.get("question") or state.get("query") or state.get("objective") or "")
    route = str(state.get("route") or _route(question))
    plan = {
        "route": route,
        "graph_depth": _graph_depth(question, route),
        "top_k": int(state.get("top_k", settings.top_k)),
        "use_memory": route != "action",
        "use_reranking": route in {"vector", "graph", "hybrid"},
        "token_budget": _token_budget(question, route),
    }
    return {**state, "query_plan": plan, "route": route}
