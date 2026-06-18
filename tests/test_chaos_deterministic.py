from app.chaos.chaos_score import calculate_chaos_score
from app.chaos.entropy import calculate_entropy
from app.chaos.volatility import calculate_volatility


def test_calculate_entropy_for_repeated_values():
    assert calculate_entropy(["a", "a", "a"]) == 0.0
    assert calculate_entropy(["a", "b", "a", "b"]) == 1.0


def test_calculate_volatility_normalized():
    assert calculate_volatility([1, 1, 1]) == 0.0
    assert calculate_volatility([0, 10]) == 1.0


def test_calculate_chaos_score_is_bounded():
    score = calculate_chaos_score(
        {"entropy": 2.0, "volatility": 0.5, "instability": 0.5, "complexity_score": 0.5}
    )

    assert 0.0 < score <= 1.0
