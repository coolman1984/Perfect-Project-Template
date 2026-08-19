"""Reusable AI master ZIP and final cloud-delivery contracts."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from tools.master_template_package import (
    build,
    build_delivery,
    verify_folder,
    verify_zip,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestMasterTemplatePackage(unittest.TestCase):
    def _source(self, root: Path) -> Path:
        source = root / "source"
        source.mkdir()
        required_files = (
            "00_START_HERE_AI_AGENT.md", "AGENTS.md", "CHATGPT.md",
            "CLAUDE.md", "GEMINI.md", "PROJECT_SKILL.md",
            "UNIVERSAL_ENGINE_SKILL.md", "PROJECT_TOOL.bat", "project_tool.sh",
        )
        for name in required_files:
            (source / name).write_text(f"test {name}\n", encoding="utf-8")
        (source / "tools").mkdir()
        (source / "tools" / "portable.py").write_text("VALUE = 1\n", encoding="utf-8")
        (source / "contracts").mkdir()
        for name in ("master_template_package.json", "operator_package.json"):
            (source / "contracts" / name).write_bytes(
                (REPO_ROOT / "contracts" / name).read_bytes())
        (source / "projects" / "_REFERENCE_A").mkdir(parents=True)
        (source / "projects" / "_REFERENCE_A" / "project.toml").write_text(
            'id = "reference_a"\n', encoding="utf-8")
        (source / "projects" / "private_client").mkdir()
        (source / "projects" / "private_client" / "project.toml").write_text(
            'id = "private_client"\n', encoding="utf-8")
        (source / "projects" / "private_client" / "secret.xlsx").write_bytes(b"private")
        core = {
            path.relative_to(source).as_posix(): _digest(path)
            for path in (
                source / "tools" / "portable.py",
                source / "contracts" / "master_template_package.json",
                source / "contracts" / "operator_package.json",
            )
        }
        baseline = {
            "schema_version": 1,
            "template_id": "test-template",
            "template_version": "1.0.0",
            "status": "sealed_master_template",
            "sealed": True,
            "source_commit": "test-commit",
            "core_files": core,
            "scope_rules": [
                {"pattern": "projects/**", "scope": "project_config"},
                {"pattern": "contracts/**", "scope": "universal_core"},
                {"pattern": "tools/**", "scope": "tooling"},
            ],
        }
        (source / "TEMPLATE_BASELINE.json").write_text(
            json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
        return source

    def _release(self, root: Path) -> Path:
        release = root / "release"
        (release / "app").mkdir(parents=True)
        (release / "app" / "excel-intelligence.exe").write_bytes(b"exe")
        (release / "projects" / "_REFERENCE_A").mkdir(parents=True)
        (release / "projects" / "_REFERENCE_A" / "project.toml").write_text(
            'id = "reference_a"\n', encoding="utf-8")
        (release / "projects" / "private_client").mkdir()
        (release / "projects" / "private_client" / "project.toml").write_text(
            'id = "private_client"\n', encoding="utf-8")
        (release / "web").mkdir()
        (release / "web" / "index.html").write_text("offline\n", encoding="utf-8")
        (release / "contracts").mkdir()
        (release / "contracts" / "operator_package.json").write_text(
            '{}\n', encoding="utf-8")
        (release / "START_APP.bat").write_bytes(b"@echo off\r\n")
        (release / "VERSION.json").write_text(
            '{"version":"test"}\n', encoding="utf-8")
        (release / "checksums.sha256").write_text("old\n", encoding="utf-8")
        (release / "IMPLEMENTATION_BASELINE.lock.json").write_text(
            '{}\n', encoding="utf-8")
        return release

    def test_build_excludes_private_projects_and_business_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = build(self._source(root), self._release(root), root / "out")
            self.assertEqual(verify_zip(package), [])
            with zipfile.ZipFile(package) as archive:
                names = set(archive.namelist())
            self.assertIn(
                "MASTER_TEMPLATE/projects/_REFERENCE_A/project.toml", names)
            self.assertFalse(any("private_client" in name for name in names))
            self.assertFalse(any(name.endswith(".xlsx") for name in names))
            self.assertIn("MASTER_TEMPLATE/sealed_runtime/app/excel-intelligence.exe", names)

    def test_verified_master_can_build_single_project_delivery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = build(self._source(root), self._release(root), root / "out")
            extracted = root / "extracted"
            with zipfile.ZipFile(package) as archive:
                archive.extractall(extracted)
            master = extracted / "MASTER_TEMPLATE"
            project = master / "projects" / "client_one"
            project.mkdir()
            (project / "project.toml").write_text(
                'id = "client_one"\n', encoding="utf-8")
            self.assertEqual(verify_folder(master), [])
            delivery = build_delivery(
                master, "client_one", "Client One", root / "delivery")
            with zipfile.ZipFile(delivery) as archive:
                names = set(archive.namelist())
            self.assertIn(
                "Client One/Application/projects/client_one/project.toml", names)
            project_paths = {
                name.split("/projects/", 1)[1].split("/", 1)[0]
                for name in names if "/projects/" in name
            }
            self.assertEqual(project_paths, {"client_one"})


if __name__ == "__main__":
    unittest.main()
