"""Safe upload file helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_ALLOWED_SUFFIXES = {".txt", ".md", ".log", ".json", ".yaml", ".yml", ".tf"}


def safe_write_upload(file: Any, destination_dir: str | Path, max_bytes: int = 5 * 1024 * 1024) -> Path:
    filename = Path(str(getattr(file, "filename", ""))).name
    if not filename or filename in {".", ".."}:
        raise ValueError("Invalid upload filename")
    if Path(filename).suffix.lower() not in _ALLOWED_SUFFIXES:
        raise ValueError("Unsupported upload file type")
    destination = Path(destination_dir)
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / filename
    data = file.file.read() if hasattr(file, "file") else file.read()
    if isinstance(data, str):
        data = data.encode("utf-8")
    if len(data) > int(max_bytes):
        raise ValueError("Upload exceeds maximum size")
    target.write_bytes(data)
    return target
