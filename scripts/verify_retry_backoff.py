"""Verify durable retry scheduling and exponential backoff end-to-end.

This script creates a background job, forces two worker failures, and checks
that `next_retry_at` is persisted and moves further into the future.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
from typing import Sequence

from app.memory.postgres import execute, fetch_all
from app.services.background_jobs import JobType, create_job, run_worker_loop
from app.services.background_worker import build_job_handler_map, dispatch_job


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify retry scheduling/backoff behavior")
    parser.add_argument("--worker-id", default="projectrag-worker-retry-demo", help="Worker identity used for claims")
    parser.add_argument("--poll-interval", type=float, default=0.1, help="Worker poll interval in seconds")
    parser.add_argument("--max-attempts", type=int, default=3, help="Job max attempts for demo job")
    parser.add_argument(
        "--missing-file",
        default="data/raw/nonexistent_forced_failure.txt",
        help="Missing file path used by ingest_document payload",
    )
    parser.add_argument(
        "--force-retry-due-seconds",
        type=float,
        default=1.0,
        help="How far in the past to set next_retry_at before second attempt",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Exit non-zero if the expected retry/backoff patterns are not met (default: enabled)",
    )
    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Always exit zero, even if checks fail",
    )
    return parser.parse_args(argv)


def _get_job_state(job_id: str) -> dict | None:
    rows = fetch_all(
        """
        SELECT id, status, attempts, max_attempts, next_retry_at, error, created_at, started_at, completed_at
        FROM background_jobs
        WHERE id = %s
        """,
        (job_id,),
    )
    return dict(rows[0]) if rows else None


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    handlers = build_job_handler_map()

    job = create_job(
        JobType.INGEST_DOCUMENT,
        metadata={"file_path": args.missing_file},
        max_attempts=args.max_attempts,
    )
    job_id = job["id"]

    def failing_handler(job_row: dict) -> dict:
        # Exercise real dispatch path, then force a runtime failure to trigger retry logic.
        _ = dispatch_job(job_row, handlers=handlers)
        raise RuntimeError("forced_runtime_failure_for_retry_demo")

    before = _get_job_state(job_id)
    print("created", job_id)
    print("before", before)

    stats1 = run_worker_loop(
        job_handler=failing_handler,
        worker_id=args.worker_id,
        poll_interval_seconds=args.poll_interval,
        max_iterations=1,
    )
    after_attempt_1 = _get_job_state(job_id)

    execute(
        "UPDATE background_jobs SET next_retry_at = %s WHERE id = %s",
        (datetime.now(UTC) - timedelta(seconds=args.force_retry_due_seconds), job_id),
    )

    stats2 = run_worker_loop(
        job_handler=failing_handler,
        worker_id=args.worker_id,
        poll_interval_seconds=args.poll_interval,
        max_iterations=1,
    )
    after_attempt_2 = _get_job_state(job_id)

    now = datetime.now(UTC)
    eta1 = int((after_attempt_1["next_retry_at"] - now).total_seconds()) if after_attempt_1 and after_attempt_1.get("next_retry_at") else None
    eta2 = int((after_attempt_2["next_retry_at"] - now).total_seconds()) if after_attempt_2 and after_attempt_2.get("next_retry_at") else None

    checks = {
        "attempt1_retrying": bool(after_attempt_1 and after_attempt_1.get("status") == "retrying"),
        "attempt1_attempts_is_1": bool(after_attempt_1 and after_attempt_1.get("attempts") == 1),
        "attempt1_has_next_retry_at": bool(after_attempt_1 and after_attempt_1.get("next_retry_at") is not None),
        "attempt2_retrying": bool(after_attempt_2 and after_attempt_2.get("status") == "retrying"),
        "attempt2_attempts_is_2": bool(after_attempt_2 and after_attempt_2.get("attempts") == 2),
        "backoff_increased": bool(eta1 is not None and eta2 is not None and eta2 > eta1),
    }

    print("attempt1_stats", stats1)
    print("attempt1_state", after_attempt_1)
    print("attempt2_stats", stats2)
    print("attempt2_state", after_attempt_2)
    print("eta_seconds", {"after_attempt_1": eta1, "after_attempt_2": eta2})
    print("checks", checks)

    ok = all(checks.values())
    print("result", "PASS" if ok else "FAIL")
    if args.strict and not ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())