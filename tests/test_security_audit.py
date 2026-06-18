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
    monkeypatch.setattr(audit, "fetch_all", lambda query, params=(): [{"action": "query"}])

    assert audit.list_security_events()[0]["action"] == "query"
