.PHONY: install freeze up down logs init-db db-upgrade db-current ingest api ui test format lint typecheck graph-test smoke-test

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
	uvicorn app.main:app --reload --host $${APP_HOST:-127.0.0.1} --port $${APP_PORT:-8000}

ui:
	streamlit run ui/streamlit_app.py

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
	curl http://localhost:8000/health || true
