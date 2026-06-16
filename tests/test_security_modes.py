from app.agents.execution_agent import run as execute
from app.core import security_modes


def test_default_mode_is_read_only(monkeypatch):
    monkeypatch.delenv("PROJECTRAG_MODE", raising=False)
    assert security_modes.get_current_mode() == security_modes.READ_ONLY


def test_invalid_mode_falls_back_to_read_only(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "bad")
    assert security_modes.get_current_mode() == security_modes.READ_ONLY


def test_require_approval_and_no_execution(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "APPROVAL")
    assert security_modes.require_approval() is True
    assert security_modes.can_execute_actions() is False


def test_execution_agent_always_disabled(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_MODE", "APPROVAL")
    result = execute({})["execution"]
    assert result["status"] == "execution_disabled"
    assert result["executed"] is False
    assert result["mode"] == "APPROVAL"
