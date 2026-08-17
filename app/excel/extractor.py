"""Adaptive block extraction (Part 7.3).

Task contract (Part 17.1):

    LAYER             layer 2
    INPUTS            session + mapping + chunk policy
    OUTPUTS           a stream of chunks
    VALIDATION        row count equals expected; no cell-by-cell call exists
    FAILURE BEHAVIOR  A failed chunk preserves completed checkpoints and requests a retry;
                      partial data never reaches trusted history.
"""

from __future__ import annotations


def extract(port: object, config: dict):
    """Size chunks in cells, not rows. Write each chunk straight to
    staging; never hold the whole file in memory.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
