"""Golden evaluation runner for RAG quality assurance with background job integration."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.logging import get_logger
from app.memory.postgres import execute, fetch_all
from app.services.background_jobs import JobStatus, JobType, create_job, mark_completed, mark_failed

logger = get_logger(__name__)

DATASET_DIR = Path("data/evaluation")

DATASET_CATEGORIES = {
    "graph": "Graph-based deterministic queries",
    "vector": "Semantic vector search queries",
    "hybrid": "Combined graph and vector retrieval",
    "safety": "Security and safety validation",
}


def create_golden_evaluation_job(
    dataset_category: str, idempotency_key: str | None = None
) -> dict[str, Any]:
    """Create a background job to run golden evaluation on a dataset category.

    Args:
        dataset_category: One of 'graph', 'vector', 'hybrid', 'safety'
        idempotency_key: Optional idempotency key for safe retries

    Returns:
        Job metadata dict
    """
    if dataset_category not in DATASET_CATEGORIES:
        raise ValueError(f"Unknown dataset category: {dataset_category}")

    idempotency = idempotency_key or f"golden_eval#{dataset_category}#{datetime.utcnow().isoformat()}"

    job = create_job(
        job_type=JobType.EVALUATE_GOLDEN_SET.value,
        resource_type="evaluation_dataset",
        resource_id=dataset_category,
        metadata={"category": dataset_category, "created_at": datetime.utcnow().isoformat()},
        max_attempts=3,
        idempotency_key=idempotency,
    )

    logger.info("Created golden evaluation job: job_id=%s category=%s", job["id"], dataset_category)
    return job


def load_golden_questions(category: str) -> list[dict[str, Any]]:
    """Load golden questions for a specific category.

    Args:
        category: One of 'graph', 'vector', 'hybrid', 'safety'

    Returns:
        List of question items
    """
    path = DATASET_DIR / f"{category}_questions.json"
    if not path.exists():
        logger.warning("Golden question set not found: path=%s", path)
        return []

    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load golden questions: category=%s error=%s", category, e)
        return []


def run_golden_evaluation(category: str, job_id: str | None = None) -> dict[str, Any]:
    """Execute golden evaluation on a dataset category.

    Args:
        category: Evaluation category ('graph', 'vector', 'hybrid', 'safety')
        job_id: Optional background job ID to update with results

    Returns:
        Evaluation summary with pass/fail counts and details
    """
    questions = load_golden_questions(category)
    if not questions:
        result = {
            "status": "failed",
            "category": category,
            "reason": "no_questions_found",
            "passed": 0,
            "total": 0,
            "errors": ["Golden question set not found"],
        }
        if job_id:
            mark_failed(job_id, f"No questions found for category: {category}")
        return result

    passed = 0
    failed = 0
    errors: list[str] = []
    details: list[dict[str, Any]] = []

    for question in questions:
        question_id = question.get("id", "unknown")
        try:
            # Validate question structure
            required_fields = {
                "graph": ["id", "category", "question", "expected_route"],
                "vector": ["id", "category", "question", "expected_route"],
                "hybrid": ["id", "category", "question", "expected_route"],
                "safety": ["id", "category", "question", "expected_behavior"],
            }

            required = required_fields.get(category, [])
            missing = [f for f in required if f not in question]
            if missing:
                failed += 1
                error_msg = f"Question {question_id} missing fields: {missing}"
                errors.append(error_msg)
                logger.warning(error_msg)
                details.append(
                    {
                        "question_id": question_id,
                        "status": "failed",
                        "error": error_msg,
                    }
                )
                continue

            # For now, just validate structure - actual execution happens at runtime
            passed += 1
            details.append(
                {
                    "question_id": question_id,
                    "status": "validated",
                    "question": question.get("question"),
                }
            )

        except Exception as e:
            failed += 1
            error_msg = f"Error processing question {question_id}: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
            details.append(
                {
                    "question_id": question_id,
                    "status": "error",
                    "error": error_msg,
                }
            )

    result = {
        "status": "completed",
        "category": category,
        "timestamp": datetime.utcnow().isoformat(),
        "passed": passed,
        "failed": failed,
        "total": len(questions),
        "pass_rate": round(passed / len(questions) * 100, 2) if questions else 0,
        "details": details,
    }

    if errors:
        result["errors"] = errors

    if job_id:
        if failed == 0:
            mark_completed(job_id, {"result": result})
        else:
            mark_failed(job_id, f"Golden evaluation failed: {failed} issues found")

    logger.info(
        "Completed golden evaluation: category=%s passed=%d failed=%d total=%d",
        category,
        passed,
        failed,
        len(questions),
    )

    return result


def run_all_golden_evaluations(job_id: str | None = None) -> dict[str, Any]:
    """Run all golden evaluations across all categories.

    Args:
        job_id: Optional parent job ID for tracking

    Returns:
        Aggregated results across all categories
    """
    all_results = {}
    total_passed = 0
    total_failed = 0
    total_questions = 0

    for category in DATASET_CATEGORIES:
        result = run_golden_evaluation(category, None)
        all_results[category] = result
        total_passed += result.get("passed", 0)
        total_failed += result.get("failed", 0)
        total_questions += result.get("total", 0)

    final_result = {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat(),
        "categories": all_results,
        "summary": {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_questions": total_questions,
            "overall_pass_rate": round(
                total_passed / total_questions * 100, 2
            ) if total_questions else 0,
        },
    }

    if job_id:
        if total_failed == 0:
            mark_completed(job_id, {"result": final_result})
        else:
            mark_failed(job_id, f"Overall evaluation failed: {total_failed} issues found")

    logger.info(
        "Completed all golden evaluations: passed=%d failed=%d total=%d",
        total_passed,
        total_failed,
        total_questions,
    )

    return final_result


def store_evaluation_result(
    dataset_category: str, question_id: str, result: dict[str, Any]
) -> str:
    """Store evaluation result in database for audit and trending.

    Args:
        dataset_category: Category of evaluation
        question_id: Question ID from golden set
        result: Evaluation result dict

    Returns:
        Result record ID
    """
    result_id = str(uuid4())
    try:
        execute(
            """
            INSERT INTO evaluation_results (id, dataset_name, question, answer, metrics)
            VALUES (%s, %s, %s, %s, %s::jsonb)
            """,
            (
                result_id,
                f"golden_{dataset_category}",
                question_id,
                result.get("answer", ""),
                json.dumps(result),
            ),
        )
        logger.info("Stored evaluation result: result_id=%s", result_id)
        return result_id
    except Exception as e:
        logger.error("Failed to store evaluation result: error=%s", e)
        return ""


def list_evaluation_history(
    dataset_category: str | None = None, limit: int = 50, offset: int = 0
) -> list[dict[str, Any]]:
    """List evaluation history.

    Args:
        dataset_category: Optional filter by category
        limit: Maximum results to return
        offset: Pagination offset

    Returns:
        List of evaluation records
    """
    query = "SELECT * FROM evaluation_results WHERE 1=1"
    params: list[Any] = []

    if dataset_category:
        query += " AND dataset_name = %s"
        params.append(f"golden_{dataset_category}")

    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        return fetch_all(query, tuple(params))
    except Exception as e:
        logger.error("Failed to list evaluation history: error=%s", e)
        return []
