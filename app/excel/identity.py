"""Exact workbook and source matching (Part 27.1).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            a configured source and an open workbook
    OUTPUTS           a verified WorkbookIdentity
    VALIDATION        a similar-but-wrong workbook is rejected, not silently accepted
    FAILURE BEHAVIOR  Ambiguous match raises EXCEL_WORKBOOK_AMBIGUOUS and asks the user to
                      close the extra workbooks.

Why this is its own module, and why it is strict:

Attach mode looks at the workbooks the employee already has open and picks the
one we were configured to read. That is a moment where being approximately
right is worse than failing. `Q3 Orders.xlsx` and `Q3 Orders (1).xlsx` and
`Q3 Orders - Copy.xlsx` are all plausible neighbours of each other in a real
Downloads folder, and quietly extracting the wrong one produces a dashboard
that is confidently wrong — the failure mode this whole engine exists to
prevent (Part 7.1).

So matching is on the **canonical full path only**. Never the file name, never
a prefix, never a fuzzy score. If two open workbooks canonicalize to the same
path we refuse rather than choose.

This module deliberately contains no COM calls. A candidate is anything
carrying a `FullName` (the Excel COM `Workbook.FullName` property), which keeps
the rule that must be right testable on any machine, while the Windows-bound
session handling stays in `session.py`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from app.errors import AppError


def canonical_path(value: str | os.PathLike[str]) -> str:
    """Return the comparison form of a workbook path.

    Resolves `.`, `..` and symlinks, and normalises case on case-insensitive
    platforms only. Lower-casing unconditionally would wrongly equate two
    genuinely different files on Linux, where `Orders.xlsx` and `orders.xlsx`
    can coexist.
    """
    resolved = Path(os.path.expanduser(str(value)))
    try:
        resolved = resolved.resolve()
    except OSError:
        resolved = Path(os.path.abspath(str(resolved)))
    text = str(resolved)
    # os.path.normcase lower-cases on Windows and is a no-op on POSIX, which is
    # exactly the platform rule we want.
    return os.path.normcase(text)


def _candidate_path(candidate: Any) -> str | None:
    """Read the full path off a COM workbook, or off anything shaped like one."""
    for attribute in ("FullName", "full_name", "fullname", "path"):
        value = getattr(candidate, attribute, None)
        if isinstance(value, str) and value:
            return value
    return None


def matches(expected_path: str | os.PathLike[str], candidate: Any) -> bool:
    """True when `candidate` is exactly the configured workbook."""
    actual = _candidate_path(candidate)
    if actual is None:
        return False
    return canonical_path(actual) == canonical_path(expected_path)


def verify(expected_path: str, candidate: object):
    """Match the canonical full path and expected workbook identity.

    Accepts either a single candidate or an iterable of open workbooks. Returns
    the one candidate that is the configured workbook.

    Raises `EXCEL_WORKBOOK_AMBIGUOUS` when the open workbooks cannot identify a
    single answer — none matched, or more than one did. Both are ambiguity from
    the operator's point of view: in each case we cannot say which file the
    numbers would have come from.
    """
    if candidate is None:
        candidates: list[Any] = []
    elif isinstance(candidate, (str, bytes)) or not isinstance(
            candidate, Iterable):
        candidates = [candidate]
    else:
        candidates = list(candidate)

    expected = canonical_path(expected_path)
    matched = [item for item in candidates if matches(expected_path, item)]

    if len(matched) == 1:
        return matched[0]

    if not matched:
        near = sorted({
            Path(path).name
            for path in (_candidate_path(item) for item in candidates)
            if path
        })
        raise AppError(
            "EXCEL_WORKBOOK_AMBIGUOUS",
            support_detail=(
                f"no open workbook matches the configured path {expected!r}; "
                f"open workbooks: {near or 'none'}"),
            expected_path=expected,
            candidate_count=len(candidates),
        )

    raise AppError(
        "EXCEL_WORKBOOK_AMBIGUOUS",
        support_detail=(
            f"{len(matched)} open workbooks resolve to the configured path "
            f"{expected!r}; refusing to guess which one to read"),
        expected_path=expected,
        candidate_count=len(matched),
    )
