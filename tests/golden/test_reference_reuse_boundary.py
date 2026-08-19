"""The Phase I4 claim, asserted mechanically rather than narrated.

V10 Part 34 requires Reference D to be "created through the normal employee
adaptation workflow, not hand-built through hidden architecture changes", and
Part 4 requires reuse to be reported as measured evidence rather than a
flattering percentage.

So this file does not check that PPV is arithmetically right — that is
`test_finance_ppv_reference.py`. It checks the thing a reader would otherwise
have to take on trust: that adding an entire new finance department to this
engine touched **no Universal Core file at all**.

The check is deliberately mechanical. `tools/path_scope.classify_scope` reads
`TEMPLATE_BASELINE.json`, the same machine authority the core-change guard
uses, so this test cannot drift away from the definition of "core" that the
rest of the repository enforces.
"""

from __future__ import annotations

import hashlib
import io
import unittest

from factory.reuse_report import build_reuse_report
from tools._common import REPO_ROOT
from tools.path_scope import classify_scope, is_core_owned

#: Every file that exists because Reference D exists.
REFERENCE_D_FILES = (
    "projects/_REFERENCE_FINANCE_PPV/project.toml",
    "projects/_REFERENCE_FINANCE_PPV/sources.toml",
    "projects/_REFERENCE_FINANCE_PPV/relationships.toml",
    "projects/_REFERENCE_FINANCE_PPV/dashboard.toml",
    "projects/_REFERENCE_FINANCE_PPV/business_rules/metrics.sql",
    "projects/_REFERENCE_FINANCE_PPV/business_rules/insights.sql",
    "tests/golden/test_finance_ppv_reference.py",
    "tests/golden/test_reference_reuse_boundary.py",
    "tests/expected/finance_ppv/expected.json",
    "tests/fixtures/finance_ppv/purchases_p1.csv",
    "tests/fixtures/finance_ppv/purchases_p2.csv",
    "tests/fixtures/finance_ppv/purchases_orphan.csv",
    "tests/fixtures/finance_ppv/standard_cost_p1.csv",
    "tests/fixtures/finance_ppv/standard_cost_p2.csv",
    "tests/fixtures/finance_ppv/vendors_p1.csv",
    "tests/fixtures/finance_ppv/vendors_p2.csv",
    "tests/fixtures/finance_ppv/ppv_budget_p1.csv",
)

#: The shared engine surface an ordinary adaptation must not need to touch.
UNIVERSAL_CORE_SAMPLE = (
    "app/project_pipeline.py",
    "app/pipeline.py",
    "app/orchestrator.py",
    "app/state_machine.py",
    "app/data/database.py",
    "app/data/history.py",
    "app/data/staging.py",
    "app/data/archive.py",
    "app/data/migrations.py",
    "app/data/project_migrations.py",
    "app/quality/engine.py",
    "app/quality/reconciliation.py",
    "app/quality/quarantine.py",
    "app/analytics/runner.py",
    "app/analytics/configured.py",
    "app/analytics/patterns.py",
    "app/rules/runner.py",
    "app/dashboard/project_json_builder.py",
    "factory/project_contract.py",
)


class TestReferenceDChangedNoCore(unittest.TestCase):
    def test_every_reference_d_file_exists(self):
        missing = [
            path for path in REFERENCE_D_FILES
            if not (REPO_ROOT / path).is_file()
        ]
        self.assertEqual(missing, [], f"Reference D is incomplete: {missing}")

    def test_no_reference_d_file_is_core_owned(self):
        """The whole Phase I4 claim in one assertion.

        A finance department was added using project configuration, project
        SQL, fixtures and tests. If any file here classified as
        universal_core or tooling, the adaptation would have required an
        engine change and the reuse claim would be false.
        """
        core_owned = [
            f"{path} -> {classify_scope(path)}"
            for path in REFERENCE_D_FILES if is_core_owned(path)
        ]
        self.assertEqual(
            core_owned, [],
            "Reference D touched Universal Core; the 'configuration and "
            f"project SQL only' claim does not hold: {core_owned}")

    def test_reference_d_files_are_only_config_logic_and_tests(self):
        allowed = {"project_config", "business_logic", "presentation", "test",
                   "project_test"}
        wrong = {
            path: classify_scope(path) for path in REFERENCE_D_FILES
            if classify_scope(path) not in allowed
        }
        self.assertEqual(wrong, {}, f"unexpected scopes: {wrong}")

    def test_reuse_report_records_zero_core_files_changed(self):
        """Part 4: report measured evidence, not a percentage."""
        report = build_reuse_report(
            "reference_finance_ppv", projects_root=REPO_ROOT / "projects")

        self.assertEqual(report["project_id"], "reference_finance_ppv")
        self.assertEqual(
            report["core_files_changed"], [],
            "the reuse report itself must show no Universal Core change")
        self.assertTrue(
            report["project_config_files_changed"],
            "an adaptation that changed no configuration proves nothing")
        self.assertTrue(
            report["business_logic_files_changed"],
            "Reference D owns its PPV SQL and must report it")
        self.assertIn(
            "No reuse percentage is used as acceptance evidence",
            report["note"])

    def test_reuse_report_resolves_every_reference_by_declared_project_id(self):
        """Directory name is not project_id, for any reference pack.

        `projects/_REFERENCE_FINANCE_PPV` declares `reference_finance_ppv`, and
        the directory name is not even a valid identifier. Any caller that
        passes the directory name where a project_id is expected fails
        validation, so this pins the resolution for every reference at once.
        """
        from factory.project_contract import find_project_directory, load_project

        projects_root = REPO_ROOT / "projects"
        for directory in sorted(projects_root.iterdir()):
            if not (directory / "project.toml").is_file():
                continue
            project = load_project(directory)
            with self.subTest(project=project.project_id):
                self.assertEqual(
                    find_project_directory(projects_root, project.project_id),
                    directory)
                report = build_reuse_report(
                    project.project_id, projects_root=projects_root)
                self.assertEqual(report["project_id"], project.project_id)
                self.assertEqual(report["core_files_changed"], [])

    def test_running_the_finance_reference_mutates_no_core_source_file(self):
        """A reference that quietly rewrote engine code would be no proof.

        Fingerprints the shared engine, runs the full Reference D golden
        suite, and fingerprints again.
        """
        def fingerprint():
            return {
                path: hashlib.sha256(
                    (REPO_ROOT / path).read_bytes()).hexdigest()
                for path in UNIVERSAL_CORE_SAMPLE
                if (REPO_ROOT / path).is_file()
            }

        before = fingerprint()
        self.assertTrue(before, "no core files were fingerprinted")

        suite = unittest.defaultTestLoader.loadTestsFromName(
            "tests.golden.test_finance_ppv_reference")
        result = unittest.TextTestRunner(
            verbosity=0, stream=io.StringIO()).run(suite)
        self.assertTrue(
            result.wasSuccessful(),
            f"Reference D suite failed: {result.errors or result.failures}")

        after = fingerprint()
        changed = sorted(k for k in before if before[k] != after.get(k))
        self.assertEqual(
            changed, [],
            f"running Reference D modified Universal Core: {changed}")


if __name__ == "__main__":
    unittest.main()
