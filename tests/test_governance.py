from app.governance.constitutional_engine import evaluate_constitution, list_constitution_rules
from app.governance.governance_agent import run as governance_run
from app.governance.trust_agent import calculate_trust_score
from app.governance.trust_agent import run as trust_run


def test_default_constitution_contains_required_rules():
    rules = list_constitution_rules()

    assert "protect availability" in rules
    assert "protect human authority" in rules
    assert len(rules) == 6


def test_constitution_detects_violation():
    result = evaluate_constitution("shutdown database without approval")

    assert result["allowed"] is False
    assert result["requires_human_review"] is True
    assert result["execution"] == "disabled"


def test_trust_agent_scores_grounded_evidence():
    result = calculate_trust_score({"validation": {"grounded": True, "confidence": 0.9}, "evidence": [1]})

    assert result["trust_score"] > 0.5
    assert result["mode"] == "recommendation_only"


def test_trust_run_adds_state_key():
    state = trust_run({"validation": {"grounded": False}})

    assert "trust" in state


def test_governance_agent_requires_review_for_bad_decision():
    state = governance_run({"decision": "autonomous execute change without approval"})

    assert state["governance"]["requires_human_review"] is True
    assert state["governance"]["execution"] == "disabled"
