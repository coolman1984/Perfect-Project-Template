"""Control totals and the population equation (Parts 9.4, 25.3).

Task contract (Part 17.1):

    LAYER             layer 4
    INPUTS            source totals and database totals
    OUTPUTS           a difference that must be exactly zero
    VALIDATION        difference == 0 at the defined decimal precision, not 'approximately'
    FAILURE BEHAVIOR  Any non-zero difference fails the run and leaves history untouched.
                      This is the check that turns a nice dashboard into a number you can
                      present to management.
"""

from __future__ import annotations


def check_control_total(run_id: str, column: str):
    """Exact equality at the defined precision.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )

def check_population(run_id: str):
    """source_rows = accepted + rejected + intentionally_filtered. Filters
    are named evidence, never balancing figures.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
