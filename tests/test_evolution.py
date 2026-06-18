from app.evolution.evolution_sandbox import create_patch_proposal, validate_proposal_patch
from app.evolution.fitness_engine import calculate_fitness_score, rank_proposals


def test_patch_proposal_is_reviewable_and_non_executing():
    result = create_patch_proposal("Improve docs", "clarity", "diff --git a/README.md b/README.md")

    assert result["proposal"].status == "review_required"
    assert result["production_modified"] is False
    assert result["automatic_deployment"] is False
    assert result["direct_code_overwrite"] is False


def test_patch_validation_blocks_execution_instructions():
    result = validate_proposal_patch("run sudo rm -rf /")

    assert result["valid"] is False
    assert result["execution"] == "disabled"


def test_fitness_score_requires_safety():
    result = calculate_fitness_score({"test_score": 1.0, "safety_score": 0.7, "maintainability_score": 1.0})

    assert result["fitness_score"] > 0
    assert result["passed"] is False
    assert result["requires_human_review"] is True


def test_rank_proposals():
    ranked = rank_proposals([{"id": "low", "fitness_score": 0.1}, {"id": "high", "fitness_score": 0.9}])

    assert ranked[0]["id"] == "high"
