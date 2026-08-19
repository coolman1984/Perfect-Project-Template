"""Adaptive block extraction (Constitution Parts 7.2, 7.3).

`extractor.py` drives reads through a `read_block(first_row, last_row)` callable
and holds no COM import, so the arithmetic that decides how many rows are read —
and which columns they map to — is provable on any machine. The recorded block
requests are the assertion that matters most here: they are what proves reads
are rectangular rather than per-cell.
"""

from __future__ import annotations

import unittest

from app.errors import AppError
from app.excel import extractor
from app.excel.discovery import DataRegion
from app.excel.port import as_row_major

HEADER = ("production_date", "line", "order_number", "produced_qty")


def region(first_data_row=2, last_row=101, column_names=HEADER):
    return DataRegion(
        sheet_name="Raw Data",
        header_row=1,
        first_data_row=first_data_row,
        last_row=last_row,
        first_column=1,
        last_column=len(column_names),
        column_names=column_names,
        strategy="discover",
    )


class RecordingReader:
    """Returns synthetic rows and records every block it was asked for."""

    def __init__(self, columns=len(HEADER), rows_override=None):
        self.calls: list[tuple[int, int]] = []
        self._columns = columns
        self._rows_override = rows_override

    def __call__(self, first_row, last_row):
        self.calls.append((first_row, last_row))
        if self._rows_override is not None:
            return self._rows_override
        return tuple(
            tuple(f"r{row}c{column}" for column in range(1, self._columns + 1))
            for row in range(first_row, last_row + 1)
        )


class TestAsRowMajor(unittest.TestCase):
    """COM does not return a consistent shape; every caller depends on this."""

    def test_normalises_the_three_shapes_com_returns(self):
        self.assertEqual(as_row_major((("a", "b"), ("c", "d"))),
                         (("a", "b"), ("c", "d")))
        self.assertEqual(as_row_major("solo"), (("solo",),))   # single cell
        self.assertEqual(as_row_major(None), ())               # empty range
        self.assertEqual(as_row_major(("a", "b")), (("a", "b"),))  # one flat row

    def test_a_single_cell_does_not_become_a_row_of_characters(self):
        # The bug this guards: str is iterable, so a naive tuple() would turn
        # "solo" into four one-character columns.
        self.assertEqual(as_row_major("solo"), (("solo",),))


class TestChunkPlanning(unittest.TestCase):
    def test_covers_every_row_exactly_once_with_no_gaps_or_overlap(self):
        plans = extractor.plan_chunks(2, 101, 30)
        self.assertEqual([(p.first_row, p.last_row) for p in plans],
                         [(2, 31), (32, 61), (62, 91), (92, 101)])
        self.assertEqual(sum(p.row_count for p in plans), 100)
        self.assertEqual([p.chunk_number for p in plans], [1, 2, 3, 4])

    def test_an_empty_region_plans_no_chunks_rather_than_one_empty_chunk(self):
        # The control-total check distinguishes "no rows" from "a chunk of
        # nothing"; planning a phantom chunk would blur them.
        self.assertEqual(extractor.plan_chunks(2, 1, 30), ())

    def test_a_single_row_region_still_plans_one_chunk(self):
        plans = extractor.plan_chunks(2, 2, 30)
        self.assertEqual([(p.first_row, p.last_row) for p in plans], [(2, 2)])

    def test_rejects_a_nonsense_chunk_size(self):
        with self.assertRaises(ValueError):
            extractor.plan_chunks(2, 100, 0)

    def test_chunk_size_comes_from_cells_not_rows(self):
        wide = extractor.chunk_rows({"extraction": {"min_rows_per_chunk": 1}}, 272)
        narrow = extractor.chunk_rows({"extraction": {"min_rows_per_chunk": 1}}, 12)
        self.assertGreater(narrow, wide)


class TestProjection(unittest.TestCase):
    def test_maps_by_approved_name_not_position(self):
        """Part 7.2 — inserting a column upstream must not shift the mapping."""
        shifted = ("inserted_by_finance",) + HEADER
        names, indexes = extractor.projection(shifted, ["produced_qty", "line"])
        self.assertEqual(names, ("produced_qty", "line"))
        self.assertEqual(indexes, (4, 2))

    def test_projection_is_case_and_whitespace_insensitive(self):
        names, indexes = extractor.projection(
            ("  Produced_Qty  ", "line"), ["produced_qty"])
        self.assertEqual(indexes, (0,))
        self.assertEqual(names, ("produced_qty",))

    def test_an_absent_approved_column_fails_closed(self):
        with self.assertRaises(AppError) as caught:
            extractor.projection(HEADER, ["produced_qty", "scrap_qty"])
        self.assertEqual(caught.exception.code, "SCHEMA_REQUIRED_COLUMN_MISSING")
        self.assertIn("scrap_qty", caught.exception.support_detail)

    def test_no_projection_configured_keeps_every_column_in_order(self):
        names, indexes = extractor.projection(HEADER, [])
        self.assertEqual(names, HEADER)
        self.assertEqual(indexes, (0, 1, 2, 3))

    def test_short_rows_are_padded_rather_than_raising(self):
        # COM omits trailing empties on some ranges; a short row is missing
        # data, not a crash.
        self.assertEqual(
            extractor.project_rows((("a", "b"),), (0, 1, 2)),
            (("a", "b", None),))


class TestReadRegion(unittest.TestCase):
    def config(self, **extraction):
        base = {"target_cells_per_chunk": 120, "min_rows_per_chunk": 1,
                "max_rows_per_chunk": 10_000}
        base.update(extraction)
        return {"extraction": base}

    def test_reads_rectangular_blocks_not_cells(self):
        """The core performance rule, asserted on the calls actually made.

        100 rows x 4 columns is 400 cells. A per-cell implementation would make
        400 calls; this must make 4.
        """
        reader = RecordingReader()
        chunks = list(extractor.read_region(reader, region(), self.config()))

        self.assertEqual(len(reader.calls), 4)
        self.assertEqual(reader.calls, [(2, 31), (32, 61), (62, 91), (92, 101)])
        self.assertEqual(sum(chunk.row_count for chunk in chunks), 100)

    def test_every_source_row_survives_chunking(self):
        reader = RecordingReader()
        chunks = list(extractor.read_region(reader, region(), self.config()))
        first_cells = [row[0] for chunk in chunks for row in chunk.values]
        self.assertEqual(first_cells[0], "r2c1")
        self.assertEqual(first_cells[-1], "r101c1")
        self.assertEqual(len(first_cells), len(set(first_cells)), "rows duplicated")

    def test_projects_to_the_approved_columns_only(self):
        reader = RecordingReader()
        config = self.config()
        config["extraction"]["projected_columns"] = ["produced_qty", "line"]
        chunks = list(extractor.read_region(reader, region(), config))

        self.assertEqual(chunks[0].column_names, ("produced_qty", "line"))
        self.assertEqual(chunks[0].values[0], ("r2c4", "r2c2"))

    def test_a_short_read_is_caught_rather_than_silently_losing_rows(self):
        """Excel returning fewer rows than requested must not pass as success.

        Silent row loss here becomes an unexplained dip in a dashboard number
        weeks later, with no way back to the cause.
        """
        reader = RecordingReader(rows_override=(("a", "b", "c", "d"),))
        with self.assertRaises(AppError) as caught:
            list(extractor.read_region(reader, region(), self.config()))
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")
        self.assertIn("returned 1", caught.exception.support_detail)

    def test_a_com_failure_becomes_a_retryable_registry_code(self):
        def exploding(first_row, last_row):
            raise OSError("COM call failed")

        with self.assertRaises(AppError) as caught:
            list(extractor.read_region(exploding, region(), self.config()))
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")
        self.assertTrue(caught.exception.retryable)

    def test_an_empty_region_yields_nothing_and_reads_nothing(self):
        reader = RecordingReader()
        chunks = list(extractor.read_region(
            reader, region(first_data_row=2, last_row=1), self.config()))
        self.assertEqual(chunks, [])
        self.assertEqual(reader.calls, [])


class TestExtractRowCountGuard(unittest.TestCase):
    class Port:
        def __init__(self, chunks):
            self._chunks = chunks

        def chunks(self):
            return iter(self._chunks)

    def test_passes_chunks_through_when_the_counts_agree(self):
        reader = RecordingReader()
        produced = list(extractor.read_region(
            reader, region(), {"extraction": {"target_cells_per_chunk": 120,
                                              "min_rows_per_chunk": 1}}))
        streamed = list(extractor.extract(self.Port(produced), {}))
        self.assertEqual(sum(c.row_count for c in streamed), 100)

    def test_a_chunk_whose_bounds_lie_about_its_size_is_rejected(self):
        from app.excel.port import Chunk
        lying = Chunk(chunk_number=1, first_row=2, last_row=101,
                      column_names=HEADER, values=(("a", "b", "c", "d"),))
        with self.assertRaises(AppError) as caught:
            list(extractor.extract(self.Port([lying]), {}))
        self.assertEqual(caught.exception.code, "EXCEL_READ_FAILED")


if __name__ == "__main__":
    unittest.main()
