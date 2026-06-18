from app.devops.action_planner import create_action_plan
from app.devops.risk_classifier import classify_action_risk
from app.devops.verifier import verify_plan


def test_destructive_action_is_blocked():
    risk = classify_action_risk("delete VM1")

    assert risk["risk_level"] == "high"
    assert risk["blocked"] is True


def test_action_plan_includes_risk_and_rollback():
    plan = create_action_plan("restart service", ["restart ServiceA", "delete VM1"])

    assert plan["execution_allowed"] is False
    assert all("risk_level" in action for action in plan["actions"])
    assert all("rollback_plan" in action for action in plan["actions"])
    assert plan["actions"][1]["blocked"] is True
    assert plan["verification"]["passed"] is True


def test_verifier_detects_missing_rollback():
    result = verify_plan({"actions": [{"risk_level": "low"}]})

    assert result["passed"] is False
    assert "missing rollback_plan" in result["warnings"][0]
