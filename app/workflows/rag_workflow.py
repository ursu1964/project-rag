"""LangGraph RAG workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents import (
    context_compressor,
    context_merger,
    graph_retriever,
    memory_agent,
    reasoner,
    router,
    validator,
    vector_retriever,
)


class RAGState(TypedDict, total=False):
    question: str
    route: str
    memory_context: list[dict[str, Any]]
    vector_context: list[dict[str, Any]]
    graph_context: dict[str, Any]
    merged_context: dict[str, Any]
    compressed_context: dict[str, Any]
    evidence: list[dict[str, Any]]
    evidence_summary: dict[str, Any]
    answer: str
    validation: dict[str, Any]
    metrics: dict[str, Any]
    workflow_id: str


def build_workflow():
    graph = StateGraph(RAGState)

    graph.add_node("router", router.run)
    graph.add_node("memory", memory_agent.run)
    graph.add_node("vector", vector_retriever.run)
    graph.add_node("graph", graph_retriever.run)
    graph.add_node("merge", context_merger.run)
    graph.add_node("compress", context_compressor.run)
    graph.add_node("reason", reasoner.run)
    graph.add_node("validate", validator.run)

    graph.set_entry_point("router")
    graph.add_edge("router", "memory")
    graph.add_edge("memory", "vector")
    graph.add_edge("vector", "graph")
    graph.add_edge("graph", "merge")
    graph.add_edge("merge", "compress")
    graph.add_edge("compress", "reason")
    graph.add_edge("reason", "validate")
    graph.add_edge("validate", END)

    return graph.compile()
