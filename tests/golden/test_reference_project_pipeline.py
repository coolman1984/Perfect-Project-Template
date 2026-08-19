"""Reference A on the project-centric contract (V10 build program S4).

`tests/golden/test_reference_pipeline.py` already proves scenarios A-D of the
Golden Production Quality workflow through the legacy report contract
(`app.pipeline.Pipeline` + `reports/_REFERENCE`). This file proves the SAME
hand-derived numbers (`tests/expected/reference/expected.json`) run correctly
through the project-centric contract (`app.project_pipeline.ProjectPipeline` +
`projects/_REFERENCE_PRODUCTION_QUALITY`) — the S4 exit gate: "References A, B
and C all execute through the project pipeline."

Only the trusted-history table name differs between the two paths (project
tables are namespaced `{project_id}_{source_id}`); the fixtures, the formulas
and the expected answers are identical.
"""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestReferenceProjectPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT

        cls.root = REPO_ROOT
        cls.expected = json.loads(
            (REPO_ROOT / "tests/expected/reference/expected.json")
            .read_text("utf-8"))

    def setUp(self):
        from app.data.database import Database
        from app.excel.fixture_adapter import ACK_VARIABLE
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(self.database.close)
        self.contract = load_project(
            self.root / "projects/_REFERENCE_PRODUCTION_QUALITY")
        self.pipeline = ProjectPipeline(
            self.database, self.contract, application_version="test")
        self.pipeline.prepare()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _port(self, filename: str, run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        source = self.contract.source("production")
        path = self.root / "tests/fixtures/reference" / filename
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
        return {"production": adapter}

    def _history_totals(self):
        row = self.database.query("""
            SELECT COALESCE(SUM(produced_qty), 0), COALESCE(SUM(defect_qty), 0),
                   count(*)
            FROM analytics.history_reference_production_quality_production
            WHERE is_active = TRUE
        """)[0]
        return {
            "produced_total": Decimal(str(row[0])),
            "defect_total": Decimal(str(row[1])),
            "active_rows": int(row[2]),
        }

    def _kpis(self, outcome):
        return {item["id"]: item["value"] for item in outcome.dashboard["kpis"]}

    # -------------------------------------------------------- scenario A/B/C

    def test_scenario_a_first_period_end_to_end(self):
        expected = self.expected["after_period_1"]
        outcome = self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))

        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(outcome.quality_status, expected["quality_status"])
        source = outcome.sources["production"]
        self.assertEqual(source.rows_extracted, expected["rows_extracted"])
        self.assertEqual(source.rows_rejected, expected["rows_rejected"])
        self.assertEqual(source.rows_filtered, expected["rows_filtered"])
        self.assertEqual(source.history.inserted, expected["inserted"])
        self.assertEqual(source.history.updated, expected["updated"])

        totals = self._history_totals()
        self.assertEqual(totals["produced_total"], Decimal(expected["produced_total"]))
        self.assertEqual(totals["defect_total"], Decimal(expected["defect_total"]))
        self.assertEqual(totals["active_rows"], expected["active_rows"])

    def test_scenario_c_correction_and_quarantine(self):
        self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))
        expected = self.expected["after_period_2"]
        outcome = self.pipeline.run("REF-P2", self._port("period_2.csv", "REF-P2"))

        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(outcome.quality_status, expected["quality_status"])
        source = outcome.sources["production"]
        self.assertEqual(source.rows_extracted, expected["rows_extracted"])
        self.assertEqual(source.rows_rejected, expected["rows_rejected"])
        self.assertEqual(source.rows_filtered, expected["rows_filtered"])
        self.assertEqual(source.history.inserted, expected["inserted"])
        self.assertEqual(source.history.updated, expected["updated"])

        totals = self._history_totals()
        self.assertEqual(totals["produced_total"], Decimal(expected["produced_total"]))
        self.assertEqual(totals["active_rows"], expected["active_rows"])

        corrected = expected["corrected_record"]
        row = self.database.query("""
            SELECT produced_qty FROM analytics.history_reference_production_quality_production
            WHERE is_active = TRUE
              AND production_date = ? AND line = ? AND order_number = ? AND model_code = ?
        """, [corrected["production_date"], corrected["line"],
              corrected["order_number"], corrected["model_code"]])[0]
        self.assertEqual(Decimal(str(row[0])), Decimal(corrected["produced_qty_after"]))

    def test_idempotent_rerun_of_the_same_period(self):
        self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))
        self.pipeline.run("REF-P2", self._port("period_2.csv", "REF-P2"))
        expected = self.expected["idempotent_rerun"]
        outcome = self.pipeline.run(
            "REF-P2-RERUN", self._port("period_2.csv", "REF-P2-RERUN"))

        source = outcome.sources["production"]
        self.assertEqual(source.history.inserted, expected["inserted"])
        self.assertEqual(source.history.updated, expected["updated"])
        self.assertEqual(source.history.unchanged, expected["unchanged"])

        totals = self._history_totals()
        self.assertEqual(totals["produced_total"], Decimal(expected["produced_total"]))
        self.assertEqual(totals["active_rows"], expected["active_rows"])

    # ---------------------------------------------------------- scenario D

    def test_scenario_d_bad_file_blocks_without_touching_history(self):
        # blocking_failure in expected.json assumes periods 1 and 2 already
        # committed — its "unchanged" totals are the post-period-2 totals.
        self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))
        self.pipeline.run("REF-P2", self._port("period_2.csv", "REF-P2"))
        expected = self.expected["blocking_failure"]
        outcome = self.pipeline.run(
            "REF-P3-BAD", self._port("period_3_bad.csv", "REF-P3-BAD"))

        self.assertEqual(outcome.status, expected["run_status"])
        self.assertEqual(outcome.quality_status, expected["quality_status"])

        totals = self._history_totals()
        self.assertEqual(
            totals["produced_total"], Decimal(expected["produced_total_unchanged"]))
        self.assertEqual(totals["active_rows"], expected["active_rows_unchanged"])

    # --------------------------------------------------------- KPIs/dashboard

    def test_dashboard_kpis_match_the_same_derived_metrics(self):
        self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))
        outcome = self.pipeline.run("REF-P2", self._port("period_2.csv", "REF-P2"))
        kpis = self._kpis(outcome)
        expected = self.expected["metrics"]

        self.assertEqual(
            str(round(Decimal(str(kpis["defect_rate_ppm"])), 2)),
            expected["defect_rate_ppm_rounded_2dp"])

        chart = next(
            c for c in outcome.dashboard["charts"] if c["id"] == "pareto")
        pareto = [[point["x"], Decimal(str(point["y"]))]
                  for point in chart["series"][0]["points"]]
        expected_pareto = [[name, Decimal(value)]
                           for name, value in expected["pareto_defects_by_model"]]
        self.assertEqual(pareto, expected_pareto)

    def test_filter_definitions_reach_the_dashboard_json(self):
        """S6 depends on this: the local app UI renders filters from here."""
        outcome = self.pipeline.run("REF-P1", self._port("period_1.csv", "REF-P1"))
        definitions = {f["id"]: f for f in outcome.dashboard["filters"]["definitions"]}
        self.assertEqual(set(definitions), {"model_code", "line"})
        self.assertEqual(definitions["model_code"]["label"], "Model")


if __name__ == "__main__":
    unittest.main()
