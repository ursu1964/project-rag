"""Optional Prometheus metrics helpers."""

from __future__ import annotations

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
QUERY_COUNTER = _counter("projectrag_queries_total", "Total RAG queries")
INGESTION_COUNTER = _counter("projectrag_ingestions_total", "Total ingestion runs")
WORKFLOW_DURATION = _histogram("projectrag_workflow_duration_ms", "Workflow duration in milliseconds")
VECTOR_RETRIEVAL_DURATION = _histogram("projectrag_vector_retrieval_ms", "Vector retrieval duration in milliseconds")
GRAPH_RETRIEVAL_DURATION = _histogram("projectrag_graph_retrieval_ms", "Graph retrieval duration in milliseconds")
LLM_LATENCY = _histogram("projectrag_llm_latency_ms", "LLM generation latency in milliseconds")


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
    if "llm_generation_ms" in metrics:
        LLM_LATENCY.observe(metrics["llm_generation_ms"])
