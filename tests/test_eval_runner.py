
from app.evaluation.eval_runner import evaluate_response, run_all_evaluations, summarize_results


def test_evaluate_response_metrics():
    item = {
        "question": "What does VM1 depend on?",
        "expected_route": "graph",
        "expected_keywords": ["VM1", "Database01"],
        "should_require_approval": False,
    }
    response = {
        "route": "graph",
        "answer": "VM1 depends on Database01.",
        "evidence": {"graph": [{"object": "Database01"}], "vector": []},
        "validation": {"confidence": 0.8, "requires_human_approval": False},
    }

    result = evaluate_response(item, response)

    assert result["route_correct"] is True
    assert result["keyword_match"] == 1.0
    assert result["graph_evidence_used"] is True
    assert result["safety_approval_correct"] is True


def test_summarize_results():
    summary = summarize_results(
        {
            "graph": [
                {
                    "route_correct": True,
                    "keyword_match": 1.0,
                    "graph_evidence_used": True,
                    "vector_evidence_used": False,
                    "validation_confidence": 0.7,
                    "safety_approval_correct": True,
                }
            ]
        }
    )

    assert summary["total_questions"] == 1
    assert summary["route_accuracy"] == 1.0


def test_run_all_evaluations_writes_report(tmp_path, monkeypatch):
    def fake_answer(question: str):
        route = "action" if "Delete" in question or "terraform" in question else "graph"
        return {
            "route": route,
            "answer": f"Answer for {question} Database01 VM1 topology document",
            "evidence": {"graph": [{"fact": "x"}], "vector": [{"chunk": "y"}]},
            "validation": {"confidence": 0.9, "requires_human_approval": route == "action"},
        }

    report_path = tmp_path / "evaluation_report.md"
    result = run_all_evaluations(answer_fn=fake_answer, output_path=report_path)

    # Total questions grows as datasets expand — assert it is a reasonable non-zero integer
    assert isinstance(result["summary"]["total_questions"], int)
    assert result["summary"]["total_questions"] > 0
    assert report_path.exists()
    assert "ProjectRAG Evaluation Report" in report_path.read_text(encoding="utf-8")
