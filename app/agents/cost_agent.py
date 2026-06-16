"""Cost and local resource impact placeholder agent."""

from __future__ import annotations

LOCAL_ASSUMPTIONS = {
    "ram_gb": 32,
    "storage_gb": 1024,
    "gpu_gb": 4,
}


def _estimate_storage_growth(state: dict) -> dict:
    chunks = len(state.get("vector_context") or []) or int(state.get("estimated_chunks", 0) or 0)
    documents = int(state.get("estimated_documents", 1 if chunks else 0) or 0)
    estimated_mb = round((documents * 0.25) + (chunks * 0.02), 3)
    return {"documents": documents, "chunks": chunks, "estimated_mb": estimated_mb}


def _estimate_graph_growth(state: dict) -> dict:
    graph_context = state.get("graph_context") or {}
    facts = 0
    if isinstance(graph_context, dict):
        facts = sum(len(graph_context.get(key) or []) for key in ("incoming", "outgoing", "paths"))
    facts = facts or int(state.get("estimated_graph_facts", 0) or 0)
    return {"facts": facts, "estimated_mb": round(facts * 0.005, 3)}


def _estimate_embedding_growth(state: dict) -> dict:
    chunks = len(state.get("vector_context") or []) or int(state.get("estimated_chunks", 0) or 0)
    dimensions = 768
    estimated_mb = round((chunks * dimensions * 4) / (1024 * 1024), 3)
    return {"chunks": chunks, "dimensions": dimensions, "estimated_mb": estimated_mb}


def _estimate_inference_cost(state: dict) -> dict:
    token_budget = int((state.get("query_plan") or {}).get("token_budget", 0) or 0)
    if not token_budget:
        question = str(state.get("question") or state.get("objective") or "")
        token_budget = max(512, len(question.split()) * 32)
    gpu_warning = token_budget > 3000 and LOCAL_ASSUMPTIONS["gpu_gb"] <= 4
    return {
        "currency_cost": 0.0,
        "deployment": "local_ollama",
        "estimated_tokens": token_budget,
        "gpu_memory_warning": gpu_warning,
    }


def run(state: dict) -> dict:
    cost = {
        "impact": "local_resource_estimate",
        "assumptions": LOCAL_ASSUMPTIONS,
        "storage_growth": _estimate_storage_growth(state),
        "graph_growth": _estimate_graph_growth(state),
        "embedding_growth": _estimate_embedding_growth(state),
        "inference_cost": _estimate_inference_cost(state),
        "notes": "Estimates assume local deployment with 32 GB RAM, 1 TB storage, and 4 GB GPU.",
    }
    return {**state, "cost": cost}
