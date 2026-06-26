"""Document routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile

from app.core.config import settings
from app.core.metrics import INGESTION_COUNTER, REQUEST_COUNTER
from app.core.metrics import INGESTION_FAILURE_COUNTER, PII_SCAN_COUNTER
from app.core.schemas import DocumentRecord, IngestResponse
from app.rag.ingestion import ingest_directory, ingest_file
from app.security.audit import record_security_event
from app.security.rbac import permission_dependency
from app.repositories.documents_repository import delete_document as repository_delete_document
from app.repositories.documents_repository import get_document as repository_get_document
from app.repositories.documents_repository import list_documents as repository_list_documents
from app.tools.file_tools import safe_write_upload

router = APIRouter()

_RAW_DATA_DIR = Path("data/raw")


@router.get("/documents", response_model=list[DocumentRecord], dependencies=[Depends(permission_dependency("read"))])
def list_documents() -> list[dict]:
    REQUEST_COUNTER.labels("/documents").inc()
    return repository_list_documents()


@router.delete("/documents/{document_id}", dependencies=[Depends(permission_dependency("ingest"))])
def delete_document(document_id: str) -> dict[str, str]:
    REQUEST_COUNTER.labels("/documents/{document_id}:delete").inc()
    if not repository_delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": document_id}


@router.post("/documents/{document_id}/reindex", dependencies=[Depends(permission_dependency("ingest"))])
def reindex_document(document_id: str) -> dict[str, object]:
    REQUEST_COUNTER.labels("/documents/{document_id}/reindex").inc()
    document = repository_get_document(document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    source = Path(str(document["source"]))
    if not source.exists():
        raise HTTPException(status_code=404, detail="Document source file not found")

    if not repository_delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "status": "reindexed",
        "previous_document_id": document_id,
        "result": ingest_file(source),
    }


def _save_upload(file: UploadFile, ingest: bool = False) -> dict[str, object]:
    try:
        destination = safe_write_upload(file, _RAW_DATA_DIR, max_bytes=settings.max_upload_size_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response: dict[str, object] = {"filename": destination.name, "path": str(destination)}
    if ingest:
        response["ingestion"] = ingest_file(destination)
    return response


def _save_uploads(files: list[UploadFile], ingest: bool = False) -> list[dict[str, object]]:
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Missing upload file")

    max_files = int(settings.max_upload_files_per_request)
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many upload files; maximum allowed is {max_files}",
        )

    return [_save_upload(file, ingest=ingest) for file in files]


@router.post("/documents/upload", dependencies=[Depends(permission_dependency("ingest"))])
async def upload_document(request: Request, ingest: bool = Query(default=False)) -> dict[str, object]:
    REQUEST_COUNTER.labels("/documents/upload").inc()
    form = await request.form()
    files = [item for item in form.getlist("file") if isinstance(item, UploadFile)]
    results = _save_uploads(files, ingest=ingest)
    result: dict[str, object] = results[0] if len(results) == 1 else {"files": results}
    record_security_event(
        action="upload",
        resource="/documents/upload",
        decision="allow",
        risk_level="low",
        metadata={
            "filename": result.get("filename") if len(results) == 1 else None,
            "file_count": len(results),
            "ingested": ingest,
        },
    )
    return result


@router.post("/ingest", response_model=IngestResponse, dependencies=[Depends(permission_dependency("ingest"))])
def ingest_raw_documents() -> dict[str, object]:
    REQUEST_COUNTER.labels("/ingest").inc()
    INGESTION_COUNTER.inc()
    results = ingest_directory("data/raw", max_files=settings.ingest_max_files_per_run)
    pii_flagged = sum(int(r.get("pii_chunks_sanitised") or 0) for r in results if isinstance(r, dict))
    failed = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "failed")
    if pii_flagged > 0:
        PII_SCAN_COUNTER.inc()
    if failed > 0:
        INGESTION_FAILURE_COUNTER.inc()
    record_security_event(
        action="ingest",
        resource="/ingest",
        decision="allow",
        risk_level="medium" if pii_flagged > 0 else "low",
        metadata={"total_files": len(results), "pii_chunks_sanitised": pii_flagged},
    )
    return {"status": "ok", "results": results}
