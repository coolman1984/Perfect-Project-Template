"""Scan-boundary correctness for the tool tier (Constitution Parts 20.5, 20.8).

Regression cover for a real bug: `data` was excluded by directory *name* at any
depth, so `app/data/` — the entire history-engine layer — was invisible to the
map and to every verifier. A COM import could be added there and the
architecture scan reported PASS.

A scanner that silently skips a layer is worse than no scanner, because it
produces confident green output. These tests pin the boundary in both
directions: what must be excluded, and what must never be.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from tools._common import is_excluded, iter_source_files


class TestExclusionBoundary(unittest.TestCase):
    def test_data_folders_are_excluded_only_at_the_repository_root(self):
        # data/ holds DuckDB files and must never be read (Part 20.8 rule 3).
        self.assertTrue(is_excluded(Path("data/warehouse.duckdb")))
        # app/data/ is the history-engine SOURCE layer and must be scanned.
        self.assertFalse(is_excluded(Path("app/data/history.py")))

    def test_every_app_layer_is_visible(self):
        files = {str(path).replace("\\", "/") for path in iter_source_files()}
        for layer in ("excel", "data", "quality", "analytics",
                      "dashboard", "observability"):
            matching = [f for f in files if f.startswith(f"app/{layer}/")]
            self.assertTrue(matching, f"app/{layer}/ is invisible to the scanners")

    def test_generated_and_data_roots_are_excluded(self):
        for path in ("runtime/python/python.exe", "offline_packages/x.whl",
                     "repair_payload/app.exe", "inbox/source.xlsx",
                     "workspace/run/chunk.tmp", "archive/part-0.parquet",
                     "output/dashboard.html", "runs/RUN-1/manifest.json",
                     "logs/run.log", "release/current/app.exe"):
            self.assertTrue(is_excluded(Path(path)), f"{path} should be excluded")

    def test_vendor_assets_are_excluded_but_web_source_is_not(self):
        self.assertTrue(is_excluded(Path("web/vendor/echarts.min.js")))
        self.assertFalse(is_excluded(Path("web/app.js")))

    def test_tooling_caches_are_excluded_at_any_depth(self):
        self.assertTrue(is_excluded(Path("app/__pycache__/history.cpython-311.pyc")))
        self.assertTrue(is_excluded(Path(".git/config")))

    def test_data_bearing_file_types_are_excluded_anywhere(self):
        # These may contain extracted business data without DRM (Part 13.5).
        for path in ("tests/fixtures/leak.xlsx", "somewhere/db.duckdb",
                     "anywhere/part.parquet"):
            self.assertTrue(is_excluded(Path(path)), f"{path} should be excluded")

    def test_scan_reaches_a_meaningful_number_of_files(self):
        # A guard against an exclusion change silently emptying the scan.
        self.assertGreater(len(iter_source_files()), 60)


class TestScannerCoverage(unittest.TestCase):
    def test_architecture_scan_covers_every_app_and_web_file(self):
        from tools.verify_architecture import _scan_targets

        scanned = {str(path).replace("\\", "/") for path in _scan_targets()}
        source = {
            str(path).replace("\\", "/") for path in iter_source_files()
            if str(path).replace("\\", "/").startswith(("app/", "web/"))
            and path.suffix in {".py", ".js", ".html", ".css"}
        }
        missing = source - scanned
        self.assertEqual(missing, set(),
                         f"files the architecture scan cannot see: {sorted(missing)}")


if __name__ == "__main__":
    unittest.main()
