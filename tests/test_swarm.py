from app.swarm.agent_registry import clear_registry, list_agents, register_agent
from app.swarm.consensus import majority_vote
from app.swarm.reputation import calculate_reputation, update_reputation


def setup_function():
    clear_registry()


def test_register_agent_stores_required_fields():
    record = register_agent("router", "routing", 0.9, 20, 0.8, "low")

    assert record.agent_name == "router"
    assert record.capability == "routing"
    assert list_agents("routing") == [record]


def test_reputation_penalizes_latency():
    fast = register_agent("fast", "reasoning", 0.9, 10, 0.9)
    slow = register_agent("slow", "reasoning", 0.9, 5000, 0.9)

    assert calculate_reputation(fast) > calculate_reputation(slow)


def test_update_reputation_changes_scores():
    record = register_agent("validator", "validation", 0.5, 100, 0.5)
    updated = update_reputation(record, success=True, latency_ms=50)

    assert updated.reliability_score > record.reliability_score
    assert updated.average_latency < record.average_latency


def test_majority_vote_weighted():
    result = majority_vote(
        [
            {"agent_name": "a", "answer": "yes", "confidence": 0.9},
            {"agent_name": "b", "answer": "yes", "confidence": 0.8},
            {"agent_name": "c", "answer": "no", "confidence": 0.7},
        ]
    )

    assert result["answer"] == "yes"
    assert result["support"] == 2
