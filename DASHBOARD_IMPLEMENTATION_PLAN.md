# ProjectRAG Dashboard Implementation Plan

## Current Working State

The Docker stack starts with `./run.sh`.

Working services:
- Frontend: http://localhost:3000
- API: http://localhost:18000
- API Docs: http://localhost:18000/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9091
- GraphDB: http://localhost:7200
- Qdrant: http://localhost:6333/dashboard
- Alertmanager: http://localhost:19094

## Existing Frontend Pages

| Page | File | Status |
|---|---|---|
| Home | frontend/app/page.tsx | Exists |
| Admin | frontend/app/admin/page.tsx | Exists |
| Ask | frontend/app/ask/page.tsx | Exists |
| Documents | frontend/app/documents/page.tsx | Exists |
| Audit | frontend/app/audit/page.tsx | Exists |
| Evaluation | frontend/app/evaluation/page.tsx | Exists |
| Topology | frontend/app/topology/page.tsx | Exists |

## Existing Backend APIs

| API | Purpose |
|---|---|
| /health/live | API live check |
| /health/ready | API readiness |
| /health/deep | Deep dependency check |
| /metrics | Prometheus metrics |
| /query | Ask/RAG query |
| /documents | List documents |
| /documents/upload | Upload documents |
| /documents/{document_id} | Get document |
| /documents/{document_id}/reindex | Reindex document |
| /ingest | Ingest documents |
| /topology | Infrastructure topology |

## Dashboard-to-API Map

| Dashboard | Frontend Route | Backend API | Status | Next Action |
|---|---|---|---|---|
| Home | / | health, topology, metrics | Partial | Add launcher/status cards |
| Admin | /admin | MISSING | Blocked | Create /admin/summary |
| Ask | /ask | /query | Partial | Verify request/response schema |
| Documents | /documents | /documents | Partial | Verify list/upload/reindex |
| Audit | /audit | MISSING | Blocked | Create /audit/events |
| Topology | /topology | /topology | Working/basic | Improve real topology data |
| Evaluation | /evaluation | MISSING | Blocked | Create /evaluation/summary |

## Implementation Order

### Phase 1: Stabilize Existing Working Dashboards

1. Home launcher
2. Ask dashboard
3. Documents dashboard
4. Topology dashboard

### Phase 2: Add Missing Backend APIs

1. /admin/summary
2. /audit/events
3. /evaluation/summary

### Phase 3: Improve UI Design

1. AppShell navigation
2. Dashboard cards
3. Status badges
4. Tables
5. Dark-compatible design

### Phase 4: Add New Dashboards

1. Agents
2. Memory
3. Vector DB
4. Graph DB
5. Workflows
6. Settings
7. Monitoring

## Safety Rules

- One dashboard at a time.
- One commit per dashboard.
- Always run:
  - npm run build
  - python3 -m py_compile app/main.py
  - docker compose up -d --build
  - ./run.sh
- Never edit frontend and backend randomly at the same time.
- Keep current working state committed before each new phase.

## Next Immediate Task

Implement the Home Launcher Dashboard with:
- links to all dashboards
- API health status
- external infrastructure links
- clear visual state
