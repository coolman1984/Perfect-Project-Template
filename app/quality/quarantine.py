"""Retained rejected rows (Part 9.5).

Task contract (Part 17.1):

    LAYER             layer 4
    INPUTS            rejected rows and their reasons
    OUTPUTS           quarantine_<report_id> entries
    VALIDATION        no row ever disappears silently
    FAILURE BEHAVIOR  Quarantine failure blocks the run: losing the audit trail of rejects
                      is worse than stopping.
"""

from __future__ import annotations


def quarantine_rows(run_id: str, rows: object, reason_code: str):
    """Store run_id, source_row_number, reason_code, reason_message and
    raw_values.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
