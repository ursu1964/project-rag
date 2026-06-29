"""Deterministic route classifier."""

from __future__ import annotations


def run(state: dict) -> dict:
    question = str(state.get("question") or "").lower()
    if any(term in question for term in ("depend", "dependency", "impact", "breaks", "fails")):
        route = "hybrid"
    elif "graph" in question:
        route = "graph" if "summarize" not in question else "hybrid"
    elif any(term in question for term in ("ingest", "upload", "delete")):
        route = "action"
    else:
        route = "vector"
    if "explain" in question and "graph" in question:
        route = "hybrid"
    return {**state, "route": route}
