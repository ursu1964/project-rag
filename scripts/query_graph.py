"""Run a raw SPARQL query against GraphDB."""

import sys
from pprint import pprint

from app.graph.graphdb_client import sparql_query


DEFAULT_QUERY = """

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
__test__ = False
PREFIX project: <http://projectrag.local/>
SELECT ?dependency WHERE {
  project:ProjectRAG project:dependsOn ?dependency .
}
""".strip()


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or DEFAULT_QUERY
    pprint(sparql_query(query))
