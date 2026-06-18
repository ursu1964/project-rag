from unittest.mock import MagicMock

import app.agents.discovery_agent as discovery_agent
import app.discovery.docker_discovery as docker_discovery


def test_discover_containers_parses_docker_ps(monkeypatch):
    completed = MagicMock(
        returncode=0,
        stdout='{"ID":"abc","Names":"web","Image":"nginx:latest","Ports":"0.0.0.0:80->80/tcp","Networks":"bridge","Status":"Up 1 minute (healthy)"}\n',
        stderr="",
    )
    monkeypatch.setattr(docker_discovery, "_run_docker", lambda args: completed)

    containers = docker_discovery.discover_containers()

    assert containers[0]["name"] == "web"
    assert containers[0]["image"] == "nginx:latest"
    assert containers[0]["health_status"] == "healthy"
    assert containers[0]["networks"] == ["bridge"]


def test_docker_inventory_normalizes_entities(monkeypatch):
    monkeypatch.setattr(docker_discovery.socket, "gethostname", lambda: "host1")
    monkeypatch.setattr(
        docker_discovery,
        "discover_containers",
        lambda: [
            {
                "id": "abc",
                "name": "web",
                "image": "nginx:latest",
                "ports": ["80/tcp"],
                "networks": ["bridge"],
                "status": "Up",
                "health_status": "running",
            }
        ],
    )

    inventory = docker_discovery.docker_inventory()

    assert any(entity["entity_type"] == "DockerContainer" for entity in inventory["entities"])
    assert any(rel["relationship"] == "connectedTo" for rel in inventory["relationships"])
    assert any(rel["relationship"] == "uses" for rel in inventory["relationships"])


def test_discovery_agent_no_persist(monkeypatch):
    monkeypatch.setattr(
        discovery_agent,
        "docker_inventory",
        lambda: {"source": "docker", "entities": [], "relationships": []},
    )

    state = discovery_agent.run({"source": "docker", "persist": False})

    assert state["discovery_context"]["status"] == "completed"
    assert state["discovery_context"]["persisted"] is None


def test_discovery_agent_unsupported_source():
    state = discovery_agent.run({"source": "aws"})

    assert state["discovery_context"]["status"] == "unsupported_source"
