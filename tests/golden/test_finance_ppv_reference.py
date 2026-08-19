"""Reference D — Finance Purchase Price Variance (V10 Part 34, Phase I4).

This reference exists to answer one question the other three cannot: can a
genuinely different department be adapted through **configuration and project
SQL alone**, with zero Universal Core edits?

It is deliberately unlike the Supply Chain reference:

- four sources rather than three, including a *target* role;
- an **optional** source (`ppv_budget`) whose absence must warn, not block;
- an **optional** relationship (`purchases_to_ppv_budget`, require_match=false);
- `replace_period` history, which no other reference exercises;
- a money variance calculation joining three sources at once.

`tests/golden/test_reference_reuse_boundary.py` asserts the zero-core-change
claim mechanically. This file proves the numbers.
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
class TestFinancePpvReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT

        cls.root = REPO_ROOT
        cls.expected = json.loads(
            (REPO_ROOT / "tests/expected/finance_ppv/expected.json")
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
            self.root / "projects/_REFERENCE_FINANCE_PPV")
        self.pipeline = ProjectPipeline(
            self.database, self.contract, application_version="test")
        self.pipeline.prepare()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _ports(self, files: dict[str, str], run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        ports = {}
        for source_id, filename in files.items():
            source = self.contract.source(source_id)
            path = self.root / "tests/fixtures/finance_ppv" / filename
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": run_id,
                "report_id": self.contract.project_id,
                "sheet": source.sheet,
                "schema_version": "1",
                "extraction": {
                    "target_cells_per_chunk": 1000,
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 100,
                },
            })
            ports[source_id] = adapter
        return ports

    def _period_1_ports(self, run_id: str):
        return self._ports({
            "purchases": "purchases_p1.csv",
            "standard_cost": "standard_cost_p1.csv",
            "vendors": "vendors_p1.csv",
            "ppv_budget": "ppv_budget_p1.csv",
        }, run_id)

    def _period_2_ports(self, run_id: str):
        # No ppv_budget file: Finance has not approved the September budget.
        return self._ports({
            "purchases": "purchases_p2.csv",
            "standard_cost": "standard_cost_p2.csv",
            "vendors": "vendors_p2.csv",
        }, run_id)

    def _run_period_1(self, run_id="FIN-P1"):
        return self.pipeline.run(
            run_id, self._period_1_ports(run_id),
            requested_periods={"ppv_budget": "2026-08"})

    def _metric(self, name):
        from app.analytics.runner import SqlRunner

        runner = SqlRunner(
            self.database, self.contract.directory / "business_rules")
        return runner.run_named("metrics.sql", name)

    def _scalar_metric(self, name) -> Decimal:
        """Compare decimals by value, not by rendered scale.

        DECIMAL(18,4) arithmetic widens the result scale, so `-175.00` and
        `-175.00000000` are the same trusted number reported differently.
        Asserting on the string would test DuckDB's formatting rather than the
        business result.
        """
        return Decimal(str(self._metric(name)[0][0]))

    def _kpis(self, outcome):
        return {item["id"]: item["value"] for item in outcome.dashboard["kpis"]}

    def _chart(self, outcome, chart_id):
        chart = next(
            c for c in outcome.dashboard["charts"] if c["id"] == chart_id)
        return [[point["x"], point["y"]]
                for point in chart["series"][0]["points"]]

    # ------------------------------------------------------------------ tests
    def test_period_one_matches_hand_derived_variance(self):
        expected = self.expected["period_1"]
        outcome = self._run_period_1()

        self.assertTrue(outcome.succeeded, outcome.error_message)
        self.assertEqual(outcome.quality_status, expected["quality_status"])
        self.assertEqual(
            outcome.sources["purchases"].history.inserted,
            expected["purchases_inserted"])

        self.assertEqual(
            self._scalar_metric("ppv_amount"), Decimal(expected["ppv_amount"]))
        self.assertEqual(
            self._scalar_metric("purchase_spend"),
            Decimal(expected["purchase_spend"]))
        self.assertEqual(
            self._scalar_metric("standard_spend"),
            Decimal(expected["standard_spend"]))

        kpis = self._kpis(outcome)
        self.assertAlmostEqual(kpis["ppv_rate"], expected["ppv_rate"], places=9)
        self.assertEqual(kpis["ppv_amount"], -175.0)
        self.assertEqual(kpis["ppv_budget_amount"], -100.0)

        self.assertEqual(
            self._chart(outcome, "ppv_by_vendor"),
            [list(row) for row in expected["ppv_by_vendor"]])
        self.assertEqual(
            self._chart(outcome, "ppv_by_category"),
            [list(row) for row in expected["ppv_by_category"]])

        for control in outcome.control_totals:
            self.assertEqual(control.difference, 0, control)

    def test_insight_names_the_largest_unfavourable_vendor_with_evidence(self):
        expected = self.expected["period_1"]
        outcome = self._run_period_1()
        insight = next(
            item for item in outcome.dashboard["insights"]
            if item["id"] == "top_unfavourable_vendor")

        self.assertEqual(insight["current"], expected["top_vendor_ppv"])
        self.assertIn(expected["top_vendor"], insight["text"])
        self.assertEqual(insight["confidence"], "verified")
        self.assertIn("metric:ppv_amount", insight["evidence_refs"])
        # Part 20: an insight may prioritise investigation, never assert cause.
        self.assertIn("investigation priority", insight["text"])
        for forbidden in ("because", "caused by", "due to"):
            self.assertNotIn(forbidden, insight["text"].lower())

    def test_absent_optional_budget_warns_and_still_publishes(self):
        """The distinguishing behaviour of this reference.

        September has no approved PPV budget. The optional source is simply
        absent, the optional relationship cannot match, and the engine must
        warn while still publishing trusted actuals — a required relationship
        in the same position would block (proved below).
        """
        expected = self.expected["period_2"]
        self._run_period_1()
        outcome = self.pipeline.run("FIN-P2", self._period_2_ports("FIN-P2"))

        self.assertTrue(outcome.succeeded, outcome.error_message)
        self.assertEqual(outcome.quality_status, expected["quality_status"])

        budget_check = self.database.query(
            "SELECT status FROM quality.check_result "
            "WHERE run_id = 'FIN-P2' "
            "AND check_id = 'relationship.purchases_to_ppv_budget.match'")
        self.assertEqual(budget_check, [("WARNING",)])

        self.assertEqual(
            self._scalar_metric("ppv_amount"), Decimal(expected["ppv_amount"]))
        history = outcome.sources["purchases"].history
        self.assertEqual(
            (history.inserted, history.updated, history.unchanged),
            (expected["purchases_inserted"], expected["purchases_updated"],
             expected["purchases_unchanged"]))

    def test_correction_restates_variance_without_duplicating_history(self):
        expected = self.expected["period_2"]
        self._run_period_1()
        outcome = self.pipeline.run("FIN-P2", self._period_2_ports("FIN-P2"))

        self.assertEqual(
            self._chart(outcome, "ppv_by_vendor"),
            [list(row) for row in expected["ppv_by_vendor"]],
            "the corrected PO-1001/1 price must restate Acme's variance from "
            "+25.00 to -5.00 rather than appending a second line")
        self.assertEqual(
            self.database.scalar(
                "SELECT count(*) FROM "
                "analytics.history_reference_finance_ppv_purchases"),
            expected["purchases_active"])

    def test_unmatched_required_standard_cost_blocks_the_run(self):
        """The required relationship in the same shape as the optional one.

        Without an approved standard cost, PPV is undefined — so this must
        block where the missing budget only warned.
        """
        self._run_period_1()
        before = self.database.query(
            "SELECT po_number, po_line, actual_unit_price FROM "
            "analytics.history_reference_finance_ppv_purchases "
            "ORDER BY po_number, po_line")

        blocked = self.pipeline.run("FIN-ORPHAN", self._ports({
            "purchases": "purchases_orphan.csv",
            "standard_cost": "standard_cost_p1.csv",
            "vendors": "vendors_p1.csv",
        }, "FIN-ORPHAN"))

        self.assertFalse(blocked.succeeded)
        self.assertEqual(blocked.quality_status, "BLOCK")
        self.assertIn(
            ("relationship.purchases_to_standard_cost.match", "BLOCK"),
            self.database.query(
                "SELECT check_id, status FROM quality.check_result "
                "WHERE run_id = 'FIN-ORPHAN' "
                "AND check_id LIKE 'relationship.%match'"))
        self.assertEqual(
            before,
            self.database.query(
                "SELECT po_number, po_line, actual_unit_price FROM "
                "analytics.history_reference_finance_ppv_purchases "
                "ORDER BY po_number, po_line"),
            "a blocked run must leave trusted purchase history untouched")

    def test_replace_period_restates_a_budget_without_merging_into_it(self):
        """`replace_period`, which no other reference exercises.

        A restated August budget must replace that period wholesale, so the
        superseded amount cannot survive as trusted history.
        """
        self._run_period_1()
        self.assertEqual(
            self._scalar_metric("ppv_budget_amount"), Decimal("-100.00"))

        restated = Path(self.temp.name) / "ppv_budget_restated.csv"
        restated.write_text(
            "period,ppv_budget_amount,budget_effective_date\n"
            "2026-08,-60.00,2026-08-15\n", encoding="utf-8")

        from app.excel.fixture_adapter import FixtureExtractionAdapter

        adapter = FixtureExtractionAdapter(restated)
        adapter.open(str(restated), {
            "run_id": "FIN-P1B",
            "report_id": self.contract.project_id,
            "sheet": self.contract.source("ppv_budget").sheet,
            "schema_version": "1",
            "extraction": {
                "target_cells_per_chunk": 1000,
                "min_rows_per_chunk": 1,
                "max_rows_per_chunk": 100,
            },
        })
        ports = self._ports({
            "purchases": "purchases_p1.csv",
            "standard_cost": "standard_cost_p1.csv",
            "vendors": "vendors_p1.csv",
        }, "FIN-P1B")
        ports["ppv_budget"] = adapter

        outcome = self.pipeline.run(
            "FIN-P1B", ports, requested_periods={"ppv_budget": "2026-08"})
        self.assertTrue(outcome.succeeded, outcome.error_message)

        self.assertEqual(
            self._scalar_metric("ppv_budget_amount"), Decimal("-60.00"),
            "replace_period must restate August wholesale; -160.00 would mean "
            "the superseded budget merged instead of being replaced")
        self.assertEqual(
            self.database.scalar(
                "SELECT count(*) FROM "
                "analytics.history_reference_finance_ppv_ppv_budget"),
            1)

    def test_rerunning_the_same_period_is_idempotent(self):
        self._run_period_1()
        first = self.database.query(
            "SELECT po_number, po_line, business_key_hash, row_content_hash "
            "FROM analytics.history_reference_finance_ppv_purchases "
            "ORDER BY business_key_hash")
        ppv_first = self._scalar_metric("ppv_amount")

        self._run_period_1("FIN-P1-RERUN")

        self.assertEqual(
            first,
            self.database.query(
                "SELECT po_number, po_line, business_key_hash, row_content_hash "
                "FROM analytics.history_reference_finance_ppv_purchases "
                "ORDER BY business_key_hash"))
        self.assertEqual(self._scalar_metric("ppv_amount"), ppv_first)


if __name__ == "__main__":
    unittest.main()
