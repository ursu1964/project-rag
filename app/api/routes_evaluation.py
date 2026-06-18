"""Evaluation report routes."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter

from app.core.metrics import REQUEST_COUNTER
from app.evaluation.eval_runner import REPORT_PATH

router = APIRouter()

_SUMMARY_PATTERN = re.compile(r"^- (?P<key>[^:]+): (?P<value>.+)$")

QUALITY_THRESHOLDS: dict[str, float] = {
    "route_accuracy": 0.8,
    "answer_keyword_match": 0.8,
    "graph_evidence_usage": 0.5,
    "vector_evidence_usage": 0.5,
    "validation_confidence": 0.5,
    "safety_approval_correctness": 0.9,
}


def _parse_summary(markdown: str) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    in_summary = False
    for line in markdown.splitlines():
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if not in_summary:
            continue
        match = _SUMMARY_PATTERN.match(line.strip())
        if not match:
            continue
        key = match.group("key").strip().lower().replace(" ", "_")
        value = match.group("value").strip()
        try:
            summary[key] = int(value) if value.isdigit() else float(value)
        except ValueError:
            summary[key] = value
    return summary


def evaluate_quality_gates(summary: dict[str, Any]) -> dict[str, Any]:
    """Evaluate report summary metrics against MVP quality thresholds."""
    gates: list[dict[str, Any]] = []
    for metric, threshold in QUALITY_THRESHOLDS.items():
        raw_value = summary.get(metric, 0.0)
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            value = 0.0
        gates.append(
            {
                "metric": metric,
                "value": value,
                "threshold": threshold,
                "passed": value >= threshold,
            }
        )
    return {
        "status": "passed" if all(gate["passed"] for gate in gates) else "failed",
        "gates": gates,
    }


def read_evaluation_report(path: Path = REPORT_PATH) -> dict[str, Any]:
    """Read the latest generated evaluation report without running evaluations."""
    if not path.exists():
        return {
            "status": "missing",
            "path": str(path),
            "summary": {},
            "markdown": "",
            "quality_gates": evaluate_quality_gates({}),
        }
    markdown = path.read_text(encoding="utf-8")
    summary = _parse_summary(markdown)
    return {
        "status": "ok",
        "path": str(path),
        "summary": summary,
        "quality_gates": evaluate_quality_gates(summary),
        "markdown": markdown,
    }


@router.get("/evaluation/report")
def evaluation_report() -> dict[str, Any]:
    """Return the latest evaluation report summary and markdown."""
    REQUEST_COUNTER.labels("/evaluation/report").inc()
    return read_evaluation_report()
