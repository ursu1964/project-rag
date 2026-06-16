"""Document routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request, UploadFile

from app.core.metrics import INGESTION_COUNTER, REQUEST_COUNTER
from app.core.schemas import DocumentRecord, IngestResponse
from app.repositories.documents_repository import list_documents as repository_list_documents
from app.rag.ingestion import ingest_directory, ingest_file
from app.tools.file_tools import safe_write_upload

router = APIRouter()

_RAW_DATA_DIR = Path("data/raw")


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents() -> list[dict]:
    REQUEST_COUNTER.labels("/documents").inc()
    return repository_list_documents()


def _save_upload(file: UploadFile, ingest: bool = False) -> dict[str, object]:
    try:
        destination = safe_write_upload(file, _RAW_DATA_DIR)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response: dict[str, object] = {"filename": destination.name, "path": str(destination)}
    if ingest:
        response["ingestion"] = ingest_file(destination)
    return response


@router.post("/documents/upload")
async def upload_document(request: Request, ingest: bool = Query(default=False)) -> dict[str, object]:
    REQUEST_COUNTER.labels("/documents/upload").inc()
    form = await request.form()
    file = form.get("file")
    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=400, detail="Missing upload file")
    return _save_upload(file, ingest=ingest)


@router.post("/ingest", response_model=IngestResponse)
def ingest_raw_documents() -> dict[str, object]:
    REQUEST_COUNTER.labels("/ingest").inc()
    INGESTION_COUNTER.inc()
    results = ingest_directory("data/raw")
    return {"status": "ok", "results": results}
