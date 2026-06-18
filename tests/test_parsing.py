from app.rag.parsing import infer_document_type, is_supported_text_file, parse_text_document


def test_supported_text_file_suffixes():
    assert is_supported_text_file("a.txt") is True
    assert is_supported_text_file("a.md") is True
    assert is_supported_text_file("a.log") is True
    assert is_supported_text_file("a.json") is True
    assert is_supported_text_file("a.yaml") is True
    assert is_supported_text_file("a.yml") is True
    assert is_supported_text_file("a.tf") is True
    assert is_supported_text_file("a.pdf") is False


def test_infer_document_type():
    assert infer_document_type("incident_runbook.md") == "runbook"
    assert infer_document_type("server.log") == "log"
    assert infer_document_type("notes.md") == "markdown"
    assert infer_document_type("main.tf") == "terraform"
    assert infer_document_type("kubernetes_manifest.yaml") == "kubernetes_manifest"
    assert infer_document_type("ansible_playbook.yml") == "ansible"
    assert infer_document_type("cmdb_inventory.json") == "inventory"


def test_parse_text_document_extracts_metadata(tmp_path):
    path = tmp_path / "runbook.md"
    path.write_text("# Runbook\nStep 1", encoding="utf-8")

    parsed = parse_text_document(path)

    assert parsed["text"] == "# Runbook\nStep 1"
    assert parsed["metadata"]["filename"] == "runbook.md"
    assert parsed["metadata"]["suffix"] == ".md"
    assert parsed["metadata"]["source_type"] == "runbook"
    assert parsed["metadata"]["line_count"] == 2


def test_parse_json_extracts_top_level_keys(tmp_path):
    path = tmp_path / "cmdb_inventory.json"
    path.write_text('{"servers": [], "networks": []}', encoding="utf-8")

    metadata = parse_text_document(path)["metadata"]

    assert metadata["parse_status"] == "ok"
    assert metadata["json_type"] == "object"
    assert metadata["top_level_keys"] == ["networks", "servers"]


def test_parse_yaml_extracts_kubernetes_metadata(tmp_path):
    path = tmp_path / "kubernetes_manifest.yaml"
    path.write_text("apiVersion: v1\nkind: Service\nmetadata:\n  name: api\n", encoding="utf-8")

    metadata = parse_text_document(path)["metadata"]

    assert metadata["source_type"] == "kubernetes_manifest"
    assert metadata["yaml_apiVersion"] == "v1"
    assert metadata["yaml_kind"] == "Service"


def test_parse_terraform_extracts_resource_metadata(tmp_path):
    path = tmp_path / "main.tf"
    path.write_text('provider "aws" {}\nresource "aws_instance" "web" {}\nmodule "network" {}', encoding="utf-8")

    metadata = parse_text_document(path)["metadata"]

    assert metadata["terraform_resource_count"] == 1
    assert metadata["terraform_resources"] == ["aws_instance.web"]
    assert metadata["terraform_module_count"] == 1
    assert metadata["terraform_modules"] == ["network"]
    assert metadata["terraform_providers"] == ["aws"]


def test_parse_log_extracts_level_counts(tmp_path):
    path = tmp_path / "app.log"
    path.write_text("INFO started\nERROR failed\nWARN retry", encoding="utf-8")

    metadata = parse_text_document(path)["metadata"]

    assert metadata["log_level_counts"] == {"error": 1, "warn": 1, "info": 1}
