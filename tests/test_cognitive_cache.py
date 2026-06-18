import time

from app.ragos import cognitive_cache


def setup_function():
    cognitive_cache.clear_cache()


def test_cache_repeated_questions():
    cognitive_cache.cache_question("What is VM1?", {"answer": "vm"})

    assert cognitive_cache.get_cached_question("What is VM1?") == {"answer": "vm"}


def test_cache_graph_queries():
    cognitive_cache.cache_graph_query("SELECT * WHERE { ?s ?p ?o }", {"rows": []})

    assert cognitive_cache.get_cached_graph_query("SELECT * WHERE { ?s ?p ?o }") == {"rows": []}


def test_cache_model_responses():
    cognitive_cache.cache_model_response("prompt", "response")

    assert cognitive_cache.get_cached_model_response("prompt") == "response"


def test_ttl_expiration():
    cognitive_cache.cache_question("short", "value", ttl_seconds=1)
    time.sleep(1.01)

    assert cognitive_cache.get_cached_question("short") is None


def test_invalidation_by_document_ingestion():
    cognitive_cache.cache_question("q", "a")
    cognitive_cache.cache_graph_query("g", {})

    assert cognitive_cache.invalidate_by_document_ingestion() == 2
    assert cognitive_cache.cache_stats()["total"] == 0
