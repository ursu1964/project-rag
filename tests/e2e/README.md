# E2E smoke tests

Run the minimal authenticated RAG smoke test with:

```bash
pytest tests/e2e/test_smoke_rag_flow.py
```

The test starts the FastAPI app in-process with test settings. PostgreSQL,
GraphDB, embedding, and LLM calls are replaced with in-memory/test doubles so no
external services are required.
