"""Automated dashboard verification (Parts 11.5, 26.10).

Task contract (Part 17.1):

    LAYER             layer 10
    INPUTS            a built dashboard
    OUTPUTS           a verification verdict and evidence
    VALIDATION        zero network requests, zero JS errors, KPIs present, filters work, light/dark/RTL/print all render
    FAILURE BEHAVIOR  If verification fails, the run is FAILED and the previous dashboard
                      stays in place. Publication is atomic.
"""

from __future__ import annotations


def verify(html_path: str):
    """Headless browser check. Block and detect every unexpected network
    request.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
