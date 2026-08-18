"""Scenarios E, F, G — attacks on the boundary, not the happy path.

These tests try to BREAK the rules the rest of the suite assumes. A control
that has never been attacked is an assumption, not a control.

    E  incomplete business meaning  prototype watermarked, production blocked
    F  missing dependency           fail closed, no reduced fallback
    G  approval bypass              blocked

On G specifically: `factory/approvals.py` documents an honest trust model. An
agent with write access can forge a record, and no test here pretends
otherwise. What these tests prove is that every *casual* and *accidental* route
is closed, and that a forged record is DETECTABLE in review — which is what
makes the pull-request and signed-artifact options meaningful.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from factory import approvals
from factory.questionnaire import Interview
from tools._common import REPO_ROOT


def _approval(**overrides) -> approvals.Approval:
    base = {
        "approval_id": "APR-20260818000000-abcdef12",
        "decision_id": "business_key",
        "report_id": "probe",
        "report_version": 1,
        "approved_value": ["a", "b"],
        "value_hash": approvals.value_hash(["a", "b"]),
        "human_identity": "Sara Ahmed <sara@example.com>",
        "approved_at": "2026-08-18T00:00:00Z",
        "approval_method": "wizard_confirmation",
        "evidence_reference": "setup review 2026-08-18",
    }
    base.update(overrides)
    return approvals.Approval(**base)


class TestScenarioGApprovalBypass(unittest.TestCase):
    """G — every attempt to approve without a legitimate human is refused."""

    def test_agent_cannot_name_itself_as_the_approver(self):
        for identity in ("AI Agent", "Claude", "GPT-4", "automation",
                         "the assistant", "copilot", "build bot", "system"):
            approval = _approval(human_identity=identity)
            problems = approvals.validate(approval)
            self.assertTrue(
                problems,
                f"{identity!r} was accepted as a human approver — an agent may "
                f"propose but never approve (Part 41.3)")

    def test_empty_approver_is_refused(self):
        self.assertTrue(approvals.validate(_approval(human_identity="")))
        self.assertTrue(approvals.validate(_approval(human_identity="   ")))

    def test_unrecognised_approval_method_is_refused(self):
        for method in ("assumed", "implied", "obvious", "auto", "agent_decision"):
            self.assertTrue(
                approvals.validate(_approval(approval_method=method)),
                f"method {method!r} was accepted as a human action")

    def test_approving_the_sentinel_itself_is_refused(self):
        approval = _approval(
            approved_value="PENDING_APPROVAL",
            value_hash=approvals.value_hash("PENDING_APPROVAL"))
        self.assertTrue(approvals.validate(approval))

    def test_missing_evidence_is_refused(self):
        self.assertTrue(approvals.validate(_approval(evidence_reference="")))

    def test_tampered_record_is_detected(self):
        """The value binding is the strongest property this store has."""
        approval = _approval(approved_value=["a", "b"])
        # Someone edits the approved value but leaves the hash alone.
        approval.approved_value = ["a", "b", "c_sneaked_in"]
        problems = approvals.validate(approval)
        self.assertTrue(any("value_hash" in problem for problem in problems))

    def test_record_refuses_to_persist_an_invalid_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(approvals.ApprovalError):
                approvals.record(_approval(human_identity="AI Agent"), root=root)
            self.assertEqual(list(root.glob("*.jsonl")), [],
                             "a refused approval must leave no trace behind")

    def test_changing_the_value_after_approval_voids_it(self):
        """The scenario that matters: approve X, then quietly ship Y."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            approvals.record(_approval(approved_value=["date", "line"],
                                       value_hash=approvals.value_hash(["date", "line"])),
                             root=root)

            still_good = approvals.status_for(
                "probe", {"business_key": ["date", "line"]}, root=root)
            self.assertEqual(still_good[0].state, "CONFIRMED")

            after_edit = approvals.status_for(
                "probe", {"business_key": ["date", "line", "shift"]}, root=root)
            self.assertEqual(after_edit[0].state, "NEEDS_YOUR_APPROVAL")
            self.assertIn("changed after approval", after_edit[0].detail)

    def test_fixture_approval_is_rejected_in_production(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            approvals.record(_approval(approval_method="fixture",
                                       human_identity="Test Fixture Owner"), root=root)
            prototype = approvals.status_for(
                "probe", {"business_key": ["a", "b"]}, root=root, mode="prototype")
            production = approvals.status_for(
                "probe", {"business_key": ["a", "b"]}, root=root, mode="production")
            self.assertEqual(prototype[0].state, "CONFIRMED")
            self.assertEqual(production[0].state, "NEEDS_YOUR_APPROVAL")

    def test_agent_proposal_is_never_binding(self):
        proposal = approvals.propose(
            "business_key", ["date", "line"], "these columns look unique in the sample")
        self.assertFalse(proposal["binding"])
        self.assertIn("HUMAN APPROVAL REQUIRED", proposal["status"])

    def test_cli_refuses_an_agent_approval_end_to_end(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "tools/project_tool.py", "factory", "approve",
             "--id", "line_downtime", "--decision", "business_key",
             "--by", "Claude the AI assistant", "--method", "wizard_confirmation",
             "--evidence", "I checked it myself"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0,
                            "the CLI accepted an agent as a human approver")
        self.assertIn("automated actor", result.stdout + result.stderr)


class TestScenarioEIncompleteBusinessMeaning(unittest.TestCase):
    """E — an unfinished contract may prototype, but must never reach production."""

    def test_unanswered_decisions_stay_unknown(self):
        interview = Interview(report_id="incomplete")
        # Only the human-owned decisions Part 3.1 reserves have a real approval
        # workflow; derived scheduling defaults like lookback_days are not
        # themselves approvable values.
        human_owned = {"business_key", "control_total_column", "storage_allowed"}
        contract = {k: v for k, v in interview.technical_contract().items()
                   if k in human_owned}
        statuses = approvals.status_for("incomplete", contract)
        self.assertTrue(statuses)
        self.assertTrue(all(s.state == "UNKNOWN" for s in statuses))

    def test_production_validation_fails_with_pending_approval(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "tools/project_tool.py", "report", "validate",
             "--id", "line_downtime", "--mode", "production"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        if "no such report" in result.stdout:
            self.skipTest("the employee report is not present in this checkout")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PENDING_APPROVAL", result.stdout)

    def test_prototype_mode_allows_it_but_warns(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "tools/project_tool.py", "report", "validate",
             "--id", "line_downtime", "--mode", "prototype"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        if "no such report" in result.stdout:
            self.skipTest("the employee report is not present in this checkout")
        self.assertEqual(result.returncode, 0)
        self.assertIn("WARNING", result.stdout)


class TestScenarioFFailClosed(unittest.TestCase):
    """F — a missing required component fails closed, never degrades."""

    def test_fixture_adapter_refuses_without_explicit_acknowledgement(self):
        import os

        from app.excel.fixture_adapter import (
            FixtureAdapterNotAcknowledged, FixtureExtractionAdapter,
        )

        saved = os.environ.pop("ADAPTER_FIXTURE_ACK", None)
        try:
            with self.assertRaises(FixtureAdapterNotAcknowledged):
                FixtureExtractionAdapter("tests/fixtures/reference/period_1.csv")
        finally:
            if saved is not None:
                os.environ["ADAPTER_FIXTURE_ACK"] = saved

    def test_com_adapter_raises_rather_than_falling_back_to_fixtures(self):
        """Part 44.3 rule 4: COM failure must never silently select fixtures."""
        from app.excel.com_adapter import ComExtractionAdapter

        adapter = ComExtractionAdapter()
        with self.assertRaises(NotImplementedError):
            adapter.open("C:/nowhere.xlsx", {})

    def test_unregistered_error_code_cannot_be_raised(self):
        from app.errors import AppError

        with self.assertRaises(KeyError):
            AppError("I_MADE_THIS_UP")

    def test_unknown_load_mode_is_refused(self):
        """The engine never guesses a human-owned decision."""
        try:
            import duckdb  # noqa: F401
        except ImportError:
            self.skipTest("duckdb is an application-tier dependency")

        from app.data.database import Database
        from app.data.history import HistoryEngine, HistoryError

        with tempfile.TemporaryDirectory() as temporary:
            database = Database(Path(temporary) / "probe.duckdb")
            engine = HistoryEngine(
                database, history_table="analytics.h", clean_table="clean.c",
                business_columns=["a"], key_columns=["a"], event_date_column="d")
            with self.assertRaises(HistoryError):
                engine.apply("RUN-1", load_mode="whatever_seems_reasonable")
            database.close()

    def test_metric_not_in_approved_sql_is_refused(self):
        """No trusted number may be produced outside approved SQL (Part 10.2)."""
        try:
            import duckdb  # noqa: F401
        except ImportError:
            self.skipTest("duckdb is an application-tier dependency")

        from app.analytics.runner import MetricError, SqlRunner
        from app.data.database import Database

        with tempfile.TemporaryDirectory() as temporary:
            database = Database(Path(temporary) / "probe.duckdb")
            runner = SqlRunner(database, REPO_ROOT / "reports" / "_REFERENCE" / "sql")
            with self.assertRaises(MetricError):
                runner.run_named("metrics.sql", "a_metric_i_invented")
            database.close()


class TestReferenceCannotSatisfyProductionGate(unittest.TestCase):
    """No amount of fixture testing advances the protected-file gate."""

    def test_protected_file_gate_is_not_pass(self):
        from tools import gates

        gate = next(r for r in gates.load_ledger()
                    if r["id"] == "GATE_PROTECTED_FILE_PROOF")
        self.assertNotEqual(
            gate["status"], "pass",
            "the protected-file gate may only be satisfied by a real COM read "
            "of a real protected workbook (Part 44.3 rule 3)")

    def test_reference_report_is_never_in_production_mode(self):
        import tomllib

        config = tomllib.loads(
            (REPO_ROOT / "reports" / "_REFERENCE" / "report.toml").read_text("utf-8"))
        self.assertNotEqual(config.get("mode"), "production")
        self.assertEqual(config["excel"]["adapter"], "fixture")

    def test_fixture_adapter_declares_it_is_not_production_evidence(self):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        self.assertFalse(FixtureExtractionAdapter.provides_production_evidence)


if __name__ == "__main__":
    unittest.main()
