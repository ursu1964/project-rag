"""LangGraph RAG workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

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


class RagState(TypedDict, total=False):
    question: str
    workflow_id: str
    route: str
    memory_context: list[dict[str, Any]]
    vector_context: list[dict[str, Any]]
    graph_context: dict[str, Any]
    merged_context: dict[str, Any]
    compressed_context: dict[str, Any]
    answer: str
    validation: dict[str, Any]
    metrics: dict[str, Any]
    citations: list[dict[str, Any]]


def build_workflow():  # noqa: ANN201
    """Build the RAG workflow as a LangGraph StateGraph.

    Node order intentionally preserves the previous deterministic workflow:
    router -> memory -> vector -> graph -> merge -> compress -> reason -> validate.
    """
    graph = StateGraph(RagState)
    graph.add_node("router", router.run)
    graph.add_node("memory", memory_agent.run)
    graph.add_node("vector", vector_retriever.run)
    graph.add_node("graph", graph_retriever.run)
    graph.add_node("merge", context_merger.run)
    graph.add_node("compress", context_compressor.run)
    graph.add_node("reason", reasoner.run)
    graph.add_node("validate", validator.run)

    graph.add_edge(START, "router")
    graph.add_edge("router", "memory")
    graph.add_edge("memory", "vector")
    graph.add_edge("vector", "graph")
    graph.add_edge("graph", "merge")
    graph.add_edge("merge", "compress")
    graph.add_edge("compress", "reason")
    graph.add_edge("reason", "validate")
    graph.add_edge("validate", END)
    return graph.compile()
