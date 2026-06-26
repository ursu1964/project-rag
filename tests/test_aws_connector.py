import pytest

from app.connectors.aws.inventory import discover_inventory
from app.connectors.aws.models import AWSInventoryEntity


def test_discover_inventory_raises_when_connectors_disabled(monkeypatch):
    """discover_inventory must raise RuntimeError when ENABLE_CLOUD_CONNECTORS is false."""
    import app.connectors.aws.inventory as inv
    monkeypatch.setattr(inv.settings, "enable_cloud_connectors", False)
    with pytest.raises(RuntimeError, match="AWS connector is disabled"):
        discover_inventory()


def test_discover_inventory_returns_empty_list_when_connectors_enabled(monkeypatch):
    """discover_inventory must return a list (empty skeleton) when ENABLE_CLOUD_CONNECTORS is true."""
    import app.connectors.aws.inventory as inv
    monkeypatch.setattr(inv.settings, "enable_cloud_connectors", True)
    assert discover_inventory() == []


def test_aws_inventory_entity_defaults():
    entity = AWSInventoryEntity(name="i-123", entity_type="EC2Instance")
    assert entity.provider == "aws"
    assert entity.region == "unknown"
    assert entity.metadata == {}
