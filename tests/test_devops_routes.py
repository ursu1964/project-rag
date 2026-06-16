import json

import pytest
from fastapi import HTTPException

import app.api.routes_devops as routes_devops
from app.api.routes_devops import InventoryImportRequest, import_inventory


def test_import_inventory_validates_raw_path_and_returns_counts(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    inventory = raw / "inventory.json"
    inventory.write_text(json.dumps({"entities": [], "relationships": []}), encoding="utf-8")
    monkeypatch.setattr(routes_devops, "_RAW_DATA_DIR", raw)
    monkeypatch.setattr(
        routes_devops,
        "import_inventory_from_json",
        lambda path: {"entities": [{"name": "VM1"}], "relationships": [{"source": "VM1"}], "triple_count": 2},
    )

    result = import_inventory(InventoryImportRequest(path=str(inventory)))

    assert result == {"status": "ok", "entity_count": 1, "relationship_count": 1, "triple_count": 2}


def test_import_inventory_rejects_outside_raw(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    outside = tmp_path / "inventory.json"
    outside.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(routes_devops, "_RAW_DATA_DIR", raw)

    with pytest.raises(HTTPException) as exc:
        import_inventory(InventoryImportRequest(path=str(outside)))

    assert exc.value.status_code == 400


def test_import_inventory_rejects_non_json(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    file_path = raw / "inventory.txt"
    file_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(routes_devops, "_RAW_DATA_DIR", raw)

    with pytest.raises(HTTPException) as exc:
        import_inventory(InventoryImportRequest(path=str(file_path)))

    assert exc.value.status_code == 400
