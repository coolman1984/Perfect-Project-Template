"""Reference B on the project-centric contract (V10 build program S4).

`tests/golden/test_second_report_pipeline.py` already proves the Maintenance
downtime workflow through the legacy report contract
(`app.pipeline.Pipeline` + `reports/line_downtime`). This file proves the SAME
hand-checked numbers run correctly through the project-centric contract
(`app.project_pipeline.ProjectPipeline` +
`projects/_REFERENCE_MAINTENANCE_DOWNTIME`) — the S4 exit gate: "References A,
B and C all execute through the project pipeline."
"""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestMaintenanceDowntimeProjectPipeline(unittest.TestCase):
    def setUp(self):
        from app.data.database import Database
        from app.excel.fixture_adapter import ACK_VARIABLE
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project
        from tools._common import REPO_ROOT

        self.root = REPO_ROOT
        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(self.database.close)
        self.contract = load_project(
            self.root / "projects/_REFERENCE_MAINTENANCE_DOWNTIME")
        self.pipeline = ProjectPipeline(
            self.database, self.contract, application_version="test")
        self.pipeline.prepare()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def run_fixture(self, filename: str, run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        source = self.contract.source("downtime")
        path = self.root / "tests/fixtures/downtime" / filename
        adapter = FixtureExtractionAdapter(path)
        adapter.open(str(path), {
            "run_id": run_id,
            "report_id": self.contract.project_id,
            "sheet": source.sheet,
            "extraction": {
                "target_cells_per_chunk": 250_000,
                "min_rows_per_chunk": 2,
                "max_rows_per_chunk": 10_000,
            },
        })
        return self.pipeline.run(run_id, {"downtime": adapter})

    def test_different_department_runs_through_same_project_engine(self):
        first = self.run_fixture("period_1.csv", "RUN-DOWN-001")
        second = self.run_fixture("period_2.csv", "RUN-DOWN-002")

        self.assertEqual(first.status, "COMPLETE")
        self.assertEqual(second.status, "COMPLETE")
        self.assertEqual(second.quality_status, "WARNING")
        source = second.sources["downtime"]
        self.assertEqual(source.history.updated, 1)
        self.assertEqual(source.history.inserted, 3)
        self.assertEqual(source.rows_rejected, 1)
        self.assertEqual(source.rows_filtered, 1)

        total = self.database.scalar(
            "SELECT SUM(downtime_minutes) FROM "
            "analytics.history_reference_maintenance_downtime_downtime "
            "WHERE is_active=TRUE")
        rows = self.database.scalar(
            "SELECT count(*) FROM "
            "analytics.history_reference_maintenance_downtime_downtime "
            "WHERE is_active=TRUE")
        self.assertEqual(Decimal(str(total)), Decimal("305.0000"))
        self.assertEqual(int(rows), 7)

        dashboard = second.dashboard
        self.assertEqual(
            [x["label"] for x in dashboard["kpis"]],
            ["Downtime", "Downtime events", "Average event"])
        self.assertEqual(
            [x["id"] for x in dashboard["charts"]],
            ["downtime_trend", "line_pareto"])
        self.assertEqual(dashboard["report"]["period"], "2026-08-03")
        self.assertTrue(any("L1" in x["text"] for x in dashboard["insights"]))

    def test_second_period_rerun_is_idempotent(self):
        self.run_fixture("period_1.csv", "RUN-DOWN-001")
        self.run_fixture("period_2.csv", "RUN-DOWN-002")
        rerun = self.run_fixture("period_2.csv", "RUN-DOWN-003")
        source = rerun.sources["downtime"]

        self.assertEqual(source.history.inserted, 0)
        self.assertEqual(source.history.updated, 0)
        self.assertEqual(source.history.unchanged, 4)
        rows = self.database.scalar(
            "SELECT count(*) FROM "
            "analytics.history_reference_maintenance_downtime_downtime "
            "WHERE is_active=TRUE")
        self.assertEqual(int(rows), 7)

    def test_unexpected_reason_warns_but_loads(self):
        self.run_fixture("period_1.csv", "RUN-DOWN-001")
        outcome = self.run_fixture("period_2.csv", "RUN-DOWN-002")

        rows = self.database.query("""
            SELECT check_id, status FROM quality.check_result
            WHERE run_id = ? AND status = 'WARNING'
        """, [outcome.run_id])
        self.assertTrue(any("reason" in check_id for check_id, _ in rows))

        utility_rows = self.database.scalar(
            "SELECT count(*) FROM "
            "analytics.history_reference_maintenance_downtime_downtime "
            "WHERE reason='Utility' AND is_active=TRUE")
        self.assertEqual(int(utility_rows), 1)

    def test_control_total_balances_with_reject_and_duplicate(self):
        self.run_fixture("period_1.csv", "RUN-DOWN-001")
        outcome = self.run_fixture("period_2.csv", "RUN-DOWN-002")
        control = next(
            c for c in outcome.control_totals if c.name.endswith("downtime_minutes"))
        self.assertEqual(control.difference, Decimal(0))

    def test_filter_definitions_reach_the_dashboard_json(self):
        """S6 depends on this: the local app UI renders filters from here."""
        outcome = self.run_fixture("period_1.csv", "RUN-DOWN-001")
        definitions = {f["id"]: f for f in outcome.dashboard["filters"]["definitions"]}
        self.assertEqual(set(definitions), {"line", "reason"})


if __name__ == "__main__":
    unittest.main()
