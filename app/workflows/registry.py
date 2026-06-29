"""Workflow registry metadata."""

from __future__ import annotations

from typing import Any

WORKFLOWS: list[dict[str, Any]] = [
    {
        "id": "rag",
        "name": "RAG Workflow",
        "engine": "langgraph",
        "module": "app.workflows.rag_workflow",
        "nodes": [
            "router",
            "memory",
            "vector",
            "graph",
            "merge",
            "compress",
            "reason",
            "validate",
        ],
    },
    {
        "id": "cognitive",
        "name": "Cognitive Recommendation Workflow",
        "engine": "deterministic",
        "module": "app.workflows.cognitive_workflow",
        "nodes": ["chief_summary", "plan", "security", "cost", "validation"],
    },
]


def list_workflows() -> list[dict[str, Any]]:
    return [dict(workflow) for workflow in WORKFLOWS]
