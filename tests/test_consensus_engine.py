from app.swarm.consensus_engine import build_consensus, run


def test_build_consensus_selects_majority():
    result = build_consensus(
        [
            {"agent_name": "a", "recommendation": "scale", "confidence": 0.8},
            {"agent_name": "b", "recommendation": "scale", "confidence": 0.6},
            {"agent_name": "c", "recommendation": "restart", "confidence": 0.9},
        ]
    )

    assert result["final_recommendation"] == "scale"
    assert result["support"] == 2
    assert len(result["dissenting_opinions"]) == 1
    assert result["execution"] == "disabled"


def test_build_consensus_tie_breaks_by_confidence():
    result = build_consensus(
        [
            {"recommendation": "a", "confidence": 0.4},
            {"recommendation": "b", "confidence": 0.9},
        ]
    )

    assert result["final_recommendation"] == "b"


def test_run_adds_consensus_to_state():
    state = run({"candidate_answers": [{"answer": "ok", "confidence": 1.0}]})

    assert state["consensus"]["final_recommendation"] == "ok"
