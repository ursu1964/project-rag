"""Document ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger
from app.graph.graph_ingestion import ingest_graph_from_text
from app.memory.graph_fact_store import count_graph_facts_for_document
from app.rag.chunking import chunk_text
from app.rag.document_registry import calculate_file_hash, register_document
from app.rag.parsing import is_supported_text_file, parse_text_document
from app.rag.vector_store import insert_chunk
from app.ragos.cognitive_cache import invalidate_by_document_ingestion
from app.repositories.chunks_repository import list_chunk_indexes
from app.repositories.documents_repository import get_document_by_hash
from app.security.pii_filter import redact_sensitive_text
from app.tools.ollama_client import create_embedding

logger = get_logger(__name__)


def ingest_file(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)
    if not is_supported_text_file(path):
        logger.info("Skipping unsupported file type: %s", path.suffix.lower())
        return {"status": "skipped", "reason": "unsupported_file_type", "file_path": str(path)}

    file_hash = calculate_file_hash(path)
    parsed = parse_text_document(path)
    text = str(parsed["text"])
    document_metadata = dict(parsed["metadata"])
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    existing_document = get_document_by_hash(file_hash)
    existing_chunk_indexes: set[int] = set()
    repaired = False

    if existing_document:
        document_id = str(existing_document["id"])
        existing_chunk_indexes = set(list_chunk_indexes(document_id))
        graph_fact_count = count_graph_facts_for_document(document_id)
        if len(existing_chunk_indexes) >= len(chunks) and graph_fact_count > 0:
            logger.info("Skipping duplicate document: %s", path.name)
            return {
                "status": "skipped",
                "reason": "duplicate",
                "file_path": str(path),
                "file_hash": file_hash,
                "document_id": document_id,
                "chunks": len(existing_chunk_indexes),
            }
        repaired = True
        logger.info("Repairing partial document ingestion: %s", path.name)
    else:
        logger.info("Ingesting document: %s", path.name)
        document_id = register_document(path.name, str(path), file_hash, metadata=document_metadata)
        graph_fact_count = 0

    graph_result: dict[str, Any] = {"status": "skipped", "reason": "graph_facts_exist"}
    if graph_fact_count == 0:
        graph_result = ingest_graph_from_text(text, source_document_id=document_id)

    inserted_chunks = 0
    pii_chunks_sanitised = 0
    for chunk_index, content in enumerate(chunks):
        if chunk_index in existing_chunk_indexes:
            continue
        # Scan chunk for PII/secrets before embedding — redact rather than abort
        sanitised = redact_sensitive_text(content)
        if sanitised != content:
            pii_chunks_sanitised += 1
            logger.warning(
                "PII or secret detected in chunk %s of document %s — redacted before embedding",
                chunk_index,
                document_id,
            )
        embedding = create_embedding(sanitised)
        insert_chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            chunk_text=sanitised,
            embedding=embedding,
            metadata=document_metadata,
        )
        inserted_chunks += 1

    invalidate_by_document_ingestion()
    logger.info("Completed document ingestion: %s chunks_inserted=%s pii_chunks_sanitised=%s", path.name, inserted_chunks, pii_chunks_sanitised)

    return {
        "status": "repaired" if repaired else "ingested",
        "document_id": document_id,
        "file_path": str(path),
        "file_hash": file_hash,
        "chunks": len(chunks),
        "inserted_chunks": inserted_chunks,
        "pii_chunks_sanitised": pii_chunks_sanitised,
        "graph": graph_result,
    }


def ingest_directory(directory: str | Path, max_files: int | None = None) -> list[dict[str, Any]]:
    path = Path(directory)
    logger.info("Ingesting directory: %s", path)
    files = [
        file_path
        for file_path in sorted(path.rglob("*"))
        if file_path.is_file() and is_supported_text_file(file_path)
    ]

    if max_files is None:
        selected = files
        dropped: list[Path] = []
    else:
        limit = max(int(max_files), 0)
        selected = files[:limit]
        dropped = files[limit:]

    results = [ingest_file(file_path) for file_path in selected]
    for dropped_file in dropped:
        results.append(
            {
                "status": "skipped",
                "reason": "max_files_limit",
                "file_path": str(dropped_file),
            }
        )
    return results
