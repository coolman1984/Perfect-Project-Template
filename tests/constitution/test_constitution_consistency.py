"""Constitution consistency gates (Constitution Part 34.3)."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from tools import verify_constitution
from tools._common import EXIT_PASS, read_text


class TestConstitutionAudit(unittest.TestCase):
    def test_full_audit_passes(self):
        result = verify_constitution.main(SimpleNamespace(command="audit"))
        self.assertEqual(result, EXIT_PASS)

    def test_cross_references_resolve(self):
        self.assertEqual(
            verify_constitution.main(SimpleNamespace(command="cross-references")),
            EXIT_PASS)

    def test_no_unguarded_downgrade_language(self):
        self.assertEqual(
            verify_constitution.main(SimpleNamespace(command="architecture-terms")),
            EXIT_PASS)

    def test_every_named_command_is_implemented(self):
        self.assertEqual(
            verify_constitution.main(SimpleNamespace(command="commands")),
            EXIT_PASS)


class TestAmendmentDiscipline(unittest.TestCase):
    """Part 36.2 — the constitution has changelog discipline for itself."""

    def setUp(self):
        self.text = read_text(verify_constitution.CONSTITUTION_PATH)
        self.changelog = read_text(verify_constitution.CHANGELOG_PATH)

    def test_original_parts_are_preserved(self):
        # Amendments are additive. Parts 0-35 are the approved 7.1 text.
        for part in (0, 1, 9, 20, 24, 31, 34, 35):
            self.assertIn(f"## PART {part}", self.text)

    def test_amendment_parts_exist(self):
        for part in range(36, 45):
            self.assertIn(f"## PART {part}", self.text)

    def test_amendment_notice_is_present(self):
        self.assertIn("Amendment notice", self.text)

    def test_changelog_records_both_versions(self):
        self.assertIn("| 7.2 |", self.changelog)
        self.assertIn("| 7.1 |", self.changelog)

    def test_seventeen_non_negotiable_rules_survive(self):
        # Part 1.4. If an amendment ever weakened these, this test should fail.
        self.assertIn("seventeen non-negotiable rules", self.text)
        for phrase in ("Never bypass DRM",
                       "Range.Value2",
                       "never as a Windows Service",
                       "All trusted arithmetic lives in tested SQL",
                       "AI never invents business meaning"):
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
