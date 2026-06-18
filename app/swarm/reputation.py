"""Agent reputation scoring helpers."""

from __future__ import annotations

from app.swarm.agent_registry import AgentRecord


def calculate_reputation(record: AgentRecord) -> float:
    """Calculate deterministic reputation from reliability, success, and latency."""
    latency_penalty = min(0.3, record.average_latency / 10000.0)
    score = (record.reliability_score * 0.5) + (record.success_rate * 0.4) - latency_penalty
    return round(max(0.0, min(1.0, score)), 6)


def update_reputation(
    record: AgentRecord,
    *,
    success: bool,
    latency_ms: float,
) -> AgentRecord:
    """Return an updated immutable agent record after one observation."""
    observed_success = 1.0 if success else 0.0
    success_rate = (record.success_rate * 0.8) + (observed_success * 0.2)
    reliability = (record.reliability_score * 0.8) + (observed_success * 0.2)
    latency = (record.average_latency * 0.8) + (max(0.0, float(latency_ms)) * 0.2)
    return AgentRecord(
        agent_name=record.agent_name,
        capability=record.capability,
        reliability_score=round(max(0.0, min(1.0, reliability)), 6),
        average_latency=round(latency, 6),
        success_rate=round(max(0.0, min(1.0, success_rate)), 6),
        risk_class=record.risk_class,
    )
