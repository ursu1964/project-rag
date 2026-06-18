"""Insert a small sample dependency graph into GraphDB."""

from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle

if __name__ == "__main__":
    turtle = build_turtle(
        [
            build_triple("ProjectRAG", "dependsOn", "PostgreSQL"),
            build_triple("ProjectRAG", "dependsOn", "GraphDB"),
            build_triple("ProjectRAG", "dependsOn", "Ollama"),
        ]
    )
    insert_turtle(turtle)
    print("Inserted sample ProjectRAG graph.")

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
__test__ = False
