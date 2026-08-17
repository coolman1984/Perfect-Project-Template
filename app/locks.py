"""One writer, with stale-lock recovery (Part 27.5).

Task contract (Part 17.1):

    LAYER             orchestrator
    INPUTS            a report id
    OUTPUTS           an exclusive report lock
    VALIDATION        a second run waits or exits clearly; it never writes concurrently
    FAILURE BEHAVIOR  A stale lock from a crashed run is detected and recovered; a live
                      lock is never stolen.
"""

from __future__ import annotations


def acquire_report_lock(report_id: str):
    """Raises REPORT_LOCKED when another run holds it.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
