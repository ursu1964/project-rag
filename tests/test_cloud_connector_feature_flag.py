import sys
import types

import pytest


def test_projectrag_cloud_connector_flag_defaults_false(monkeypatch):
    monkeypatch.delenv("PROJECTRAG_CLOUD_CONNECTORS_ENABLED", raising=False)
    from app.core.config import Settings

    assert Settings().enable_cloud_connectors is False


def test_projectrag_cloud_connector_flag_enables_connectors(monkeypatch):
    monkeypatch.setenv("PROJECTRAG_CLOUD_CONNECTORS_ENABLED", "true")
    from app.core.config import Settings

    assert Settings().enable_cloud_connectors is True


def test_aws_does_not_initialize_boto3_when_disabled(monkeypatch):
    from app.connectors.aws import inventory as aws_inv

    monkeypatch.setattr(aws_inv.settings, "enable_cloud_connectors", False)
    boto3 = types.SimpleNamespace(client=lambda *args, **kwargs: pytest.fail("boto3 initialized"))
    monkeypatch.setitem(sys.modules, "boto3", boto3)

    with pytest.raises(RuntimeError, match="AWS connector is disabled"):
        aws_inv.discover_inventory()


def test_azure_does_not_initialize_sdk_when_disabled(monkeypatch):
    from app.connectors.azure import inventory as az_inv

    monkeypatch.setattr(az_inv.settings, "enable_cloud_connectors", False)
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    azure_identity = types.SimpleNamespace(
        DefaultAzureCredential=lambda *args, **kwargs: pytest.fail("Azure credential initialized")
    )
    azure_resource = types.SimpleNamespace(
        ResourceManagementClient=lambda *args, **kwargs: pytest.fail("Azure client initialized")
    )
    monkeypatch.setitem(sys.modules, "azure.identity", azure_identity)
    monkeypatch.setitem(sys.modules, "azure.mgmt.resource", azure_resource)

    with pytest.raises(RuntimeError, match="Azure connector is disabled"):
        az_inv.discover_inventory()


def test_aws_initializes_lazily_when_enabled(monkeypatch):
    from app.connectors.aws import inventory as aws_inv

    calls = []
    monkeypatch.setattr(aws_inv.settings, "enable_cloud_connectors", True)
    monkeypatch.setitem(sys.modules, "boto3", types.SimpleNamespace(client=lambda name: calls.append(name) or object()))

    connector = aws_inv.AWSInventoryConnector()
    assert calls == []
    assert connector.discover_inventory() == []
    assert calls == ["sts"]


def test_azure_initializes_lazily_when_enabled(monkeypatch):
    from app.connectors.azure import inventory as az_inv

    calls = []
    monkeypatch.setattr(az_inv.settings, "enable_cloud_connectors", True)
    monkeypatch.setenv("AZURE_SUBSCRIPTION_ID", "sub-1")
    monkeypatch.setitem(
        sys.modules,
        "azure.identity",
        types.SimpleNamespace(DefaultAzureCredential=lambda: calls.append("credential") or object()),
    )
    monkeypatch.setitem(
        sys.modules,
        "azure.mgmt.resource",
        types.SimpleNamespace(
            ResourceManagementClient=lambda credential, subscription_id: calls.append(subscription_id) or object()
        ),
    )

    connector = az_inv.AzureInventoryConnector()
    assert calls == []
    assert connector.discover_inventory() == []
    assert calls == ["credential", "sub-1"]
