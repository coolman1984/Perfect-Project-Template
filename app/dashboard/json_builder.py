"""The validated dashboard package (Part 11.1).

Task contract (Part 17.1):

    LAYER             layer 9
    INPUTS            analytics + quality + lineage
    OUTPUTS           dashboard JSON validated against its schema
    VALIDATION        validates against contracts/dashboard.schema.json; size within limits
    FAILURE BEHAVIOR  A contract failure fails the run and leaves the previous dashboard
                      published.
"""

from __future__ import annotations


def build(run_id: str):
    """KPI values in tens, trend points in hundreds. The browser never sums
    a million rows. Set demo_data / unapproved_definitions watermarks
    when applicable (Parts 41.3, 44.3).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
