from app.api.routes_cognitive import CognitiveQueryRequest, cognitive_query


def test_cognitive_query_formats_workflow_state(monkeypatch):
    class Workflow:
        def invoke(self, state):
            return {
                **state,
                "chief_summary": {"tasks": ["Assess VM1"]},
                "plan": [{"step": 1, "action": "Assess VM1"}],
                "security": {"blocked": True},
                "cost": {"estimate": "placeholder"},
                "validation": {"grounded": False},
                "lessons_learned": ["Require approval."],
            }

    monkeypatch.setattr("app.api.routes_cognitive.build_workflow", lambda: Workflow())

    result = cognitive_query(CognitiveQueryRequest(objective="Assess VM1"))

    assert result["objective"] == "Assess VM1"
    assert result["analysis"] == {"tasks": ["Assess VM1"]}
    assert result["plan"]["steps"][0]["action"] == "Assess VM1"
    assert result["security"]["blocked"] is True
    assert result["cost"]["estimate"] == "placeholder"
    assert result["validation"]["grounded"] is False
    assert "blocked" in result["recommendation"].lower()
    assert result["learning"]["lessons_learned"] == ["Require approval."]
