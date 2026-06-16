from app.api.routes_health import metrics
from app.core.metrics import observe_query_metrics, render_metrics


def test_render_metrics_returns_bytes():
    assert isinstance(render_metrics(), bytes)


def test_metrics_endpoint_returns_response():
    response = metrics()
    assert response.status_code == 200


def test_observe_query_metrics_accepts_basic_metrics():
    observe_query_metrics(
        {
            "duration_ms": 1,
            "vector_retrieval_ms": 1,
            "graph_retrieval_ms": 1,
            "llm_generation_ms": 1,
        }
    )
