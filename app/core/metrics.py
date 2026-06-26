"""Optional Prometheus metrics helpers."""

from __future__ import annotations

from typing import Any

CONTENT_TYPE_LATEST: str
Counter: Any
Histogram: Any
generate_latest: Any

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ImportError:  # pragma: no cover - optional dependency fallback
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    Counter = None
    Histogram = None
    generate_latest = None


class _NoopMetric:
    def labels(self, *args, **kwargs):
        return self

    def inc(self, *args, **kwargs) -> None:
        return None

    def observe(self, *args, **kwargs) -> None:
        return None


def _counter(name: str, description: str, labelnames: tuple[str, ...] = ()):  # noqa: ANN001
    if Counter is None:
        return _NoopMetric()
    return Counter(name, description, labelnames)


def _histogram(name: str, description: str, labelnames: tuple[str, ...] = ()):  # noqa: ANN001
    if Histogram is None:
        return _NoopMetric()
    return Histogram(name, description, labelnames)


REQUEST_COUNTER = _counter("projectrag_requests_total", "Total HTTP requests", ("endpoint",))
HTTP_REQUEST_COUNTER = _counter(
    "projectrag_http_requests_total",
    "Total HTTP requests by method, path, and status",
    ("method", "path", "status"),
)
HTTP_ERROR_COUNTER = _counter(
    "projectrag_http_errors_total",
    "Total HTTP 5xx responses by method, path, and status",
    ("method", "path", "status"),
)
HTTP_REQUEST_DURATION = _histogram(
    "projectrag_http_request_duration_ms",
    "HTTP request duration in milliseconds",
    ("method", "path", "status"),
)
QUERY_COUNTER = _counter("projectrag_queries_total", "Total RAG queries")
INGESTION_COUNTER = _counter("projectrag_ingestions_total", "Total ingestion runs")
INGESTION_FAILURE_COUNTER = _counter("projectrag_ingestion_failures_total", "Total ingestion failures")
PII_SCAN_COUNTER = _counter("projectrag_pii_chunks_sanitised_total", "Total chunks with PII sanitised before embedding")
RETRIEVAL_CACHE_COUNTER = _counter(
    "projectrag_retrieval_cache_total",
    "Retrieval cache outcomes",
    ("endpoint", "result"),
)
WORKFLOW_DURATION = _histogram("projectrag_workflow_duration_ms", "Workflow duration in milliseconds")
VECTOR_RETRIEVAL_DURATION = _histogram("projectrag_vector_retrieval_ms", "Vector retrieval duration in milliseconds")
GRAPH_RETRIEVAL_DURATION = _histogram("projectrag_graph_retrieval_ms", "Graph retrieval duration in milliseconds")
HYBRID_RETRIEVAL_DURATION = _histogram("projectrag_hybrid_retrieval_ms", "Hybrid retrieval duration in milliseconds")
LLM_LATENCY = _histogram("projectrag_llm_latency_ms", "LLM generation latency in milliseconds")
LLM_CALL_LATENCY = _histogram(
    "projectrag_llm_call_latency_ms",
    "External LLM or embedding call latency in milliseconds",
    ("operation", "model"),
)
LLM_CALL_ERRORS = _counter(
    "projectrag_llm_call_errors_total",
    "External LLM or embedding call errors",
    ("operation", "model"),
)
VALIDATION_CONFIDENCE = _histogram("projectrag_validation_confidence", "RAG answer validation confidence scores")
WORKFLOW_RUN_COUNTER = _counter(
    "projectrag_workflow_runs_total",
    "Workflow run transitions by status",
    ("status",),
)
AGENT_RUN_COUNTER = _counter(
    "projectrag_agent_runs_total",
    "Agent runs by name and status",
    ("agent_name", "status"),
)
AGENT_RUN_LATENCY = _histogram(
    "projectrag_agent_run_latency_ms",
    "Agent run latency in milliseconds",
    ("agent_name", "status"),
)


def metrics_enabled() -> bool:
    return generate_latest is not None


def render_metrics() -> bytes:
    if generate_latest is None:
        return b"# prometheus-client is not installed\n"
    return generate_latest()


def observe_query_metrics(metrics: dict) -> None:
    QUERY_COUNTER.inc()
    if "duration_ms" in metrics:
        WORKFLOW_DURATION.observe(metrics["duration_ms"])
    if "vector_retrieval_ms" in metrics:
        VECTOR_RETRIEVAL_DURATION.observe(metrics["vector_retrieval_ms"])
    if "graph_retrieval_ms" in metrics:
        GRAPH_RETRIEVAL_DURATION.observe(metrics["graph_retrieval_ms"])
    if "hybrid_retrieval_ms" in metrics:
        HYBRID_RETRIEVAL_DURATION.observe(metrics["hybrid_retrieval_ms"])
    if "llm_generation_ms" in metrics:
        LLM_LATENCY.observe(metrics["llm_generation_ms"])


def observe_validation_confidence(confidence: float) -> None:
    VALIDATION_CONFIDENCE.observe(max(0.0, min(1.0, float(confidence))))


def observe_http_request(method: str, path: str, status: int, duration_ms: float) -> None:
    normalized_status = str(status)
    normalized_method = method.upper()
    HTTP_REQUEST_COUNTER.labels(method=normalized_method, path=path, status=normalized_status).inc()
    if int(status) >= 500:
        HTTP_ERROR_COUNTER.labels(method=normalized_method, path=path, status=normalized_status).inc()
    HTTP_REQUEST_DURATION.labels(method=normalized_method, path=path, status=normalized_status).observe(
        max(0.0, float(duration_ms))
    )


def observe_llm_call(operation: str, model: str, duration_ms: float, error: bool = False) -> None:
    safe_operation = str(operation or "unknown")
    safe_model = str(model or "unknown")
    LLM_CALL_LATENCY.labels(operation=safe_operation, model=safe_model).observe(
        max(0.0, float(duration_ms))
    )
    if error:
        LLM_CALL_ERRORS.labels(operation=safe_operation, model=safe_model).inc()


def observe_workflow_transition(status: str) -> None:
    WORKFLOW_RUN_COUNTER.labels(status=str(status or "unknown")).inc()


def observe_agent_run(agent_name: str, status: str, latency_ms: int = 0) -> None:
    safe_agent = str(agent_name or "unknown")
    safe_status = str(status or "unknown")
    AGENT_RUN_COUNTER.labels(agent_name=safe_agent, status=safe_status).inc()
    AGENT_RUN_LATENCY.labels(agent_name=safe_agent, status=safe_status).observe(max(0, int(latency_ms)))
