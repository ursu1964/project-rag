from app.research.evidence_agent import run as evidence_run
from app.research.experiment_agent import run as experiment_run
from app.research.hypothesis_agent import run as hypothesis_run
from app.research.theory_agent import run as theory_run


def test_hypothesis_agent_recommendation_only():
    state = hypothesis_run({"objective": "reduce incidents"})

    assert state["hypothesis"]["mode"] == "recommendation_only"
    assert state["hypothesis"]["execution"] == "disabled"


def test_experiment_agent_does_not_execute():
    state = experiment_run({"hypothesis": {"statement": "x causes y"}})

    assert state["experiment_plan"]["status"] == "planned"
    assert state["experiment_plan"]["execution"] == "disabled"


def test_evidence_agent_collects_existing_context():
    state = evidence_run({"graph_context": {"entity": "VM1"}, "memory_context": []})

    assert state["evidence_summary"]["count"] == 1
    assert state["evidence_summary"]["execution"] == "disabled"


def test_theory_agent_draft_only():
    state = theory_run({"hypothesis": {"statement": "x"}, "evidence_summary": {"count": 2}})

    assert state["theory"]["status"] == "draft"
    assert state["theory"]["evidence_count"] == 2
    assert state["theory"]["execution"] == "disabled"
