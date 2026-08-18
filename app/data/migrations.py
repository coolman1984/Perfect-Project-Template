"""Ordered, immutable schema migrations (Part 16.4).

Task contract (Part 17.1):

    LAYER             all data layers
    INPUTS            the migration folder
    OUTPUTS           an upgraded schema
    VALIDATION        sys.schema_migration records version, name, checksum and applied_at
    FAILURE BEHAVIOR  A failed migration rolls back, retains the prior version, and blocks
                      application start if the schema is incompatible (Part 27.5).
"""

from __future__ import annotations


def migrate(target_version: int | None = None):
    """Never change a production schema by hand.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
