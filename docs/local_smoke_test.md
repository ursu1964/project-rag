# Local Smoke Test

This guide verifies the local ProjectRAG MVP stack end-to-end.

## 1. Start containers

```bash
docker compose up -d
```

## 2. Initialize PostgreSQL

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

## 3. Start Ollama in a separate terminal

In a separate terminal:

```bash
ollama serve
```

## 4. Pull models

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

## 5. Create sample data

Create `data/raw/topology_example.txt`:

```bash
cat > data/raw/topology_example.txt <<'DATA'
VM1 is connected to SubnetA.
VM1 depends on Database01.
Database01 is protected by Firewall01.
ServiceA calls API01.
API01 uses Database01.
ApplicationA runs on VM1.
SubnetA belongs to VNetDev.
DATA
```

## 6. Run ingestion

```bash
python -m scripts.ingest_documents
```

## 7. Start the API

```bash
uvicorn app.main:app --reload
```

## 8. Verify health

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"ok","service":"ProjectRAG"}
```

## 9. Test a query

```bash
curl -X POST http://127.0.0.1:8001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What does VM1 depend on?"}'
```

## 10. Run the graph query script

```bash
python -m scripts.query_graph
```
