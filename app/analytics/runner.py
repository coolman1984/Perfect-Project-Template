"""Executes approved SQL only (Part 10.2).

Task contract (Part 17.1):

    LAYER             layer 8
    INPUTS            trusted data + period
    OUTPUTS           KPI and chart tables
    VALIDATION        golden tests pass with known answers
    FAILURE BEHAVIOR  A failed calculation test fails the run and publishes nothing.
"""

from __future__ import annotations


def run_metric_sql(metric_id: str, period: str):
    """Python orchestrates, validates, converts and formats. It never
    contains a second hidden KPI formula.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
