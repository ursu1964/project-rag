"""Validate production observability wiring statically."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = ROOT / "deploy/monitoring/grafana/dashboards"
PROMETHEUS = ROOT / "deploy/monitoring/prometheus/prometheus.yml"
ALERTS = ROOT / "deploy/monitoring/prometheus/alerts.yml"
METRICS = ROOT / "app/core/metrics.py"
PROD_COMPOSE = ROOT / "docker-compose.prod.yml"

REQUIRED_METRICS = {
    "projectrag_http_requests_total",
    "projectrag_http_errors_total",
    "projectrag_http_request_duration_ms",
    "projectrag_ingestions_total",
    "projectrag_ingestion_failures_total",
    "projectrag_vector_retrieval_ms",
    "projectrag_llm_call_latency_ms",
    "projectrag_llm_call_errors_total",
}

ALLOWED_EXTERNAL_PREFIXES = ("up", "probe_")


def _metric_names_from_code() -> set[str]:
    text = METRICS.read_text()
    return set(re.findall(r'"(projectrag_[a-zA-Z0-9_]+)"', text))


def _projectrag_metrics_in_promql(text: str) -> set[str]:
    names = set(re.findall(r"\b(projectrag_[a-zA-Z0-9_]+)(?:_bucket|_sum|_count)?(?=\s*(?:\{|\[|\)))", text))
    return {name.removesuffix("_bucket").removesuffix("_sum").removesuffix("_count") for name in names}


def _dashboard_promql() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in sorted(DASHBOARD_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        exprs: list[str] = []
        for panel in data.get("panels", []):
            for target in panel.get("targets", []):
                expr = target.get("expr")
                if expr:
                    exprs.append(expr)
        result[path.name] = exprs
    return result


def main() -> int:
    metric_names = _metric_names_from_code()
    missing_required = REQUIRED_METRICS - metric_names
    if missing_required:
        raise SystemExit(f"Missing required metric definitions: {sorted(missing_required)}")

    compose_text = PROD_COMPOSE.read_text()
    for required in ("OTEL_ENABLED", "OTEL_EXPORTER_OTLP_ENDPOINT", "projectrag-otel-collector"):
        if required not in compose_text:
            raise SystemExit(f"Production compose missing {required}")

    prometheus_text = PROMETHEUS.read_text()
    for required in ("job_name: projectrag_api", "metrics_path: /metrics", "projectrag_otel_collector"):
        if required not in prometheus_text:
            raise SystemExit(f"Prometheus config missing {required}")

    referenced = _projectrag_metrics_in_promql(ALERTS.read_text())
    for exprs in _dashboard_promql().values():
        referenced.update(_projectrag_metrics_in_promql("\n".join(exprs)))
    missing_references = referenced - metric_names
    if missing_references:
        raise SystemExit(f"PromQL references undefined metrics: {sorted(missing_references)}")

    print("observability validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
