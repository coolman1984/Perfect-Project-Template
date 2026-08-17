"""Architecture compliance runs as part of the test suite (Part 23.10).

RUN_TESTS, the pre-commit gate and CI all call these. A material change cannot
be committed or released while they fail (Part 20.9).
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from tools import verify_architecture
from tools._common import EXIT_PASS


def _args(**overrides):
    base = dict(command="verify", baseline=False, source_scan=False, release=None,
                simulate_clean_pc=False, simulate_missing=None,
                standard_user_loopback=False)
    base.update(overrides)
    return SimpleNamespace(**base)


class TestArchitectureBaseline(unittest.TestCase):
    def test_baseline_lock_passes(self):
        self.assertEqual(verify_architecture.main(_args(baseline=True)), EXIT_PASS)

    def test_source_scan_passes(self):
        # Catches CDN references, runtime downloads, non-loopback binds,
        # elevation, COM leaking out of the adapter, dev tooling imported by
        # production code, third-party imports in the tool tier, and secrets.
        self.assertEqual(verify_architecture.main(_args(source_scan=True)), EXIT_PASS)


class TestLockedComponentsPresent(unittest.TestCase):
    """Part 23.8 — a component may not be dropped to reduce package size."""

    def setUp(self):
        import json
        from tools._common import read_text
        self.baseline = json.loads(read_text(verify_architecture.BASELINE_PATH))
        self.ids = {c["id"] for c in self.baseline["required_components"]}

    def test_loopback_transport_is_locked(self):
        # The most-attacked rule: "no external server" never means "no local
        # server" (Part 0.9).
        self.assertIn("loopback-transport", self.ids)
        self.assertIn("fastapi-stack", self.ids)

    def test_database_and_archive_are_locked(self):
        self.assertIn("duckdb", self.ids)
        self.assertIn("parquet", self.ids)

    def test_no_forbidden_runtime_requirement_was_quietly_dropped(self):
        forbidden = set(self.baseline["forbidden_runtime_requirements"])
        for requirement in ("internet", "administrator_or_elevation",
                            "system_python", "cdn"):
            self.assertIn(requirement, forbidden)

    def test_external_prerequisites_are_only_windows_and_excel(self):
        prerequisites = " ".join(self.baseline["approved_external_prerequisites"]).lower()
        self.assertIn("windows", prerequisites)
        self.assertIn("excel", prerequisites)
        self.assertNotIn("python", prerequisites)
        self.assertNotIn("node", prerequisites)

    def test_no_self_authorized_deviation(self):
        # Part 23.9: an agent cannot approve its own deviation.
        for deviation in self.baseline.get("approved_deviations", []):
            self.assertTrue(deviation.get("user_approved"),
                            f"deviation {deviation.get('id')} lacks user approval")


class TestEnvironmentBoundGatesStayHonest(unittest.TestCase):
    """Gates needing real Windows must report BLOCKED, never a false pass."""

    def test_clean_pc_simulation_reports_blocked(self):
        self.assertEqual(verify_architecture.main(_args(simulate_clean_pc=True)), 3)

    def test_standard_user_loopback_reports_blocked(self):
        self.assertEqual(verify_architecture.main(_args(standard_user_loopback=True)), 3)


if __name__ == "__main__":
    unittest.main()
