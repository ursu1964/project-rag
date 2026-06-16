"""Route questions to the right retrieval path."""

from __future__ import annotations

import json

from app.core.config import settings
from app.core.logging import get_logger
from app.tools.ollama_client import generate

logger = get_logger(__name__)
_ALLOWED_ROUTES = {"vector", "graph", "hybrid", "action"}


def _deterministic_route(question: str) -> dict:
    normalized = question.lower()

    graph_terms = ("depend", "dependency", "depends", "relationship", "related", "graph", "entity", "impact", "breaks", "fails")
    action_terms = ("ingest", "index", "upload", "delete", "create", "update", "run", "execute")
    vector_terms = ("find", "search", "summarize", "explain", "what", "how", "why", "where", "when")

    if any(term in normalized for term in action_terms):
        route = "action"
        reason = "Action term detected."
    elif any(term in normalized for term in graph_terms) and any(term in normalized for term in vector_terms):
        route = "hybrid"
        reason = "Graph and retrieval question terms detected."
    elif any(term in normalized for term in graph_terms):
        route = "graph"
        reason = "Graph relationship terms detected."
    else:
        route = "vector"
        reason = "Defaulting to vector retrieval."

    return {"route": route, "confidence": 0.8, "reason": reason, "router": "deterministic"}


def _llm_route(question: str) -> dict:
    prompt = (
        "Classify this ProjectRAG question route. Return JSON only with this schema:\n"
        '{"route":"vector|graph|hybrid|action","confidence":0.0,"reason":"..."}\n\n'
        "Routes:\n"
        "- vector: semantic document retrieval\n"
        "- graph: relationships, dependencies, impact, entities\n"
        "- hybrid: both semantic context and graph relationships\n"
        "- action: ingestion, mutation, execution, operational change\n\n"
        f"Question: {question}"
    )
    parsed = json.loads(generate(prompt))
    route = parsed.get("route")
    if route not in _ALLOWED_ROUTES:
        raise ValueError("Invalid LLM router route")
    return {
        "route": route,
        "confidence": float(parsed.get("confidence", 0.0)),
        "reason": str(parsed.get("reason", "")),
        "router": "llm",
    }


def run(state: dict) -> dict:
    question = str(state.get("question") or state.get("query") or "")
    deterministic = _deterministic_route(question)

    if not settings.use_llm_router:
        return {**state, "route": deterministic["route"], "router_decision": deterministic}

    try:
        decision = _llm_route(question)
    except Exception as exc:  # never crash workflow on routing
        logger.warning("LLM router failed, falling back to deterministic router: %s", exc.__class__.__name__)
        decision = {**deterministic, "fallback_reason": "llm_router_failed"}

    return {**state, "route": decision["route"], "router_decision": decision}
