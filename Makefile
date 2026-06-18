.PHONY: install freeze up down logs init-db db-upgrade db-current ingest api ui dashboards-all test format lint typecheck graph-test smoke-test verify-retry-backoff

install:
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.lock.txt

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

init-db:
	docker exec -i projectrag-postgres psql -U projectrag -d projectrag < scripts/init_postgres.sql

db-upgrade:
	alembic upgrade head

db-current:
	alembic current

ingest:
	python -m scripts.ingest_documents

api:
	uvicorn app.main:app --reload --host $${APP_HOST:-127.0.0.1} --port $${APP_PORT:-8001}

ui:
	streamlit run ui/streamlit_app.py

dashboards-all:
	python scripts/launch_dashboards.py --auto-port --auto-ui-port --with-observability

test:
	pytest -v

format:
	isort app scripts tests
	black app scripts tests

lint:
	ruff check app scripts tests
	python -m compileall -q app scripts tests

typecheck:
	mypy app

graph-test:
	python -m scripts.query_graph

smoke-test: up init-db ingest test
	curl http://localhost:8001/health || true

verify-retry-backoff:
	python -m scripts.verify_retry_backoff
