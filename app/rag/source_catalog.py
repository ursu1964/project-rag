"""Local source catalog for inspectable RAG inputs."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.rag.parsing import is_supported_text_file

_ALLOWED_SUFFIXES = {".txt", ".md", ".log", ".json", ".yaml", ".yml", ".tf"}


def _classify_source(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix == ".tf":
        return "terraform"
    if suffix in {".yaml", ".yml"} and any(token in name for token in ("k8s", "kubernetes", "manifest")):
        return "kubernetes_manifest"
    if suffix in {".log"}:
        return "log"
    if suffix == ".json" and any(token in name for token in ("inventory", "cmdb")):
        return "inventory"
    if any(token in name for token in ("runbook", "incident")):
        return "runbook"
    return "document"


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "filename": path.name,
        "suffix": path.suffix.lower(),
        "source_type": _classify_source(path),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "ingestable": is_supported_text_file(path),
    }


def build_source_catalog(root: str | Path = "data/raw") -> dict[str, Any]:
    """Return a read-only catalog of local source files."""
    base = Path(root)
    if not base.exists():
        return {"root": str(base), "status": "missing", "total_sources": 0, "sources": [], "counts": {}}

    sources = [
        _file_record(path, base)
        for path in sorted(base.rglob("*"))
        if path.is_file() and path.suffix.lower() in _ALLOWED_SUFFIXES
    ]
    counts: dict[str, int] = {}
    for source in sources:
        source_type = str(source["source_type"])
        counts[source_type] = counts.get(source_type, 0) + 1

    return {
        "root": str(base),
        "status": "ok",
        "total_sources": len(sources),
        "counts": counts,
        "sources": sources,
    }
