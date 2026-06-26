"""Vector retrieval agent."""

from __future__ import annotations

from app.core.config import settings
from app.core.timing import elapsed_ms, now_ms
from app.rag.vector_store import similarity_search
from app.tools.ollama_client import create_embedding


def run(state: dict) -> dict:
    start_ms = now_ms()
    route = str(state.get("route") or "hybrid")
    if route in {"graph", "action"}:
        metrics = {**(state.get("metrics") or {}), "vector_retrieval_ms": elapsed_ms(start_ms)}
        return {**state, "vector_context": [], "metrics": metrics}

    question = str(state.get("question") or state.get("query") or "")
    embedding = create_embedding(question)
    rows = similarity_search(embedding, int(state.get("top_k", settings.top_k)))
    metrics = {**(state.get("metrics") or {}), "vector_retrieval_ms": elapsed_ms(start_ms)}
    return {**state, "question_embedding": embedding, "vector_context": rows, "metrics": metrics}
