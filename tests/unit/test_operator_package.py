"""Simple final-user ZIP contract."""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.operator_package import (
    PackageError,
    build,
    start_script,
    validate_project_name,
    verify_zip,
)


class TestOperatorPackage(unittest.TestCase):
    def _sealed_app(self, root: Path) -> Path:
        release = root / "sealed-release"
        (release / "app").mkdir(parents=True)
        (release / "app" / "excel-intelligence.exe").write_bytes(b"test")
        (release / "web").mkdir()
        (release / "web" / "index.html").write_text(
            "offline app", encoding="utf-8")
        return release

    def test_builds_the_exact_simple_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = build("Factory Quality", self._sealed_app(root), root / "out")
            self.assertEqual(verify_zip(package), [])
            with zipfile.ZipFile(package) as archive:
                names = set(archive.namelist())
            self.assertIn("Factory Quality/START.bat", names)
            self.assertIn("Factory Quality/QUICK_START.html", names)
            self.assertIn(
                "Factory Quality/Application/app/excel-intelligence.exe", names)

    def test_developer_folders_are_not_exposed_at_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = build("Simple Project", self._sealed_app(root), root / "out")
            with zipfile.ZipFile(package) as archive:
                root_entries = {
                    name.split("/", 2)[1]
                    for name in archive.namelist()
                    if name.count("/") >= 1
                }
            for technical in ("tools", "tests", "projects", ".git"):
                self.assertNotIn(technical, root_entries)

    def test_refuses_a_release_without_the_executable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            empty = root / "empty"
            empty.mkdir()
            with self.assertRaises(PackageError):
                build("Project", empty, root / "out")

    def test_project_name_cannot_be_a_path(self):
        for unsafe in ("../Project", "A/B", "A\\B", "", "."):
            with self.assertRaises(PackageError, msg=unsafe):
                validate_project_name(unsafe)

    def test_launcher_preserves_the_application_exit_code(self):
        launcher = start_script()
        self.assertIn('set "APP_EXIT=%ERRORLEVEL%"', launcher)
        self.assertIn("exit /b %APP_EXIT%", launcher)

    def test_zip_verifier_rejects_windows_style_traversal(self):
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "unsafe.zip"
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("Project\\..\\escape.txt", "unsafe")
            self.assertEqual(verify_zip(package), ["ZIP contains an unsafe path"])


if __name__ == "__main__":
    unittest.main()
