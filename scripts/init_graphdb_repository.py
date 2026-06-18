"""Create the configured GraphDB repository for ProjectRAG."""

from app.graph.graphdb_client import create_repository

if __name__ == "__main__":
    create_repository()
    print("GraphDB repository is ready")
