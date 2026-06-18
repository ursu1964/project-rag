"""Safe local file handling helpers."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

_ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".md", ".log"}
_RAW_DATA_DIR = Path("data/raw")


def safe_filename(filename: str) -> str:
    """Return a normalized basename safe for local storage."""
    original = filename or ""
    name = Path(original).name
    if not name or name != original:
        raise ValueError("Invalid filename")

    normalized = re.sub(r"[^A-Za-z0-9._-]", "_", name).strip("._")
    if not normalized or normalized in {".", ".."}:
        raise ValueError("Invalid filename")
    return normalized


def ensure_directory(path: Path) -> None:
    """Create a directory if needed."""
    path.mkdir(parents=True, exist_ok=True)


def is_allowed_extension(filename: str, allowed: set[str]) -> bool:
    """Check filename extension against an allowed set."""
    return Path(filename).suffix.lower() in {extension.lower() for extension in allowed}


def safe_write_upload(upload_file, target_dir: Path, max_bytes: int | None = None) -> Path:
    """Safely write an UploadFile-like object under data/raw and return its path."""
    raw_root = _RAW_DATA_DIR.resolve()
    target_root = target_dir.resolve()
    if target_root != raw_root:
        raise ValueError("Uploads may only be written to data/raw")

    filename = safe_filename(upload_file.filename or "")
    if not is_allowed_extension(filename, _ALLOWED_UPLOAD_EXTENSIONS):
        raise ValueError("Unsupported file type")

    ensure_directory(target_dir)
    destination = (target_dir / filename).resolve()
    if raw_root not in destination.parents:
        raise ValueError("Invalid upload path")

    limit = int(max_bytes) if max_bytes is not None else 0
    if limit < 0:
        raise ValueError("Invalid upload size limit")
    if limit and hasattr(upload_file, "size") and upload_file.size and int(upload_file.size) > limit:
        raise ValueError("Upload file exceeds configured size limit")

    with destination.open("wb") as output:
        shutil.copyfileobj(upload_file.file, output)
    if limit and destination.stat().st_size > limit:
        destination.unlink(missing_ok=True)
        raise ValueError("Upload file exceeds configured size limit")
    return destination
