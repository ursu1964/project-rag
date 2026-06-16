"""Cognitive architecture workflow skeleton."""

from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents import (
    chief_agent,
    cost_agent,
    graph_retriever,
    learning_agent,
    memory_agent,
    planning_agent,
    security_agent,
    validator,
    vector_retriever,
)


class CognitiveState(TypedDict, total=False):
    question: str
    objective: str
    tasks: list[str]
    needed_agents: list[str]
    chief_summary: dict[str, Any]
    memory_context: list[dict[str, Any]]
    vector_context: list[dict[str, Any]]
    graph_context: dict[str, Any]
    plan: list[dict[str, Any]]
    security: dict[str, Any]
    cost: dict[str, Any]
    validation: dict[str, Any]
    lessons_learned: list[str]


def build_workflow():
    graph = StateGraph(CognitiveState)

    graph.add_node("chief", chief_agent.run)
    graph.add_node("memory", memory_agent.run)
    graph.add_node("retrieval", vector_retriever.run)
    graph.add_node("graph", graph_retriever.run)
    graph.add_node("planning", planning_agent.run)
    graph.add_node("security", security_agent.run)
    graph.add_node("cost", cost_agent.run)
    graph.add_node("validation", validator.run)
    graph.add_node("learning", learning_agent.run)

    graph.set_entry_point("chief")
    graph.add_edge("chief", "memory")
    graph.add_edge("memory", "retrieval")
    graph.add_edge("retrieval", "graph")
    graph.add_edge("graph", "planning")
    graph.add_edge("planning", "security")
    graph.add_edge("security", "cost")
    graph.add_edge("cost", "validation")
    graph.add_edge("validation", "learning")
    graph.add_edge("learning", END)

    return graph.compile()
