"""Internal tool contract definitions for future MCP integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

TOOL_MODES = {"read_only", "recommendation", "approval_required", "execution_disabled"}


@dataclass(frozen=True)
class ToolContract:
    name: str
    description: str
    callable: Callable
    mode: str
