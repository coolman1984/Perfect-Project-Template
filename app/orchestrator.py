"""The full run order (Part 12.1).

Task contract (Part 17.1):

    LAYER             all layers
    INPUTS            a run request
    OUTPUTS           a COMPLETE, FAILED or CANCELLED run
    VALIDATION        the 26 steps execute in order and the quality gate halts step 14
    FAILURE BEHAVIOR  Any failure preserves trusted history and the last approved
                      dashboard (Part 12.6).
"""

from __future__ import annotations


def run(report_id: str, sources: object):
    """Owns ORDER only. Contains no business formula and no SQL.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
