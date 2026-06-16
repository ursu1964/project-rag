import app.validation.llm_judge as llm_judge
from app.agents import validator


class JudgeSettings:
    use_llm_judge = True


class NoJudgeSettings:
    use_llm_judge = False


def test_judge_answer_returns_json_scores(monkeypatch):
    monkeypatch.setattr(
        llm_judge,
        "generate",
        lambda prompt: '{"correctness":0.9,"completeness":0.8,"groundedness":0.7,"reason":"ok"}',
    )

    result = llm_judge.judge_answer("q", "a", {"e": []})

    assert result["correctness"] == 0.9
    assert result["completeness"] == 0.8
    assert result["groundedness"] == 0.7


def test_judge_answer_falls_back_on_bad_json(monkeypatch):
    monkeypatch.setattr(llm_judge, "generate", lambda prompt: "bad")
    assert llm_judge.judge_answer("q", "a", {})["groundedness"] == 0.0


def test_validator_optionally_uses_llm_judge(monkeypatch):
    monkeypatch.setattr(validator, "settings", JudgeSettings())
    monkeypatch.setattr(validator, "judge_answer", lambda question, answer, evidence: {"groundedness": 0.4})

    result = validator.run({"question": "q", "answer": "a", "evidence": [{"a": 1}]})["validation"]

    assert result["llm_judge"] == {"groundedness": 0.4}
    assert result["requires_human_approval"] is True
