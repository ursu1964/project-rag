"""Deterministic prompt security policy checks."""

from __future__ import annotations

import re
from typing import Any

_BLOCK_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_instructions", re.compile(r"\b(ignore|forget|bypass|override)\b.{0,40}\b(instructions?|policy|safety|system prompt)\b", re.I)),
    ("secret_exfiltration", re.compile(r"\b(show|reveal|print|dump|exfiltrate)\b.{0,40}\b(secret|password|token|api[_ -]?keys?|private keys?|credentials?)\b", re.I)),
    ("system_prompt_exfiltration", re.compile(r"\b(system prompt|developer message|hidden instruction|internal policy)\b", re.I)),
    ("destructive_execution", re.compile(r"\b(rm\s+-rf|drop\s+database|delete\s+all|wipe\s+disk|shutdown\s+production)\b", re.I)),
)

_PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("possible_ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("possible_credit_card", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("possible_private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)


def evaluate_prompt_policy(question: str) -> dict[str, Any]:
    """Return a prompt security policy decision for a user question."""
    text = str(question or "")
    violations: list[str] = []
    warnings: list[str] = []

    for name, pattern in _BLOCK_PATTERNS:
        if pattern.search(text):
            violations.append(name)

    for name, pattern in _PII_PATTERNS:
        if pattern.search(text):
            warnings.append(name)

    blocked = bool(violations)
    requires_human_approval = blocked or bool(warnings)
    return {
        "allowed": not blocked,
        "blocked": blocked,
        "requires_human_approval": requires_human_approval,
        "risk_level": "high" if blocked else "medium" if warnings else "low",
        "violations": violations,
        "warnings": warnings,
        "reason": "Prompt policy blocked unsafe request." if blocked else "Prompt policy passed.",
    }
