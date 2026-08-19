from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestMultiSourceSupplyChainReference(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools._common import REPO_ROOT

        cls.root = REPO_ROOT
        cls.expected = json.loads(
            (REPO_ROOT / "tests/expected/supply_chain/expected.json")
            .read_text("utf-8"))

    def setUp(self):
        from app.data.database import Database
        from app.excel.fixture_adapter import ACK_VARIABLE
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

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
            "orders": (
                "orders_orphan.csv" if orphan else f"orders_{suffix}.csv"),
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
                "extraction": {
                    "target_cells_per_chunk": 1000,
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 100,
                },
            })
            ports[source_id] = adapter
        return ports

    def _scalar(self, sql: str):
        return self.database.scalar(sql)

    def _trusted_history_snapshot(self):
        """Capture trusted business state, not expected-to-move audit metadata.

        An idempotent rerun must preserve business values, hashes, activity and
        first-seen identity. `last_seen_run_id` is deliberately excluded here:
        re-observing an unchanged row should advance that audit field to the new
        run while leaving the trusted business record unchanged.
        """
        result = {}
        for source in self.contract.sources:
            business = ", ".join(source.business_columns)
            result[source.source_id] = self.database.query(
                f"SELECT {business}, business_key_hash, row_content_hash, "
                f"is_active, first_seen_run_id "
                f"FROM {self.pipeline.history_table(source)} "
                "ORDER BY business_key_hash")
        return result

    def _full_history_snapshot(self):
        """Use the full row only where rollback must preserve audit metadata too."""
        return {
            source.source_id: self.database.query(
                f"SELECT * FROM {self.pipeline.history_table(source)} "
                "ORDER BY business_key_hash")
            for source in self.contract.sources
        }

    def test_two_periods_prove_independent_history_quality_and_cross_source_metrics(self):
        first = self.pipeline.run("SC-P1", self._ports(1, "SC-P1"))
        self.assertTrue(first.succeeded, first.error_message)
        self.assertEqual(
            first.quality_status, self.expected["period_1"]["quality_status"])
        self.assertEqual(
            self._scalar(
                "SELECT count(*) FROM "
                "analytics.history_reference_supply_chain_orders "
                "WHERE is_active"),
            3,
        )
        self.assertEqual(
            str(self._scalar(
                "SELECT SUM(ordered_qty) FROM "
                "analytics.history_reference_supply_chain_orders "
                "WHERE is_active")),
            self.expected["period_1"]["orders_ordered_qty"],
        )

        second = self.pipeline.run("SC-P2", self._ports(2, "SC-P2"))
        self.assertTrue(second.succeeded, second.error_message)
        expected = self.expected["period_2"]
        self.assertEqual(second.quality_status, expected["quality_status"])

        orders = second.sources["orders"]
        self.assertEqual(
            (orders.history.inserted,
             orders.history.updated,
             orders.history.unchanged),
            (expected["orders_inserted"],
             expected["orders_updated"],
             expected["orders_unchanged"]),
        )
        self.assertEqual(orders.rows_rejected, expected["orders_rejected"])
        self.assertEqual(orders.rows_filtered, expected["orders_filtered"])
        self.assertEqual(
            self._scalar(
                "SELECT count(*) FROM "
                "analytics.history_reference_supply_chain_inventory"),
            expected["inventory_history_rows"],
        )
        self.assertEqual(
            self._scalar(
                "SELECT count(*) FROM "
                "analytics.history_reference_supply_chain_item_master "
                "WHERE is_active"),
            expected["item_master_active"],
        )
        self.assertEqual(
            str(self._scalar(
                "SELECT SUM(ordered_qty) FROM "
                "analytics.history_reference_supply_chain_orders "
                "WHERE is_active")),
            expected["orders_ordered_qty"],
        )
        self.assertEqual(
            str(self._scalar(
                "SELECT SUM(fulfilled_qty) FROM "
                "analytics.history_reference_supply_chain_orders "
                "WHERE is_active")),
            expected["orders_fulfilled_qty"],
        )
        for control in second.control_totals:
            self.assertEqual(control.difference, 0, control)

        dashboard = second.dashboard
        self.assertTrue(dashboard["demo_data"])
        self.assertEqual(
            dashboard["project"]["id"], "reference_supply_chain")
        kpis = {item["id"]: item["value"] for item in dashboard["kpis"]}
        self.assertAlmostEqual(
            kpis["fulfillment_rate"], expected["fulfillment_rate"], places=6)
        self.assertEqual(kpis["on_hand_qty"], 133.0)
        shortage = next(
            chart for chart in dashboard["charts"]
            if chart["id"] == "shortage_by_item")
        self.assertEqual(
            shortage["series"][0]["points"][0]["x"],
            expected["top_shortage_item"],
        )
        self.assertEqual(
            shortage["series"][0]["points"][0]["y"], 15.0)
        reasons = dict(self.database.query(
            "SELECT reason_code, count(*) FROM quality.quarantine "
            "WHERE run_id='SC-P2' GROUP BY reason_code"))
        self.assertEqual(reasons.get("NEGATIVE_MEASURE"), 1)
        self.assertEqual(reasons.get("EXACT_DUPLICATE"), 1)

    def test_idempotent_rerun_preserves_truth_and_advances_audit_observation(self):
        self.pipeline.run("SC-I1", self._ports(1, "SC-I1"))
        self.pipeline.run("SC-I2", self._ports(2, "SC-I2"))
        before = self._trusted_history_snapshot()

        rerun = self.pipeline.run("SC-I3", self._ports(2, "SC-I3"))
        self.assertTrue(rerun.succeeded)
        expected = self.expected["idempotent_rerun"]
        self.assertEqual(
            rerun.sources["orders"].history.unchanged,
            expected["orders_unchanged"])
        self.assertEqual(
            rerun.sources["orders"].history.inserted,
            expected["orders_inserted"])
        self.assertEqual(
            rerun.sources["orders"].history.updated, 0)
        self.assertEqual(
            rerun.sources["inventory"].history.unchanged,
            expected["inventory_unchanged"])
        self.assertEqual(
            rerun.sources["inventory"].history.updated, 0)
        self.assertEqual(
            rerun.sources["item_master"].history.unchanged,
            expected["item_master_unchanged"])
        self.assertEqual(
            rerun.sources["item_master"].history.updated, 0)

        # Strong idempotence: every trusted business value and content hash is
        # identical after the rerun.
        self.assertEqual(before, self._trusted_history_snapshot())

        # Strong observability: rows re-seen in the identical rerun record the
        # new run as their latest observation rather than pretending no rerun
        # occurred. All four accepted order records are present in period 2.
        order_last_seen = {
            row[0] for row in self.database.query(
                "SELECT DISTINCT last_seen_run_id FROM "
                "analytics.history_reference_supply_chain_orders "
                "WHERE is_active")
        }
        self.assertEqual(order_last_seen, {"SC-I3"})

        # Inventory is snapshot history, so the prior snapshot stays auditably
        # tied to SC-I1 while the re-seen 2026-08-03 snapshot advances to SC-I3.
        latest_inventory_seen = {
            row[0] for row in self.database.query(
                "SELECT DISTINCT last_seen_run_id FROM "
                "analytics.history_reference_supply_chain_inventory "
                "WHERE snapshot_date = DATE '2026-08-03'")
        }
        self.assertEqual(latest_inventory_seen, {"SC-I3"})

    def test_unmatched_required_relationship_blocks_before_history(self):
        self.pipeline.run("SC-R1", self._ports(1, "SC-R1"))
        before = self._full_history_snapshot()
        blocked = self.pipeline.run(
            "SC-R2", self._ports(2, "SC-R2", orphan=True))
        self.assertFalse(blocked.succeeded)
        self.assertEqual(blocked.quality_status, "BLOCK")
        self.assertEqual(before, self._full_history_snapshot())
        matches = self.database.query(
            "SELECT check_id, status FROM quality.check_result "
            "WHERE run_id='SC-R2' AND check_id LIKE 'relationship.%match'")
        self.assertIn(
            ("relationship.orders_to_item.match", "BLOCK"), matches)

    def test_analytics_failure_rolls_back_every_source_history_together(self):
        self.pipeline.run("SC-A1", self._ports(1, "SC-A1"))
        before = self._full_history_snapshot()
        self.pipeline.analytics.metrics_file = "missing_metrics.sql"
        with self.assertRaises(Exception):
            self.pipeline.run("SC-A2", self._ports(2, "SC-A2"))
        self.assertEqual(
            before,
            self._full_history_snapshot(),
            "outer project transaction must roll back every source, including "
            "audit metadata",
        )

    def _active_history_snapshot(self):
        """Capture only what the archive is contracted to preserve.

        `archive_history` stores active trusted rows, so recovery is judged on
        active business state rather than on superseded audit rows.
        """
        result = {}
        for source in self.contract.sources:
            business = ", ".join(source.business_columns)
            result[source.source_id] = self.database.query(
                f"SELECT {business}, business_key_hash, row_content_hash "
                f"FROM {self.pipeline.history_table(source)} "
                "WHERE is_active ORDER BY business_key_hash")
        return result

    def _shortage_by_item(self):
        """Evaluate the project's own three-source trusted SQL.

        Re-running the shipped statement keeps the formula in one place; a copy
        of the join here would be exactly the duplication Part 14.4 forbids.
        """
        from app.analytics.runner import SqlRunner

        runner = SqlRunner(
            self.database, self.contract.directory / "business_rules")
        return runner.run_named("metrics.sql", "shortage_by_item")

    def test_archive_rebuild_restores_every_source_history_from_parquet(self):
        """GATE_ARCHIVE_REBUILD for a multi-source project.

        Losing the database must stay a minutes-long recovery, not a
        re-extraction: every source rebuilds from Parquet alone, each on its own
        event date, and the cross-source metric still reconciles afterwards.
        """
        from app.data.archive import archive_history, rebuild_history_from_archive

        self.pipeline.run("SC-B1", self._ports(1, "SC-B1"))
        self.pipeline.run("SC-B2", self._ports(2, "SC-B2"))

        before = self._active_history_snapshot()
        shortage_before = self._shortage_by_item()
        self.assertTrue(
            any(row[1] for row in shortage_before),
            "the reconciliation target must carry a non-zero shortage")

        archive_root = Path(self.temp.name) / "archive"
        archived = {}
        for source in self.contract.sources:
            archived[source.source_id] = archive_history(
                self.database,
                history_table=self.pipeline.history_table(source),
                report_id=f"{self.contract.project_id}_{source.source_id}",
                archive_root=archive_root,
                event_date_column=source.event_date,
            ).rows
        self.assertTrue(all(rows > 0 for rows in archived.values()), archived)

        # Lose every trusted table exactly as a disk failure would.
        for source in self.contract.sources:
            table = self.pipeline.history_table(source)
            self.database.execute(f"DELETE FROM {table}")
            self.assertEqual(
                self._scalar(f"SELECT count(*) FROM {table}"), 0)

        for source in self.contract.sources:
            restored = rebuild_history_from_archive(
                self.database,
                history_table=self.pipeline.history_table(source),
                archive_root=archive_root,
                report_id=f"{self.contract.project_id}_{source.source_id}",
            )
            self.assertEqual(restored, archived[source.source_id], source.source_id)

        self.assertEqual(
            before,
            self._active_history_snapshot(),
            "archive recovery must restore every source's trusted history")
        self.assertEqual(
            shortage_before,
            self._shortage_by_item(),
            "cross-source metrics must reconcile against rebuilt history")

    def test_archiving_a_source_with_no_active_rows_still_recovers(self):
        """Recovery must survive a source that legitimately holds nothing.

        A project can carry a source that has received no data yet, or whose
        every row has been deactivated. Archiving it produces a real archive
        directory containing no Parquet files, and restoring that means
        restoring zero rows. Failing there would turn a recoverable state into
        a failed recovery — the opposite of what the archive exists for.
        """
        from app.data.archive import archive_history, rebuild_history_from_archive

        self.pipeline.run("SC-E1", self._ports(1, "SC-E1"))
        source = self.contract.source("orders")
        table = self.pipeline.history_table(source)
        archive_root = Path(self.temp.name) / "archive-empty"

        # Deactivate everything, exactly as a fully superseded source looks.
        self.database.execute(f"UPDATE {table} SET is_active = FALSE")
        result = archive_history(
            self.database, history_table=table,
            report_id=f"{self.contract.project_id}_orders_empty",
            archive_root=archive_root, event_date_column=source.event_date)
        self.assertEqual(result.rows, 0)

        self.database.execute(f"DELETE FROM {table}")
        restored = rebuild_history_from_archive(
            self.database, history_table=table, archive_root=archive_root,
            report_id=f"{self.contract.project_id}_orders_empty")
        self.assertEqual(restored, 0)
        self.assertEqual(
            self._scalar(f"SELECT count(*) FROM {table}"), 0)

    def test_rebuilding_from_an_archive_that_was_never_taken_still_fails(self):
        """The empty-archive tolerance must not swallow a missing archive.

        No archive at all is a different situation from an archive of nothing,
        and only one of them is safe to report as a successful recovery.
        """
        from app.data.archive import rebuild_history_from_archive

        with self.assertRaises(FileNotFoundError):
            rebuild_history_from_archive(
                self.database,
                history_table=self.pipeline.history_table(
                    self.contract.source("orders")),
                archive_root=Path(self.temp.name) / "never-archived",
                report_id="absent")


if __name__ == "__main__":
    unittest.main()
