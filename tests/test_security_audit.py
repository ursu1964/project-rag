import app.security.audit as audit
from app.security.identity import Identity


def test_record_security_event(monkeypatch):
    calls = []
    monkeypatch.setattr(audit, "execute", lambda query, params=(): calls.append((query, params)))

    event = audit.record_security_event(
        action="query",
        resource="/query",
        decision="allowed",
        risk_level="low",
        identity=Identity(subject="u1", role="analyst"),
    )

    assert event["user"] == "u1"
    assert event["role"] == "analyst"
    assert calls


def test_list_security_events(monkeypatch):
    captured = {}

    def fake_fetch_all(query, params=()):
        captured["query"] = query
        captured["params"] = params
        return [{"action": "query"}]

    monkeypatch.setattr(audit, "fetch_all", fake_fetch_all)

    assert audit.list_security_events()[0]["action"] == "query"
    assert "metadata->>'tenant_id'" in captured["query"]
    assert captured["params"][0] == "local"
