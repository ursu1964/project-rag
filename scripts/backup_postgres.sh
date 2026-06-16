#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="backups/postgres"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="${BACKUP_DIR}/projectrag_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

docker exec projectrag-postgres pg_dump -U projectrag -d projectrag -Fc > "${OUTPUT}"

echo "PostgreSQL backup written to ${OUTPUT}"
