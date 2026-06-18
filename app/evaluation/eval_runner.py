"""End-to-end evaluation runner for ProjectRAG datasets."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from app.api.routes_query import query as query_route
from app.core.schemas import QueryRequest

DATASET_DIR = Path("data/evaluation")
REPORT_PATH = Path("docs/evaluation_report.md")
DATASET_FILES = {
    "vector": DATASET_DIR / "vector_questions.json",
    "graph": DATASET_DIR / "graph_questions.json",
    "hybrid": DATASET_DIR / "hybrid_questions.json",
    "safety": DATASET_DIR / "safety_questions.json",
}

AnswerFn = Callable[[str], dict[str, Any]]


def load_evaluation_questions(dataset_dir: Path = DATASET_DIR) -> dict[str, list[dict[str, Any]]]:
    """Load all evaluation datasets."""
    datasets: dict[str, list[dict[str, Any]]] = {}
    for name, path in DATASET_FILES.items():
        resolved = dataset_dir / path.name if dataset_dir != DATASET_DIR else path
        with resolved.open("r", encoding="utf-8") as file:
            datasets[name] = json.load(file)
    return datasets


def run_query_direct(question: str) -> dict[str, Any]:
    """Run a question through the /query route implementation."""
    return query_route(QueryRequest(question=question))


def _keyword_match(answer: str, expected_keywords: list[str]) -> float:
    if not expected_keywords:
        return 1.0
    text = answer.lower()
    matched = sum(1 for keyword in expected_keywords if str(keyword).lower() in text)
    return round(matched / len(expected_keywords), 3)


def _has_evidence(response: dict[str, Any], evidence_type: str) -> bool:
    evidence = response.get("evidence") or {}
    value = evidence.get(evidence_type) if isinstance(evidence, dict) else None
    return bool(value)


def _validation_confidence(response: dict[str, Any]) -> float:
    validation = response.get("validation") or {}
    try:
        return float(validation.get("confidence", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _requires_approval(response: dict[str, Any]) -> bool:
    validation = response.get("validation") or {}
    return bool(validation.get("requires_human_approval", False))


def evaluate_response(item: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one response against an evaluation item."""
    expected_route = str(item.get("expected_route") or "")
    actual_route = str(response.get("route") or "")
    answer = str(response.get("answer") or "")
    expected_approval = bool(item.get("should_require_approval", False))
    actual_approval = _requires_approval(response)

    return {
        "question": item.get("question"),
        "expected_route": expected_route,
        "actual_route": actual_route,
        "route_correct": actual_route == expected_route,
        "keyword_match": _keyword_match(answer, list(item.get("expected_keywords") or [])),
        "graph_evidence_used": _has_evidence(response, "graph"),
        "vector_evidence_used": _has_evidence(response, "vector"),
        "validation_confidence": _validation_confidence(response),
        "expected_requires_approval": expected_approval,
        "actual_requires_approval": actual_approval,
        "safety_approval_correct": actual_approval == expected_approval,
        "answer": answer,
    }


def run_dataset(
    dataset_name: str,
    questions: list[dict[str, Any]],
    answer_fn: AnswerFn = run_query_direct,
) -> list[dict[str, Any]]:
    """Run one evaluation dataset."""
    results = []
    for item in questions:
        question = str(item["question"])
        try:
            response = answer_fn(question)
            result = evaluate_response(item, response)
            result["status"] = "ok"
        except Exception as exc:  # pragma: no cover - external dependency failures vary
            result = {
                "question": question,
                "expected_route": item.get("expected_route"),
                "actual_route": "",
                "route_correct": False,
                "keyword_match": 0.0,
                "graph_evidence_used": False,
                "vector_evidence_used": False,
                "validation_confidence": 0.0,
                "expected_requires_approval": bool(item.get("should_require_approval", False)),
                "actual_requires_approval": False,
                "safety_approval_correct": False,
                "answer": "",
                "status": "error",
                "error": f"{exc.__class__.__name__}: {exc}",
            }
        results.append(result)
    return results


def summarize_results(results_by_dataset: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    """Summarize evaluation results across datasets."""
    all_results = [item for results in results_by_dataset.values() for item in results]
    if not all_results:
        return {
            "total_questions": 0,
            "route_accuracy": 0.0,
            "answer_keyword_match": 0.0,
            "graph_evidence_usage": 0.0,
            "vector_evidence_usage": 0.0,
            "validation_confidence": 0.0,
            "safety_approval_correctness": 0.0,
        }

    return {
        "total_questions": len(all_results),
        "route_accuracy": round(mean(1.0 if item["route_correct"] else 0.0 for item in all_results), 3),
        "answer_keyword_match": round(mean(float(item["keyword_match"]) for item in all_results), 3),
        "graph_evidence_usage": round(mean(1.0 if item["graph_evidence_used"] else 0.0 for item in all_results), 3),
        "vector_evidence_usage": round(mean(1.0 if item["vector_evidence_used"] else 0.0 for item in all_results), 3),
        "validation_confidence": round(mean(float(item["validation_confidence"]) for item in all_results), 3),
        "safety_approval_correctness": round(
            mean(1.0 if item["safety_approval_correct"] else 0.0 for item in all_results), 3
        ),
    }


def render_markdown_report(results_by_dataset: dict[str, list[dict[str, Any]]]) -> str:
    """Render evaluation results as Markdown."""
    summary = summarize_results(results_by_dataset)
    lines = [
        "# ProjectRAG Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Total questions: {summary['total_questions']}",
        f"- Route accuracy: {summary['route_accuracy']}",
        f"- Answer keyword match: {summary['answer_keyword_match']}",
        f"- Graph evidence usage: {summary['graph_evidence_usage']}",
        f"- Vector evidence usage: {summary['vector_evidence_usage']}",
        f"- Validation confidence: {summary['validation_confidence']}",
        f"- Safety approval correctness: {summary['safety_approval_correctness']}",
        "",
    ]

    for dataset_name, results in results_by_dataset.items():
        lines.extend([f"## Dataset: {dataset_name}", ""])
        lines.append(
            "| Question | Expected Route | Actual Route | Route OK | Keyword Match | Graph Evidence | Vector Evidence | Confidence | Approval OK | Status |"
        )
        lines.append("| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- |")
        for item in results:
            question = str(item["question"]).replace("|", "\\|")
            lines.append(
                "| "
                f"{question} | {item['expected_route']} | {item['actual_route']} | "
                f"{item['route_correct']} | {item['keyword_match']} | "
                f"{item['graph_evidence_used']} | {item['vector_evidence_used']} | "
                f"{item['validation_confidence']} | {item['safety_approval_correct']} | {item['status']} |"
            )
        lines.append("")
    return "\n".join(lines)


def run_all_evaluations(
    answer_fn: AnswerFn = run_query_direct,
    output_path: Path = REPORT_PATH,
) -> dict[str, Any]:
    """Run all datasets and write a Markdown report."""
    datasets = load_evaluation_questions()
    results_by_dataset = {
        name: run_dataset(name, questions, answer_fn=answer_fn)
        for name, questions in datasets.items()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown_report(results_by_dataset), encoding="utf-8")
    return {"summary": summarize_results(results_by_dataset), "results": results_by_dataset}


if __name__ == "__main__":  # pragma: no cover - manual E2E entrypoint
    result = run_all_evaluations()
    print(json.dumps(result["summary"], indent=2))
