"""Route knowledge requests to local ProjectRAG stores."""

from __future__ import annotations

from typing import Any


def route_knowledge_request(question: str) -> dict[str, Any]:
    """Choose retrieval stores using deterministic keywords."""
    text = str(question or "").lower()
    use_graph = any(term in text for term in ("depend", "impact", "connected", "relationship", "breaks"))
    use_vector = any(term in text for term in ("document", "explain", "why", "what", "how")) or not use_graph
    use_memory = any(term in text for term in ("remember", "previous", "project", "session"))
    return {
        "use_graph": use_graph,
        "use_vector": use_vector,
        "use_memory": use_memory,
        "route": "hybrid" if use_graph and use_vector else "graph" if use_graph else "vector",
    }
