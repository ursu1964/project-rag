"""Lightweight text document parsing and metadata extraction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SUPPORTED_SUFFIXES = {".txt", ".md", ".log", ".json", ".yaml", ".yml", ".tf"}


def is_supported_text_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_SUFFIXES


def _source_type(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".log":
        return "log"
    if suffix == ".tf":
        return "terraform"
    if suffix in {".yaml", ".yml"} and ("apiVersion:" in text or "kind:" in text):
        return "kubernetes_manifest"
    if suffix in {".md"}:
        return "runbook"
    if suffix == ".json":
        return "json"
    return "document"


def parse_text_document(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    text = resolved.read_text(encoding="utf-8")
    metadata: dict[str, Any] = {
        "filename": resolved.name,
        "suffix": resolved.suffix.lower(),
        "source": str(resolved),
        "source_type": _source_type(resolved, text),
        "line_count": len(text.splitlines()),
        "char_count": len(text),
    }
    if resolved.suffix.lower() == ".json":
        try:
            data = json.loads(text)
            metadata["json_type"] = type(data).__name__
            if isinstance(data, dict):
                metadata["top_level_keys"] = sorted(data.keys())
            elif isinstance(data, list):
                metadata["array_item_count"] = len(data)
        except json.JSONDecodeError:
            metadata["json_parse_error"] = True
    return {"text": text, "metadata": metadata}
