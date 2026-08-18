"""Regression tests for the V8.1 deep-audit architecture findings."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from factory.project_contract import load_project
from tools._common import REPO_ROOT
from tools.path_scope import classify_scope


class TestProjectCentricContracts(unittest.TestCase):
    def test_supply_chain_reference_has_three_independent_sources(self):
        project = load_project(REPO_ROOT / "projects" / "_REFERENCE_SUPPLY_CHAIN")
        self.assertEqual(project.source_ids, {"orders", "inventory", "item_master"})
        self.assertEqual(project.source("orders").load_mode, "upsert")
        self.assertEqual(project.source("inventory").load_mode, "snapshot")
        self.assertEqual(project.source("item_master").load_mode, "upsert")

    def test_relationships_are_explicit_and_source_checked(self):
        project = load_project(REPO_ROOT / "projects" / "_REFERENCE_SUPPLY_CHAIN")
        self.assertEqual(len(project.relationships), 2)
        self.assertTrue(all(r.approval_state == "CONFIRMED" for r in project.relationships))
        self.assertEqual({r.cardinality for r in project.relationships}, {"many_to_one"})

    def test_presentation_is_project_configuration_not_frontend_core(self):
        path = REPO_ROOT / "projects" / "_REFERENCE_SUPPLY_CHAIN" / "dashboard.toml"
        self.assertTrue(path.is_file())
        self.assertEqual(classify_scope(path.relative_to(REPO_ROOT)), "presentation")


class TestBaselineAndOwnership(unittest.TestCase):
    def test_baseline_is_git_independent_and_scope_is_machine_readable(self):
        baseline = json.loads((REPO_ROOT / "TEMPLATE_BASELINE.json").read_text("utf-8"))
        self.assertIn("scope_rules", baseline)
        self.assertIn("core_files", baseline)
        self.assertEqual(classify_scope("app/pipeline.py"), "universal_core")
        self.assertEqual(classify_scope("projects/acme/sources.toml"), "project_config")
        self.assertEqual(classify_scope("projects/acme/business_rules/special.py"), "business_logic")

    def test_development_baseline_is_not_falsely_claimed_sealed(self):
        baseline = json.loads((REPO_ROOT / "TEMPLATE_BASELINE.json").read_text("utf-8"))
        self.assertFalse(baseline["sealed"])
        self.assertEqual(baseline["status"], "development_unsealed")


class TestMissingMachineContractsNowExist(unittest.TestCase):
    def test_required_schemas_exist(self):
        names = {
            "template_baseline.schema.json", "project.schema.json",
            "source_registry.schema.json", "relationships.schema.json",
            "adaptation_manifest.schema.json", "reuse_report.schema.json",
            "source_profile.schema.json", "capability_registry.schema.json",
        }
        present = {p.name for p in (REPO_ROOT / "contracts").glob("*.json")}
        self.assertTrue(names <= present, sorted(names - present))

    def test_capability_registry_is_concrete(self):
        registry = json.loads((REPO_ROOT / "capabilities" / "registry.json").read_text("utf-8"))
        ids = {item["id"] for item in registry["capabilities"]}
        for capability in ("source.multi_role_registry", "history.standard_modes", "dashboard.configured", "ai.map_context"):
            self.assertIn(capability, ids)
        for item in registry["capabilities"]:
            self.assertTrue(item["config_entry_points"] or item["id"] == "runtime.loopback")
            self.assertIn("tests", item)
            self.assertIn("limitations", item)


class TestSecurityOwnership(unittest.TestCase):
    def test_profile_policy_defaults_to_metadata_only(self):
        text = (REPO_ROOT / "policy" / "security_policy.toml").read_text("utf-8")
        self.assertIn('default_profile_mode = "metadata_only"', text)
        self.assertIn("raw_values_allowed = false", text)
        self.assertIn("owner = \"IT_SECURITY\"", text)


if __name__ == "__main__":
    unittest.main()
