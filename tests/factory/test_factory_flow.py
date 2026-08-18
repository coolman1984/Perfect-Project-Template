"""The Factory: business setup, approvals, generation, and the core boundary.

The question every test here answers is the one that decides whether this
repository is a factory or a pile of copy-pasted demos:

    Can a new report be created through CONFIGURATION, without editing the
    shared engine?
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from factory import approvals
from factory.generator import GeneratorError, generate
from factory.questionnaire import (
    CORE_QUESTIONS, LOAD_MODE_BY_ANSWER, Interview,
)
from tools._common import REPO_ROOT

#: Shared engine. An ordinary new report must not change a single byte of this.
FACTORY_CORE_PATHS = (
    "app/pipeline.py", "app/orchestrator.py", "app/state_machine.py",
    "app/errors.py", "app/data/database.py", "app/data/history.py",
    "app/data/staging.py", "app/data/migrations.py", "app/data/archive.py",
    "app/quality/engine.py", "app/quality/reconciliation.py",
    "app/quality/quarantine.py", "app/analytics/runner.py",
    "app/local_transport.py", "app/server.py",
    "contracts/run_states.json", "contracts/error_codes.json",
    "contracts/dashboard.schema.json", "contracts/report_config.schema.json",
    "tools/project_tool.py", "tools/_common.py",
    "factory/generator.py", "factory/questionnaire.py", "factory/approvals.py",
)


def _fingerprint(paths) -> dict[str, str]:
    return {
        path: hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest()
        for path in paths if (REPO_ROOT / path).exists()
    }


def _complete_interview(report_id: str = "probe_report") -> Interview:
    interview = Interview(report_id=report_id)
    interview.answers.update({
        "purpose": "The weekly scrap report I build by hand",
        "sources": ["scrap.xlsx"],
        "grain": "One scrap event on one machine on one date",
        "control_total_column": "Total scrap weight",
        "corrections": "can_be_corrected",
        "correction_window": "14",
        "disappearing_rows": "mark_inactive",
        "dashboard_decision": "Which machine wastes the most material",
        "business_owner": "Quality Lead - Omar Hassan",
        "storage_allowed": ["D:/secure/scrap"],
        "business_key_columns": ["event_date", "machine", "event_id"],
    })
    return interview


class TestPlainLanguageTranslation(unittest.TestCase):
    """The employee answers business questions; the Factory does the jargon."""

    def test_no_core_question_uses_technical_vocabulary(self):
        jargon = ("grain", "upsert", "snapshot", "idempot", "schema", "primary key",
                  "foreign key", "sql", "duckdb", "parquet", "api", "com ",
                  "load mode", "business key")
        for question in CORE_QUESTIONS:
            text = question.prompt.lower()
            for term in jargon:
                self.assertNotIn(
                    term, text,
                    f"question {question.id!r} exposes the word {term!r} to a "
                    f"non-technical employee: {question.prompt!r}")

    def test_every_question_explains_why_it_is_asked(self):
        for question in CORE_QUESTIONS:
            self.assertTrue(question.why.strip(),
                            f"{question.id} does not say why it is asked")

    def test_plain_answers_map_to_every_load_mode(self):
        # All four Part 8.1 modes must be reachable without the employee ever
        # seeing their names.
        self.assertEqual(
            set(LOAD_MODE_BY_ANSWER.values()),
            {"append", "upsert", "snapshot", "replace_period"})

    def test_corrections_answer_becomes_upsert(self):
        interview = _complete_interview()
        self.assertEqual(interview.load_mode(), "upsert")
        self.assertEqual(interview.lookback_days(), 14)

    def test_unanswered_questions_stay_pending_approval(self):
        interview = Interview(report_id="empty")
        contract = interview.technical_contract()
        for key in ("business_key", "control_total_column", "storage_allowed"):
            self.assertEqual(contract[key], "PENDING_APPROVAL",
                             f"{key} was invented instead of left for a human")

    def test_progressive_disclosure_hides_irrelevant_questions(self):
        interview = Interview(report_id="x")
        interview.answer("corrections", "only_new")
        visible = {q.id for q in interview.visible_questions()}
        self.assertNotIn("correction_window", visible,
                         "the lookback question must not appear when nothing "
                         "is ever corrected")

    def test_understanding_review_is_plain_language(self):
        review = _complete_interview().understanding_review()
        self.assertTrue(review)
        for item in review:
            self.assertTrue(item["item"] and item["understanding"])
            self.assertTrue(item["explanation"],
                            "every reviewed item explains itself")


class TestFactoryCoreBoundary(unittest.TestCase):
    """Creating a report must not touch the shared engine."""

    def test_generating_a_report_changes_no_factory_core_file(self):
        before = _fingerprint(FACTORY_CORE_PATHS)

        with tempfile.TemporaryDirectory() as temporary:
            interview = _complete_interview("boundary_probe")
            generate(interview, title="Boundary Probe",
                     reports_root=Path(temporary))

        after = _fingerprint(FACTORY_CORE_PATHS)
        changed = sorted(path for path in before if before[path] != after.get(path))
        self.assertEqual(
            changed, [],
            f"creating a report modified Factory Core: {changed}. A new report is "
            f"configuration, not engine surgery.")

    def test_generated_report_only_writes_inside_its_own_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            interview = _complete_interview("scope_probe")
            project = generate(interview, title="Scope Probe", reports_root=root)

            written = {p for p in root.rglob("*") if p.is_file()}
            outside = [p for p in written if project.directory not in p.parents]
            self.assertEqual(outside, [],
                             "the generator wrote outside the report directory")

    def test_generated_report_is_seeded_from_the_golden_reference(self):
        """New reports start from the proven pattern, not from a blank page."""
        with tempfile.TemporaryDirectory() as temporary:
            interview = _complete_interview("seed_probe")
            project = generate(interview, title="Seed Probe",
                               reports_root=Path(temporary))
            for expected in ("sql/clean.sql", "sql/metrics.sql", "sql/checks.sql",
                             "pipeline.toml", "report.toml"):
                self.assertTrue((project.directory / expected).exists(),
                                f"generated report is missing {expected}")

    def test_refuses_to_overwrite_an_existing_report(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            interview = _complete_interview("dup_probe")
            generate(interview, title="Dup", reports_root=root)
            with self.assertRaises(GeneratorError):
                generate(interview, title="Dup", reports_root=root)


class TestGeneratedContract(unittest.TestCase):
    def setUp(self) -> None:
        self._temp = tempfile.TemporaryDirectory()
        self.project = generate(
            _complete_interview("contract_probe"), title="Contract Probe",
            reports_root=Path(self._temp.name))
        self.config_text = (self.project.directory / "report.toml").read_text("utf-8")

    def tearDown(self) -> None:
        self._temp.cleanup()

    def test_translated_values_reach_the_contract(self):
        import tomllib
        config = tomllib.loads(self.config_text)
        self.assertEqual(config["load_mode"], "upsert")
        self.assertEqual(config["history"]["lookback_days"], 14)
        self.assertEqual(config["history"]["deletion_rule"], "mark_inactive")
        self.assertEqual(config["quality"]["control_total_column"], "Total scrap weight")

    def test_undecided_values_remain_pending_approval(self):
        self.assertIn("PENDING_APPROVAL", self.config_text,
                      "the generator must not invent values it was not told")

    def test_generated_report_uses_the_production_adapter(self):
        # Only the Golden Reference runs on fixtures (Part 44.3).
        import tomllib
        config = tomllib.loads(self.config_text)
        self.assertEqual(config["excel"]["adapter"], "com")

    def test_definition_explains_meaning_not_implementation(self):
        definition = (self.project.directory / "report_definition.md").read_text("utf-8")
        # Normalise wrapping AND blockquote markers before asserting on prose:
        # the document is correct even when a sentence breaks across lines
        # inside a "> " quoted block.
        flat = " ".join(
            line.lstrip("> ").strip() for line in definition.splitlines())
        flat = " ".join(flat.split())
        self.assertIn("approves the meaning below, not the implementation", flat)
        self.assertIn("One record", definition)
        self.assertIn("What one row in your file represents", definition)


class TestBuildBrief(unittest.TestCase):
    """The agent work package must be complete and must carry no raw data."""

    def setUp(self) -> None:
        from factory import build_brief
        self.brief = build_brief.generate("line_downtime") \
            if (REPO_ROOT / "reports" / "line_downtime" / "report.toml").exists() else None

    def test_brief_names_the_core_boundary(self):
        if self.brief is None:
            self.skipTest("no employee report configured")
        self.assertIn("Factory Core", self.brief)
        self.assertIn("app/pipeline.py", self.brief)
        self.assertIn("Variation points", self.brief)

    def test_brief_points_at_the_golden_reference(self):
        if self.brief is None:
            self.skipTest("no employee report configured")
        self.assertIn("_REFERENCE", self.brief)
        self.assertIn("Do not redesign it", self.brief)

    def test_brief_lists_required_tests_and_gates(self):
        if self.brief is None:
            self.skipTest("no employee report configured")
        self.assertIn("unittest discover", self.brief)
        self.assertIn("GATE_CONTROL_TOTAL", self.brief)

    def test_brief_contains_no_raw_business_rows(self):
        if self.brief is None:
            self.skipTest("no employee report configured")
        # Part 30.5: structure and approved meaning only.
        for fixture_value in ("ORD-1001", "MDL-A", "1200,12"):
            self.assertNotIn(fixture_value, self.brief)


class TestProjectHealthDerivesFromEvidence(unittest.TestCase):
    def test_every_health_item_explains_itself(self):
        from factory.health import project_health

        for item in project_health():
            self.assertTrue(item.what_it_means.strip(), item.area)
            self.assertTrue(item.why_it_matters.strip(), item.area)
            self.assertTrue(item.what_remains.strip(), item.area)
            self.assertTrue(item.who_acts.strip(), item.area)

    def test_health_shows_no_invented_percentages(self):
        from factory.health import project_health, render

        text = render(project_health())
        self.assertNotIn("%", text,
                         "project health must not show a meaningless percentage")


if __name__ == "__main__":
    unittest.main()
