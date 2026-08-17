"""Bounded structural discovery (Parts 7.2, 28.4).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            a workbook
    OUTPUTS           a profile of sheets, headers, tables and ranges
    VALIDATION        discovered bounds match the configured table or range
    FAILURE BEHAVIOR  Discovery is for initial setup only; results are written into config
                      and never re-guessed at runtime.
"""

from __future__ import annotations


def profile(workbook: object):
    """Find data by table -> named range -> header row -> bounded
    discovery. Never trust UsedRange (Part 7.2).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
