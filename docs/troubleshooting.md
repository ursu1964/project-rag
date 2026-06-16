# ProjectRAG Troubleshooting

## Python version is wrong

Check your active Python:

```bash
python --version
which python
```

ProjectRAG is intended for modern Python 3.12+ development. If the wrong version is active, create a new virtual environment with the desired interpreter:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python --version
```

## Virtual environment uses Python 3.9 instead of 3.12

Remove and recreate the virtual environment:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Docker permission denied

If Docker commands fail with permission errors:

```bash
docker ps
```

Fix options:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

Then retry:

```bash
docker compose up -d
```

## PostgreSQL container not running

Check containers:

```bash
docker compose ps
```

Start or restart:

```bash
docker compose up -d postgres
```

View logs:

```bash
docker compose logs postgres
```

## pgvector extension missing

Initialize the database schema:

```bash
docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql
```

Verify extension:

```bash
docker exec -it projectrag-postgres psql -U projectrag -d projectrag -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

## GraphDB not reachable

Check container status:

```bash
docker compose ps graphdb
```

Check logs:

```bash
docker compose logs graphdb
```

Test endpoint:

```bash
curl http://localhost:7200/rest/repositories
```

## Ollama not running

Start Ollama:

```bash
ollama serve
```

Test it:

```bash
curl http://localhost:11434/api/tags
```

## Ollama model missing

Pull required models:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

List installed models:

```bash
ollama list
```

## ModuleNotFoundError

Activate the virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Run commands from the repository root:

```bash
pwd
python -m scripts.ingest_documents
```

## requirements install failed

Upgrade packaging tools:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If your system Python is externally managed, use a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Port already in use

Find the process:

```bash
lsof -i :8000
lsof -i :5432
lsof -i :7200
lsof -i :11434
```

Stop the conflicting process or change ports in `docker-compose.yml` / `.env`.

For API reload conflicts:

```bash
pkill -f "uvicorn app.main:app" || true
uvicorn app.main:app --reload
```

## .env missing

Create it from the example:

```bash
cp .env.example .env
```

Then edit local values if needed:

```bash
nano .env
```

Never commit `.env`.
