"""Bounded structural discovery (Constitution Part 7.2).

These tests run on any machine. `discovery.py` holds no COM import by design
(Part 44.2), so the bounds rules — the ones that silently corrupt a dashboard
when they are wrong — are exercised here against plain fakes rather than only on
the authorized Windows box.

The fakes below implement just the Excel object surface `discovery` touches:
`Worksheets`, `Range`, `ListObjects`, `Names`, `Value2`, `End`.
"""

from __future__ import annotations

import re
import unittest

from app.errors import AppError
from app.excel import discovery

ADDRESS = re.compile(r"^([A-Z]+)(\d+)(?::([A-Z]+)(\d+))?$")


class FakeCount:
    def __init__(self, count: int) -> None:
        self.Count = count


class FakeCollection:
    """An Excel collection: callable by name *and* iterable, as COM ones are."""

    def __init__(self, items):
        self._items = list(items)

    def __call__(self, name=None):
        if name is None:
            return self
        for item in self._items:
            if item.Name == name:
                return item
        raise ValueError(f"no such item: {name}")

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class FakeName:
    def __init__(self, name, com_range):
        self.Name = name
        self.RefersToRange = com_range


class FakeRange:
    def __init__(self, sheet, first_row, first_column, last_row, last_column):
        self._sheet = sheet
        self.Row = first_row
        self.Column = first_column
        self._last_row = last_row
        self._last_column = last_column
        self.Rows = FakeCount(last_row - first_row + 1)
        self.Columns = FakeCount(last_column - first_column + 1)

    @property
    def Address(self) -> str:
        return discovery.a1(self.Row, self.Column, self._last_row, self._last_column)

    @property
    def Value2(self):
        return tuple(
            tuple(self._sheet.cell(row, column)
                  for column in range(self.Column, self._last_column + 1))
            for row in range(self.Row, self._last_row + 1)
        )

    def End(self, direction):
        if direction != discovery.XL_UP:
            raise NotImplementedError(direction)
        populated = [
            row for (row, column), value in self._sheet.grid.items()
            if column == self.Column and value not in (None, "") and row <= self.Row
        ]
        found = max(populated, default=1)
        return FakeRange(self._sheet, found, self.Column, found, self.Column)


class FakeTable:
    def __init__(self, name, com_range):
        self.Name = name
        self.Range = com_range


class FakeSheet:
    """A sparse grid keyed by (row, column), both 1-based."""

    def __init__(self, name, rows, first_row=1, first_column=1):
        self.Name = name
        self.grid: dict[tuple[int, int], object] = {}
        for row_offset, row in enumerate(rows):
            for column_offset, value in enumerate(row):
                if value in (None, ""):
                    continue
                self.grid[(first_row + row_offset,
                           first_column + column_offset)] = value
        self._tables: dict[str, FakeTable] = {}

    def cell(self, row, column):
        return self.grid.get((row, column))

    def add_table(self, name, first_row, first_column, last_row, last_column):
        self._tables[name] = FakeTable(
            name, FakeRange(self, first_row, first_column, last_row, last_column))

    def Range(self, address):
        match = ADDRESS.match(address)
        if not match:
            raise ValueError(f"fake sheet got an unparseable address: {address!r}")
        first_column, first_row, last_column, last_row = match.groups()
        # A single-cell address is legal as an `End()` anchor — it is only a
        # single-cell *read* that the per-cell rule forbids.
        return FakeRange(
            self,
            int(first_row), discovery.column_index(first_column),
            int(last_row or first_row),
            discovery.column_index(last_column or first_column))

    @property
    def ListObjects(self):
        return FakeCollection(self._tables.values())


class FakeWorkbook:
    def __init__(self, sheets, names=None):
        self._sheets = list(sheets)
        self._names = [FakeName(name, com_range)
                       for name, com_range in (names or {}).items()]

    @property
    def Worksheets(self):
        return FakeCollection(self._sheets)

    @property
    def Names(self):
        return FakeCollection(self._names)


HEADER = ["production_date", "line", "produced_qty"]
ROWS = [
    HEADER,
    ["2026-01-01", "L1", 100],
    ["2026-01-02", "L2", 200],
    ["2026-01-03", "L1", 300],
]


def workbook_with_data(sheet_name="Raw Data"):
    return FakeWorkbook([FakeSheet(sheet_name, ROWS)])


class TestColumnLetters(unittest.TestCase):
    def test_round_trips_across_the_boundaries(self):
        for index, letter in ((1, "A"), (26, "Z"), (27, "AA"),
                              (52, "AZ"), (703, "AAA"), (16384, "XFD")):
            self.assertEqual(discovery.column_letter(index), letter)
            self.assertEqual(discovery.column_index(letter), index)

    def test_rejects_a_zero_or_negative_index(self):
        with self.assertRaises(ValueError):
            discovery.column_letter(0)

    def test_block_addresses_are_never_single_cells(self):
        # A bare `A1` is the shape GATE_NO_CELL_BY_CELL forbids.
        self.assertIn(":", discovery.a1(1, 1, 1, 1))
        self.assertEqual(discovery.a1(2, 1, 100, 3), "A2:C100")


class TestParseDataArea(unittest.TestCase):
    def test_parses_each_supported_form(self):
        self.assertEqual(discovery.parse_data_area("table:tblProduction"),
                         ("table", "tblProduction"))
        self.assertEqual(discovery.parse_data_area("range:MyRange"),
                         ("range", "MyRange"))
        self.assertEqual(discovery.parse_data_area("discover"), ("discover", ""))
        self.assertEqual(discovery.parse_data_area("header_columns"),
                         ("header_columns", ""))

    def test_rejects_unknown_or_empty_forms(self):
        for bad in ("", "   ", "usedrange", "table:", "sheet:Raw"):
            with self.assertRaises(ValueError, msg=bad):
                discovery.parse_data_area(bad)


class TestLocate(unittest.TestCase):
    def config(self, **overrides):
        excel = {"sheet": "Raw Data", "header_row": 1, "data_start_row": 2,
                 "data_area": "discover"}
        excel.update(overrides)
        return {"excel": excel}

    def test_discovers_bounds_without_using_usedrange(self):
        region = discovery.locate(workbook_with_data(), self.config())
        self.assertEqual(region.column_names, tuple(HEADER))
        self.assertEqual(region.header_row, 1)
        self.assertEqual(region.first_data_row, 2)
        self.assertEqual(region.last_row, 4)
        self.assertEqual(region.row_count, 3)
        self.assertEqual(region.column_count, 3)

    def test_trailing_blank_rows_do_not_extend_the_region(self):
        """The phantom-row case UsedRange gets wrong.

        Excel would report a used range reaching row 900 here; walking up from
        the bottom finds the last row that actually holds data.
        """
        sheet = FakeSheet("Raw Data", ROWS)
        # Simulate Excel's memory of deleted rows: a formatted-but-empty cell.
        sheet.grid[(900, 2)] = ""
        region = discovery.locate(FakeWorkbook([sheet]), self.config())
        self.assertEqual(region.last_row, 4)

    def test_a_table_defines_its_own_bounds(self):
        sheet = FakeSheet("Raw Data", ROWS)
        sheet.add_table("tblProduction", 1, 1, 4, 3)
        region = discovery.locate(
            FakeWorkbook([sheet]), self.config(data_area="table:tblProduction"))
        self.assertEqual(region.strategy, "table")
        self.assertEqual(region.header_row, 1)
        self.assertEqual(region.first_data_row, 2)
        self.assertEqual(region.last_row, 4)
        self.assertEqual(region.column_names, tuple(HEADER))

    def test_a_defined_name_defines_its_own_bounds(self):
        sheet = FakeSheet("Raw Data", ROWS)
        workbook = FakeWorkbook(
            [sheet], names={"ProductionData": FakeRange(sheet, 1, 1, 4, 3)})
        region = discovery.locate(
            workbook, self.config(data_area="range:ProductionData"))
        self.assertEqual(region.strategy, "range")
        self.assertEqual(region.last_row, 4)

    def test_a_missing_table_fails_closed_rather_than_falling_back(self):
        # Silently re-guessing a moved table is how the wrong rectangle gets
        # extracted and reported with full confidence.
        with self.assertRaises(AppError) as caught:
            discovery.locate(workbook_with_data(),
                             self.config(data_area="table:tblGone"))
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")

    def test_a_missing_sheet_fails_closed(self):
        with self.assertRaises(AppError) as caught:
            discovery.locate(workbook_with_data(), self.config(sheet="Nope"))
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")

    def test_an_unnamed_sheet_is_rejected_never_guessed(self):
        # Part 7.5: "read all sheets" is not a supported behaviour.
        with self.assertRaises(ValueError):
            discovery.locate(workbook_with_data(), {"excel": {"sheet": ""}})

    def test_an_empty_header_row_is_an_error_not_an_empty_extract(self):
        sheet = FakeSheet("Raw Data", [["", "", ""], ["a", "b", "c"]])
        with self.assertRaises(AppError) as caught:
            discovery.locate(FakeWorkbook([sheet]), self.config())
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")

    def test_a_header_banner_above_the_real_header_is_honoured(self):
        """Real workbooks routinely open with a title row."""
        sheet = FakeSheet("Raw Data", [["Production Report", "", ""]] + ROWS)
        region = discovery.locate(
            FakeWorkbook([sheet]), self.config(header_row=2, data_start_row=3))
        self.assertEqual(region.column_names, tuple(HEADER))
        self.assertEqual(region.first_data_row, 3)
        self.assertEqual(region.last_row, 5)


class TestProfile(unittest.TestCase):
    def test_reports_structure_without_sampling_data_rows(self):
        sheet = FakeSheet("Raw Data", ROWS)
        sheet.add_table("tblProduction", 1, 1, 4, 3)
        result = discovery.profile(FakeWorkbook([sheet]))

        self.assertEqual(len(result["sheets"]), 1)
        entry = result["sheets"][0]
        self.assertEqual(entry["name"], "Raw Data")
        self.assertEqual([t["name"] for t in entry["tables"]], ["tblProduction"])
        self.assertEqual(entry["header_candidates"], HEADER)

        # Metadata only: no business row reaches the profile (security policy
        # default is metadata-only AI profiling).
        flattened = repr(result)
        self.assertNotIn("2026-01-01", flattened)
        self.assertNotIn("300", flattened)


if __name__ == "__main__":
    unittest.main()
