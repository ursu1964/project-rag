from app.rag.citations import build_citations


def test_build_citations_from_vector_evidence():
    citations = build_citations(
        {
            "vector": [
                {
                    "document_id": "doc-1",
                    "chunk_index": 2,
                    "content": "VM1 depends on Database01.",
                    "metadata": {"filename": "topology.txt"},
                }
            ],
            "graph": {},
            "memory": [],
        }
    )

    assert citations == [
        {
            "id": "V1",
            "type": "vector",
            "source": "topology.txt",
            "document_id": "doc-1",
            "chunk_index": 2,
            "excerpt": "VM1 depends on Database01.",
        }
    ]


def test_build_citations_from_graph_evidence():
    citations = build_citations(
        {
            "vector": [],
            "graph": {
                "entity": "VM1",
                "outgoing": [
                    {
                        "subject": {"value": "VM1"},
                        "predicate": {"value": "dependsOn"},
                        "object": {"value": "Database01"},
                    }
                ],
            },
            "memory": [],
        }
    )

    assert citations[0]["id"] == "G1"
    assert citations[0]["type"] == "graph"
    assert citations[0]["excerpt"] == "VM1 dependsOn Database01"


def test_build_citations_from_memory_evidence():
    citations = build_citations(
        {
            "vector": [],
            "graph": {},
            "memory": [{"id": "mem-1", "memory_type": "knowledge", "value": {"fact": "Use runbook A"}}],
        }
    )

    assert citations[0]["id"] == "M1"
    assert citations[0]["type"] == "memory"
    assert citations[0]["memory_id"] == "mem-1"
