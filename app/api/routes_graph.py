"""Graph routes."""

from fastapi import APIRouter, Query

from app.core.schemas import GraphQueryRequest
from app.graph.graphdb_client import sparql_query
from app.memory.graph_fact_store import list_all_graph_facts

router = APIRouter()


@router.post("/graph/query")
def graph_query(request: GraphQueryRequest) -> dict:
    return sparql_query(request.query)


@router.get("/graph/export")
def graph_export(limit: int = Query(default=1000, ge=1, le=5000)) -> dict:
    """Export graph facts as nodes and edges for visualization clients."""
    facts = list_all_graph_facts(limit=limit)
    node_ids: set[str] = set()
    edges: list[dict] = []

    for fact in facts:
        subject = fact.get("subject")
        predicate = fact.get("predicate")
        obj = fact.get("object")
        if not subject or not predicate or not obj:
            continue

        node_ids.update([subject, obj])
        edges.append(
            {
                "id": str(fact.get("id")),
                "source": subject,
                "target": obj,
                "label": predicate,
                "confidence": float(fact.get("confidence") or 0.0),
                "metadata": fact.get("metadata") or {},
            }
        )

    return {
        "nodes": [{"id": node_id, "label": node_id} for node_id in sorted(node_ids)],
        "edges": edges,
    }
