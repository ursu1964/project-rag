from __future__ import annotations

from scripts import run_background_worker


def test_worker_script_calls_run_loop(monkeypatch):
    captured = {}

    monkeypatch.setattr(
        run_background_worker,
        "run_worker_loop",
        lambda **kwargs: captured.update(kwargs) or {"iterations": 1, "processed": 0, "skipped": 0, "failed": 0, "idle_cycles": 1},
    )
    monkeypatch.setattr(
        run_background_worker,
        "build_job_handler_map",
        lambda: {"ingest_document": lambda job: {"ok": True}},
    )

    code = run_background_worker.main(["--worker-id", "w1", "--once"])

    assert code == 0
    assert captured["worker_id"] == "w1"
    assert captured["max_iterations"] == 1
    assert callable(captured["job_handler"])
