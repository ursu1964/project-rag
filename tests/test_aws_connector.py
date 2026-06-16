from app.connectors.aws.inventory import discover_inventory
from app.connectors.aws.models import AWSInventoryEntity


def test_discover_inventory_skeleton_returns_empty_list():
    assert discover_inventory() == []


def test_aws_inventory_entity_defaults():
    entity = AWSInventoryEntity(name="i-123", entity_type="EC2Instance")
    assert entity.provider == "aws"
    assert entity.region == "unknown"
    assert entity.metadata == {}
