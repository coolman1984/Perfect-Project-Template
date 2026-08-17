"""Exact workbook and source matching (Part 27.1).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            a configured source and an open workbook
    OUTPUTS           a verified WorkbookIdentity
    VALIDATION        a similar-but-wrong workbook is rejected, not silently accepted
    FAILURE BEHAVIOR  Ambiguous match raises EXCEL_WORKBOOK_AMBIGUOUS and asks the user to
                      close the extra workbooks.
"""

from __future__ import annotations


def verify(expected_path: str, candidate: object):
    """Match the canonical full path and expected workbook identity.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
