import app.graph.impact_analysis as impact_analysis


def test_calculate_direct_impact(monkeypatch):
    monkeypatch.setattr(
        impact_analysis,
        "get_reverse_dependencies",
        lambda entity: {"reverse_dependencies": [{"source": "API01"}]},
    )

    assert impact_analysis.calculate_direct_impact("Database01") == [{"source": "API01"}]


def test_calculate_indirect_impact(monkeypatch):
    monkeypatch.setattr(
        impact_analysis,
        "get_impact_path",
        lambda entity: {"paths": [{"impacted": "ServiceA"}]},
    )

    assert impact_analysis.calculate_indirect_impact("Database01") == [{"impacted": "ServiceA"}]


def test_build_impact_report(monkeypatch):
    monkeypatch.setattr(impact_analysis, "calculate_direct_impact", lambda entity: [{"source": "API01"}])
    monkeypatch.setattr(
        impact_analysis,
        "calculate_indirect_impact",
        lambda entity: [{"impacted": "ServiceA"}, {"impacted": "ApplicationA"}],
    )

    report = impact_analysis.build_impact_report("Database01")

    assert report["direct_dependencies"] == [{"source": "API01"}]
    assert len(report["indirect_dependencies"]) == 2
    assert report["risk_score"] == 0.45
    assert "Database01" in report["explanation"]
