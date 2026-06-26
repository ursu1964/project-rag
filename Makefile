.PHONY: install freeze up down logs init-db db-upgrade db-current ingest api ui dashboards-all test frontend-verify e2e-smoke openapi-snapshot openapi-check secret-scan docker-image-pins compose-prod-config k8s-validate deployment-package-validate observability-static observability-metrics observability-prometheus-targets observability-grafana-queries observability-validate verify format lint typecheck graph-test smoke-test verify-retry-backoff

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

frontend-verify:
	cd frontend && npm run verify
	python -m scripts.validate_frontend_auth

e2e-smoke:
	python -m scripts.e2e_smoke

openapi-snapshot:
	python -m scripts.export_openapi_snapshot

openapi-check:
	python -m scripts.export_openapi_snapshot --check

secret-scan:
	python -m scripts.scan_secrets

docker-image-pins:
	python -m scripts.check_docker_image_pins --require-digest

compose-prod-config:
	OLLAMA_URL=http://ollama:11434 PROJECTRAG_OIDC_ISSUER=https://issuer.example.com POSTGRES_DB=projectrag POSTGRES_USER=projectrag POSTGRES_PASSWORD=replace-me GRAFANA_ADMIN_USER=admin GRAFANA_ADMIN_PASSWORD=replace-me docker compose -f docker-compose.prod.yml config >/dev/null

k8s-validate:
	python -m scripts.validate_deployment_packaging

deployment-package-validate: docker-image-pins compose-prod-config k8s-validate

observability-static:
	python -m scripts.validate_observability

observability-metrics:
	curl -fsS http://localhost:$${APP_PORT:-8001}/metrics | grep -E "projectrag_requests_total|python_info"

observability-prometheus-targets:
	curl -fsS "http://localhost:$${PROMETHEUS_PORT:-9091}/api/v1/targets?state=active" | grep -E "projectrag_api|projectrag_otel_collector|blackbox_http"

observability-grafana-queries:
	python -m scripts.validate_observability
	grep -R "projectrag_" deploy/monitoring/grafana/dashboards >/dev/null

observability-validate: up observability-static observability-metrics observability-prometheus-targets observability-grafana-queries

verify: lint test frontend-verify openapi-check secret-scan docker-image-pins

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
