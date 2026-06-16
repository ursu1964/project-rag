"""Ingest .txt documents from data/raw into ProjectRAG."""

from pprint import pprint

from app.rag.ingestion import ingest_directory


if __name__ == "__main__":
    pprint(ingest_directory("data/raw"))

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
__test__ = False
