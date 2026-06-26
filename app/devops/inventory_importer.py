"""Import normalized inventory JSON into graph-like facts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.graph.graphdb_client import insert_turtle
from app.graph.triple_builder import build_triple, build_turtle


def import_inventory_from_json(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    entities = data.get("entities", []) if isinstance(data, dict) else []
    relationships = data.get("relationships", []) if isinstance(data, dict) else []
    triples: list[str] = []
    for relationship in relationships:
        if not isinstance(relationship, dict):
            continue
        source = relationship.get("source") or relationship.get("from") or relationship.get("source_entity")
        target = relationship.get("target") or relationship.get("to") or relationship.get("target_entity")
        rel = relationship.get("relationship") or relationship.get("type") or relationship.get("predicate")
        if source and target and rel:
            triples.append(build_triple(str(source), str(rel), str(target)))
    if triples:
        insert_turtle(build_turtle(triples))
    return {"entities": entities, "relationships": relationships, "triple_count": len(triples)}
