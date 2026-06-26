"""Local source catalog builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.rag.parsing import is_supported_text_file


def build_source_catalog(root: str | Path = "data/raw") -> dict[str, Any]:
    path = Path(root)
    if not path.exists():
        return {"status": "missing", "total_sources": 0, "sources": [], "counts": {}}
    sources = []
    counts: dict[str, int] = {}
    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        ingestable = is_supported_text_file(file_path)
        counts[suffix or "none"] = counts.get(suffix or "none", 0) + 1
        sources.append({"path": str(file_path), "filename": file_path.name, "suffix": suffix, "ingestable": ingestable})
    return {"status": "ok", "total_sources": len(sources), "sources": sources, "counts": counts}
