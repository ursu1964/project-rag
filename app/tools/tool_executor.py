"""Policy-controlled executor for registered internal tools."""

from __future__ import annotations

from typing import Any

from app.tools.tool_policy import evaluate_tool_policy
from app.tools.tool_registry import get_tool


def execute_tool(
    name: str,
    *args: Any,
    approved: bool = False,
    explicit_approval: bool = False,
    rollback_plan: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Execute a registered tool only when policy allows it.

    This function never executes arbitrary shell commands. It only invokes
    callables previously registered in app.tools.tool_registry.
    """
    tool = get_tool(name)
    decision = evaluate_tool_policy(
        tool.risk_class,
        approved=approved,
        explicit_approval=explicit_approval,
        rollback_plan=rollback_plan,
    )
    if not decision["allowed"]:
        return {
            "tool": name,
            "executed": False,
            "policy": decision,
            "result": None,
        }

    result = tool.callable(*args, **kwargs)
    return {
        "tool": name,
        "executed": True,
        "policy": decision,
        "result": result,
    }
