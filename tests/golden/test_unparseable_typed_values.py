"""A value that cannot be read must be quarantined, whatever its type
(Part 9.5).

An unparseable *number* was always rejected to quarantine. An unparseable
*date* was not: it became NULL, the row was accepted into trusted history, no
quarantine entry was written and no quality check mentioned it. The money on
that row still reached the KPI, so the totals looked right while the record
had quietly lost its date.

That is worst when the column is the source's declared `event_date`, because
the lookback window for corrections, the replace-period boundary check and the
Parquet archive partitioning all read it — each of them would have been working
from a NULL nobody was told about.

"Nothing is silently dropped" has to cover a field, not only a row.
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
GOOD = "PO-2,1,2026-08-04,2026-08,ITM-A,V-100,5,12.00,60.00\n"

HISTORY = "analytics.history_reference_finance_ppv_purchases"


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestUnparseableTypedValues(unittest.TestCase):
    def setUp(self):
        from app.excel.fixture_adapter import ACK_VARIABLE
        from tools._common import REPO_ROOT

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.repo_root = REPO_ROOT
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _run(self, purchases_body: str, *, standard_cost: str | None = None):
        from app.data.database import Database
        from app.excel.fixture_adapter import FixtureExtractionAdapter
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        purchases = self.root / "purchases.csv"
        purchases.write_text(HEADER + purchases_body, encoding="utf-8")

        if standard_cost is None:
            cost_path = (self.repo_root
                         / "tests/fixtures/finance_ppv/standard_cost_p1.csv")
        else:
            cost_path = self.root / "standard_cost.csv"
            cost_path.write_text(standard_cost, encoding="utf-8")

        contract = load_project(
            self.repo_root / "projects/_REFERENCE_FINANCE_PPV")
        database = Database(self.root / "project.duckdb")
        self.addCleanup(database.close)
        pipeline = ProjectPipeline(
            database, contract, application_version="test")
        pipeline.prepare()

        files = {
            "purchases": purchases,
            "standard_cost": cost_path,
            "vendors": self.repo_root
            / "tests/fixtures/finance_ppv/vendors_p1.csv",
        }
        ports = {}
        for source_id, path in files.items():
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": "TYPED",
                "report_id": contract.project_id,
                "sheet": contract.source(source_id).sheet,
                "schema_version": "1",
                "extraction": {
                    "target_cells_per_chunk": 1000,
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 100,
                },
            })
            ports[source_id] = adapter
        outcome = pipeline.run("TYPED", ports)
        return outcome, database

    def _reasons(self, database):
        return dict(database.query(
            "SELECT reason_code, count(*) FROM quality.quarantine "
            "WHERE run_id = 'TYPED' GROUP BY reason_code"))

    def test_an_unparseable_date_is_quarantined_not_silently_nulled(self):
        outcome, database = self._run(
            "PO-1,1,not-a-date,2026-08,ITM-A,V-100,10,12.00,120.00\n" + GOOD)

        self.assertEqual(self._reasons(database).get("UNPARSEABLE_DATE"), 1)
        self.assertEqual(outcome.sources["purchases"].rows_rejected, 1)

    def test_no_null_event_date_ever_reaches_trusted_history(self):
        """The event date drives lookback, replace-period and archiving."""
        _, database = self._run(
            "PO-1,1,not-a-date,2026-08,ITM-A,V-100,10,12.00,120.00\n" + GOOD)

        self.assertEqual(
            database.scalar(
                f"SELECT count(*) FROM {HISTORY} WHERE posting_date IS NULL"),
            0)
        self.assertEqual(
            database.query(f"SELECT po_number FROM {HISTORY}"), [("PO-2",)])

    def test_the_rejected_row_does_not_contribute_to_the_trusted_total(self):
        """Previously the row was excluded from nothing: its money counted
        while its date was gone."""
        _, database = self._run(
            "PO-1,1,not-a-date,2026-08,ITM-A,V-100,10,12.00,120.00\n" + GOOD)

        self.assertEqual(
            database.scalar(
                f"SELECT SUM(line_amount) FROM {HISTORY} WHERE is_active"),
            60)

    def test_an_unparseable_integer_is_still_quarantined(self):
        """The existing numeric behaviour must be unchanged."""
        _, database = self._run(
            "PO-1,x,2026-08-03,2026-08,ITM-A,V-100,10,12.00,120.00\n" + GOOD)
        self.assertEqual(self._reasons(database).get("UNPARSEABLE_NUMBER"), 1)

    def test_several_bad_types_in_one_file_are_each_reported(self):
        outcome, database = self._run(
            "PO-1,1,not-a-date,2026-08,ITM-A,V-100,10,12.00,120.00\n"
            "PO-3,x,2026-08-05,2026-08,ITM-A,V-100,3,12.00,36.00\n" + GOOD)
        reasons = self._reasons(database)
        self.assertEqual(reasons.get("UNPARSEABLE_DATE"), 1)
        self.assertEqual(reasons.get("UNPARSEABLE_NUMBER"), 1)
        self.assertEqual(outcome.sources["purchases"].rows_rejected, 2)

    def test_a_blank_date_is_still_accepted(self):
        """Only an unreadable value is rejected. Blank is a legitimate absence
        and rejecting it would break every optional date column."""
        outcome, database = self._run(
            GOOD,
            standard_cost=(
                "item_id,item_name,category,standard_unit_cost,"
                "cost_effective_date\n"
                "ITM-A,Widget A,Components,12.00,\n"
                "ITM-B,Widget B,Packaging,8.50,2026-07-01\n"))

        self.assertTrue(outcome.succeeded, outcome.error_message)
        self.assertEqual(outcome.sources["standard_cost"].rows_rejected, 0)
        self.assertEqual(self._reasons(database), {})

    def test_the_population_equation_still_balances(self):
        """Part 25.3: every source row is accounted for."""
        outcome, _ = self._run(
            "PO-1,1,not-a-date,2026-08,ITM-A,V-100,10,12.00,120.00\n" + GOOD)
        source = outcome.sources["purchases"]
        accepted = (source.rows_extracted - source.rows_rejected
                    - source.rows_filtered)
        self.assertEqual(
            source.rows_extracted,
            accepted + source.rows_rejected + source.rows_filtered)
        self.assertEqual(source.rows_extracted, 2)
        self.assertEqual(accepted, 1)


if __name__ == "__main__":
    unittest.main()
