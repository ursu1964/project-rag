import app.agents.router as router


class Settings:
    use_llm_router = True


class DisabledSettings:
    use_llm_router = False


def test_router_uses_deterministic_by_default(monkeypatch):
    monkeypatch.setattr(router, "settings", DisabledSettings())
    result = router.run({"question": "what depends on VM1"})
    assert result["route"] == "hybrid"
    assert result["router_decision"]["router"] == "deterministic"


def test_router_uses_llm_when_enabled(monkeypatch):
    monkeypatch.setattr(router, "settings", Settings())
    monkeypatch.setattr(router, "generate", lambda prompt: '{"route":"graph","confidence":0.9,"reason":"dependency"}')

    result = router.run({"question": "what depends on VM1"})

    assert result["route"] == "graph"
    assert result["router_decision"]["router"] == "llm"
    assert result["router_decision"]["confidence"] == 0.9


def test_router_falls_back_when_llm_json_fails(monkeypatch):
    monkeypatch.setattr(router, "settings", Settings())
    monkeypatch.setattr(router, "generate", lambda prompt: 'not-json')

    result = router.run({"question": "what depends on VM1"})

    assert result["route"] == "hybrid"
    assert result["router_decision"]["router"] == "deterministic"
    assert result["router_decision"]["fallback_reason"] == "llm_router_failed"
