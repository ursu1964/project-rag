"""Evaluation dataset helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl_dataset(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def sample_dataset() -> list[dict[str, str]]:
    return [
        {
            "question": "What does VM1 depend on?",
            "expected_answer": "VM1 depends on Database01.",
        }
    ]
