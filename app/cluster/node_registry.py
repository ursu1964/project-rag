"""Single-node cluster node registry backed by PostgreSQL."""

from __future__ import annotations

import json
import socket
from typing import Any

from app.memory.postgres import fetch_all, get_connection

LOCAL_NODE_TYPE = "local"


def _default_node_name() -> str:
    return socket.gethostname() or "projectrag-local"


def register_node(
    node_name: str | None = None,
    capabilities: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    status: str = "active",
) -> str:
    """Register or refresh the local node. Single-node only; no Redis/queue state."""
    name = node_name or _default_node_name()
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cluster_nodes (
                    node_name, node_type, status, capabilities, metadata, last_seen_at, updated_at
                )
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, now(), now())
                ON CONFLICT (id) DO NOTHING
                RETURNING id
                """,
                (name, LOCAL_NODE_TYPE, status, json.dumps(capabilities or []), json.dumps(metadata or {})),
            )
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    """
                    SELECT id FROM cluster_nodes
                    WHERE node_name = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (name,),
                )
                row = cursor.fetchone()
                if row is None:
                    cursor.execute(
                        """
                        INSERT INTO cluster_nodes (
                            node_name, node_type, status, capabilities, metadata, last_seen_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, now(), now())
                        RETURNING id
                        """,
                        (
                            name,
                            LOCAL_NODE_TYPE,
                            status,
                            json.dumps(capabilities or []),
                            json.dumps(metadata or {}),
                        ),
                    )
                    row = cursor.fetchone()
                else:
                    cursor.execute(
                        """
                        UPDATE cluster_nodes
                        SET status = %s,
                            capabilities = %s::jsonb,
                            metadata = %s::jsonb,
                            last_seen_at = now(),
                            updated_at = now()
                        WHERE id = %s
                        """,
                        (
                            status,
                            json.dumps(capabilities or []),
                            json.dumps(metadata or {}),
                            row["id"],
                        ),
                    )
        connection.commit()
    return str(row["id"])


def list_nodes(status: str | None = None) -> list[dict[str, Any]]:
    """List registered cluster nodes."""
    if status:
        return fetch_all(
            """
            SELECT id, node_name, node_type, status, capabilities, metadata,
                   last_seen_at, created_at, updated_at
            FROM cluster_nodes
            WHERE status = %s
            ORDER BY node_name ASC
            """,
            (status,),
        )
    return fetch_all(
        """
        SELECT id, node_name, node_type, status, capabilities, metadata,
               last_seen_at, created_at, updated_at
        FROM cluster_nodes
        ORDER BY node_name ASC
        """
    )
