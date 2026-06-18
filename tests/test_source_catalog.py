from app.rag.source_catalog import build_source_catalog


def test_build_source_catalog_missing_path(tmp_path):
    result = build_source_catalog(tmp_path / "missing")

    assert result["status"] == "missing"
    assert result["total_sources"] == 0


def test_build_source_catalog_classifies_sources(tmp_path):
    (tmp_path / "runbook.txt").write_text("runbook", encoding="utf-8")
    (tmp_path / "main.tf").write_text("resource x", encoding="utf-8")
    (tmp_path / "app.log").write_text("error", encoding="utf-8")
    (tmp_path / "kubernetes_manifest.yaml").write_text("kind: Pod", encoding="utf-8")
    (tmp_path / "cmdb_inventory.json").write_text("{}", encoding="utf-8")
    (tmp_path / "ignore.bin").write_bytes(b"x")

    result = build_source_catalog(tmp_path)

    assert result["status"] == "ok"
    assert result["total_sources"] == 5
    assert result["counts"]["runbook"] == 1
    assert result["counts"]["terraform"] == 1
    assert result["counts"]["log"] == 1
    assert result["counts"]["kubernetes_manifest"] == 1
    assert result["counts"]["inventory"] == 1
    txt = next(item for item in result["sources"] if item["filename"] == "runbook.txt")
    assert txt["ingestable"] is True
    log = next(item for item in result["sources"] if item["filename"] == "app.log")
    assert log["ingestable"] is True
    manifest = next(item for item in result["sources"] if item["filename"] == "kubernetes_manifest.yaml")
    assert manifest["ingestable"] is True
