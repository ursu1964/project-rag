"""Memory retrieval agent."""

from __future__ import annotations

from app.memory.memory_store import search_memory


def run(state: dict) -> dict:
    question = str(state.get("question") or state.get("query") or "")
    rows = search_memory(question, int(state.get("memory_top_k", 5)))
    return {**state, "memory_context": rows}
