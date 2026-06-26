"""DevOps inventory API routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.devops.inventory_importer import import_inventory_from_json
from app.security.rbac import permission_dependency

router = APIRouter(dependencies=[Depends(permission_dependency("ingest"))])
_RAW_DATA_DIR = Path("data/raw")


class InventoryImportRequest(BaseModel):
    path: str = Field(min_length=1)


def _validate_raw_path(path_value: str) -> Path:
    path = Path(path_value)
    resolved = path.resolve()
    raw_root = _RAW_DATA_DIR.resolve()
    if raw_root not in resolved.parents:
        raise HTTPException(status_code=400, detail="Inventory path must be inside data/raw")
    if not resolved.is_file():
        raise HTTPException(status_code=404, detail="Inventory file not found")
    if resolved.suffix.lower() != ".json":
        raise HTTPException(status_code=400, detail="Inventory file must be JSON")
    return resolved


@router.post("/devops/inventory/import")
def import_inventory(request: InventoryImportRequest) -> dict[str, object]:
    path = _validate_raw_path(request.path)
    result = import_inventory_from_json(path)
    return {
        "status": "ok",
        "entity_count": len(result["entities"]),
        "relationship_count": len(result["relationships"]),
        "triple_count": result["triple_count"],
    }
