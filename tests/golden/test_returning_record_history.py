"""A record that comes back must come back (Part 8.3).

The scenario is ordinary, not exotic. An export runs with a filter set wrong,
or a system is mid-sync, and one purchase order line is missing from that
week's file. The deletion rule correctly marks it inactive. The next week's
export is complete again and the line is present, unchanged.

Before this was fixed, that line stayed inactive forever. It had been
deactivated, and the upsert only restored `is_active` for rows whose *content*
had changed — so a record that returned identical, which is the common case,
was silently excluded from every KPI, every control total and every export,
while `last_seen_run_id` kept advancing as though it were being observed
normally.

That is a silent drop, arriving through history rather than through ingest.
The population equation cannot catch it: the row was accepted at ingest and
disappears afterwards.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None

HEADER = ("po_number,po_line,posting_date,period,item_id,vendor_id,"
          "quantity,actual_unit_price,line_amount\n")
LINE_ONE = "PO-1,1,2026-08-03,2026-08,ITM-A,V-100,10,12.00,120.00\n"
LINE_TWO = "PO-2,1,2026-08-04,2026-08,ITM-A,V-100,5,12.00,60.00\n"

HISTORY = "analytics.history_reference_finance_ppv_purchases"


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestReturningRecordIsReactivated(unittest.TestCase):
    def setUp(self):
        from app.data.database import Database
        from app.excel.fixture_adapter import ACK_VARIABLE
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project
        from tools._common import REPO_ROOT

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.repo_root = REPO_ROOT
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

        self.complete = self.root / "purchases_complete.csv"
        self.complete.write_text(HEADER + LINE_ONE + LINE_TWO, encoding="utf-8")
        self.partial = self.root / "purchases_partial.csv"
        self.partial.write_text(HEADER + LINE_ONE, encoding="utf-8")

        self.contract = load_project(
            REPO_ROOT / "projects/_REFERENCE_FINANCE_PPV")
        self.database = Database(self.root / "project.duckdb")
        self.addCleanup(self.database.close)
        self.pipeline = ProjectPipeline(
            self.database, self.contract, application_version="test")
        self.pipeline.prepare()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _run(self, run_id: str, purchases: Path):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        files = {
            "purchases": purchases,
            "standard_cost": self.repo_root
            / "tests/fixtures/finance_ppv/standard_cost_p1.csv",
            "vendors": self.repo_root
            / "tests/fixtures/finance_ppv/vendors_p1.csv",
        }
        ports = {}
        for source_id, path in files.items():
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": run_id,
                "report_id": self.contract.project_id,
                "sheet": self.contract.source(source_id).sheet,
                "schema_version": "1",
                "extraction": {
                    "target_cells_per_chunk": 1000,
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 100,
                },
            })
            ports[source_id] = adapter
        outcome = self.pipeline.run(run_id, ports)
        self.assertTrue(outcome.succeeded, outcome.error_message)
        return outcome

    def _activity(self):
        return dict(self.database.query(
            f"SELECT po_number, is_active FROM {HISTORY} ORDER BY po_number"))

    def _active_spend(self):
        return self.database.scalar(
            f"SELECT SUM(line_amount) FROM {HISTORY} WHERE is_active")

    def test_a_record_that_reappears_unchanged_is_made_active_again(self):
        self._run("RET-1", self.complete)
        self.assertEqual(self._activity(), {"PO-1": True, "PO-2": True})

        self._run("RET-2", self.partial)
        self.assertEqual(
            self._activity(), {"PO-1": True, "PO-2": False},
            "a record missing from the source must be deactivated")

        self._run("RET-3", self.complete)
        self.assertEqual(
            self._activity(), {"PO-1": True, "PO-2": True},
            "a record present in the source again must be active again; "
            "leaving it inactive drops it from every KPI permanently")

    def test_totals_recover_when_the_record_returns(self):
        """The reason this matters: the money has to come back too."""
        self._run("RET-1", self.complete)
        full_total = self._active_spend()

        self._run("RET-2", self.partial)
        self.assertLess(self._active_spend(), full_total)

        self._run("RET-3", self.complete)
        self.assertEqual(
            self._active_spend(), full_total,
            "the trusted total must return to its correct value")

    def test_a_returning_record_keeps_its_original_first_seen_identity(self):
        """Reactivation is not re-creation.

        The record's history did not restart when the export glitched, so
        `first_seen_run_id` must still point at the run that first observed it.
        """
        self._run("RET-1", self.complete)
        first_seen = dict(self.database.query(
            f"SELECT po_number, first_seen_run_id FROM {HISTORY}"))
        self._run("RET-2", self.partial)
        self._run("RET-3", self.complete)

        self.assertEqual(
            dict(self.database.query(
                f"SELECT po_number, first_seen_run_id FROM {HISTORY}")),
            first_seen)
        self.assertEqual(
            dict(self.database.query(
                f"SELECT po_number, last_seen_run_id FROM {HISTORY}"))["PO-2"],
            "RET-3",
            "the returning record must record the run that saw it again")

    def test_no_duplicate_row_is_created_when_a_record_returns(self):
        """Reactivating must not race the insert path into a second row."""
        self._run("RET-1", self.complete)
        self._run("RET-2", self.partial)
        self._run("RET-3", self.complete)
        self.assertEqual(
            self.database.scalar(f"SELECT count(*) FROM {HISTORY}"), 2)
        self.assertEqual(
            self.database.scalar(
                f"SELECT count(DISTINCT business_key_hash) FROM {HISTORY}"), 2)

    def test_a_record_that_stays_missing_stays_inactive(self):
        """The fix must not resurrect records the source no longer carries."""
        self._run("RET-1", self.complete)
        self._run("RET-2", self.partial)
        self._run("RET-3", self.partial)
        self.assertEqual(self._activity(), {"PO-1": True, "PO-2": False})


if __name__ == "__main__":
    unittest.main()
