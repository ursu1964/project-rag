"""Discovery agent for read-only local infrastructure discovery."""

from __future__ import annotations

from app.discovery.docker_discovery import discover_and_persist, docker_inventory


def run(state: dict) -> dict:
    """Run discovery. Persists only when state['persist'] is true."""
    source = str(state.get("source") or "docker").lower()
    if source != "docker":
        return {
            **state,
            "discovery_context": {
                "source": source,
                "status": "unsupported_source",
                "entities": [],
                "relationships": [],
                "persisted": None,
            },
        }

    if bool(state.get("persist", True)):
        result = discover_and_persist()
        context = {"source": "docker", "status": "completed", **result}
    else:
        inventory = docker_inventory()
        context = {"source": "docker", "status": "completed", "inventory": inventory, "persisted": None}
    return {**state, "discovery_context": context}
