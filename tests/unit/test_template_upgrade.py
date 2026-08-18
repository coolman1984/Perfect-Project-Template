from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.template_upgrade import (
    UpgradeError, apply_upgrade, rollback_upgrade, verify_sealed_root)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_sealed(root: Path, version: str, files: dict[str, str]) -> None:
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    baseline = {
        "schema_version": 1,
        "template_id": "engine",
        "template_version": version,
        "sealed": True,
        "status": "sealed_master_template",
        "scope_rules": [
            {"pattern": "app/**", "scope": "universal_core"},
            {"pattern": "tools/**", "scope": "tooling"},
            {"pattern": "projects/**", "scope": "project_config"},
        ],
        "core_files": {
            relative: digest(root / relative)
            for relative in sorted(files)
        },
    }
    (root / "TEMPLATE_BASELINE.json").write_text(
        json.dumps(baseline, indent=2) + "\n", encoding="utf-8")


class TestTemplateUpgrade(unittest.TestCase):
    def test_apply_changes_only_core_and_rollback_restores_previous_core(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            current = base / "current"
            payload = base / "payload"
            current.mkdir()
            payload.mkdir()
            make_sealed(
                current, "1.0.0",
                {"app/core.txt": "old core", "tools/helper.txt": "old helper"})
            make_sealed(
                payload, "2.0.0",
                {"app/core.txt": "new core", "app/new.txt": "new capability"})
            project = current / "projects" / "finance"
            project.mkdir(parents=True)
            project_file = project / "business_rule.sql"
            project_file.write_text("SELECT 42;", encoding="utf-8")

            backup = apply_upgrade(
                current, payload, validate_projects=False)
            verified = verify_sealed_root(current)
            self.assertEqual(verified["template_version"], "2.0.0")
            self.assertEqual(
                (current / "app/core.txt").read_text("utf-8"), "new core")
            self.assertEqual(
                (current / "app/new.txt").read_text("utf-8"), "new capability")
            self.assertFalse((current / "tools/helper.txt").exists())
            self.assertEqual(project_file.read_text("utf-8"), "SELECT 42;")
            self.assertTrue((current / "UPGRADE_HISTORY.jsonl").is_file())

            rollback_upgrade(current, backup)
            verified = verify_sealed_root(current)
            self.assertEqual(verified["template_version"], "1.0.0")
            self.assertEqual(
                (current / "app/core.txt").read_text("utf-8"), "old core")
            self.assertEqual(
                (current / "tools/helper.txt").read_text("utf-8"), "old helper")
            self.assertFalse((current / "app/new.txt").exists())
            self.assertEqual(project_file.read_text("utf-8"), "SELECT 42;")

    def test_invalid_payload_hash_is_rejected_before_current_core_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            current = base / "current"
            payload = base / "payload"
            current.mkdir()
            payload.mkdir()
            make_sealed(current, "1.0.0", {"app/core.txt": "old core"})
            make_sealed(payload, "2.0.0", {"app/core.txt": "new core"})
            (payload / "app/core.txt").write_text("tampered", encoding="utf-8")
            with self.assertRaises(UpgradeError):
                apply_upgrade(current, payload, validate_projects=False)
            self.assertEqual(
                (current / "app/core.txt").read_text("utf-8"), "old core")
            self.assertEqual(
                verify_sealed_root(current)["template_version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
