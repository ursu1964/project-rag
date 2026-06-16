from app.agents.validator import run as validate
from app.tools.safety import block_execution_by_default, classify_question_risk, require_approval_for_action


def test_classify_question_risk_high():
    result = classify_question_risk("Please drop database projectrag")
    assert result["risk_level"] == "high"
    assert result["requires_human_approval"] is True


def test_classify_question_risk_medium():
    result = classify_question_risk("Update the service plan")
    assert result["risk_level"] == "medium"
    assert result["requires_human_approval"] is True


def test_classify_question_risk_low():
    result = classify_question_risk("What does VM1 depend on?")
    assert result["risk_level"] == "low"
    assert result["requires_human_approval"] is False


def test_execution_is_blocked_by_default():
    assert block_execution_by_default() is True
    assert require_approval_for_action("What is the topology?") is True


def test_validator_includes_safety_and_requires_approval_for_high_risk_question():
    result = validate({"question": "execute reboot", "answer": "ok", "evidence": [{"x": 1}]})["validation"]
    assert result["grounded"] is True
    assert result["safety"]["risk_level"] == "high"
    assert result["requires_human_approval"] is True
