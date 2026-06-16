#!/usr/bin/env bash
set -euo pipefail

"$(dirname "$0")/backup_postgres.sh"
"$(dirname "$0")/backup_graphdb.sh"
