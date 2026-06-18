"""Safety helpers for action and question risk classification."""

from __future__ import annotations

import re

_HIGH_RISK_TERMS = (
    "delete",
    "destroy",
    "terminate",
    "remove",
    "shutdown",
    "reboot",
    "modify firewall",
    "change route",
    "drop database",
    "execute",
    "apply terraform",
)

_MEDIUM_RISK_TERMS = (
    "deploy",
    "update",
    "change",
    "create",
    "restart",
    "ingest",
    "upload",
)

# Prompt injection patterns to detect
_PROMPT_INJECTION_PATTERNS = (
    r"ignore\s+(?:the\s+)?(?:system\s+)?prompt",
    r"forget\s+(?:your\s+)?(?:system\s+)?instructions",
    r"reveal\s+(?:your\s+)?(?:api\s+)?keys?",
    r"disclose\s+(?:your\s+)?secrets?",
    r"bypass",
    r"pretend\s+(?:you\s+)?(?:are|were|will\s+be)",
    r"roleplay\s+as",
    r"you\s+are\s+(?:no\s+longer|not)",
    r"your\s+(?:instructions|guidelines|rules)",
    r"(?:act|behave)\s+as",
    r"(?:now|from\s+now\s+on)\s+you",
    r"(?:test|jailbreak|prompt\s+injection)",
    r"(?:in\s+)?(?:developer|debug)\s+mode",
)

_COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in _PROMPT_INJECTION_PATTERNS]


def block_execution_by_default() -> bool:
    """ProjectRAG does not execute real actions without an approval mode."""
    return True


def classify_question_risk(question: str) -> dict:
    """Classify question/action risk and approval requirements."""
    normalized = question.lower()
    matched_high = next((term for term in _HIGH_RISK_TERMS if term in normalized), None)
    if matched_high:
        return {
            "risk_level": "high",
            "requires_human_approval": True,
            "reason": f"High-risk action term detected: {matched_high}",
        }

    matched_medium = next((term for term in _MEDIUM_RISK_TERMS if term in normalized), None)
    if matched_medium:
        return {
            "risk_level": "medium",
            "requires_human_approval": True,
            "reason": f"Operational change term detected: {matched_medium}",
        }

    return {
        "risk_level": "low",
        "requires_human_approval": False,
        "reason": "No high-risk action terms detected.",
    }


def require_approval_for_action(question: str) -> bool:
    """Return whether a question/action needs human approval."""
    return block_execution_by_default() or bool(classify_question_risk(question)["requires_human_approval"])


def detect_prompt_injection(text: str) -> dict:
    """Detect common prompt injection patterns in text.
    
    Returns a dict with:
    - detected: bool indicating if injection was found
    - pattern: the regex pattern that matched (if detected)
    - text_snippet: the matching text from the input
    - risk_level: "high" if injection detected
    """
    if not text:
        return {
            "detected": False,
            "pattern": None,
            "text_snippet": None,
            "risk_level": "low",
        }
    
    normalized_text = str(text).lower()
    for i, pattern in enumerate(_COMPILED_PATTERNS):
        match = pattern.search(normalized_text)
        if match:
            return {
                "detected": True,
                "pattern": _PROMPT_INJECTION_PATTERNS[i],
                "text_snippet": match.group(0),
                "risk_level": "high",
            }
    
    return {
        "detected": False,
        "pattern": None,
        "text_snippet": None,
        "risk_level": "low",
    }

