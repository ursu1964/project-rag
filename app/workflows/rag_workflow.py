"""Small deterministic RAG workflow."""

from __future__ import annotations

from app.agents import context_compressor, context_merger, graph_retriever, memory_agent, reasoner, router, validator, vector_retriever


class _Workflow:
    def invoke(self, state: dict) -> dict:
        for agent in (router, memory_agent, vector_retriever, graph_retriever, context_merger, context_compressor, reasoner, validator):
            state = agent.run(state)
        return state


def build_workflow() -> _Workflow:
    return _Workflow()
