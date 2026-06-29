#!/usr/bin/env bash
set -euo pipefail

PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin}"

docker compose exec -T grafana grafana cli admin reset-admin-password "$PASSWORD"
echo "Grafana admin password reset. Login: ${GRAFANA_ADMIN_USER:-admin} / $PASSWORD"
