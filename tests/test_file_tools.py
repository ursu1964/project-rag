from io import BytesIO

import pytest
from fastapi import UploadFile

import app.tools.file_tools as file_tools


def _upload(name: str, content: bytes = b"hello") -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(content))


def test_safe_filename_normalizes_simple_name():
    assert file_tools.safe_filename("my file.txt") == "my_file.txt"


def test_safe_filename_rejects_path_traversal():
    with pytest.raises(ValueError):
        file_tools.safe_filename("../secret.txt")


def test_is_allowed_extension():
    assert file_tools.is_allowed_extension("a.TXT", {".txt"}) is True
    assert file_tools.is_allowed_extension("a.pdf", {".txt"}) is False


def test_safe_write_upload_writes_inside_raw(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", raw)

    saved = file_tools.safe_write_upload(_upload("note.txt"), raw)

    assert saved == raw.resolve() / "note.txt"
    assert saved.read_bytes() == b"hello"


def test_safe_write_upload_rejects_non_raw_target(tmp_path, monkeypatch):
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", tmp_path / "data" / "raw")

    with pytest.raises(ValueError):
        file_tools.safe_write_upload(_upload("note.txt"), tmp_path / "other")


def test_safe_write_upload_rejects_unsupported_extension(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", raw)

    with pytest.raises(ValueError):
        file_tools.safe_write_upload(_upload("note.pdf"), raw)


def test_safe_write_upload_rejects_file_too_large(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    monkeypatch.setattr(file_tools, "_RAW_DATA_DIR", raw)

    with pytest.raises(ValueError, match="size limit"):
        file_tools.safe_write_upload(_upload("note.txt", content=b"x" * 8), raw, max_bytes=4)
