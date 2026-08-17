"""Run evidence and hashes (Parts 12.7, 25.1).

Task contract (Part 17.1):

    LAYER             all layers
    INPUTS            the completed run
    OUTPUTS           an immutable run_manifest.json
    VALIDATION        validates against contracts/run_manifest.schema.json
    FAILURE BEHAVIOR  A run without a manifest is not COMPLETE.
"""

from __future__ import annotations


def write_manifest(run_id: str):
    """Record what ran, what happened and what was PROVEN — including
    source hash before and after (Part 31.1).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
