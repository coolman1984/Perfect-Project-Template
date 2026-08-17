"""Schema, type and distribution drift (Part 9.1).

Task contract (Part 17.1):

    LAYER             layer 4
    INPUTS            the current schema and recent history
    OUTPUTS           schema_diff.json plus a verdict
    VALIDATION        a moved column still works; a renamed critical column FAILS loudly
    FAILURE BEHAVIOR  Never fuzzy-match an important field. A required column that is
                      missing or renamed is a hard FAIL (Part 9.1).
"""

from __future__ import annotations


def compare_schema(run_id: str):
    """Column moved -> OK. New optional column -> WARNING. Required
    missing/renamed, or critical type changed -> FAIL.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
