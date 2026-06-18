from app.api.routes_evaluation import _parse_summary, evaluate_quality_gates, read_evaluation_report


def test_parse_evaluation_summary():
    markdown = """# Report

## Summary

- Total questions: 8
- Route accuracy: 0.5
- Safety approval correctness: 1.0

## Dataset: vector
"""

    assert _parse_summary(markdown) == {
        "total_questions": 8,
        "route_accuracy": 0.5,
        "safety_approval_correctness": 1.0,
    }


def test_evaluate_quality_gates_passes_when_thresholds_met():
    result = evaluate_quality_gates(
        {
            "route_accuracy": 1.0,
            "answer_keyword_match": 1.0,
            "graph_evidence_usage": 1.0,
            "vector_evidence_usage": 1.0,
            "validation_confidence": 0.9,
            "safety_approval_correctness": 1.0,
        }
    )

    assert result["status"] == "passed"
    assert all(gate["passed"] for gate in result["gates"])


def test_evaluate_quality_gates_fails_when_thresholds_missing():
    result = evaluate_quality_gates({})

    assert result["status"] == "failed"
    assert not all(gate["passed"] for gate in result["gates"])


def test_read_evaluation_report_missing(tmp_path):
    result = read_evaluation_report(tmp_path / "missing.md")

    assert result["status"] == "missing"
    assert result["summary"] == {}
    assert result["quality_gates"]["status"] == "failed"


def test_read_evaluation_report_ok(tmp_path):
    report = tmp_path / "evaluation_report.md"
    report.write_text("# Report\n\n## Summary\n\n- Total questions: 2\n", encoding="utf-8")

    result = read_evaluation_report(report)

    assert result["status"] == "ok"
    assert result["summary"] == {"total_questions": 2}
    assert result["quality_gates"]["status"] == "failed"
    assert "# Report" in result["markdown"]
