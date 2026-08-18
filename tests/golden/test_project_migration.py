"""End-to-end proof for project-owned schema migrations (V10 Part 15, Phase I2).

The unit tests in `tests/unit/test_project_migrations.py` exercise the
migration ledger in isolation. This test proves the real scenario Part 15
exists for: a project that was already running, whose business needs one more
column, gets that column through an additive migration rather than through
someone editing a trusted table by hand — and the pipeline's own drift check
would otherwise refuse to start.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None

PROJECT_TOML = """
project_id = "migration_probe"
project_version = {version}
mode = "prototype"
outputs = ["dashboard"]

[template]
template_id = "universal-excel-automation-engine"
template_version = "0.2.0-development"
baseline_digest = "PENDING_SEALED_TEMPLATE"

[business]
purpose = "Prove the project migration path end to end"
owner = "FIXTURE"
decision = "Does the new warehouse_note column survive a schema evolution?"

[execution]
fixture_adapter = true
"""

SOURCES_TOML_V1 = """
[[sources]]
source_id = "orders"
role = "transaction"
required = true
grain = "One order line for one item"
business_key = ["order_id", "order_line"]
event_date = "order_date"

[sources.column_types]
order_id = "VARCHAR"
order_line = "INTEGER"
order_date = "DATE"
item_id = "VARCHAR"
ordered_qty = "DECIMAL(18,4)"

[sources.match]
file_patterns = ["orders*.csv"]
[sources.discovery]
sheet = "Orders"
header_row = 1
[sources.history]
mode = "upsert"
lookback_days = 30
deletion_rule = "mark_inactive"
[sources.quality]
required_columns = ["order_id", "order_line", "order_date", "item_id", "ordered_qty"]
control_totals = ["ordered_qty"]
non_negative_columns = ["ordered_qty"]
"""

# V2 adds warehouse_note, matched by an additive migration.
SOURCES_TOML_V2 = SOURCES_TOML_V1.replace(
    'ordered_qty = "DECIMAL(18,4)"\n\n[sources.match]',
    'ordered_qty = "DECIMAL(18,4)"\nwarehouse_note = "VARCHAR"\n\n[sources.match]',
).replace(
    'required_columns = ["order_id", "order_line", "order_date", "item_id", "ordered_qty"]',
    'required_columns = ["order_id", "order_line", "order_date", "item_id", "ordered_qty", "warehouse_note"]',
)

RELATIONSHIPS_TOML = "# no relationships: single-source project\n"

DASHBOARD_TOML = """
[meta]
title = "Migration Probe"
period_query = "latest_order_date"
"""

METRICS_SQL = """
-- name: latest_order_date
SELECT max(order_date) FROM analytics.history_migration_probe_orders WHERE is_active;
"""

INSIGHTS_SQL = "-- no insights for this probe\n"

MIGRATION_SQL = """
-- 0001_add_warehouse_note.sql
-- Additive: a fresh database already has the column from current sources.toml,
-- so this must be idempotent rather than assume it is starting from v1.
ALTER TABLE raw.migration_probe_orders ADD COLUMN IF NOT EXISTS warehouse_note VARCHAR;
ALTER TABLE clean.migration_probe_orders ADD COLUMN IF NOT EXISTS warehouse_note VARCHAR;
ALTER TABLE analytics.history_migration_probe_orders ADD COLUMN IF NOT EXISTS warehouse_note VARCHAR;
"""

ORDERS_CSV_V1 = """order_id,order_line,order_date,item_id,ordered_qty
O1,1,2026-08-01,I1,100
"""

ORDERS_CSV_V2 = """order_id,order_line,order_date,item_id,ordered_qty,warehouse_note
O1,1,2026-08-01,I1,100,checked
O2,1,2026-08-02,I2,40,damaged carton
"""


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestProjectSchemaMigration(unittest.TestCase):
    def setUp(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "migration_probe"
        self.root.mkdir()
        self.db_path = Path(self.temp.name) / "project.duckdb"

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _write_project(self, *, sources: str, version: int, orders_csv: str,
                        migration: str | None = None) -> None:
        (self.root / "project.toml").write_text(
            PROJECT_TOML.format(version=version), encoding="utf-8")
        (self.root / "sources.toml").write_text(sources, encoding="utf-8")
        (self.root / "relationships.toml").write_text(
            RELATIONSHIPS_TOML, encoding="utf-8")
        (self.root / "dashboard.toml").write_text(DASHBOARD_TOML, encoding="utf-8")
        rules = self.root / "business_rules"
        rules.mkdir(exist_ok=True)
        (rules / "metrics.sql").write_text(METRICS_SQL, encoding="utf-8")
        (rules / "insights.sql").write_text(INSIGHTS_SQL, encoding="utf-8")
        (self.root / "orders.csv").write_text(orders_csv, encoding="utf-8")
        if migration is not None:
            migrations_dir = self.root / "migrations"
            migrations_dir.mkdir(exist_ok=True)
            (migrations_dir / "0001_add_warehouse_note.sql").write_text(
                migration, encoding="utf-8")

    def _port(self, run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        path = self.root / "orders.csv"
        adapter = FixtureExtractionAdapter(path)
        adapter.open(str(path), {
            "run_id": run_id,
            "report_id": "migration_probe",
            "sheet": "Orders",
            "schema_version": "1",
            "extraction": {
                "target_cells_per_chunk": 1000,
                "min_rows_per_chunk": 1,
                "max_rows_per_chunk": 100,
            },
        })
        return {"orders": adapter}

    def test_configured_column_without_a_migration_fails_closed(self):
        """The drift check this migration path exists to satisfy.

        Simulates the real failure: an employee edits sources.toml to add a
        column but writes no migration. `prepare()` must refuse rather than
        silently reconcile — Part 15: "schema drift never silently changes
        trusted tables". This is not exercised by the migration unit tests,
        which never touch ProjectPipeline.
        """
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline, ProjectPipelineError
        from factory.project_contract import load_project

        self._write_project(
            sources=SOURCES_TOML_V1, version=1, orders_csv=ORDERS_CSV_V1)
        database = Database(self.db_path)
        self.addCleanup(database.close)
        contract = load_project(self.root)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()
        pipeline.run("MP-1", self._port("MP-1"))
        database.close()

        # Now the business needs one more column, but no migration is written.
        self._write_project(
            sources=SOURCES_TOML_V2, version=2, orders_csv=ORDERS_CSV_V1)
        database = Database(self.db_path)
        self.addCleanup(database.close)
        contract = load_project(self.root)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        with self.assertRaises(ProjectPipelineError) as caught:
            pipeline.prepare()
        self.assertIn("migration", str(caught.exception))

    def test_additive_migration_lets_an_existing_project_evolve(self):
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        # Period 1: the project as it always was, no migrations directory.
        self._write_project(
            sources=SOURCES_TOML_V1, version=1, orders_csv=ORDERS_CSV_V1)
        database = Database(self.db_path)
        self.addCleanup(database.close)
        contract = load_project(self.root)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()
        first = pipeline.run("MP-1", self._port("MP-1"))
        self.assertTrue(first.succeeded, first.error_message)
        database.close()

        # Period 2: business adds warehouse_note, backed by an additive
        # migration on the same existing database.
        self._write_project(
            sources=SOURCES_TOML_V2, version=2, orders_csv=ORDERS_CSV_V2,
            migration=MIGRATION_SQL)
        database = Database(self.db_path)
        self.addCleanup(database.close)
        contract = load_project(self.root)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()  # must not raise: the migration closes the drift.

        applied = database.query(
            "SELECT version, name FROM sys.project_schema_migration "
            "WHERE project_id = 'migration_probe'")
        self.assertEqual(applied, [(1, "add_warehouse_note")])

        second = pipeline.run("MP-2", self._port("MP-2"))
        self.assertTrue(second.succeeded, second.error_message)
        rows = dict(database.query(
            "SELECT order_id, warehouse_note FROM "
            "analytics.history_migration_probe_orders WHERE is_active"))
        # O1 is upserted again in period 2 and picks up the new column; O2 is
        # entirely new. Both prove the migrated column round-trips through the
        # ordinary pipeline, not just through the migration's own DDL.
        self.assertEqual(rows["O1"], "checked")
        self.assertEqual(rows["O2"], "damaged carton")

    def test_migration_directory_created_fresh_is_idempotent_on_a_new_database(self):
        """A brand-new employee copy applies the full current config plus the
        full migration history at once. The migration must be a no-op there,
        not a failure, because `_create_source_tables` already created the
        column from current `sources.toml` before the migration ever runs.
        """
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        self._write_project(
            sources=SOURCES_TOML_V2, version=2, orders_csv=ORDERS_CSV_V2,
            migration=MIGRATION_SQL)
        database = Database(self.db_path)
        self.addCleanup(database.close)
        contract = load_project(self.root)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()  # must not raise on a database that never existed.
        outcome = pipeline.run("MP-FRESH", self._port("MP-FRESH"))
        self.assertTrue(outcome.succeeded, outcome.error_message)


if __name__ == "__main__":
    unittest.main()
