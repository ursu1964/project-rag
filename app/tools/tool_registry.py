"""Safe registry for ProjectRAG internal tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.tools.tool_policy import LOW, normalize_risk


@dataclass(frozen=True)
class RegisteredTool:
    name: str
    description: str
    callable: Callable[..., Any]
    risk_class: str = LOW


_TOOLS: dict[str, RegisteredTool] = {}
_FORBIDDEN_TOOL_NAMES = {"shell", "exec", "bash", "sh", "subprocess", "system"}


def register_tool(
    name: str,
    description: str,
    callable: Callable[..., Any],
    risk_class: str = LOW,
) -> RegisteredTool:
    """Register a safe internal callable. Arbitrary shell tools are rejected."""
    normalized_name = str(name).strip()
    if not normalized_name:
        raise ValueError("Tool name is required")
    if normalized_name.lower() in _FORBIDDEN_TOOL_NAMES:
        raise ValueError("Arbitrary shell execution tools are not allowed")
    if not callable:
        raise ValueError("Tool callable is required")

    tool = RegisteredTool(
        name=normalized_name,
        description=description,
        callable=callable,
        risk_class=normalize_risk(risk_class),
    )
    _TOOLS[tool.name] = tool
    return tool


def list_tools() -> list[RegisteredTool]:
    """List registered tools."""
    return list(_TOOLS.values())


def get_tool(name: str) -> RegisteredTool:
    """Return a registered tool by name."""
    return _TOOLS[name]


def clear_tools() -> None:
    """Clear registry. Intended for tests and controlled bootstrapping."""
    _TOOLS.clear()
