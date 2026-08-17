"""Excel session ownership (Part 7.1).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            source config + open mode
    OUTPUTS           an open read-only workbook
    VALIDATION        source file unchanged; the correct workbook matched by exact full path
    FAILURE BEHAVIOR  Restore every changed Excel setting in `finally`. Close only the
                      process this run created — never all EXCEL.EXE (Part 23.5).
"""

from __future__ import annotations


def acquire(source_path: str, open_mode: str):
    """Open dedicated, or attach to the exact full path. Never close a
    workbook the user owns.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
