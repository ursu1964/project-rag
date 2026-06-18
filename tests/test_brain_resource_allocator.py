from app.brain.resource_allocator import allocate_model, run


def test_routing_uses_small_local_model(monkeypatch):
    monkeypatch.delenv("PROJECTRAG_REMOTE_MODEL_URL", raising=False)
    allocation = allocate_model("routing")

    assert allocation["model_tier"] == "small"
    assert allocation["provider"] == "local"
    assert allocation["local_first"] is True


def test_validation_uses_medium_model():
    assert allocate_model("validation")["model_tier"] == "medium"


def test_reasoning_uses_large_model():
    assert allocate_model("reasoning")["model_tier"] == "large"


def test_remote_only_used_when_configured_and_requested(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_REMOTE_MODEL_URL", "https://example.invalid")
    monkeypatch.setenv("PROJECTRAG_REMOTE_LARGE_MODEL", "remote-large")

    local = allocate_model("reasoning", prefer_remote=False)
    remote = allocate_model("reasoning", prefer_remote=True)

    assert local["provider"] == "local"
    assert remote["provider"] == "remote"
    assert remote["model"] == "remote-large"


def test_run_adds_model_allocation():
    state = run({"task_type": "validation"})

    assert state["model_allocation"]["model_tier"] == "medium"


def test_claude_provider_stays_dormant_by_default(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_REMOTE_MODEL_URL", "https://example.invalid")
    monkeypatch.setenv("PROJECTRAG_REMOTE_LARGE_MODEL", "claude-remote-large")
    monkeypatch.setenv("PROJECTRAG_REMOTE_PROVIDER", "claude")
    monkeypatch.setattr("app.brain.resource_allocator.settings.enable_claude_provider", False)

    allocation = allocate_model("reasoning", prefer_remote=True)

    assert allocation["provider"] == "local"
    assert allocation["remote_configured"] is True
    assert allocation["remote_used"] is False
    assert allocation["remote_eligible"] is False
    assert allocation["dormant_reason"] == "claude_provider_disabled"


def test_claude_provider_can_be_enabled_explicitly(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_REMOTE_MODEL_URL", "https://example.invalid")
    monkeypatch.setenv("PROJECTRAG_REMOTE_LARGE_MODEL", "claude-remote-large")
    monkeypatch.setenv("PROJECTRAG_REMOTE_PROVIDER", "claude")
    monkeypatch.setattr("app.brain.resource_allocator.settings.enable_claude_provider", True)

    allocation = allocate_model("reasoning", prefer_remote=True)

    assert allocation["provider"] == "claude"
    assert allocation["model"] == "claude-remote-large"
    assert allocation["remote_used"] is True
    assert allocation["dormant_reason"] is None
