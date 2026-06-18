"""Generate a Markdown metrics report from ProjectRAG PostgreSQL tables."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.memory.postgres import fetch_all

REPORT_PATH = Path("docs/metrics_report.md")


def _scalar(query: str, default: Any = 0) -> Any:
    rows = fetch_all(query)
    if not rows:
        return default
    return next(iter(rows[0].values()), default)


def collect_metrics() -> dict[str, Any]:
    """Collect high-level operational metrics from PostgreSQL."""
    return {
        "documents": _scalar("SELECT COUNT(*) AS count FROM documents"),
        "chunks": _scalar("SELECT COUNT(*) AS count FROM chunks"),
        "graph_facts": _scalar("SELECT COUNT(*) AS count FROM graph_facts"),
        "workflow_runs": _scalar("SELECT COUNT(*) AS count FROM workflow_runs"),
        "avg_validation_confidence": _scalar(
            """
            SELECT COALESCE(AVG((details->>'confidence')::numeric), 0) AS average
            FROM validation_results
            WHERE details ? 'confidence'
              AND details->>'confidence' ~ '^[0-9]+(\\.[0-9]+)?$'
            """,
            0,
        ),
        "failed_workflows": fetch_all(
            """
            SELECT id, workflow_name, status, error, created_at, updated_at
            FROM workflow_runs
            WHERE status <> 'completed'
            ORDER BY created_at DESC
            LIMIT 25
            """
        ),
        "slowest_agent_runs": fetch_all(
            """
            SELECT id, workflow_id, agent_name, status,
                   COALESCE((input->>'latency_ms')::numeric, 0) AS latency_ms,
                   created_at
            FROM agent_runs
            WHERE input ? 'latency_ms'
              AND input->>'latency_ms' ~ '^[0-9]+(\\.[0-9]+)?$'
            ORDER BY COALESCE((input->>'latency_ms')::numeric, 0) DESC
            LIMIT 10
            """
        ),
    }


def _format_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "No rows.\n"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join([header, separator, *body]) + "\n"


def render_report(metrics: dict[str, Any]) -> str:
    """Render collected metrics as Markdown."""
    average_confidence = float(metrics.get("avg_validation_confidence") or 0)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return f"""# ProjectRAG Metrics Report

Generated at: `{generated_at}`

## Summary

| Metric | Value |
|---|---:|
| Documents | {metrics['documents']} |
| Chunks | {metrics['chunks']} |
| Graph facts | {metrics['graph_facts']} |
| Workflow runs | {metrics['workflow_runs']} |
| Average validation confidence | {average_confidence:.3f} |

## Failed Workflows

{_format_table(metrics['failed_workflows'], ['id', 'workflow_name', 'status', 'error', 'created_at', 'updated_at'])}

## Slowest Agent Runs

{_format_table(metrics['slowest_agent_runs'], ['id', 'workflow_id', 'agent_name', 'status', 'latency_ms', 'created_at'])}
"""


def write_report(path: Path = REPORT_PATH) -> Path:
    """Collect metrics and write the Markdown report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_report(collect_metrics()), encoding="utf-8")
    return path


if __name__ == "__main__":
    print(write_report())
