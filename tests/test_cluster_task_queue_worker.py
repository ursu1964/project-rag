import app.cluster.scheduler as scheduler
import app.cluster.task_queue as task_queue
import app.cluster.worker as worker


def setup_function():
    worker.clear_safe_agents()


def test_schedule_agent_task(monkeypatch):
    monkeypatch.setattr(scheduler, "enqueue_task", lambda **kwargs: "task-1")

    result = scheduler.schedule_agent_task("router", "route", {"question": "x"})

    assert result["task_id"] == "task-1"
    assert result["status"] == "pending"


def test_list_tasks_uses_fetch_all(monkeypatch):
    monkeypatch.setattr(task_queue, "fetch_all", lambda query, params=(): [{"id": "task-1"}])

    assert task_queue.list_tasks()[0]["id"] == "task-1"


def test_worker_executes_registered_safe_agent(monkeypatch):
    worker.register_safe_agent("echo", lambda state: {"echo": state})
    monkeypatch.setattr(worker, "complete_task", lambda task, output=None, latency_ms=0: "result-1")

    result = worker.execute_task({"id": "task-1", "agent_name": "echo", "input": {"x": 1}})

    assert result["executed"] is True
    assert result["status"] == "completed"
    assert result["output"] == {"echo": {"x": 1}}


def test_worker_blocks_unregistered_agent(monkeypatch):
    monkeypatch.setattr(worker, "fail_task", lambda task, error, latency_ms=0: "result-1")

    result = worker.execute_task({"id": "task-1", "agent_name": "unsafe", "input": {}})

    assert result["executed"] is False
    assert result["status"] == "failed"
    assert "unsafe" in result["error"]


def test_run_once_idle(monkeypatch):
    monkeypatch.setattr(worker, "claim_next_task", lambda agent_name=None: None)

    assert worker.run_once()["status"] == "idle"
