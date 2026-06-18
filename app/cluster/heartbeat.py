"""Single-node heartbeat updates."""

from __future__ import annotations

from app.cluster.node_registry import _default_node_name, register_node
from app.memory.postgres import execute


def update_heartbeat(node_name: str | None = None, status: str = "active") -> dict[str, str]:
    """Update local node heartbeat timestamp."""
    name = node_name or _default_node_name()
    register_node(name, status=status)
    execute(
        """
        UPDATE cluster_nodes
        SET status = %s, last_seen_at = now(), updated_at = now()
        WHERE node_name = %s
        """,
        (status, name),
    )
    return {"node_name": name, "status": status, "heartbeat": "updated"}
