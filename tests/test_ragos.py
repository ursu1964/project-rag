from app.ragos.context_manager import assemble_context, summarize_context
from app.ragos.goal_manager import clear_goals, create_goal, get_goal, update_goal_status
from app.ragos.knowledge_router import route_knowledge_request
from app.ragos.model_runtime_manager import select_runtime
from app.ragos.resource_manager import estimate_request_resources, local_capacity
from app.ragos.scheduler import clear_tasks, next_task, schedule_task


def setup_function():
    clear_tasks()
    clear_goals()


def test_scheduler_orders_by_priority():
    schedule_task("slow", priority=50)
    urgent = schedule_task("urgent", priority=1)

    assert next_task() == urgent


def test_resource_manager_local_capacity():
    assert local_capacity()["ram_gb"] == 32
    assert estimate_request_resources("reasoning", 100)["fits_local"] is True


def test_model_runtime_manager_local_first():
    result = select_runtime("routing")

    assert result["runtime"] == "ollama"
    assert result["allocation"]["model_tier"] == "small"


def test_knowledge_router_graph_question():
    result = route_knowledge_request("What depends on VM1?")

    assert result["use_graph"] is True
    assert result["route"] in {"graph", "hybrid"}


def test_context_manager_merges_and_summarizes():
    result = assemble_context({"vector": [1, 2]}, {"vector": [3], "graph": {"a": 1}})

    assert result["context"]["vector"] == [1, 2, 3]
    assert summarize_context(result["context"])["list_counts"]["vector"] == 3


def test_goal_manager_lifecycle():
    goal = create_goal("stabilize system")
    updated = update_goal_status(goal.id, "complete")

    assert get_goal(goal.id) == updated
    assert updated.status == "complete"
