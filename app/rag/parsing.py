"""Text-like document parsing and metadata extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SUPPORTED_TEXT_SUFFIXES = {".txt", ".md", ".log", ".json", ".yaml", ".yml", ".tf"}


def is_supported_text_file(path: str | Path) -> bool:
    """Return whether a file can be parsed by the local text parser."""
    return Path(path).suffix.lower() in SUPPORTED_TEXT_SUFFIXES


def infer_document_type(path: str | Path) -> str:
    """Infer a lightweight source type from filename and suffix."""
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    name = file_path.name.lower()
    if suffix == ".tf":
        return "terraform"
    if suffix in {".yaml", ".yml"}:
        if any(token in name for token in ("k8s", "kubernetes", "manifest")):
            return "kubernetes_manifest"
        if "ansible" in name or "playbook" in name:
            return "ansible"
        return "yaml"
    if suffix == ".json":
        if any(token in name for token in ("inventory", "cmdb")):
            return "inventory"
        return "json"
    if suffix == ".log":
        return "log"
    if "runbook" in name or "incident" in name:
        return "runbook"
    if suffix == ".md":
        return "markdown"
    return "document"


def _json_metadata(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {"parse_status": "invalid_json"}
    if isinstance(parsed, dict):
        return {
            "parse_status": "ok",
            "json_type": "object",
            "top_level_keys": sorted(str(key) for key in parsed.keys())[:25],
        }
    if isinstance(parsed, list):
        return {"parse_status": "ok", "json_type": "array", "item_count": len(parsed)}
    return {"parse_status": "ok", "json_type": type(parsed).__name__}


def _yaml_metadata(text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for key in ("apiVersion", "kind", "name", "namespace"):
        match = re.search(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", text, flags=re.MULTILINE)
        if match:
            metadata[f"yaml_{key}"] = match.group(1).strip().strip('"\'')
    metadata["document_separator_count"] = len(re.findall(r"^---\s*$", text, flags=re.MULTILINE))
    return metadata


def _terraform_metadata(text: str) -> dict[str, Any]:
    resources = re.findall(r'^\s*resource\s+"([^"]+)"\s+"([^"]+)"', text, flags=re.MULTILINE)
    modules = re.findall(r'^\s*module\s+"([^"]+)"', text, flags=re.MULTILINE)
    providers = re.findall(r'^\s*provider\s+"([^"]+)"', text, flags=re.MULTILINE)
    return {
        "terraform_resource_count": len(resources),
        "terraform_resources": [f"{resource_type}.{name}" for resource_type, name in resources[:25]],
        "terraform_module_count": len(modules),
        "terraform_modules": modules[:25],
        "terraform_providers": sorted(set(providers))[:25],
    }


def _log_metadata(text: str) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for level in ("ERROR", "WARN", "WARNING", "INFO", "DEBUG", "CRITICAL"):
        counts[level.lower()] = len(re.findall(rf"\b{level}\b", text, flags=re.IGNORECASE))
    return {"log_level_counts": {key: value for key, value in counts.items() if value > 0}}


def _structured_metadata(file_path: Path, text: str) -> dict[str, Any]:
    suffix = file_path.suffix.lower()
    if suffix == ".json":
        return _json_metadata(text)
    if suffix in {".yaml", ".yml"}:
        return _yaml_metadata(text)
    if suffix == ".tf":
        return _terraform_metadata(text)
    if suffix == ".log":
        return _log_metadata(text)
    return {}


def parse_text_document(path: str | Path) -> dict[str, Any]:
    """Parse a UTF-8 text-like document and return content plus metadata."""
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    metadata = {
        "filename": file_path.name,
        "suffix": file_path.suffix.lower(),
        "source_type": infer_document_type(file_path),
        "line_count": len(lines),
        "char_count": len(text),
    }
    metadata.update(_structured_metadata(file_path, text))
    return {"text": text, "metadata": metadata}
