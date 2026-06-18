from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import app.services.background_jobs as background_jobs


def test_list_retry_eta_computes_due_flags(monkeypatch):
    now = datetime.now(UTC)
    monkeypatch.setattr(
        background_jobs,
        "fetch_all",
        lambda query, params=(): [
            {
                "id": "job-1",
                "job_type": "ingest_document",
                "status": "retrying",
                "attempts": 1,
                "max_attempts": 3,
                "next_retry_at": now + timedelta(seconds=5),
                "error": "timeout",
                "created_at": now,
            },
            {
                "id": "job-2",
                "job_type": "ingest_document",
                "status": "queued",
                "attempts": 0,
                "max_attempts": 3,
                "next_retry_at": None,
                "error": None,
                "created_at": now,
            },
        ],
    )

    rows = background_jobs.list_retry_eta(limit=10)

    assert len(rows) == 2
    assert rows[0]["retry_eta_seconds"] >= 0
    assert rows[1]["due_now"] is True


def test_run_worker_loop_processes_claimed_jobs(monkeypatch):
    claimed = iter([
        {"id": "job-1", "job_type": "ingest_document"},
        None,
    ])
    completed = []
    failed = []
    sleeps = []

    monkeypatch.setattr(background_jobs, "claim_next_due_job", lambda worker_id="local-worker": next(claimed))
    monkeypatch.setattr(background_jobs, "mark_completed", lambda job_id, result=None: completed.append((job_id, result)) or True)
    monkeypatch.setattr(background_jobs, "mark_failed", lambda job_id, error=None: failed.append((job_id, error)) or True)

    stats = background_jobs.run_worker_loop(
        job_handler=lambda job: {"handled": job["id"]},
        worker_id="w-1",
        poll_interval_seconds=0.01,
        max_iterations=2,
        sleep_fn=lambda seconds: sleeps.append(seconds),
    )

    assert stats["processed"] == 1
    assert stats["skipped"] == 0
    assert stats["failed"] == 0
    assert completed[0][0] == "job-1"
    assert sleeps


def test_run_worker_loop_marks_failures(monkeypatch):
    claimed = iter([
        {"id": "job-err", "job_type": "ingest_document"},
    ])
    failed = []

    monkeypatch.setattr(background_jobs, "claim_next_due_job", lambda worker_id="local-worker": next(claimed, None))
    monkeypatch.setattr(background_jobs, "mark_completed", lambda job_id, result=None: True)
    monkeypatch.setattr(background_jobs, "mark_failed", lambda job_id, error=None: failed.append((job_id, error)) or True)

    stats = background_jobs.run_worker_loop(
        job_handler=lambda job: (_ for _ in ()).throw(RuntimeError("boom")),
        max_iterations=1,
        sleep_fn=lambda _: None,
    )

    assert stats["failed"] == 1
    assert failed[0][0] == "job-err"


def test_run_worker_loop_marks_skipped_from_handler(monkeypatch):
    claimed = iter([
        {"id": "job-skip", "job_type": "citation_validation"},
    ])
    skipped = []

    monkeypatch.setattr(background_jobs, "claim_next_due_job", lambda worker_id="local-worker": next(claimed, None))
    monkeypatch.setattr(background_jobs, "mark_completed", lambda job_id, result=None: True)
    monkeypatch.setattr(background_jobs, "mark_failed", lambda job_id, error=None: True)
    monkeypatch.setattr(background_jobs, "mark_skipped", lambda job_id, reason=None: skipped.append((job_id, reason)) or True)

    stats = background_jobs.run_worker_loop(
        job_handler=lambda job: {"_job_status": "skipped", "_skip_reason": "handler_not_implemented"},
        max_iterations=1,
        sleep_fn=lambda _: None,
    )

    assert stats["processed"] == 0
    assert stats["skipped"] == 1
    assert stats["failed"] == 0
    assert skipped[0][0] == "job-skip"


def test_claim_next_due_job_uses_atomic_query(monkeypatch):
    called = {"executed": None, "params": None, "committed": False}
    row = {
        "id": "job-atomic",
        "status": "running",
    }

    class _Cursor:
        def execute(self, query, params):
            called["executed"] = query
            called["params"] = params

        def fetchone(self):
            return row

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Connection:
        def cursor(self):
            return _Cursor()

        def commit(self):
            called["committed"] = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(background_jobs, "get_connection", lambda: _Connection())
    monkeypatch.setattr(background_jobs, "_supports_next_retry_at", lambda: True)

    claimed = background_jobs.claim_next_due_job(worker_id="worker-a")

    assert claimed["id"] == "job-atomic"
    assert "FOR UPDATE SKIP LOCKED" in (called["executed"] or "")
    assert called["params"][4] == "worker-a"
    assert called["committed"] is True


def test_claim_next_due_job_legacy_schema_query(monkeypatch):
    called = {"executed": None, "params": None, "committed": False}
    row = {"id": "job-legacy", "status": "running"}

    class _Cursor:
        def execute(self, query, params):
            called["executed"] = query
            called["params"] = params

        def fetchone(self):
            return row

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Connection:
        def cursor(self):
            return _Cursor()

        def commit(self):
            called["committed"] = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(background_jobs, "get_connection", lambda: _Connection())
    monkeypatch.setattr(background_jobs, "_supports_next_retry_at", lambda: False)

    claimed = background_jobs.claim_next_due_job(worker_id="worker-legacy")

    assert claimed["id"] == "job-legacy"
    assert "next_retry_at" not in (called["executed"] or "")
    assert called["params"][4] == "worker-legacy"
    assert called["committed"] is True


def test_next_retryable_job_legacy_schema(monkeypatch):
    monkeypatch.setattr(background_jobs, "_supports_next_retry_at", lambda: False)
    calls = []

    def _fetch_all(query, params=()):
        calls.append(query)
        if "WHERE status = %s" in query and "RETRYING" not in query:
            return [{"id": "job-retry", "status": "retrying"}]
        return []

    monkeypatch.setattr(background_jobs, "fetch_all", _fetch_all)

    job = background_jobs.next_retryable_job()

    assert job is not None
    assert job["id"] == "job-retry"
    assert any("next_retry_at" not in query for query in calls)


def test_list_retry_eta_legacy_schema(monkeypatch):
    monkeypatch.setattr(background_jobs, "_supports_next_retry_at", lambda: False)
    now = datetime.now(UTC)
    monkeypatch.setattr(
        background_jobs,
        "fetch_all",
        lambda query, params=(): [
            {
                "id": "job-legacy",
                "job_type": "ingest_document",
                "status": "retrying",
                "attempts": 1,
                "max_attempts": 3,
                "error": "timeout",
                "created_at": now,
            }
        ],
    )

    rows = background_jobs.list_retry_eta(limit=10)

    assert rows[0]["due_now"] is True
    assert rows[0]["retry_eta_seconds"] == 0
