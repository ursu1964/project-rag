from unittest.mock import MagicMock

import app.tools.docker_tool as docker_tool
import app.tools.github_tool as github_tool
import app.tools.graphdb_tool as graphdb_tool
import app.tools.postgres_tool as postgres_tool


def test_postgres_select_allows_select(monkeypatch):
    monkeypatch.setattr(postgres_tool, "fetch_all", lambda query, params=(): [{"ok": 1}])

    result = postgres_tool.postgres_select("SELECT 1 AS ok")

    assert result["status"] == "ok"
    assert result["count"] == 1


def test_postgres_select_blocks_drop():
    result = postgres_tool.postgres_select("DROP TABLE documents")

    assert result["status"] == "blocked"


def test_graphdb_select_allows_select(monkeypatch):
    monkeypatch.setattr(graphdb_tool, "sparql_query", lambda query: {"results": {"bindings": []}})

    result = graphdb_tool.graphdb_select("SELECT * WHERE { ?s ?p ?o }")

    assert result["status"] == "ok"


def test_graphdb_select_blocks_delete():
    result = graphdb_tool.graphdb_select("DELETE WHERE { ?s ?p ?o }")

    assert result["status"] == "blocked"


def test_docker_ps_uses_allowed_command(monkeypatch):
    completed = MagicMock(returncode=0, stdout="containers", stderr="")
    run = MagicMock(return_value=completed)
    monkeypatch.setattr(docker_tool.subprocess, "run", run)

    result = docker_tool.docker_ps()

    assert result["status"] == "ok"
    assert run.call_args.args[0] == ["docker", "ps"]


def test_docker_logs_blocks_unsafe_container():
    result = docker_tool.docker_logs("docker rm projectrag-postgres")

    assert result["status"] == "blocked"


def test_git_status_uses_allowed_command(monkeypatch):
    completed = MagicMock(returncode=0, stdout="", stderr="")
    run = MagicMock(return_value=completed)
    monkeypatch.setattr(github_tool.subprocess, "run", run)

    result = github_tool.git_status()

    assert result["status"] == "ok"
    assert run.call_args.args[0] == ["git", "status", "--short"]


def test_git_blocks_unallowed_command():
    result = github_tool._run_git(["reset", "--hard"])

    assert result["status"] == "blocked"
