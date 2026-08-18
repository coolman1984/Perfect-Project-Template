"""Raw chunk writer and checkpoints (Part 6 layer 3).

Task contract (Part 17.1):

    LAYER             layer 3
    INPUTS            one chunk
    OUTPUTS           raw rows plus a durable checkpoint
    VALIDATION        the run is restartable after a crash
    FAILURE BEHAVIOR  A crash mid-chunk resumes from the last completed checkpoint; it
                      never duplicates staged rows.
"""

from __future__ import annotations


def write_chunk(chunk: object, lineage: object):
    """Stamp every row with the Part 7.7 lineage fields, then checkpoint.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
