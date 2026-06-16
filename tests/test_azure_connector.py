from app.connectors.azure.inventory import discover_inventory
from app.connectors.azure.models import AzureInventoryEntity


def test_discover_inventory_skeleton_returns_empty_list():
    assert discover_inventory() == []


def test_azure_inventory_entity_defaults():
    entity = AzureInventoryEntity(name="vm1", entity_type="VirtualMachine")
    assert entity.provider == "azure"
    assert entity.region == "unknown"
    assert entity.metadata == {}
