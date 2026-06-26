"""Memory retrieval placeholder."""

from __future__ import annotations


def run(state: dict) -> dict:
    return {**state, "memory_context": state.get("memory_context") or []}
