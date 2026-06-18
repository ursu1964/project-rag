import pytest

from app.tools import tool_registry
from app.tools.tool_executor import execute_tool
from app.tools.tool_policy import evaluate_tool_policy


def setup_function():
    tool_registry.clear_tools()


def test_low_risk_tool_can_run_read_only(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "READ_ONLY")
    tool_registry.register_tool("ping", "test", lambda: "pong", "low")

    result = execute_tool("ping")

    assert result["executed"] is True
    assert result["result"] == "pong"


def test_medium_requires_approval(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "READ_ONLY")
    tool_registry.register_tool("write_memory", "test", lambda: "ok", "medium")

    assert execute_tool("write_memory")["executed"] is False
    assert execute_tool("write_memory", approved=True)["executed"] is True


def test_high_requires_explicit_approval_and_rollback(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "READ_ONLY")
    tool_registry.register_tool("change_plan", "test", lambda: "ok", "high")

    assert execute_tool("change_plan", explicit_approval=True)["executed"] is False
    result = execute_tool("change_plan", explicit_approval=True, rollback_plan={"steps": ["restore"]})

    assert result["executed"] is True


def test_critical_blocked_by_default():
    decision = evaluate_tool_policy("critical", approved=True, explicit_approval=True, rollback_plan={"steps": ["restore"]})

    assert decision["allowed"] is False


def test_shell_tools_rejected():
    with pytest.raises(ValueError):
        tool_registry.register_tool("shell", "bad", lambda: None, "low")
