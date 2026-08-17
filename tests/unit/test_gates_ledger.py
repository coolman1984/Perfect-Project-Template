"""Acceptance gate ledger integrity (Constitution Part 38)."""

from __future__ import annotations

import unittest

from tools import gates


class TestGateLedger(unittest.TestCase):
    def setUp(self):
        self.records = gates.load_ledger()

    def test_ledger_is_populated(self):
        self.assertGreater(len(self.records), 30,
                           "the ledger should cover Parts 14, 28.1, 31.1 and 33")

    def test_ids_are_unique(self):
        ids = [record["id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))

    def test_statuses_and_severities_are_valid(self):
        for record in self.records:
            self.assertIn(record["status"], gates.VALID_STATUS, record["id"])
            self.assertIn(record["severity"], gates.VALID_SEVERITY, record["id"])

    def test_every_gate_cites_a_constitution_part(self):
        for record in self.records:
            self.assertTrue(record.get("part", "").strip(),
                            f"{record['id']} does not cite a Part")

    def test_passing_gates_cite_evidence_that_exists(self):
        # Part 38.2 rule 1: a gate cannot pass on a sentence.
        for record in self.records:
            if record["status"] != "pass":
                continue
            evidence = record.get("evidence", "").strip()
            self.assertTrue(evidence, f"{record['id']} passes with no evidence")
            self.assertTrue((gates.REPO_ROOT / evidence).exists(),
                            f"{record['id']} cites missing evidence: {evidence}")

    def test_conditional_gates_name_a_reason_and_next_action(self):
        for record in self.records:
            if record["status"] != "conditional":
                continue
            self.assertTrue(record.get("conditional_reason", "").strip(), record["id"])
            self.assertTrue(record.get("next_action", "").strip(), record["id"])

    def test_not_applicable_gates_explain_themselves(self):
        for record in self.records:
            if record["status"] == "not_applicable":
                self.assertTrue(record.get("conditional_reason", "").strip(),
                                f"{record['id']} is N/A with no reason")

    def test_protected_file_gate_exists_and_is_blocking(self):
        # Part 44.3 rule 3: no fixture testing can ever advance this gate.
        gate = next(r for r in self.records if r["id"] == "GATE_PROTECTED_FILE_PROOF")
        self.assertEqual(gate["severity"], "block")

    def test_open_gates_name_a_next_action(self):
        for record in self.records:
            if record["status"] in ("not_started", "in_progress", "fail"):
                self.assertTrue(record.get("next_action", "").strip(),
                                f"{record['id']} is open with no next action")


if __name__ == "__main__":
    unittest.main()
