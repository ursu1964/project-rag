from fastapi.testclient import TestClient

from app.main import create_app


def test_cors_preflight_allows_frontend_query_request():
    client = TestClient(create_app())

    response = client.request(
        "OPTIONS",
        "/query",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": (
                "content-type,x-projectrag-user,x-projectrag-role,x-projectrag-tenant-id"
            ),
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
