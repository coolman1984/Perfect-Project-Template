"""Explicit value conversion (Constitution Parts 7.4, 7.6).

`Value2` is fast because it returns raw values, which makes conversion our
responsibility. Every rule here is deterministic: the same input produces the
same output, always. That is what makes reconciliation land on exactly zero
rather than approximately zero.

This module is pure logic with no environment dependency, so it is complete and
tested from day one.
"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

#: Excel error values. Count them; never silently convert them to zero (7.4).
EXCEL_ERRORS = frozenset({
    "#N/A", "#VALUE!", "#DIV/0!", "#REF!", "#NAME?", "#NUM!", "#NULL!",
})

#: Arabic-Indic and Eastern Arabic-Indic digits -> ASCII (Part 7.4).
_DIGIT_MAP = str.maketrans(
    "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹",
    "01234567890123456789",
)

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def normalize_column_name(raw: str, position: int = 0) -> str:
    """Deterministic column-name normalization (Part 7.6).

    1. trim spaces
    2. lowercase
    3. replace every run of non-letter/non-digit with a single "_"
    4. remove leading/trailing "_"
    5. if it starts with a digit, prefix "c_"
    6. if empty, use "col_<position>"

    Rule 7 (duplicate suffixes) needs the whole header row, so it lives in
    `normalize_header` below.

    >>> normalize_column_name("  Total Cost (USD) ")
    'total_cost_usd'
    """
    name = _NON_ALNUM.sub("_", str(raw).strip().lower()).strip("_")
    if not name:
        return f"col_{position}"
    if name[0].isdigit():
        return f"c_{name}"
    return name


def normalize_header(raw_names: list[str]) -> list[str]:
    """Normalize a whole header row, applying the duplicate rule (Part 7.6.7).

    Duplicates get deterministic `_2`, `_3` suffixes. A duplicate header is a
    warning, and the mapping must then choose the exact normalized field
    explicitly — never fuzzy-match an important column (Part 27.3).

    >>> normalize_header(["Part", "Part", "Qty"])
    ['part', 'part_2', 'qty']
    """
    seen: dict[str, int] = {}
    result: list[str] = []
    for position, raw in enumerate(raw_names):
        name = normalize_column_name(raw, position)
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        result.append(name)
    return result


def is_blank(value: object) -> bool:
    """Blank or whitespace-only becomes NULL (Part 7.4)."""
    return value is None or (isinstance(value, str) and not value.strip())


def is_excel_error(value: object) -> bool:
    return isinstance(value, str) and value.strip().upper() in EXCEL_ERRORS


def to_decimal(value: object) -> Decimal | None:
    """Parse money and quantities as DECIMAL, never floating point (Part 7.4).

    Handles the dirty-Excel reality: thousands separators, accounting negatives
    `(1,234)` -> `-1234`, trailing minus, percent-free text, and Arabic-Indic
    digits. Text that does not parse returns None and must be counted as a
    conversion failure — never coerced to zero.

    >>> to_decimal("(1,234.50)")
    Decimal('-1234.50')
    >>> to_decimal("١٢٣")
    Decimal('123')
    >>> to_decimal("n/a") is None
    True
    """
    if is_blank(value) or is_excel_error(value):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        # str() keeps the shortest round-trip form, avoiding 0.1 -> 0.1000000001.
        return Decimal(str(value))

    text = str(value).strip().translate(_DIGIT_MAP)
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative, text = True, text[1:-1].strip()
    if text.endswith("-"):
        negative, text = True, text[:-1].strip()

    text = text.replace(",", "").replace(" ", "").replace(" ", "")
    if not text or text in {"-", "."}:
        return None

    try:
        parsed = Decimal(text)
    except InvalidOperation:
        return None
    return -parsed if negative else parsed


def excel_serial_to_date(serial: float, date_system_1904: bool = False) -> tuple[int, int, int]:
    """Convert an Excel date serial to (year, month, day) (Part 7.4).

    Excel has two date systems and the workbook decides which one applies, so
    the caller must pass the workbook's setting rather than assume 1900
    (Part 27.1).

    The 1900 system deliberately reproduces Excel's non-existent 29 Feb 1900:
    serials above 59 are shifted by one day so that round-tripping matches what
    the user sees in the cell.

    Known limitation: because 29 Feb 1900 has no real calendar date, serials 59
    and 60 both map to 28 Feb 1900. Real business data does not contain 1900
    dates, and the quality gate's date-range check (Part 9.2) catches it if it
    somehow does. Do not "fix" this by inventing a date — the ambiguity is in
    Excel, not in this function.

    >>> excel_serial_to_date(1)
    (1900, 1, 1)
    >>> excel_serial_to_date(25569)   # the Unix epoch, a well-known anchor
    (1970, 1, 1)
    """
    from datetime import date, timedelta

    days = int(serial)
    if date_system_1904:
        origin = date(1904, 1, 1)
        result = origin + timedelta(days=days)
    else:
        origin = date(1899, 12, 31)
        if days > 59:
            days -= 1  # Excel's phantom 29 Feb 1900
        result = origin + timedelta(days=days)
    return result.year, result.month, result.day
