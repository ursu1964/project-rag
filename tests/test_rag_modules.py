from pathlib import Path
from unittest.mock import MagicMock

import app.rag.document_registry as document_registry
import app.rag.ingestion as ingestion
import app.rag.vector_store as vector_store
import app.repositories.documents_repository as documents_repository
from app.rag.chunking import chunk_text


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
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: {"id": "doc-id"})
    monkeypatch.setattr(ingestion, "list_chunk_indexes", lambda document_id: [0])
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 1)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "skipped"
    assert result["reason"] == "duplicate"


def test_ingest_file_chunks_embeds_and_stores(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("abcdef", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: None)
    monkeypatch.setattr(ingestion, "register_document", lambda *args, **kwargs: "doc-id")
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 0)
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



def test_ingest_file_repairs_partial_duplicate(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("abcdef", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: {"id": "doc-id"})
    monkeypatch.setattr(ingestion, "list_chunk_indexes", lambda document_id: [])
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 0)
    monkeypatch.setattr(ingestion, "ingest_graph_from_text", lambda *args, **kwargs: {"triple_count": 1})
    monkeypatch.setattr(ingestion, "create_embedding", lambda text: [0.1, 0.2])
    insert_chunk = MagicMock()
    monkeypatch.setattr(ingestion, "insert_chunk", insert_chunk)
    monkeypatch.setattr(ingestion.settings, "chunk_size", 4)
    monkeypatch.setattr(ingestion.settings, "chunk_overlap", 0)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "repaired"
    assert result["inserted_chunks"] == 2
    assert insert_chunk.call_count == 2


def test_ingest_file_repairs_only_missing_chunks(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("abcdef", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: {"id": "doc-id"})
    monkeypatch.setattr(ingestion, "list_chunk_indexes", lambda document_id: [0])
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 1)
    monkeypatch.setattr(ingestion, "create_embedding", lambda text: [0.1, 0.2])
    insert_chunk = MagicMock()
    monkeypatch.setattr(ingestion, "insert_chunk", insert_chunk)
    monkeypatch.setattr(ingestion.settings, "chunk_size", 4)
    monkeypatch.setattr(ingestion.settings, "chunk_overlap", 0)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "repaired"
    assert result["inserted_chunks"] == 1
    assert insert_chunk.call_count == 1
    assert insert_chunk.call_args.kwargs["chunk_index"] == 1


def test_ingest_file_repairs_only_missing_graph_facts(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.txt"
    file_path.write_text("abcdef", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: {"id": "doc-id"})
    monkeypatch.setattr(ingestion, "list_chunk_indexes", lambda document_id: [0, 1])
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 0)
    ingest_graph = MagicMock(return_value={"triple_count": 1})
    monkeypatch.setattr(ingestion, "ingest_graph_from_text", ingest_graph)
    insert_chunk = MagicMock()
    monkeypatch.setattr(ingestion, "insert_chunk", insert_chunk)
    monkeypatch.setattr(ingestion.settings, "chunk_size", 4)
    monkeypatch.setattr(ingestion.settings, "chunk_overlap", 0)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "repaired"
    assert result["inserted_chunks"] == 0
    assert result["graph"]["triple_count"] == 1
    insert_chunk.assert_not_called()
    ingest_graph.assert_called_once()


def test_delete_document_cleans_graphdb_before_postgres(monkeypatch):
    calls = []
    monkeypatch.setattr(
        documents_repository,
        "fetch_all",
        lambda query, params=(): [{"subject": "VM1", "predicate": "dependsOn", "object": "Database01"}],
    )
    monkeypatch.setattr(documents_repository, "delete_graph_facts", lambda facts: calls.append(("graphdb", facts)) or 1)

    class Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, query, params=()):
            calls.append(("sql", query.strip().split()[0], params))

        def fetchone(self):
            return {"id": "doc-1"}

    class Connection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def cursor(self):
            return Cursor()

        def commit(self):
            calls.append(("commit",))

    monkeypatch.setattr(documents_repository, "get_connection", lambda: Connection())

    assert documents_repository.delete_document("doc-1") is True
    assert calls[0][0] == "graphdb"
    assert ("commit",) in calls


def test_ingest_file_supports_markdown_metadata(tmp_path, monkeypatch):
    file_path = tmp_path / "runbook.md"
    file_path.write_text("# Runbook", encoding="utf-8")
    monkeypatch.setattr(ingestion, "calculate_file_hash", lambda path: "hash")
    monkeypatch.setattr(ingestion, "get_document_by_hash", lambda file_hash: None)
    register_document = MagicMock(return_value="doc-id")
    monkeypatch.setattr(ingestion, "register_document", register_document)
    monkeypatch.setattr(ingestion, "count_graph_facts_for_document", lambda document_id: 0)
    monkeypatch.setattr(ingestion, "ingest_graph_from_text", lambda *args, **kwargs: {"triple_count": 0})
    monkeypatch.setattr(ingestion, "create_embedding", lambda text: [0.1, 0.2])
    monkeypatch.setattr(ingestion, "insert_chunk", MagicMock())
    monkeypatch.setattr(ingestion.settings, "chunk_size", 100)
    monkeypatch.setattr(ingestion.settings, "chunk_overlap", 0)

    result = ingestion.ingest_file(file_path)

    assert result["status"] == "ingested"
    assert register_document.call_args.kwargs["metadata"]["suffix"] == ".md"
    assert register_document.call_args.kwargs["metadata"]["source_type"] == "runbook"


def test_ingest_directory_reads_text_like_files(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "c.log").write_text("c", encoding="utf-8")
    (tmp_path / "d.tf").write_text("d", encoding="utf-8")
    (tmp_path / "kubernetes_manifest.yaml").write_text("kind: Service", encoding="utf-8")
    calls = []
    monkeypatch.setattr(ingestion, "ingest_file", lambda path: calls.append(Path(path).name) or {"ok": True})

    results = ingestion.ingest_directory(tmp_path)

    assert results == [{"ok": True}, {"ok": True}, {"ok": True}, {"ok": True}, {"ok": True}]
    assert calls == ["a.txt", "b.md", "c.log", "d.tf", "kubernetes_manifest.yaml"]


def test_ingest_directory_respects_max_files(tmp_path, monkeypatch):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.md").write_text("b", encoding="utf-8")
    (tmp_path / "c.log").write_text("c", encoding="utf-8")
    calls = []
    monkeypatch.setattr(ingestion, "ingest_file", lambda path: calls.append(Path(path).name) or {"ok": True})

    results = ingestion.ingest_directory(tmp_path, max_files=2)

    assert calls == ["a.txt", "b.md"]
    assert results[0] == {"ok": True}
    assert results[1] == {"ok": True}
    assert results[2]["status"] == "skipped"
    assert results[2]["reason"] == "max_files_limit"
