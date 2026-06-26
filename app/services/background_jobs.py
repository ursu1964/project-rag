"""Durable background job orchestration with local storage and retry logic."""

from __future__ import annotations

import json
import math
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

from app.core.logging import get_logger
from app.memory.postgres import execute, fetch_all, get_connection

UTC = timezone.utc
logger = get_logger(__name__)

_RETRY_BASE_SECONDS = 10
_RETRY_MAX_SECONDS = 60 * 60
_HAS_NEXT_RETRY_AT: bool | None = None


def _supports_next_retry_at() -> bool:
    """Return whether the connected DB schema has background_jobs.next_retry_at."""
    global _HAS_NEXT_RETRY_AT
    if _HAS_NEXT_RETRY_AT is not None:
        return _HAS_NEXT_RETRY_AT

    try:
        rows = fetch_all(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
            LIMIT 1
            """,
            ("background_jobs", "next_retry_at"),
        )
        _HAS_NEXT_RETRY_AT = bool(rows)
    except Exception:
        _HAS_NEXT_RETRY_AT = False
    return _HAS_NEXT_RETRY_AT


class JobType(str, Enum):
    """Supported background job types."""

    INGEST_DOCUMENT = "ingest_document"
    INGEST_DIRECTORY = "ingest_directory"
    EVALUATE_GOLDEN_SET = "evaluate_golden_set"
    CONNECTOR_SYNC = "connector_sync"
    CITATION_VALIDATION = "citation_validation"
    PII_SCAN = "pii_scan"


class JobStatus(str, Enum):
    """Background job execution status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


def create_job(
    job_type: JobType | str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    max_attempts: int = 3,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    """Create a new background job with optional idempotency."""
    job_id = str(uuid4())

    # Check idempotency: if key exists and job completed successfully, return existing
    if idempotency_key:
        existing = fetch_all(
            "SELECT id, status, metadata FROM background_jobs WHERE metadata->>'idempotency_key' = %s ORDER BY created_at DESC LIMIT 1",
            (idempotency_key,),
        )
        if existing:
            existing_job = existing[0]
            if existing_job["status"] in (JobStatus.COMPLETED.value, JobStatus.SKIPPED.value):
                logger.info(
                    "Idempotent job already completed: idempotency_key=%s job_id=%s",
                    idempotency_key,
                    existing_job["id"],
                )
                return {
                    "id": str(existing_job["id"]),
                    "status": existing_job["status"],
                    "idempotent": True,
                    "metadata": existing_job["metadata"],
                }

    meta = metadata or {}
    if idempotency_key:
        meta["idempotency_key"] = idempotency_key

    execute(
        """
        INSERT INTO background_jobs (id, job_type, status, resource_type, resource_id, attempts, max_attempts, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """,
        (job_id, job_type, JobStatus.QUEUED.value, resource_type, resource_id, 0, max_attempts, json.dumps(meta)),
    )

    logger.info(
        "Created background job: job_id=%s job_type=%s resource_type=%s resource_id=%s",
        job_id,
        job_type,
        resource_type,
        resource_id,
    )
    return {
        "id": job_id,
        "status": JobStatus.QUEUED.value,
        "job_type": job_type,
        "resource_type": resource_type,
        "resource_id": resource_id,
    }


def get_job(job_id: str) -> dict[str, Any] | None:
    """Fetch a background job by ID."""
    results = fetch_all("SELECT * FROM background_jobs WHERE id = %s", (job_id,))
    return results[0] if results else None


def list_jobs(
    job_type: str | None = None,
    status: str | None = None,
    resource_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """List background jobs with optional filters."""
    query = "SELECT * FROM background_jobs WHERE 1=1"
    params: list[Any] = []

    if job_type:
        query += " AND job_type = %s"
        params.append(job_type)

    if status:
        query += " AND status = %s"
        params.append(status)

    if resource_type:
        query += " AND resource_type = %s"
        params.append(resource_type)

    query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    return fetch_all(query, tuple(params))


def mark_running(job_id: str) -> bool:
    """Mark a job as currently running."""
    try:
        execute(
            "UPDATE background_jobs SET status = %s, started_at = now() WHERE id = %s AND status = %s",
            (JobStatus.RUNNING.value, job_id, JobStatus.QUEUED.value),
        )
        logger.info("Marked job as running: job_id=%s", job_id)
        return True
    except Exception as e:
        logger.error("Failed to mark job running: job_id=%s error=%s", job_id, e)
        return False


def mark_completed(job_id: str, result_metadata: dict[str, Any] | None = None) -> bool:
    """Mark a job as successfully completed."""
    try:
        meta = json.dumps(result_metadata or {})
        execute(
            """
            UPDATE background_jobs
            SET status = %s, completed_at = now(), metadata = %s::jsonb
            WHERE id = %s
            """,
            (JobStatus.COMPLETED.value, meta, job_id),
        )
        logger.info("Marked job as completed: job_id=%s", job_id)
        return True
    except Exception as e:
        logger.error("Failed to mark job completed: job_id=%s error=%s", job_id, e)
        return False


def mark_failed(job_id: str, error: str | None = None) -> bool:
    """Mark a job as failed and decide whether to retry."""
    try:
        job = get_job(job_id)
        if not job:
            return False

        attempts = job["attempts"] + 1
        if attempts < job["max_attempts"]:
            if _supports_next_retry_at():
                # Retry with persisted ETA when schema supports it.
                backoff_seconds = min(int(math.pow(2, max(attempts - 1, 0)) * _RETRY_BASE_SECONDS), _RETRY_MAX_SECONDS)
                next_retry_at = datetime.now(UTC) + timedelta(seconds=backoff_seconds)
                execute(
                    """
                    UPDATE background_jobs
                    SET status = %s, error = %s, attempts = %s, next_retry_at = %s
                    WHERE id = %s
                    """,
                    (JobStatus.RETRYING.value, error, attempts, next_retry_at, job_id),
                )
                logger.warning(
                    "Marked job for retry: job_id=%s attempt=%d/%d next_retry_at=%s error=%s",
                    job_id,
                    attempts,
                    job["max_attempts"],
                    next_retry_at.isoformat(),
                    error,
                )
            else:
                execute(
                    """
                    UPDATE background_jobs
                    SET status = %s, error = %s, attempts = %s
                    WHERE id = %s
                    """,
                    (JobStatus.RETRYING.value, error, attempts, job_id),
                )
                logger.warning(
                    "Marked job for retry (legacy schema): job_id=%s attempt=%d/%d error=%s",
                    job_id,
                    attempts,
                    job["max_attempts"],
                    error,
                )
        else:
            # Final failure: mark as failed
            if _supports_next_retry_at():
                execute(
                    """
                    UPDATE background_jobs
                    SET status = %s, error = %s, attempts = %s, next_retry_at = NULL, completed_at = now()
                    WHERE id = %s
                    """,
                    (JobStatus.FAILED.value, error, attempts, job_id),
                )
            else:
                execute(
                    """
                    UPDATE background_jobs
                    SET status = %s, error = %s, attempts = %s, completed_at = now()
                    WHERE id = %s
                    """,
                    (JobStatus.FAILED.value, error, attempts, job_id),
                )
            logger.error("Marked job as failed (max retries exceeded): job_id=%s error=%s", job_id, error)

        return True
    except Exception as e:
        logger.error("Failed to mark job failed: job_id=%s error=%s", job_id, e)
        return False


def mark_skipped(job_id: str, reason: str | None = None) -> bool:
    """Mark a job as skipped (idempotent or not applicable)."""
    try:
        meta = json.dumps({"skip_reason": reason} if reason else {})
        execute(
            """
            UPDATE background_jobs
            SET status = %s, completed_at = now(), metadata = %s::jsonb
            WHERE id = %s
            """,
            (JobStatus.SKIPPED.value, meta, job_id),
        )
        logger.info("Marked job as skipped: job_id=%s reason=%s", job_id, reason)
        return True
    except Exception as e:
        logger.error("Failed to mark job skipped: job_id=%s error=%s", job_id, e)
        return False


def next_retryable_job() -> dict[str, Any] | None:
    """Get the next job that should be retried (exponential backoff logic)."""
    if _supports_next_retry_at():
        results = fetch_all(
            """
            SELECT * FROM background_jobs
            WHERE status = %s
              AND (next_retry_at IS NULL OR next_retry_at <= now())
            ORDER BY attempts ASC, next_retry_at ASC NULLS FIRST, created_at ASC
            LIMIT 1
            """,
            (JobStatus.RETRYING.value,),
        )
    else:
        results = fetch_all(
            """
            SELECT * FROM background_jobs
            WHERE status = %s
            ORDER BY attempts ASC, created_at ASC
            LIMIT 1
            """,
            (JobStatus.RETRYING.value,),
        )
    if results:
        return results[0]

    queued = fetch_all(
        """
        SELECT * FROM background_jobs
        WHERE status = %s
        ORDER BY created_at ASC
        LIMIT 1
        """,
        (JobStatus.QUEUED.value,),
    )
    if queued:
        return queued[0]
    return None


def claim_next_due_job(worker_id: str = "local-worker") -> dict[str, Any] | None:
    """Atomically claim one due job for execution.

    Claims queued jobs first, then retrying jobs whose retry ETA has elapsed.
    Uses FOR UPDATE SKIP LOCKED to avoid duplicate claims across workers.
    """
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if _supports_next_retry_at():
                cursor.execute(
                    """
                    WITH candidate AS (
                        SELECT id
                        FROM background_jobs
                        WHERE status = %s
                           OR (status = %s AND (next_retry_at IS NULL OR next_retry_at <= now()))
                        ORDER BY
                            CASE WHEN status = %s THEN 0 ELSE 1 END,
                            attempts ASC,
                            next_retry_at ASC NULLS FIRST,
                            created_at ASC
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    UPDATE background_jobs AS bj
                    SET
                        status = %s,
                        started_at = now(),
                        next_retry_at = NULL,
                        metadata = COALESCE(bj.metadata, '{}'::jsonb)
                            || jsonb_build_object('claimed_by', %s, 'claimed_at', now()::text)
                    FROM candidate
                    WHERE bj.id = candidate.id
                    RETURNING bj.*
                    """,
                    (
                        JobStatus.QUEUED.value,
                        JobStatus.RETRYING.value,
                        JobStatus.QUEUED.value,
                        JobStatus.RUNNING.value,
                        worker_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    WITH candidate AS (
                        SELECT id
                        FROM background_jobs
                        WHERE status IN (%s, %s)
                        ORDER BY
                            CASE WHEN status = %s THEN 0 ELSE 1 END,
                            attempts ASC,
                            created_at ASC
                        FOR UPDATE SKIP LOCKED
                        LIMIT 1
                    )
                    UPDATE background_jobs AS bj
                    SET
                        status = %s,
                        started_at = now(),
                        metadata = COALESCE(bj.metadata, '{}'::jsonb)
                            || jsonb_build_object('claimed_by', %s, 'claimed_at', now()::text)
                    FROM candidate
                    WHERE bj.id = candidate.id
                    RETURNING bj.*
                    """,
                    (
                        JobStatus.QUEUED.value,
                        JobStatus.RETRYING.value,
                        JobStatus.QUEUED.value,
                        JobStatus.RUNNING.value,
                        worker_id,
                    ),
                )
            row = cursor.fetchone()
        connection.commit()
    return dict(row) if row else None


def list_retry_eta(limit: int = 100) -> list[dict[str, Any]]:
    """Return retry queue view with computed ETA in seconds."""
    if _supports_next_retry_at():
        rows = fetch_all(
            """
            SELECT id, job_type, status, attempts, max_attempts, next_retry_at, error, created_at
            FROM background_jobs
            WHERE status IN (%s, %s)
            ORDER BY next_retry_at ASC NULLS FIRST, created_at ASC
            LIMIT %s
            """,
            (JobStatus.RETRYING.value, JobStatus.QUEUED.value, limit),
        )
    else:
        rows = fetch_all(
            """
            SELECT id, job_type, status, attempts, max_attempts, error, created_at
            FROM background_jobs
            WHERE status IN (%s, %s)
            ORDER BY created_at ASC
            LIMIT %s
            """,
            (JobStatus.RETRYING.value, JobStatus.QUEUED.value, limit),
        )
    now = datetime.now(UTC)
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        next_retry_at = item.get("next_retry_at")
        if isinstance(next_retry_at, datetime):
            eta_seconds = max(int((next_retry_at - now).total_seconds()), 0)
        else:
            eta_seconds = 0
        item["retry_eta_seconds"] = eta_seconds
        item["due_now"] = eta_seconds == 0
        enriched.append(item)
    return enriched


def run_worker_loop(
    job_handler: Callable[[dict[str, Any]], dict[str, Any] | None],
    worker_id: str = "local-worker",
    poll_interval_seconds: float = 2.0,
    max_iterations: int | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> dict[str, int]:
    """Run a durable polling loop that atomically claims due jobs.

    Returns loop statistics so callers can inspect behavior in tests/ops.
    """
    processed = 0
    skipped = 0
    failed = 0
    idle_cycles = 0
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        iterations += 1

        job = claim_next_due_job(worker_id=worker_id)
        if job is None:
            idle_cycles += 1
            sleep_fn(poll_interval_seconds)
            continue

        try:
            result = job_handler(job) or {}
            if isinstance(result, dict) and result.get("_job_status") == JobStatus.SKIPPED.value:
                reason = str(result.get("_skip_reason") or "not_applicable")
                mark_skipped(str(job["id"]), reason)
                skipped += 1
            else:
                mark_completed(str(job["id"]), result if isinstance(result, dict) else {})
                processed += 1
        except Exception as exc:
            mark_failed(str(job["id"]), str(exc))
            failed += 1

    return {
        "iterations": iterations,
        "processed": processed,
        "skipped": skipped,
        "failed": failed,
        "idle_cycles": idle_cycles,
    }


def prune_completed_jobs(older_than_days: int = 7) -> int:
    """Delete completed/failed jobs older than N days (cleanup)."""
    cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
    try:
        results = fetch_all(
            """
            DELETE FROM background_jobs
            WHERE status IN (%s, %s) AND completed_at < %s
            RETURNING id
            """,
            (JobStatus.COMPLETED.value, JobStatus.FAILED.value, cutoff),
        )
        count = len(results) if results else 0
        logger.info("Pruned %d old background jobs", count)
        return count
    except Exception as e:
        logger.error("Failed to prune background jobs: error=%s", e)
        return 0
