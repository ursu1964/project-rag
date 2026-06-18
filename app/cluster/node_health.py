"""Local node health checks for single-node ProjectRAG deployments."""

from __future__ import annotations

import os
import socket
from typing import Any

from app.cluster.heartbeat import update_heartbeat
from app.cluster.node_registry import _default_node_name


def get_local_node_health(update: bool = False) -> dict[str, Any]:
    """Return local node health without distributed coordination."""
    node_name = _default_node_name()
    if update:
        update_heartbeat(node_name)
    return {
        "node_name": node_name,
        "status": "ok",
        "mode": "single-node",
        "redis": "not_configured",
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
    }
