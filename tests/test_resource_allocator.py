from app.agents.resource_allocator import run


def test_allocator_uses_small_for_routing():
    state = run({"task_type": "routing"})
    assert state["resource_allocation"]["model_tier"] == "small"


def test_allocator_uses_medium_for_validation():
    state = run({"task_type": "validation"})
    assert state["resource_allocation"]["model_tier"] == "medium"


def test_allocator_uses_large_for_reasoning():
    state = run({"task_type": "reasoning"})
    assert state["resource_allocation"]["model_tier"] == "large"


def test_allocator_defaults_to_summarization_small():
    state = run({})
    assert state["resource_allocation"]["task_type"] == "summarization"
    assert state["resource_allocation"]["model_tier"] == "small"
