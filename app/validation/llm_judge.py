"""Optional local LLM judge for answer validation."""

from __future__ import annotations

import json
from typing import Any

from app.tools.ollama_client import generate

_DEFAULT_RESULT = {
    "correctness": 0.0,
    "completeness": 0.0,
    "groundedness": 0.0,
    "reason": "LLM judge unavailable or returned invalid JSON.",
}


def judge_answer(question: str, answer: str, evidence: dict[str, Any] | list[Any]) -> dict[str, Any]:
    """Judge correctness, completeness, and groundedness using the local Ollama model."""
    prompt = (
        "You are a strict local evaluator for ProjectRAG. Return JSON only.\n"
        "Evaluate the answer against the question and evidence.\n"
        "Schema:\n"
        '{"correctness":0.0,"completeness":0.0,"groundedness":0.0,"reason":"..."}\n\n'
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        f"Evidence: {json.dumps(evidence, default=str)}\n"
    )
    try:
        parsed = json.loads(generate(prompt))
        return {
            "correctness": float(parsed.get("correctness", 0.0)),
            "completeness": float(parsed.get("completeness", 0.0)),
            "groundedness": float(parsed.get("groundedness", 0.0)),
            "reason": str(parsed.get("reason", "")),
        }
    except Exception:
        return dict(_DEFAULT_RESULT)
