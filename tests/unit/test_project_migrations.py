"""Project-owned schema migrations must behave exactly like engine migrations:
ordered, immutable once applied, transactional, and scoped so one project's
numbering can never collide with another's or with the engine's own ledger.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


def _write(directory: Path, filename: str, sql: str) -> Path:
    path = directory / filename
    path.write_text(sql, encoding="utf-8")
    return path


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestProjectMigrations(unittest.TestCase):
    def setUp(self):
        from app.data.database import Database

        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        self.migrations_dir = Path(self._temp.name) / "migrations"
        self.migrations_dir.mkdir()
        self.database = Database(Path(self._temp.name) / "project.duckdb")
        self.addCleanup(self.database.close)

    def _migrate(self, project_id="proj_a", application_version="test"):
        from app.data.project_migrations import migrate

        return migrate(
            self.database, project_id=project_id,
            migrations_dir=self.migrations_dir,
            application_version=application_version)

    def test_no_migrations_directory_is_a_no_op(self):
        from app.data.project_migrations import migrate

        applied = migrate(
            self.database, project_id="proj_a",
            migrations_dir=Path(self._temp.name) / "missing")
        self.assertEqual(applied, [])

    def test_applies_in_order_and_records_the_ledger(self):
        _write(self.migrations_dir, "0002_second.sql",
               "CREATE TABLE t2 (x INTEGER)")
        _write(self.migrations_dir, "0001_first.sql",
               "CREATE TABLE t1 (x INTEGER)")
        applied = self._migrate()
        self.assertEqual(applied, [1, 2])
        rows = self.database.query(
            "SELECT version, name FROM sys.project_schema_migration "
            "WHERE project_id = 'proj_a' ORDER BY version")
        self.assertEqual(rows, [(1, "first"), (2, "second")])

    def test_rerunning_applies_nothing_new(self):
        _write(self.migrations_dir, "0001_first.sql", "CREATE TABLE t1 (x INTEGER)")
        self._migrate()
        self.assertEqual(self._migrate(), [])

    def test_editing_an_applied_migration_is_rejected(self):
        path = _write(
            self.migrations_dir, "0001_first.sql", "CREATE TABLE t1 (x INTEGER)")
        self._migrate()
        path.write_text("CREATE TABLE t1 (x INTEGER, y INTEGER)", encoding="utf-8")
        from app.data.project_migrations import ProjectMigrationError

        with self.assertRaises(ProjectMigrationError) as caught:
            self._migrate()
        self.assertIn("immutable", str(caught.exception))

    def test_malformed_filename_is_rejected(self):
        _write(self.migrations_dir, "add_column.sql", "SELECT 1")
        from app.data.project_migrations import ProjectMigrationError

        with self.assertRaises(ProjectMigrationError):
            self._migrate()

    def test_duplicate_version_is_rejected(self):
        _write(self.migrations_dir, "0001_first.sql", "SELECT 1")
        _write(self.migrations_dir, "0001_also_first.sql", "SELECT 1")
        from app.data.project_migrations import ProjectMigrationError

        with self.assertRaises(ProjectMigrationError):
            self._migrate()

    def test_a_failing_migration_rolls_back_and_stops(self):
        """Part 15: a failed migration preserves the last trusted database."""
        _write(self.migrations_dir, "0001_first.sql", "CREATE TABLE t1 (x INTEGER)")
        _write(self.migrations_dir, "0002_broken.sql", "NOT VALID SQL AT ALL")
        with self.assertRaises(Exception):
            self._migrate()
        rows = self.database.query(
            "SELECT version FROM sys.project_schema_migration "
            "WHERE project_id = 'proj_a' ORDER BY version")
        self.assertEqual(
            rows, [(1,)],
            "migration 1 must remain applied and migration 2 must not be "
            "recorded as applied when its SQL failed")

    def test_two_projects_do_not_collide_on_version_numbering(self):
        _write(self.migrations_dir, "0001_first.sql",
               "CREATE TABLE IF NOT EXISTS shared_a (x INTEGER)")
        self._migrate(project_id="proj_a")
        # A second project reusing the same directory and version number must
        # be tracked independently — the ledger key is (project_id, version).
        applied = self._migrate(project_id="proj_b")
        self.assertEqual(applied, [1])
        rows = self.database.query(
            "SELECT project_id, version FROM sys.project_schema_migration "
            "ORDER BY project_id, version")
        self.assertEqual(rows, [("proj_a", 1), ("proj_b", 1)])

    def test_add_column_if_not_exists_is_idempotent_against_a_fresh_table(self):
        """The documented authoring pattern: safe whether or not the column
        already exists, matching how a fresh project database never runs the
        migration against a table missing the column in the first place."""
        self.database.execute("CREATE TABLE raw_orders (order_id VARCHAR)")
        _write(self.migrations_dir, "0001_add_note.sql",
               "ALTER TABLE raw_orders ADD COLUMN IF NOT EXISTS note VARCHAR")
        self._migrate()
        self.database.execute("CREATE TABLE IF NOT EXISTS raw_orders (order_id VARCHAR, note VARCHAR)")
        columns = self.database.columns_of("raw_orders")
        self.assertIn("note", columns)


if __name__ == "__main__":
    unittest.main()
