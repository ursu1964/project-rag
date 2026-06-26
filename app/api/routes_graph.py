"""Graph routes."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.schemas import GraphQueryRequest
from app.graph.graphdb_client import sparql_query
from app.memory.graph_fact_store import list_all_graph_facts
from app.security.rbac import permission_dependency

router = APIRouter()


@router.post("/graph/query", dependencies=[Depends(permission_dependency("query"))])
def graph_query(request: GraphQueryRequest) -> dict:
    statement = request.query.lstrip().lower()
    if not statement.startswith(("select", "ask", "construct", "describe", "prefix", "base")):
        raise HTTPException(status_code=400, detail="Only read-only SPARQL queries are allowed")
    if any(token in statement for token in (" insert ", " delete ", " load ", " clear ", " drop ", " create ", " move ", " copy ", " add ")):
        raise HTTPException(status_code=400, detail="SPARQL update operations are not allowed")
    return sparql_query(request.query)


@router.get("/graph/export", dependencies=[Depends(permission_dependency("read"))])
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
