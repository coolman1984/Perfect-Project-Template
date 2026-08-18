from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from factory.project_generator import ProjectGeneratorError, start_project


class TestProjectGenerator(unittest.TestCase):
    def test_new_project_is_project_owned_discovery_not_a_golden_clone(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            destination = start_project(
                "finance_variance", title="Finance Variance", projects_root=root)
            self.assertEqual(destination, root / "finance_variance")
            self.assertTrue((destination / "project.toml").is_file())
            self.assertTrue((destination / "sources.toml").is_file())
            self.assertTrue((destination / "relationships.toml").is_file())
            self.assertTrue((destination / "dashboard.toml").is_file())
            self.assertTrue((destination / "setup_answers.json").is_file())
            self.assertFalse((destination / "report.toml").exists())
            self.assertFalse((destination / "sql").exists())
            self.assertFalse((destination / "pipeline.toml").exists())

            project = (destination / "project.toml").read_text("utf-8")
            self.assertIn('mode = "discovery"', project)
            self.assertIn('purpose = "PENDING_APPROVAL"', project)
            self.assertIn('policy = "policy/security_policy.toml"', project)

            sources = (destination / "sources.toml").read_text("utf-8")
            self.assertNotIn("production_date", sources)
            self.assertNotIn("defect_qty", sources)
            self.assertNotIn("model_code", sources)

            setup = json.loads(
                (destination / "setup_answers.json").read_text("utf-8"))
            self.assertGreaterEqual(len(setup["questions"]), 10)
            self.assertTrue(all(q["answer"] is None for q in setup["questions"]))
            prompts = " ".join(q["prompt"].lower() for q in setup["questions"])
            for forbidden in ("duckdb", "fastapi", "firewall", "retention policy"):
                self.assertNotIn(forbidden, prompts)

    def test_duplicate_or_invalid_project_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            start_project("valid_project", projects_root=root)
            with self.assertRaises(ProjectGeneratorError):
                start_project("valid_project", projects_root=root)
            with self.assertRaises(ProjectGeneratorError):
                start_project("Not Valid", projects_root=root)


if __name__ == "__main__":
    unittest.main()
