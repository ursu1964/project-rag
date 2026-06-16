from app.api.routes_health import health


def test_health_returns_status_ok():
    assert health()["status"] == "ok"
