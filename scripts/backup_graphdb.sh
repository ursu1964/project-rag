#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="backups/graphdb"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="${BACKUP_DIR}/projectrag_graph_${TIMESTAMP}.ttl"
GRAPHDB_URL="${GRAPHDB_URL:-http://localhost:7200}"
GRAPHDB_REPOSITORY="${GRAPHDB_REPOSITORY:-projectrag}"

mkdir -p "${BACKUP_DIR}"

# Simple RDF export for the configured repository. If this fails, use the
# GraphDB Workbench export flow documented in docs/backups.md.
curl -fsS \
  -H "Accept: text/turtle" \
  "${GRAPHDB_URL%/}/repositories/${GRAPHDB_REPOSITORY}/statements" \
  -o "${OUTPUT}"

echo "GraphDB Turtle export written to ${OUTPUT}"
