from app.enterprise.artificial_architect import recommend_architecture
from app.enterprise.artificial_ceo import recommend_strategy
from app.enterprise.artificial_coo import recommend_operations
from app.enterprise.artificial_cto import recommend_technology_strategy


def test_enterprise_layers_are_recommendation_only():
    functions = [
        recommend_technology_strategy,
        recommend_architecture,
        recommend_operations,
        recommend_strategy,
    ]

    for func in functions:
        result = func({"risk": "low"})
        assert result["mode"] == "recommendation_only"
        assert result["execution"] == "disabled"
        assert result["context_keys"] == ["risk"]
