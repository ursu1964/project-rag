# ProjectRAG Backups and Restore

## Backup PostgreSQL

Run:

```bash
scripts/backup_postgres.sh
```

This creates a timestamped custom-format dump under:

```text
backups/postgres/
```

## Backup GraphDB

Run:

```bash
scripts/backup_graphdb.sh
```

This attempts a simple Turtle export from:

```text
http://localhost:7200/repositories/projectrag/statements
```

Output is written under:

```text
backups/graphdb/
```

If the curl export fails, use the GraphDB Workbench manual export:

1. Open `http://localhost:7200`.
2. Select the `projectrag` repository.
3. Use the export/download function.
4. Save the export into `backups/graphdb/`.

## Backup Everything

```bash
scripts/backup_all.sh
```

## Restore PostgreSQL

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Restore a `.dump` file:

```bash
cat backups/postgres/projectrag_YYYYMMDD_HHMMSS.dump | \
  docker exec -i projectrag-postgres pg_restore -U projectrag -d projectrag --clean --if-exists
```

If restoring into a fresh database, initialize extensions first if needed:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

## Restore GraphDB

Preferred manual restore:

1. Open `http://localhost:7200`.
2. Select or create the `projectrag` repository.
3. Import the Turtle file from `backups/graphdb/`.

Curl-based import example:

```bash
curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @backups/graphdb/projectrag_graph_YYYYMMDD_HHMMSS.ttl \
  http://localhost:7200/repositories/projectrag/statements
```

## Notes

- Backup files are ignored by git.
- Do not commit backups; they may contain private project data.
- Periodically test restore into a disposable local environment.
