"""The one shared calendar (Part 10.1).

Task contract (Part 17.1):

    LAYER             layer 8
    INPUTS            fiscal configuration
    OUTPUTS           day, week, month, quarter, year, fiscal period, working day, holiday
    VALIDATION        fiscal logic exists in exactly one place
    FAILURE BEHAVIOR  An undefined fiscal rule is PENDING_APPROVAL, never a guess.
"""

from __future__ import annotations


def build_calendar(start: str, end: str):
    """One shared table. Never re-implement week or fiscal logic per
    report.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
