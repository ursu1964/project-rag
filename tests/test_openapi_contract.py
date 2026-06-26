from pathlib import Path

from scripts.export_openapi_snapshot import _canonical, _openapi_schema


def test_openapi_snapshot_is_current():
    snapshot = Path("docs/openapi.snapshot.json")
    assert snapshot.exists()
    assert _canonical(_openapi_schema()) == snapshot.read_text(encoding="utf-8")
