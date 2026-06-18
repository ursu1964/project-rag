import app.cluster.heartbeat as heartbeat
import app.cluster.node_health as node_health
import app.cluster.node_registry as node_registry


def test_register_node(monkeypatch):
    class Cursor:
        def __init__(self):
            self.row = {"id": "node-1"}
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def execute(self, *args):
            pass
        def fetchone(self):
            return self.row
    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def cursor(self):
            return Cursor()
        def commit(self):
            pass
    monkeypatch.setattr(node_registry, "get_connection", lambda: Connection())

    assert node_registry.register_node("local") == "node-1"


def test_list_nodes(monkeypatch):
    monkeypatch.setattr(node_registry, "fetch_all", lambda query, params=(): [{"node_name": "local"}])

    assert node_registry.list_nodes()[0]["node_name"] == "local"


def test_update_heartbeat(monkeypatch):
    monkeypatch.setattr(heartbeat, "register_node", lambda node_name, status="active": "node-1")
    monkeypatch.setattr(heartbeat, "execute", lambda query, params=(): None)

    result = heartbeat.update_heartbeat("local")

    assert result["heartbeat"] == "updated"
    assert result["node_name"] == "local"


def test_get_local_node_health(monkeypatch):
    monkeypatch.setattr(node_health, "update_heartbeat", lambda node_name: {"heartbeat": "updated"})

    result = node_health.get_local_node_health(update=True)

    assert result["status"] == "ok"
    assert result["mode"] == "single-node"
    assert result["redis"] == "not_configured"
