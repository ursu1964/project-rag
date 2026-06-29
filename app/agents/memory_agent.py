"""Memory retrieval placeholder."""

from __future__ import annotations

from app.memory.memory_store import search_memory as _search_memory


def search_memory(question: str, top_k: int = 5) -> list[dict]:
    """Return relevant local memory items for the question."""
    return _search_memory(question, limit=top_k)


def run(state: dict) -> dict:
    if state.get("memory_context"):
        return state
    question = str(state.get("question") or state.get("query") or "")
    top_k = int(state.get("top_k") or 5)
    return {**state, "memory_context": search_memory(question, top_k)}
