"""Evaluation runner for ProjectRAG responses."""

from __future__ import annotations

import json
from typing import Any, Callable

from app.evaluation.metrics import evaluate_answer
from app.memory.postgres import execute


def store_evaluation_result(dataset_name: str, question: str, answer: str, metrics: dict[str, float]) -> None:
    execute(
        """
        INSERT INTO evaluation_results (dataset_name, question, answer, metrics)
        VALUES (%s, %s, %s, %s::jsonb)
        """,
        (dataset_name, question, answer, json.dumps(metrics)),
    )


def run_evaluation(
    dataset_name: str,
    dataset: list[dict[str, Any]],
    answer_fn: Callable[[str], dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for item in dataset:
        question = str(item["question"])
        expected_answer = str(item.get("expected_answer", ""))
        response = answer_fn(question)
        answer = str(response.get("answer", ""))
        evidence = response.get("evidence", {})
        metric_values = evaluate_answer(answer, evidence, expected_answer)
        store_evaluation_result(dataset_name, question, answer, metric_values)
        results.append({"question": question, "answer": answer, "metrics": metric_values})
    return results
