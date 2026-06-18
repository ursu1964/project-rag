from __future__ import annotations

from app.services import background_worker


def test_dispatch_unknown_job_type_returns_skip():
    result = background_worker.dispatch_job({"id": "job-1", "job_type": "unknown"}, handlers={})

    assert result["_job_status"] == "skipped"
    assert result["_skip_reason"] == "unknown_job_type"


def test_handle_ingest_document_missing_path_skips():
    result = background_worker.handle_ingest_document({"job_type": "ingest_document", "metadata": {}})

    assert result["_job_status"] == "skipped"
    assert result["_skip_reason"] == "missing_file_path"


def test_dispatch_uses_handler_map(monkeypatch):
    handlers = {"ingest_document": lambda job: {"ok": True, "id": job["id"]}}

    result = background_worker.dispatch_job({"id": "job-42", "job_type": "ingest_document"}, handlers=handlers)

    assert result["ok"] is True
    assert result["id"] == "job-42"


def test_build_job_handler_map_contains_all_known_types():
    handlers = background_worker.build_job_handler_map()

    assert "ingest_document" in handlers
    assert "ingest_directory" in handlers
    assert "evaluate_golden_set" in handlers
    assert "connector_sync" in handlers
    assert "citation_validation" in handlers
    assert "pii_scan" in handlers
