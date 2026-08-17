"""Standalone portable report (Part 11.2).

Task contract (Part 17.1):

    LAYER             layer 10
    INPUTS            dashboard JSON + template
    OUTPUTS           one self-contained HTML file
    VALIDATION        opens with no network and no JavaScript error
    FAILURE BEHAVIOR  A build failure leaves the last approved output in place.
"""

from __future__ import annotations


def build(dashboard_json: dict):
    """Embed HTML + CSS + JS + ECharts + the approved JSON. Zero remote
    references (Part 23.6).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
