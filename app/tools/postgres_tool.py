"""Safe PostgreSQL read-only query tool."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any

from app.memory.postgres import fetch_all

_BLOCKED_SQL = re.compile(r"\b(delete|drop|truncate|insert|update|alter|create|grant|revoke|copy|vacuum)\b", re.I)


def _is_select(query: str) -> bool:
    stripped = query.strip().rstrip(";")
    return bool(re.match(r"^(select|with)\b", stripped, flags=re.I)) and not _BLOCKED_SQL.search(stripped)


def postgres_select(query: str, params: Sequence[Any] = ()) -> dict[str, Any]:
    """Execute only PostgreSQL SELECT/CTE read queries."""
    if not _is_select(query):
        return {"status": "blocked", "rows": [], "error": "Only read-only SELECT queries are allowed"}
    rows = fetch_all(query, params)
    return {"status": "ok", "rows": rows, "count": len(rows)}
