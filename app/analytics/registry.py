"""The metric registry (Part 10.2).

Task contract (Part 17.1):

    LAYER             layer 8
    INPUTS            metrics.toml
    OUTPUTS           validated metric metadata and versions
    VALIDATION        the same KPI has exactly one formula everywhere
    FAILURE BEHAVIOR  An undefined or unapproved metric is refused, not approximated.
"""

from __future__ import annotations


def load_metrics(report_id: str):
    """Each record: meaning, SQL reference, source fields, grain, unit,
    null rule, zero rule, rounding, owner, version.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
