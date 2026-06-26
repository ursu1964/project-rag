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

open_url() {
  local name="$1"
  local url="$2"

  if curl -fsS --max-time 5 "$url" >/dev/null 2>&1; then
    echo -e "${GREEN}OPEN${NC} $name -> $url"
    xdg-open "$url" >/dev/null 2>&1 || echo -e "${YELLOW}WARN${NC} Could not auto-open $url"
  else
    echo -e "${RED}FAIL${NC} $name -> $url"
  fi
}

echo "========================================"
echo "Starting ProjectRAG"
echo "========================================"

docker compose down --remove-orphans
docker compose up -d --build

wait_url "API" "http://localhost:18000/health/live" 60
wait_url "Frontend" "http://localhost:3000/admin" 60

echo ""
echo "Container status:"
docker compose ps

echo ""
echo "Opening verified dashboards..."
echo "========================================"

open_url "Admin Dashboard" "http://localhost:3000/admin"
open_url "Ask Dashboard" "http://localhost:3000/ask"
open_url "Documents Dashboard" "http://localhost:3000/documents"
open_url "Audit Dashboard" "http://localhost:3000/audit"
open_url "Topology Dashboard" "http://localhost:3000/topology"
open_url "Evaluation Dashboard" "http://localhost:3000/evaluation"

open_url "API Health" "http://localhost:18000/health/live"
open_url "API Docs" "http://localhost:18000/docs"
open_url "Grafana" "http://localhost:3001"
open_url "Prometheus" "http://localhost:9091"
open_url "Qdrant" "http://localhost:6333/dashboard"
echo "OPEN GraphDB -> http://localhost:7200"
xdg-open "http://localhost:7200" >/dev/null 2>&1 || true

#open_url "Alertmanager" "http://localhost:19094"
xdg-open "http://localhost:19094" >/dev/null 2>&1 || true


echo ""
echo "========================================"
echo -e "${GREEN}ProjectRAG startup verification finished.${NC}"
echo "========================================"
