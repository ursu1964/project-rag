"""Background worker job-type dispatch and concrete handlers."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.api.routes_connectors import ConnectorSyncRequest, sync_connector
from app.core.logging import get_logger
from app.rag.ingestion import ingest_directory, ingest_file
from app.services.background_jobs import JobType
from app.services.golden_evaluation import run_golden_evaluation

logger = get_logger(__name__)

JobHandler = Callable[[dict[str, Any]], dict[str, Any]]


def _skip(reason: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "_job_status": "skipped",
        "_skip_reason": reason,
    }
    payload.update(extra)
    return payload


def _metadata(job: dict[str, Any]) -> dict[str, Any]:
    raw = job.get("metadata")
    return raw if isinstance(raw, dict) else {}


def handle_ingest_document(job: dict[str, Any]) -> dict[str, Any]:
    meta = _metadata(job)
    file_path = str(meta.get("file_path") or job.get("resource_id") or "").strip()
    if not file_path:
        return _skip("missing_file_path", job_type=job.get("job_type"))

    if not Path(file_path).exists():
        return _skip("file_not_found", file_path=file_path)

    result = ingest_file(file_path)
    return {
        "handler": "ingest_document",
        "result": result,
    }


def handle_ingest_directory(job: dict[str, Any]) -> dict[str, Any]:
    meta = _metadata(job)
    directory = str(meta.get("directory") or job.get("resource_id") or "data/raw").strip()
    max_files = meta.get("max_files")
    if isinstance(max_files, str) and max_files.isdigit():
        max_files = int(max_files)

    if not Path(directory).exists():
        return _skip("directory_not_found", directory=directory)

    result = ingest_directory(directory, max_files=max_files if isinstance(max_files, int) else None)
    return {
        "handler": "ingest_directory",
        "directory": directory,
        "files": len(result),
        "result": result,
    }


def handle_evaluate_golden_set(job: dict[str, Any]) -> dict[str, Any]:
    meta = _metadata(job)
    category = str(job.get("resource_id") or meta.get("category") or "").strip()
    if not category:
        return _skip("missing_dataset_category")

    result = run_golden_evaluation(category, job_id=None)
    return {
        "handler": "evaluate_golden_set",
        "category": category,
        "result": result,
    }


def handle_connector_sync(job: dict[str, Any]) -> dict[str, Any]:
    meta = _metadata(job)
    connector_type = str(job.get("resource_id") or meta.get("connector_type") or "").strip().lower()
    if not connector_type:
        return _skip("missing_connector_type")

    request = ConnectorSyncRequest(
        dry_run=bool(meta.get("dry_run", True)),
        config=meta.get("config") if isinstance(meta.get("config"), dict) else {},
    )
    try:
        result = sync_connector(connector_type, request)
    except HTTPException as exc:
        return _skip("connector_not_found", connector_type=connector_type, detail=exc.detail)

    if str(result.get("status") or "").lower() == "skipped":
        return _skip(str(result.get("reason") or "connector_sync_skipped"), connector_type=connector_type)
    return {
        "handler": "connector_sync",
        "connector_type": connector_type,
        "result": result,
    }


def handle_citation_validation(job: dict[str, Any]) -> dict[str, Any]:
    return _skip("handler_not_implemented", job_type=job.get("job_type"))


def handle_pii_scan(job: dict[str, Any]) -> dict[str, Any]:
    return _skip("handler_not_implemented", job_type=job.get("job_type"))


def build_job_handler_map() -> dict[str, JobHandler]:
    """Return concrete handlers keyed by job_type."""
    return {
        JobType.INGEST_DOCUMENT.value: handle_ingest_document,
        JobType.INGEST_DIRECTORY.value: handle_ingest_directory,
        JobType.EVALUATE_GOLDEN_SET.value: handle_evaluate_golden_set,
        JobType.CONNECTOR_SYNC.value: handle_connector_sync,
        JobType.CITATION_VALIDATION.value: handle_citation_validation,
        JobType.PII_SCAN.value: handle_pii_scan,
    }


def dispatch_job(job: dict[str, Any], handlers: dict[str, JobHandler] | None = None) -> dict[str, Any]:
    """Dispatch a claimed job to the mapped handler with safe fallback."""
    handler_map = handlers or build_job_handler_map()
    job_type = str(job.get("job_type") or "").strip()
    handler = handler_map.get(job_type)
    if handler is None:
        logger.warning("No handler configured for job_type=%s", job_type)
        return _skip("unknown_job_type", job_type=job_type)
    return handler(job)
