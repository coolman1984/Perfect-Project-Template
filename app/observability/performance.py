"""Measured performance evidence (Parts 14.1, 31.3).

Task contract (Part 17.1):

    LAYER             all layers
    INPUTS            run timings and resource use
    OUTPUTS           performance.json with real numbers
    VALIDATION        targets are set from measurement, never invented
    FAILURE BEHAVIOR  Missing measurements leave the benchmark blank; they are never
                      estimated.
"""

from __future__ import annotations


def record(run_id: str, **metrics: object):
    """Excel open time, rows/sec, chunk size, peak RAM, peak temp disk,
    stage timings, JSON and HTML size.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
