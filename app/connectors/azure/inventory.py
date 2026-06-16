"""Azure inventory discovery skeleton.

No credentials are read and no Azure API calls are performed yet.
"""

from __future__ import annotations

from app.connectors.azure.models import AzureInventoryEntity


def discover_inventory() -> list[dict]:
    """Return normalized Azure inventory entities.

    This is a skeleton for future Azure integration. It intentionally performs no
    cloud API calls and returns an empty inventory until credential-safe discovery
    is designed.
    """
    entities: list[AzureInventoryEntity] = []
    return [entity.model_dump() for entity in entities]
