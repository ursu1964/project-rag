"""Local model runtime manager."""

from __future__ import annotations

from typing import Any

from app.brain.resource_allocator import allocate_model
from app.core.config import settings


def select_runtime(task_type: str, prefer_remote: bool = False) -> dict[str, Any]:
    """Select local-first model runtime for a task."""
    allocation = allocate_model(task_type, prefer_remote=prefer_remote)
    if allocation["provider"] == "local":
        runtime = "ollama"
    elif allocation["provider"] == "claude":
        runtime = "claude"
    else:
        runtime = "remote"
    return {
        "runtime": runtime,
        "allocation": allocation,
        "execution": "selection_only",
    }


def runtime_health() -> dict[str, str | bool]:
    """Return static runtime manager health."""
    return {
        "status": "ok",
        "mode": "local_first",
        "claude_provider_enabled": settings.enable_claude_provider,
        "claude_provider_dormant": not settings.enable_claude_provider,
    }
