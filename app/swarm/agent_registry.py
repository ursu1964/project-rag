"""In-memory agent registry for swarm coordination."""

from __future__ import annotations

from dataclasses import dataclass

_RISK_CLASSES = {"low", "medium", "high", "critical"}


@dataclass(frozen=True)
class AgentRecord:
    agent_name: str
    capability: str
    reliability_score: float = 0.5
    average_latency: float = 0.0
    success_rate: float = 0.0
    risk_class: str = "low"


_REGISTRY: dict[str, AgentRecord] = {}


def _bounded_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 6)


def register_agent(
    agent_name: str,
    capability: str,
    reliability_score: float = 0.5,
    average_latency: float = 0.0,
    success_rate: float = 0.0,
    risk_class: str = "low",
) -> AgentRecord:
    """Register or replace an agent record."""
    normalized_risk = str(risk_class).lower()
    if normalized_risk not in _RISK_CLASSES:
        raise ValueError(f"Unsupported risk class: {risk_class}")
    if not agent_name.strip():
        raise ValueError("agent_name is required")
    if not capability.strip():
        raise ValueError("capability is required")

    record = AgentRecord(
        agent_name=agent_name,
        capability=capability,
        reliability_score=_bounded_score(reliability_score),
        average_latency=max(0.0, float(average_latency)),
        success_rate=_bounded_score(success_rate),
        risk_class=normalized_risk,
    )
    _REGISTRY[agent_name] = record
    return record


def get_agent(agent_name: str) -> AgentRecord | None:
    """Return an agent record by name."""
    return _REGISTRY.get(agent_name)


def list_agents(capability: str | None = None) -> list[AgentRecord]:
    """List registered agents, optionally filtered by capability."""
    records = list(_REGISTRY.values())
    if capability is None:
        return records
    return [record for record in records if record.capability == capability]


def clear_registry() -> None:
    """Clear registry. Intended for tests and controlled bootstrapping."""
    _REGISTRY.clear()
