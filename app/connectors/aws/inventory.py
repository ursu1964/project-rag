"""AWS inventory discovery skeleton.

No credentials are read and no AWS API calls are performed yet.
"""

from __future__ import annotations

from app.connectors.aws.models import AWSInventoryEntity


def discover_inventory() -> list[dict]:
    """Return normalized AWS inventory entities.

    This is a skeleton for future AWS integration. It intentionally performs no
    cloud API calls and returns an empty inventory until credential-safe discovery
    is designed.
    """
    entities: list[AWSInventoryEntity] = []
    return [entity.model_dump() for entity in entities]
