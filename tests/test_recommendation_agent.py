from app.agents.recommendation_agent import run


def test_recommendation_agent_ranks_recommendations():
    state = run(
        {
            "evidence": [
                {"evidence_type": "vector", "evidence_score": 0.2},
                {"evidence_type": "graph", "evidence_score": 0.9},
            ]
        }
    )

    recommendations = state["recommendations"]
    assert recommendations[0]["evidence"]["evidence_type"] == "graph"
    assert recommendations[0]["rank"] == 1
    assert recommendations[0]["execution_allowed"] is False
    assert recommendations[0]["mode"] == "recommendation_only"


def test_recommendation_agent_fallback_when_no_evidence():
    state = run({})
    assert state["recommendations"][0]["title"] == "Gather more evidence"
    assert state["recommendations"][0]["execution_allowed"] is False
