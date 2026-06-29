"""Agent capability registry."""

from __future__ import annotations

from typing import Any

AGENTS: list[dict[str, Any]] = [
    {
        "id": "router",
        "name": "Router",
        "capability": "route query intent",
        "module": "app.agents.router",
    },
    {
        "id": "memory",
        "name": "Memory",
        "capability": "retrieve durable memory",
        "module": "app.agents.memory_agent",
    },
    {
        "id": "vector",
        "name": "Vector Retriever",
        "capability": "semantic vector retrieval",
        "module": "app.agents.vector_retriever",
    },
    {
        "id": "graph",
        "name": "Graph Retriever",
        "capability": "topology graph retrieval",
        "module": "app.agents.graph_retriever",
    },
    {
        "id": "context_merger",
        "name": "Context Merger",
        "capability": "merge evidence",
        "module": "app.agents.context_merger",
    },
    {
        "id": "context_compressor",
        "name": "Context Compressor",
        "capability": "compress evidence",
        "module": "app.agents.context_compressor",
    },
    {
        "id": "reasoner",
        "name": "Reasoner",
        "capability": "generate grounded answer",
        "module": "app.agents.reasoner",
    },
    {
        "id": "validator",
        "name": "Validator",
        "capability": "validate answer grounding",
        "module": "app.agents.validator",
    },
]


def list_agents() -> list[dict[str, Any]]:
    return [dict(agent) for agent in AGENTS]
