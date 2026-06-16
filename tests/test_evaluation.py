import json
from unittest.mock import MagicMock

from app.evaluation.datasets import load_jsonl_dataset, sample_dataset
from app.evaluation.evaluation_runner import run_evaluation, store_evaluation_result
from app.evaluation.metrics import evaluate_answer
import app.evaluation.evaluation_runner as evaluation_runner


def test_evaluate_answer_metrics():
    metrics = evaluate_answer(
        "Direct Answer:\nVM1 depends on Database01.\nEvidence Used:\n- Graph evidence: yes\n- Vector evidence: yes\n- Memory evidence: none",
        {"graph": [{"object": "Database01"}], "vector": [{"content": "VM1 depends on Database01"}]},
        "VM1 depends on Database01",
    )
    assert metrics["groundedness"] > 0
    assert metrics["answer_completeness"] == 1.0
    assert metrics["graph_usage"] == 1.0
    assert metrics["citation_coverage"] > 0


def test_load_jsonl_dataset(tmp_path):
    path = tmp_path / "eval.jsonl"
    path.write_text(json.dumps({"question": "q"}) + "\n", encoding="utf-8")
    assert load_jsonl_dataset(path) == [{"question": "q"}]


def test_sample_dataset():
    assert sample_dataset()[0]["question"]


def test_store_evaluation_result(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(evaluation_runner, "execute", execute)
    store_evaluation_result("smoke", "q", "a", {"groundedness": 1.0})
    assert execute.call_args.args[1][0:3] == ("smoke", "q", "a")


def test_run_evaluation(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr(evaluation_runner, "store_evaluation_result", store)
    results = run_evaluation(
        "smoke",
        [{"question": "q", "expected_answer": "answer"}],
        lambda question: {"answer": "answer", "evidence": {"graph": []}},
    )
    assert results[0]["metrics"]["answer_completeness"] == 1.0
    store.assert_called_once()
