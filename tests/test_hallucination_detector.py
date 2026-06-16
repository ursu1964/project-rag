from app.validation.hallucination_detector import detect_hallucinations


def test_detect_hallucinations_finds_unsupported_entities_and_relationships():
    result = detect_hallucinations(
        "VM1 dependsOn Database01. ServiceX calls API99.",
        retrieved_evidence=[{"content": "VM1 dependsOn Database01"}],
        graph_evidence=[{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}],
        memory_evidence=[],
    )

    assert "ServiceX" in result["unsupported_entities"]
    assert "API99" in result["unsupported_entities"]
    assert "calls" in result["unsupported_relationships"]
    assert result["confidence"] < 1.0


def test_detect_hallucinations_high_confidence_when_supported():
    result = detect_hallucinations(
        "VM1 dependsOn Database01.",
        retrieved_evidence=[{"content": "VM1 dependsOn Database01"}],
        graph_evidence=[{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}],
        memory_evidence=[],
    )

    assert result["unsupported_entities"] == []
    assert result["unsupported_relationships"] == []
    assert result["confidence"] == 1.0
