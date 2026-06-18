"""Security audit API routes."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.security.audit import list_security_events

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events")
def audit_events(limit: int = Query(default=100, ge=1, le=500)) -> dict:
    return {"events": list_security_events(limit=limit)}
