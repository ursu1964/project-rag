"""ProjectRAG security mode helpers."""

from __future__ import annotations

import os

READ_ONLY = "READ_ONLY"
RECOMMENDATION = "RECOMMENDATION"
APPROVAL = "APPROVAL"
EXECUTION_DISABLED = "EXECUTION_DISABLED"

_MODES = {READ_ONLY, RECOMMENDATION, APPROVAL, EXECUTION_DISABLED}
_DEFAULT_MODE = READ_ONLY


def get_current_mode() -> str:
    """Return current ProjectRAG security mode from PROJECTRAG_MODE."""
    mode = os.getenv("PROJECTRAG_MODE", _DEFAULT_MODE).upper()
    return mode if mode in _MODES else _DEFAULT_MODE


def can_execute_actions() -> bool:
    """Return whether direct execution is currently allowed."""
    return False


def require_approval() -> bool:
    """Return whether action-like operations require approval."""
    return get_current_mode() in {READ_ONLY, RECOMMENDATION, APPROVAL, EXECUTION_DISABLED}
