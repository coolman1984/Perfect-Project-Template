from __future__ import annotations

import unittest

from factory.project_build_brief import build_project_brief
from tools._common import REPO_ROOT


class TestProjectBuildBrief(unittest.TestCase):
    def test_reference_brief_contains_structure_not_fixture_rows(self):
        text = build_project_brief(
            "reference_supply_chain", projects_root=REPO_ROOT / "projects")
        for source_id in ("orders", "inventory", "item_master"):
            self.assertIn(source_id, text)
        self.assertIn("orders_to_item", text)
        self.assertIn("REUSE_AS_IS", text)
        self.assertIn("capabilities/registry.json", text)
        self.assertIn("Estimated routed tokens", text)
        # These values exist only inside synthetic raw fixture rows and should
        # never be copied into the AI build brief.
        for raw_value in ("O1", "Item A", "2026-08-03,W1,I3,5"):
            self.assertNotIn(raw_value, text)


if __name__ == "__main__":
    unittest.main()
