"""GATE_SOURCE_IMMUTABILITY — extraction never alters the source file.

V10 Part 9: "preserve the source file byte-for-byte; record source hash before
and after". The employee's workbook is the business record. If a run could
modify it — even by touching a timestamp — the engine would be destroying the
evidence it exists to process, and no downstream reconciliation would be
trustworthy.

This asserts the property against a real end-to-end project run rather than
against the adapter alone, because the file is in reach of the whole pipeline,
not just the extraction step.

Scope note: this proves it for the fixture extraction port on POSIX. The COM
adapter against a real protected workbook is a separate, environment-bound
gate (GATE_PROTECTED_FILE_PROOF) and fixture execution is never evidence for
it (V10 Part 37).
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestSourceFilesAreNeverModified(unittest.TestCase):
    FIXTURES = {
        "purchases": "purchases_p1.csv",
        "standard_cost": "standard_cost_p1.csv",
        "vendors": "vendors_p1.csv",
        "ppv_budget": "ppv_budget_p1.csv",
    }

    def setUp(self):
        from app.excel.fixture_adapter import ACK_VARIABLE
        from tools._common import REPO_ROOT

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.repo_root = REPO_ROOT
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        # Work on copies so the assertion is about what the engine does, and a
        # failure can never damage the committed fixtures.
        self.sources = {}
        for source_id, filename in self.FIXTURES.items():
            origin = REPO_ROOT / "tests/fixtures/finance_ppv" / filename
            target = Path(self.temp.name) / filename
            shutil.copy2(origin, target)
            self.sources[source_id] = target

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _ports(self, contract, run_id):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        ports = {}
        for source_id, path in self.sources.items():
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": run_id,
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
        return ports

    def test_source_hash_is_identical_before_and_after_two_runs(self):
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        before = {sid: _digest(p) for sid, p in self.sources.items()}
        sizes_before = {sid: p.stat().st_size for sid, p in self.sources.items()}

        contract = load_project(
            self.repo_root / "projects/_REFERENCE_FINANCE_PPV")
        database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(database.close)
        pipeline = ProjectPipeline(
            database, contract, application_version="test")
        pipeline.prepare()

        for run_id in ("IMMUT-1", "IMMUT-2"):
            outcome = pipeline.run(
                run_id, self._ports(contract, run_id),
                requested_periods={"ppv_budget": "2026-08"})
            self.assertTrue(outcome.succeeded, outcome.error_message)

        after = {sid: _digest(p) for sid, p in self.sources.items()}
        self.assertEqual(
            after, before,
            "extraction modified a source file; the business record must be "
            "preserved byte-for-byte (V10 Part 9)")
        self.assertEqual(
            {sid: p.stat().st_size for sid, p in self.sources.items()},
            sizes_before)

    def test_recorded_lineage_hash_matches_the_file_on_disk(self):
        """The hash written into lineage must describe the real file.

        A lineage hash that did not match would make every downstream identity
        and reconciliation claim unverifiable.
        """
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        contract = load_project(
            self.repo_root / "projects/_REFERENCE_FINANCE_PPV")
        database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(database.close)
        pipeline = ProjectPipeline(
            database, contract, application_version="test")
        pipeline.prepare()
        outcome = pipeline.run(
            "IMMUT-3", self._ports(contract, "IMMUT-3"),
            requested_periods={"ppv_budget": "2026-08"})
        self.assertTrue(outcome.succeeded, outcome.error_message)

        for source_id, path in self.sources.items():
            recorded = database.query(
                f"SELECT DISTINCT _source_file_hash FROM "
                f"{pipeline.raw_table(contract.source(source_id))} "
                f"WHERE _run_id = 'IMMUT-3'")
            self.assertEqual(
                recorded, [(_digest(path),)],
                f"{source_id}: lineage hash does not match the file on disk")

    def test_a_blocked_run_also_leaves_sources_untouched(self):
        """Failure paths get the same guarantee as success paths."""
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        orphan = Path(self.temp.name) / "purchases_orphan.csv"
        shutil.copy2(
            self.repo_root / "tests/fixtures/finance_ppv/purchases_orphan.csv",
            orphan)
        self.sources["purchases"] = orphan
        before = {sid: _digest(p) for sid, p in self.sources.items()}

        contract = load_project(
            self.repo_root / "projects/_REFERENCE_FINANCE_PPV")
        database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(database.close)
        pipeline = ProjectPipeline(
            database, contract, application_version="test")
        pipeline.prepare()
        outcome = pipeline.run(
            "IMMUT-BLOCK", self._ports(contract, "IMMUT-BLOCK"),
            requested_periods={"ppv_budget": "2026-08"})

        self.assertFalse(outcome.succeeded)
        self.assertEqual(outcome.quality_status, "BLOCK")
        self.assertEqual(
            {sid: _digest(p) for sid, p in self.sources.items()}, before,
            "a blocked run modified a source file")


if __name__ == "__main__":
    unittest.main()
