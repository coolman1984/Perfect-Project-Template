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
    validate_project_id,
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
        (release / "projects" / "alpha").mkdir(parents=True)
        (release / "projects" / "alpha" / "project.toml").write_text(
            'id = "alpha"\n', encoding="utf-8")
        (release / "projects" / "other").mkdir()
        (release / "projects" / "other" / "project.toml").write_text(
            'id = "other"\n', encoding="utf-8")
        (release / "VERSION.json").write_text(
            '{"version":"test"}\n', encoding="utf-8")
        from tools.build_release import write_checksums
        write_checksums(release)
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

    def test_project_id_cannot_be_a_path_or_reference_pack(self):
        for unsafe in ("../alpha", "Alpha", "_REFERENCE_A", "a/b", ""):
            with self.assertRaises(PackageError, msg=unsafe):
                validate_project_id(unsafe)

    def test_project_delivery_contains_only_the_selected_project(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = build(
                "Alpha App", self._sealed_app(root), root / "out",
                project_id="alpha")
            self.assertEqual(verify_zip(package), [])
            with zipfile.ZipFile(package) as archive:
                names = set(archive.namelist())
                version = archive.read(
                    "Alpha App/Application/VERSION.json").decode("utf-8")
            self.assertIn(
                "Alpha App/Application/projects/alpha/project.toml", names)
            self.assertFalse(any("/projects/other/" in name for name in names))
            self.assertIn('"delivery_project_id": "alpha"', version)
            self.assertIn("Alpha App/Application/repair_payload.zip", names)
            self.assertIn("Alpha App/Application/checksums.sha256", names)

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
