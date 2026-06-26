"""Document registry helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from app.repositories.documents_repository import create_document


def calculate_file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def register_document(filename: str, source_path: str, file_hash: str, metadata: dict[str, Any] | None = None) -> str:
    return create_document(source_path, file_hash, {"filename": filename, **(metadata or {})})
