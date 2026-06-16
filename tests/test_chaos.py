from app.chaos.analysis import analyze_topology
from app.chaos.metrics import calculate_complexity_score, calculate_entropy, calculate_instability


def test_calculate_entropy_empty_graph():
    assert calculate_entropy([]) == 0.0


def test_calculate_instability_detects_cycle():
    assert calculate_instability([("A", "B"), ("B", "A")]) > 0


def test_calculate_complexity_score_is_normalized():
    score = calculate_complexity_score([("VM1", "DB1"), ("API1", "DB1")])
    assert 0.0 <= score <= 1.0


def test_analyze_topology_returns_all_metrics():
    result = analyze_topology([("VM1", "DB1"), ("API1", "DB1")])
    assert {"entropy", "instability", "complexity_score"}.issubset(result)
