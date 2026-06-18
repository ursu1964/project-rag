# MVP Acceptance Gate

ProjectRAG MVP is accepted only when every gate below passes.

## Required Gates

| Gate | Acceptance Check | Command / Evidence |
|---|---|---|
| Docker Compose starts | PostgreSQL and GraphDB containers start successfully | `docker compose up -d` |
| PostgreSQL schema initializes | Idempotent schema script completes without fatal errors | `make init-db` |
| GraphDB responds | GraphDB HTTP endpoint is reachable | `curl http://localhost:7200/rest/repositories` |
| Ollama responds | Ollama API is reachable | `curl http://localhost:11434/api/tags` |
| Health endpoint works | API returns healthy application status | `curl http://127.0.0.1:8001/health` |
| Query endpoint works | `/query` returns answer, route, validation, evidence, and metrics | `curl -X POST http://127.0.0.1:8001/query -H "Content-Type: application/json" -d '{"question":"What does VM1 depend on?"}'` |
| Ingestion works | Documents from `data/raw` ingest and store chunks/facts | `make ingest` |
| Graph extraction works | Infrastructure relationships are extracted into graph facts/triples | `python -m scripts.query_graph` |
| Tests pass | Unit and non-external tests pass | `pytest -q` |
| Dangerous execution disabled | Destructive/tool execution paths are blocked by policy/default mode | Review `app/tools/tool_policy.py`, `app/devops/approval_gate.py`, and validator safety output |

## Pass Criteria

- All required gates must pass on a clean local setup.
- Failures must be documented with root cause and remediation before release.
- External dependency tests may be run separately, but must be clearly marked.
- No real credentials or secrets may be committed.
- No autonomous destructive action may be enabled for MVP.

## Release Decision

- **PASS**: all gates pass.
- **FAIL**: one or more gates fail.
- **N/A**: only allowed for explicitly delayed scope, never for the required gates above.
