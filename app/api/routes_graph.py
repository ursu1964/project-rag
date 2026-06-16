"""Graph routes."""

from fastapi import APIRouter

from app.core.schemas import GraphQueryRequest
from app.graph.graphdb_client import sparql_query

router = APIRouter()


@router.post("/graph/query")
def graph_query(request: GraphQueryRequest) -> dict:
    return sparql_query(request.query)
