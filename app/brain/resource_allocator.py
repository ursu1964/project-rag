"""Infrastructure Brain model resource allocation policy."""

from __future__ import annotations

import os
from typing import Any

from app.core.config import settings

_TASK_TIERS = {
    "routing": "small",
    "summarization": "small",
    "validation": "medium",
    "reasoning": "large",
}

_LOCAL_MODELS = {
    "small": settings.ollama_model,
    "medium": settings.ollama_model,
    "large": settings.ollama_model,
}


def _task_type(state: dict[str, Any]) -> str:
    explicit = str(state.get("task_type") or state.get("task") or "").lower()
    if explicit:
        return explicit
    if state.get("validation") is not None:
        return "validation"
    if state.get("merged_context") or state.get("compressed_context") or state.get("question"):
        return "reasoning"
    return "routing"


def _remote_model_for_tier(tier: str) -> str | None:
    specific = os.getenv(f"PROJECTRAG_REMOTE_{tier.upper()}_MODEL")
    generic = os.getenv("PROJECTRAG_REMOTE_MODEL")
    endpoint = os.getenv("PROJECTRAG_REMOTE_MODEL_URL")
    if endpoint and (specific or generic):
        return specific or generic
    return None


def _remote_provider() -> str:
    provider = str(os.getenv("PROJECTRAG_REMOTE_PROVIDER") or "remote").strip().lower()
    return provider or "remote"


def allocate_model(task_type: str, prefer_remote: bool = False) -> dict[str, Any]:
    """Return a JSON-serializable model allocation decision."""
    normalized_task = str(task_type or "routing").lower()
    tier = _TASK_TIERS.get(normalized_task, "small")
    remote_model = _remote_model_for_tier(tier)
    remote_provider = _remote_provider()
    claude_dormant = bool(remote_provider == "claude" and not settings.enable_claude_provider)
    use_remote = bool(prefer_remote and remote_model and not claude_dormant)

    return {
        "task_type": normalized_task,
        "model_tier": tier,
        "provider": remote_provider if use_remote else "local",
        "model": remote_model if use_remote else _LOCAL_MODELS[tier],
        "local_first": True,
        "remote_configured": bool(remote_model),
        "remote_eligible": bool(remote_model and not claude_dormant),
        "remote_used": use_remote,
        "dormant_reason": "claude_provider_disabled" if claude_dormant else None,
        "reason": (
            f"Use {tier} model for {normalized_task}; local model preferred."
            if not use_remote and not claude_dormant
            else (
                "Claude provider configured but dormant. Set ENABLE_CLAUDE_PROVIDER=true to allow remote Claude usage."
                if claude_dormant
                else f"Use configured remote {tier} model for {normalized_task}."
            )
        ),
        "policy": {
            "routing": "small",
            "validation": "medium",
            "reasoning": "large",
            "local_first": True,
            "remote_only_if_configured": True,
            "claude_dormant_by_default": True,
        },
    }


def run(state: dict[str, Any]) -> dict[str, Any]:
    """Agent-compatible entrypoint returning allocation decision in JSON."""
    task = _task_type(state)
    allocation = allocate_model(task, prefer_remote=bool(state.get("prefer_remote")))
    return {**state, "model_allocation": allocation}
