"""Safe GraphDB read-only SELECT tool."""

from __future__ import annotations

import re
from typing import Any

from app.graph.graphdb_client import sparql_query

_BLOCKED_SPARQL = re.compile(r"\b(insert|delete|drop|clear|create|load|move|copy|add)\b", re.I)


def _is_select(query: str) -> bool:
    stripped = query.strip()
    return "select" in stripped.lower() and not _BLOCKED_SPARQL.search(stripped)


def graphdb_select(query: str) -> dict[str, Any]:
    """Execute only read-only GraphDB SPARQL SELECT queries."""
    if not _is_select(query):
        return {"status": "blocked", "result": {}, "error": "Only read-only SPARQL SELECT queries are allowed"}
    return {"status": "ok", "result": sparql_query(query)}
