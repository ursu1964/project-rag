import pytest

from app.connectors.azure.inventory import discover_inventory
from app.connectors.azure.models import AzureInventoryEntity


def test_discover_inventory_raises_when_connectors_disabled(monkeypatch):
    """discover_inventory must raise RuntimeError when ENABLE_CLOUD_CONNECTORS is false."""
    import app.connectors.azure.inventory as inv
    monkeypatch.setattr(inv.settings, "enable_cloud_connectors", False)
    with pytest.raises(RuntimeError, match="Azure connector is disabled"):
        discover_inventory()


def test_discover_inventory_returns_empty_list_when_connectors_enabled(monkeypatch):
    """discover_inventory must return a list (empty skeleton) when ENABLE_CLOUD_CONNECTORS is true."""
    import app.connectors.azure.inventory as inv
    monkeypatch.setattr(inv.settings, "enable_cloud_connectors", True)
    assert discover_inventory() == []


def test_azure_inventory_entity_defaults():
    entity = AzureInventoryEntity(name="vm1", entity_type="VirtualMachine")
    assert entity.provider == "azure"
    assert entity.region == "unknown"
    assert entity.metadata == {}
