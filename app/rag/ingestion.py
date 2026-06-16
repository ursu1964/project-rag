from __future__ import annotations

"""Document ingestion pipeline."""

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.rag.chunking import chunk_text
from app.rag.document_registry import calculate_file_hash, document_exists, register_document
from app.rag.vector_store import insert_chunk
from app.graph.graph_ingestion import ingest_graph_from_text
from app.tools.ollama_client import create_embedding

logger = get_logger(__name__)


def ingest_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    if path.suffix.lower() != ".txt":
        logger.info("Skipping unsupported file type: %s", path.suffix.lower())
        return {"status": "skipped", "reason": "unsupported_file_type", "file_path": str(path)}

    file_hash = calculate_file_hash(path)
    if document_exists(file_hash):
        logger.info("Skipping duplicate document: %s", path.name)
        return {"status": "skipped", "reason": "duplicate", "file_path": str(path), "file_hash": file_hash}

    logger.info("Ingesting document: %s", path.name)
    text = path.read_text(encoding="utf-8")
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    document_id = register_document(path.name, str(path), file_hash, metadata={"suffix": path.suffix})

    graph_result = ingest_graph_from_text(text, source_document_id=document_id)

    for chunk_index, content in enumerate(chunks):
        embedding = create_embedding(content)
        insert_chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_text=content,
            embedding=embedding,
            metadata={"filename": path.name},
        )

    logger.info("Completed document ingestion: %s chunks=%s", path.name, len(chunks))

    return {
        "status": "ingested",
        "document_id": document_id,
        "file_path": str(path),
        "file_hash": file_hash,
        "chunks": len(chunks),
        "graph": graph_result,
    }


def ingest_directory(directory: str | Path) -> list[dict[str, Any]]:
    path = Path(directory)
    logger.info("Ingesting directory: %s", path)
    return [ingest_file(file_path) for file_path in sorted(path.rglob("*.txt"))]
