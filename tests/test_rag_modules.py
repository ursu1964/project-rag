from pathlib import Path
from unittest.mock import MagicMock

from app.rag.chunking import chunk_text
import app.rag.document_registry as document_registry
import app.rag.ingestion as ingestion
import app.rag.vector_store as vector_store


def test_chunk_text_with_overlap():
    assert chunk_text("abcdef", chunk_size=4, overlap=2) == ["abcd", "cdef"]


def test_calculate_file_hash(tmp_path):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello", encoding="utf-8")
    assert document_registry.calculate_file_hash(file_path) == document_registry.calculate_file_hash(file_path)


def test_document_exists_uses_file_hash(monkeypatch):
    monkeypatch.setattr(document_registry, "document_exists_by_hash", lambda file_hash: True)
    assert document_registry.document_exists("hash") is True


def test_insert_chunk_uses_vector_literal(monkeypatch):
    execute = MagicMock()
    monkeypatch.setattr(vector_store, "repository_insert_chunk", execute)

    vector_store.insert_chunk("doc-id", 0, "text", [0.1, 0.2], {"a": 1})

    assert execute.call_args.args[3] == [0.1, 0.2]


def test_similarity_search_uses_top_k(monkeypatch):
    fetch_all = MagicMock(return_value=[])
    monkeypatch.setattr(vector_store, "repository_similarity_search", fetch_all)

    assert vector_store.similarity_search([0.1], top_k=3) == []
    fetch_all.assert_called_once_with([0.1], 3)


def test_ingest_file_skips_duplicate(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("hello", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "document_exists", lambda file_hash: True)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "skipped"
    assert result["reason"] == "duplicate"


def test_ingest_file_chunks_embeds_and_stores(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("abcdef", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "document_exists", lambda file_hash: False)
    monkeypatch.setattr(ingestion, "register_document", lambda *args, **kwargs: "doc-id")
    monkeypatch.setattr(ingestion, "ingest_graph_from_text", lambda *args, **kwargs: {"triple_count": 0})
    monkeypatch.setattr(ingestion, "create_embedding", lambda text: [0.1, 0.2])
    insert_chunk = MagicMock()
    monkeypatch.setattr(ingestion, "insert_chunk", insert_chunk)
    monkeypatch.setattr(ingestion.settings, "chunk_size", 4)
    monkeypatch.setattr(ingestion.settings, "chunk_overlap", 0)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "ingested"
    assert result["chunks"] == 2
    assert insert_chunk.call_count == 2


def test_ingest_directory_reads_txt_files(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    calls = []
    monkeypatch.setattr(ingestion, "ingest_file", lambda path: calls.append(Path(path).name) or {"ok": True})

    results = ingestion.ingest_directory(tmp_path)

    assert results == [{"ok": True}]
    assert calls == ["a.txt"]
