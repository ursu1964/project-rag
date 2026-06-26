"""Graph traversal helpers backed by graph facts."""

from __future__ import annotations

from app.memory.graph_fact_store import list_graph_facts


def get_impact_path(entity: str, depth: int = 1) -> dict:
    facts = list_graph_facts(entity)
    return {"entity": entity, "depth": depth, "paths": facts}


def get_dependencies(entity: str) -> dict:
    facts = [fact for fact in list_graph_facts(entity) if fact.get("subject") == entity]
    return {"entity": entity, "dependencies": facts}


def get_reverse_dependencies(entity: str) -> dict:
    facts = [fact for fact in list_graph_facts(entity) if fact.get("object") == entity]
    return {"entity": entity, "reverse_dependencies": facts}
