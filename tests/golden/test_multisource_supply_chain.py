from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


@unittest.skipUnless(_HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestMultiSourceSupplyChainReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT
        cls.root = REPO_ROOT
        cls.expected = json.loads(
            (REPO_ROOT / "tests/expected/supply_chain/expected.json").read_text("utf-8"))

    def setUp(self):
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project
        from app.excel.fixture_adapter import ACK_VARIABLE

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / "project.duckdb")
        self.contract = load_project(
            self.root / "projects/_REFERENCE_SUPPLY_CHAIN")
        self.pipeline = ProjectPipeline(
            self.database, self.contract, application_version="test")
        self.pipeline.prepare()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE
        self.database.close()
        self.temp.cleanup()
        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _ports(self, period: int, run_id: str, *, orphan: bool = False):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        suffix = f"p{period}"
        files = {
            "orders": "orders_orphan.csv" if orphan else f"orders_{suffix}.csv",
            "inventory": f"inventory_{suffix}.csv",
            "item_master": f"item_master_{suffix}.csv",
        }
        ports = {}
        for source_id, filename in files.items():
            source = self.contract.source(source_id)
            path = self.root / "tests/fixtures/supply_chain" / filename
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": run_id,
                "report_id": self.contract.project_id,
                "sheet": source.sheet,
                "schema_version": "1",
                "extraction": {"target_cells_per_chunk": 1000,
                               "min_rows_per_chunk": 1,
                               "max_rows_per_chunk": 100},
            })
            ports[source_id] = adapter
        return ports

    def _scalar(self, sql: str):
        return self.database.scalar(sql)

    def _history_snapshot(self):
        return {
            source.source_id: self.database.query(
                f"SELECT * FROM {self.pipeline.history_table(source)} "
                "ORDER BY business_key_hash")
            for source in self.contract.sources
        }

    def test_two_periods_prove_independent_history_quality_and_cross_source_metrics(self):
        first = self.pipeline.run("SC-P1", self._ports(1, "SC-P1"))
        self.assertTrue(first.succeeded, first.error_message)
        self.assertEqual(first.quality_status, self.expected["period_1"]["quality_status"])
        self.assertEqual(self._scalar(
            "SELECT count(*) FROM analytics.history_reference_supply_chain_orders WHERE is_active"), 3)
        self.assertEqual(str(self._scalar(
            "SELECT SUM(ordered_qty) FROM analytics.history_reference_supply_chain_orders WHERE is_active")),
            self.expected["period_1"]["orders_ordered_qty"])

        second = self.pipeline.run("SC-P2", self._ports(2, "SC-P2"))
        self.assertTrue(second.succeeded, second.error_message)
        expected = self.expected["period_2"]
        self.assertEqual(second.quality_status, expected["quality_status"])
        orders = second.sources["orders"]
        self.assertEqual((orders.history.inserted, orders.history.updated, orders.history.unchanged),
                         (expected["orders_inserted"], expected["orders_updated"], expected["orders_unchanged"]))
        self.assertEqual(orders.rows_rejected, expected["orders_rejected"])
        self.assertEqual(orders.rows_filtered, expected["orders_filtered"])
        self.assertEqual(self._scalar(
            "SELECT count(*) FROM analytics.history_reference_supply_chain_inventory"),
            expected["inventory_history_rows"])
        self.assertEqual(self._scalar(
            "SELECT count(*) FROM analytics.history_reference_supply_chain_item_master WHERE is_active"),
            expected["item_master_active"])
        self.assertEqual(str(self._scalar(
            "SELECT SUM(ordered_qty) FROM analytics.history_reference_supply_chain_orders WHERE is_active")),
            expected["orders_ordered_qty"])
        self.assertEqual(str(self._scalar(
            "SELECT SUM(fulfilled_qty) FROM analytics.history_reference_supply_chain_orders WHERE is_active")),
            expected["orders_fulfilled_qty"])
        for control in second.control_totals:
            self.assertEqual(control.difference, 0, control)

        dashboard = second.dashboard
        self.assertTrue(dashboard["demo_data"])
        self.assertEqual(dashboard["project"]["id"], "reference_supply_chain")
        kpis = {item["id"]: item["value"] for item in dashboard["kpis"]}
        self.assertAlmostEqual(kpis["fulfillment_rate"], expected["fulfillment_rate"], places=6)
        self.assertEqual(kpis["on_hand_qty"], 133.0)
        self.assertEqual(kpis["shortage_qty"], 15.0)
        shortage = next(c for c in dashboard["charts"] if c["id"] == "shortage_by_item")
        self.assertEqual(shortage["series"][0]["points"][0]["x"], expected["top_shortage_item"])
        self.assertEqual(shortage["series"][0]["points"][0]["y"], 15.0)
        reasons = dict(self.database.query(
            "SELECT reason_code, count(*) FROM quality.quarantine "
            "WHERE run_id='SC-P2' GROUP BY reason_code"))
        self.assertEqual(reasons.get("NEGATIVE_MEASURE"), 1)
        self.assertEqual(reasons.get("EXACT_DUPLICATE"), 1)

    def test_idempotent_rerun_changes_no_trusted_history(self):
        self.pipeline.run("SC-I1", self._ports(1, "SC-I1"))
        self.pipeline.run("SC-I2", self._ports(2, "SC-I2"))
        before = self._history_snapshot()
        rerun = self.pipeline.run("SC-I3", self._ports(2, "SC-I3"))
        self.assertTrue(rerun.succeeded)
        expected = self.expected["idempotent_rerun"]
        self.assertEqual(rerun.sources["orders"].history.unchanged, expected["orders_unchanged"])
        self.assertEqual(rerun.sources["orders"].history.inserted, expected["orders_inserted"])
        self.assertEqual(rerun.sources["inventory"].history.unchanged, expected["inventory_unchanged"])
        self.assertEqual(rerun.sources["item_master"].history.unchanged, expected["item_master_unchanged"])
        self.assertEqual(before, self._history_snapshot())

    def test_unmatched_required_relationship_blocks_before_history(self):
        self.pipeline.run("SC-R1", self._ports(1, "SC-R1"))
        before = self._history_snapshot()
        blocked = self.pipeline.run(
            "SC-R2", self._ports(2, "SC-R2", orphan=True))
        self.assertFalse(blocked.succeeded)
        self.assertEqual(blocked.quality_status, "BLOCK")
        self.assertEqual(before, self._history_snapshot())
        matches = self.database.query(
            "SELECT check_id, status FROM quality.check_result "
            "WHERE run_id='SC-R2' AND check_id LIKE 'relationship.%match'")
        self.assertIn(("relationship.orders_to_item.match", "BLOCK"), matches)

    def test_analytics_failure_rolls_back_every_source_history_together(self):
        self.pipeline.run("SC-A1", self._ports(1, "SC-A1"))
        before = self._history_snapshot()
        self.pipeline.analytics.metrics_file = "missing_metrics.sql"
        with self.assertRaises(Exception):
            self.pipeline.run("SC-A2", self._ports(2, "SC-A2"))
        self.assertEqual(before, self._history_snapshot(),
                         "outer project transaction must roll back every source")


if __name__ == "__main__":
    unittest.main()
