from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, UploadFile

import app.api.routes_documents as routes_documents
import app.tools.file_tools as file_tools


def _upload(name: str, content: bytes = b"hello") -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content))


def test_upload_document_saves_allowed_file(tmp_path, monkeypatch):
    monkeypatch.setattr(routes_documents, "_RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", tmp_path)

    result = routes_documents._save_upload(_upload("note.txt"))

    assert result["filename"] == "note.txt"
    assert Path(result["path"]).read_text() == "hello"
    assert "ingestion" not in result


def test_upload_document_rejects_unsupported_type(tmp_path, monkeypatch):
    monkeypatch.setattr(routes_documents, "_RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", tmp_path)

    with pytest.raises(HTTPException) as exc:
        routes_documents._save_upload(_upload("note.pdf"))

    assert exc.value.status_code == 400


def test_upload_document_rejects_path_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(routes_documents, "_RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", tmp_path)

    with pytest.raises(HTTPException) as exc:
        routes_documents._save_upload(_upload("../note.txt"))

    assert exc.value.status_code == 400


def test_upload_document_ingests_when_requested(tmp_path, monkeypatch):
    monkeypatch.setattr(routes_documents, "_RAW_DATA_DIR", tmp_path)
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", tmp_path)
    ingest_file = MagicMock(return_value={"status": "ingested"})
    monkeypatch.setattr(routes_documents, "ingest_file", ingest_file)

    result = routes_documents._save_upload(_upload("note.md"), ingest=True)

    assert result["ingestion"] == {"status": "ingested"}
    ingest_file.assert_called_once()


def test_upload_document_rejects_too_many_files(monkeypatch):
    monkeypatch.setattr(routes_documents.settings, "max_upload_files_per_request", 1)

    with pytest.raises(HTTPException) as exc:
        routes_documents._save_uploads([_upload("one.txt"), _upload("two.txt")])

    assert exc.value.status_code == 400
    assert "Too many upload files" in str(exc.value.detail)
