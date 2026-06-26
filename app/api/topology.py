from fastapi import APIRouter

router = APIRouter(prefix="/topology", tags=["topology"])

@router.get("")
def get_topology():
    return {
        "nodes": [
            {"id": "frontend", "label": "Frontend", "type": "service"},
            {"id": "api", "label": "API", "type": "service"},
            {"id": "postgres", "label": "PostgreSQL", "type": "database"},
            {"id": "qdrant", "label": "Qdrant", "type": "vector-db"},
            {"id": "graphdb", "label": "GraphDB", "type": "graph-db"},
        ],
        "edges": [
            {"source": "frontend", "target": "api", "label": "HTTP"},
            {"source": "api", "target": "postgres", "label": "SQL"},
            {"source": "api", "target": "qdrant", "label": "Vector search"},
            {"source": "api", "target": "graphdb", "label": "Graph facts"},
        ],
    }
