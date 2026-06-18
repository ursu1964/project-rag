from app.digital_twin.models import DigitalTwinSnapshot
from app.discovery.entity_types import ENTITY_TYPES, is_supported_entity_type


def test_supported_entity_types_include_required_values():
    required = {
        "DockerContainer",
        "VM",
        "Host",
        "Network",
        "Subnet",
        "Database",
        "Service",
        "API",
        "Cluster",
        "Namespace",
        "Pod",
    }

    assert required.issubset(ENTITY_TYPES)
    assert is_supported_entity_type("DockerContainer") is True
    assert is_supported_entity_type("Unknown") is False


def test_digital_twin_snapshot_defaults():
    snapshot = DigitalTwinSnapshot(name="local")

    assert snapshot.name == "local"
    assert snapshot.entities == []
    assert snapshot.relationships == []
    assert snapshot.metadata == {}
