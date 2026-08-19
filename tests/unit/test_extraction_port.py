"""Extraction port and adapters (Constitution Parts 7.3, 44)."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from app.errors import AppError
from app.excel.com_adapter import ComExtractionAdapter
from app.excel.fixture_adapter import FixtureAdapterNotAcknowledged, FixtureExtractionAdapter
from app.excel.port import ExtractionPort, rows_per_chunk

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "sample_production.csv"


class TestAdaptiveChunkSizing(unittest.TestCase):
    """Part 7.3 — chunks are sized in cells, not rows."""

    def test_documented_example(self):
        # 272 columns at a 250,000-cell target gives 919 rows.
        self.assertEqual(
            rows_per_chunk(target_cells=250_000, column_count=272,
                           minimum=250, maximum=10_000),
            919,
        )

    def test_narrow_file_gets_far_more_rows_than_a_wide_one(self):
        wide = rows_per_chunk(250_000, 272, 250, 10_000)
        narrow = rows_per_chunk(250_000, 12, 250, 10_000)
        self.assertGreater(narrow, wide)

    def test_clamps_to_maximum(self):
        # 250,000 / 12 = 20,833, above the 10,000 ceiling.
        self.assertEqual(rows_per_chunk(250_000, 12, 250, 10_000), 10_000)

    def test_clamps_to_minimum(self):
        # A very wide file would otherwise produce a uselessly small chunk.
        self.assertEqual(rows_per_chunk(1_000, 5_000, 250, 10_000), 250)

    def test_rejects_impossible_arguments(self):
        with self.assertRaises(ValueError):
            rows_per_chunk(250_000, 0, 250, 10_000)
        with self.assertRaises(ValueError):
            rows_per_chunk(250_000, 10, 10_000, 250)


class TestComAdapterContract(unittest.TestCase):
    def test_com_adapter_is_the_production_evidence_adapter(self):
        # Part 44.3 rule 3: only this adapter can satisfy the protected-file gate.
        self.assertTrue(ComExtractionAdapter.provides_production_evidence)

    def test_a_missing_source_file_fails_closed_with_a_registry_code(self):
        # Never a raw OSError: every failure the operator can see carries a
        # code from contracts/error_codes.json (Part 42.2).
        adapter = ComExtractionAdapter()
        with self.assertRaises(AppError) as caught:
            adapter.open("C:/nowhere/definitely-not-here.xlsx", {})
        self.assertEqual(caught.exception.code, "SRC_NOT_FOUND")

    def test_reading_before_open_is_a_programming_error_not_a_silent_empty(self):
        adapter = ComExtractionAdapter()
        with self.assertRaises(RuntimeError):
            adapter.chunks()
        with self.assertRaises(RuntimeError):
            adapter.lineage()

    def test_close_is_idempotent_and_safe_before_open(self):
        # close() runs from `finally` and from open()'s own failure path, so it
        # must never raise — including when there is nothing to release.
        adapter = ComExtractionAdapter()
        adapter.close()
        adapter.close()


class TestFixtureAdapter(unittest.TestCase):
    """Part 44.3 — dev/test only, never a fallback, never production evidence."""

    def setUp(self):
        os.environ["ADAPTER_FIXTURE_ACK"] = "1"

    def tearDown(self):
        os.environ.pop("ADAPTER_FIXTURE_ACK", None)

    def test_requires_explicit_acknowledgement(self):
        os.environ.pop("ADAPTER_FIXTURE_ACK", None)
        with self.assertRaises(FixtureAdapterNotAcknowledged):
            FixtureExtractionAdapter(FIXTURE)

    def test_never_provides_production_evidence(self):
        self.assertFalse(FixtureExtractionAdapter.provides_production_evidence)

    def test_satisfies_the_port_interface(self):
        self.assertTrue(issubclass(FixtureExtractionAdapter, ExtractionPort))

    def test_reads_the_fixture_and_reports_identity(self):
        adapter = FixtureExtractionAdapter(FIXTURE)
        identity = adapter.open(str(FIXTURE), {"report_id": "demo", "sheet": "Raw"})
        self.assertEqual(identity.sheet_name, "Raw")
        self.assertEqual(len(identity.file_hash), 64)
        self.assertGreater(identity.file_size, 0)

    def test_yields_all_rows_across_chunks(self):
        adapter = FixtureExtractionAdapter(FIXTURE)
        adapter.open(str(FIXTURE), {
            "report_id": "demo",
            "extraction": {"target_cells_per_chunk": 21,
                           "min_rows_per_chunk": 3,
                           "max_rows_per_chunk": 3},
        })
        chunks = list(adapter.chunks())
        self.assertGreater(len(chunks), 1, "the fixture should span several chunks")
        self.assertEqual(sum(chunk.row_count for chunk in chunks), 8)

    def test_chunk_row_numbers_are_one_based_and_skip_the_header(self):
        adapter = FixtureExtractionAdapter(FIXTURE)
        adapter.open(str(FIXTURE), {"report_id": "demo"})
        first = next(iter(adapter.chunks()))
        self.assertEqual(first.first_row, 2)

    def test_lineage_marks_output_as_demo_data(self):
        # Part 44.3 rule 2: fixture output is watermarked everywhere.
        adapter = FixtureExtractionAdapter(FIXTURE)
        adapter.open(str(FIXTURE), {"report_id": "demo", "run_id": "RUN-20260817-001"})
        lineage = adapter.lineage()
        self.assertEqual(lineage.extra.get("demo_data"), "true")
        self.assertEqual(lineage.run_id, "RUN-20260817-001")

    def test_control_totals_match_the_documented_fixture(self):
        # Guards the fixture itself: golden tests downstream depend on these.
        adapter = FixtureExtractionAdapter(FIXTURE)
        adapter.open(str(FIXTURE), {"report_id": "demo"})
        produced = defects = 0
        for chunk in adapter.chunks():
            produced_at = chunk.column_names.index("produced_qty")
            defect_at = chunk.column_names.index("defect_qty")
            for row in chunk.values:
                produced += int(row[produced_at])
                defects += int(row[defect_at])
        self.assertEqual(produced, 8060)
        self.assertEqual(defects, 100)


if __name__ == "__main__":
    unittest.main()
