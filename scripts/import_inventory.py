"""Import local DevOps inventory JSON into GraphDB and PostgreSQL graph_facts."""

from pathlib import Path
import sys
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
__test__ = False

from app.devops.inventory_importer import import_inventory_from_json


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.import_inventory <path-to-inventory.json>", file=sys.stderr)
        raise SystemExit(2)

    pprint(import_inventory_from_json(Path(sys.argv[1])))
