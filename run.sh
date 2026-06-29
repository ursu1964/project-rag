#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/RAG/project-rag"
cd "$PROJECT_DIR"

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

wait_url() {
  local name="$1"
  local url="$2"
  local tries="${3:-60}"

  echo "Waiting for $name..."
  for i in $(seq 1 "$tries"); do
    if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
      echo -e "${GREEN}OK${NC} $name"
      return 0
    fi
    sleep 2
  done

  echo -e "${RED}FAIL${NC} $name did not become ready: $url"
  return 1
}

print_url() {
  local name="$1"
  local url="$2"
  echo -e "${GREEN}READY${NC} $name -> $url"
}

echo "========================================"
echo "Starting ProjectRAG"
echo "========================================"

if [[ "${1:-}" == "--reset" ]]; then
  echo "Reset requested: stopping/removing containers before startup..."
  docker compose down --remove-orphans
elif [[ "${1:-}" != "" ]]; then
  echo -e "${RED}FAIL${NC} Unknown option: ${1:-}"
  echo "Usage: ./run.sh [--reset]"
  exit 2
fi

docker compose up -d --build

wait_url "API" "http://localhost:18000/health/live" 60
wait_url "Frontend" "http://localhost:3000/dashboards" 60

echo ""
echo "Container status:"
docker compose ps

echo ""
echo ""
echo "Dashboards are running. Open them manually from:"
echo "========================================"

print_url "Dashboard Launcher" "http://localhost:3000/dashboards"
print_url "Admin Dashboard" "http://localhost:3000/admin"
print_url "Ask Dashboard" "http://localhost:3000/ask"
print_url "Documents Dashboard" "http://localhost:3000/documents"
print_url "Models Dashboard" "http://localhost:3000/models"
print_url "Memory Dashboard" "http://localhost:3000/memory"
print_url "Workflows Dashboard" "http://localhost:3000/workflows"
print_url "Audit Dashboard" "http://localhost:3000/audit"
print_url "Topology Dashboard" "http://localhost:3000/topology"
print_url "Evaluation Dashboard" "http://localhost:3000/evaluation"

print_url "Grafana" "http://localhost:3001"
echo "Grafana login: use GRAFANA_ADMIN_USER/GRAFANA_ADMIN_PASSWORD from .env (defaults admin/admin if unset)."
echo "If Grafana login fails because an old volume kept the password: ./scripts/reset_grafana_admin.sh"
print_url "Grafana PostgreSQL Data" "http://localhost:3001/d/projectrag-postgres-data/projectrag-postgresql-data-and-ingestion"
print_url "Grafana Health" "http://localhost:3001/d/projectrag-health/projectrag-health-and-availability"
print_url "Grafana Latency" "http://localhost:3001/d/projectrag-latency-errors/projectrag-latency-and-error-rate-by-endpoint"
print_url "Grafana Workflows" "http://localhost:3001/d/projectrag-workflow-agents/projectrag-workflow-and-agent-performance"
print_url "API Docs" "http://localhost:18000/docs"
print_url "Prometheus" "http://localhost:9091"
print_url "Qdrant" "http://localhost:6333/dashboard"
print_url "GraphDB" "http://localhost:7200"
print_url "Alertmanager" "http://localhost:19094"
echo ""
echo "========================================"
echo -e "${GREEN}ProjectRAG startup verification finished.${NC}"
echo "========================================"
