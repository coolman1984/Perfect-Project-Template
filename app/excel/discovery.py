"""Bounded structural discovery (Parts 7.2, 28.4).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            a workbook
    OUTPUTS           a profile of sheets, headers, tables and ranges
    VALIDATION        discovered bounds match the configured table or range
    FAILURE BEHAVIOR  Discovery is for initial setup only; results are written into config
                      and never re-guessed at runtime.

Four strategies, in the Part 7.2 priority order, selected by the `data_area`
string in `[excel]`:

    table:<name>    a ListObject. Excel maintains its bounds, so this is exact.
    range:<ref>     a defined name or an A1 reference. Exact, but static.
    header_columns  the configured header row, widened to its contiguous cells.
    discover        bounded walk from the header row. The last resort.

Note what is *not* in that list: `UsedRange`. Excel's used range remembers rows
that were deleted, so it routinely reports thousands of empty trailing rows —
and a "row count changed by 40%" quality failure caused by phantom rows is
indistinguishable, to the operator, from real missing data.

This module contains no COM calls and no COM imports (Part 44.2 permits them
only in `session.py` and `com_adapter.py`). It operates on anything carrying the
Excel object shape — `.Range`, `.ListObjects`, `.Names`, `.Value2` — which is
what lets the bounds rules be tested on any machine with plain fakes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.errors import AppError
from app.excel.port import as_row_major

#: Shared with `session` rather than imported from it, to keep this module free
#: of any dependency on the COM-owning layer.
XL_UP = -4162
SHEET_MAX_ROWS = 1_048_576
SHEET_MAX_COLUMNS = 16_384

STRATEGIES = ("table", "range", "header_columns", "discover")


@dataclass(frozen=True)
class DataRegion:
    """The exact rectangle to read, resolved once at setup (Part 7.2)."""

    sheet_name: str
    header_row: int
    first_data_row: int
    last_row: int
    first_column: int
    last_column: int
    column_names: tuple[str, ...]
    #: Which of the four strategies produced these bounds, recorded so the run
    #: manifest can say how the data area was determined rather than implying
    #: it was configured exactly.
    strategy: str

    @property
    def row_count(self) -> int:
        return max(0, self.last_row - self.first_data_row + 1)

    @property
    def column_count(self) -> int:
        return max(0, self.last_column - self.first_column + 1)


def column_letter(index: int) -> str:
    """1 -> 'A', 26 -> 'Z', 27 -> 'AA', 16384 -> 'XFD'."""
    if index < 1:
        raise ValueError(f"column index must be 1-based, got {index}")
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def column_index(letter: str) -> int:
    """'A' -> 1, 'AA' -> 27. The inverse of `column_letter`."""
    text = letter.strip().upper()
    if not text or not text.isalpha():
        raise ValueError(f"not a column letter: {letter!r}")
    result = 0
    for character in text:
        result = result * 26 + (ord(character) - ord("A") + 1)
    return result


def a1(first_row: int, first_column: int, last_row: int, last_column: int) -> str:
    """Build an absolute A1 block address, always multi-cell.

    Always a range with a colon, never a bare `A1`, because a single-cell read
    is the shape `GATE_NO_CELL_BY_CELL` forbids.
    """
    return (f"{column_letter(first_column)}{first_row}:"
            f"{column_letter(last_column)}{last_row}")


def parse_data_area(value: str) -> tuple[str, str]:
    """Split `"table:tblProduction"` into `("table", "tblProduction")`.

    `header_columns` and `discover` take no argument.
    """
    text = (value or "").strip()
    if not text:
        raise ValueError("data_area must be set (Part 7.2)")
    if text in ("header_columns", "discover"):
        return text, ""
    kind, separator, argument = text.partition(":")
    kind = kind.strip()
    if not separator or kind not in ("table", "range") or not argument.strip():
        raise ValueError(
            f"data_area must be 'table:<name>', 'range:<ref>', "
            f"'header_columns' or 'discover', got {value!r}")
    return kind, argument.strip()


def _bounds(com_range: Any) -> tuple[int, int, int, int]:
    """(first_row, first_column, last_row, last_column) of a COM range."""
    first_row = int(com_range.Row)
    first_column = int(com_range.Column)
    last_row = first_row + int(com_range.Rows.Count) - 1
    last_column = first_column + int(com_range.Columns.Count) - 1
    return first_row, first_column, last_row, last_column


def _read_header(worksheet: Any, row: int, first_column: int,
                 last_column: int) -> tuple[str, ...]:
    """Read one header row as a single block and trim trailing blanks."""
    address = a1(row, first_column, row, last_column)
    rows = as_row_major(worksheet.Range(address).Value2)
    if not rows:
        return ()
    names = [("" if cell is None else str(cell).strip()) for cell in rows[0]]
    while names and not names[-1]:
        names.pop()
    return tuple(names)


def _last_data_row(worksheet: Any, column: int, header_row: int) -> int:
    """Walk up from the bottom of the sheet to the last non-empty cell.

    `End(xlUp)` from row 1,048,576 is the one bounds probe that reflects what is
    actually in the column, rather than what Excel remembers having been there.
    """
    anchor = f"{column_letter(column)}{SHEET_MAX_ROWS}"
    try:
        found = int(worksheet.Range(anchor).End(XL_UP).Row)
    except Exception as exc:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"could not determine the last row of column "
                f"{column_letter(column)}: {exc}"),
        ) from exc
    return max(found, header_row)


def _worksheet(workbook: Any, sheet_name: str) -> Any:
    try:
        return workbook.Worksheets(sheet_name)
    except Exception as exc:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"sheet {sheet_name!r} was not found in the workbook. The sheet "
                f"is named explicitly in config and never guessed (Part 7.5)."),
            sheet=sheet_name,
        ) from exc


def _resolve_table(workbook: Any, worksheet: Any,
                   name: str) -> tuple[int, int, int, int]:
    try:
        table = worksheet.ListObjects(name)
    except Exception as exc:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"table {name!r} was not found on the configured sheet. "
                f"data_area names it explicitly (Part 7.2)."),
            table=name,
        ) from exc
    return _bounds(table.Range)


def _resolve_range(workbook: Any, worksheet: Any,
                   reference: str) -> tuple[int, int, int, int]:
    """A defined name first, then a literal A1 reference."""
    try:
        return _bounds(workbook.Names(reference).RefersToRange)
    except Exception:
        pass
    try:
        return _bounds(worksheet.Range(reference))
    except Exception as exc:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"{reference!r} is neither a defined name nor a valid range "
                f"reference on the configured sheet"),
            reference=reference,
        ) from exc


def locate(workbook: Any, config: dict[str, Any]) -> DataRegion:
    """Resolve the configured data area to exact bounds.

    Runtime path. Validates that what config names still exists, and fails
    closed when it does not — a moved table is a configuration change that a
    human must approve, never something to re-guess mid-run.
    """
    excel_config = dict(config.get("excel", config))
    sheet_name = str(excel_config.get("sheet", "")).strip()
    if not sheet_name:
        raise ValueError("excel.sheet must be set; sheets are never guessed (Part 7.5)")

    header_row = int(excel_config.get("header_row", 1))
    first_data_row = int(excel_config.get("data_start_row", header_row + 1))
    kind, argument = parse_data_area(str(excel_config.get("data_area", "discover")))

    worksheet = _worksheet(workbook, sheet_name)

    if kind == "table":
        first_row, first_column, last_row, last_column = _resolve_table(
            workbook, worksheet, argument)
        # A ListObject's range includes its header row, so the header is its
        # first row and the body starts one below.
        header_row = first_row
        first_data_row = first_row + 1
        strategy = "table"
    elif kind == "range":
        first_row, first_column, last_row, last_column = _resolve_range(
            workbook, worksheet, argument)
        header_row = first_row
        first_data_row = first_row + 1
        strategy = "range"
    else:
        first_column = 1
        header_names = _read_header(worksheet, header_row, 1, SHEET_MAX_COLUMNS)
        if not header_names:
            raise AppError(
                "EXCEL_READ_FAILED",
                support_detail=(
                    f"header row {header_row} of sheet {sheet_name!r} is empty, "
                    f"so no column names could be read"),
                sheet=sheet_name,
            )
        last_column = len(header_names)
        last_row = _last_data_row(worksheet, first_column, header_row)
        strategy = kind

    column_names = _read_header(worksheet, header_row, first_column, last_column)
    if not column_names:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"no column names found in row {header_row} of sheet "
                f"{sheet_name!r}"),
            sheet=sheet_name,
        )

    return DataRegion(
        sheet_name=sheet_name,
        header_row=header_row,
        first_data_row=max(first_data_row, header_row + 1),
        last_row=last_row,
        first_column=first_column,
        last_column=first_column + len(column_names) - 1,
        column_names=column_names,
        strategy=strategy,
    )


def profile(workbook: Any) -> dict[str, Any]:
    """Describe a workbook's structure for initial setup (Part 28.4).

    Setup-time only. Its output is written into config and reviewed by a human;
    the runtime path is `locate`, which reads that config and never re-guesses.

    Deliberately structural: sheet names, table names, defined names and header
    text only. No data rows are sampled, which keeps profiling compatible with
    the metadata-only AI profiling default in `policy/security_policy.toml`.
    """
    sheets: list[dict[str, Any]] = []
    for worksheet in workbook.Worksheets:
        entry: dict[str, Any] = {
            "name": str(worksheet.Name),
            "tables": [],
            "header_candidates": [],
        }
        try:
            entry["tables"] = [
                {"name": str(table.Name), "address": str(table.Range.Address)}
                for table in worksheet.ListObjects
            ]
        except Exception:
            entry["tables"] = []

        # Row 1 is only a candidate, never an assumption — plenty of real
        # workbooks open with a title banner above the true header.
        try:
            entry["header_candidates"] = list(
                _read_header(worksheet, 1, 1, SHEET_MAX_COLUMNS))
        except Exception:
            entry["header_candidates"] = []
        sheets.append(entry)

    try:
        defined_names = [str(name.Name) for name in workbook.Names]
    except Exception:
        defined_names = []

    return {"sheets": sheets, "defined_names": defined_names}
