"""Golden Reference: the complete workflow, scenarios A-G (Constitution Part 15).

This is the executable specification. Every number asserted here was derived by
hand from the fixtures *before* the pipeline existed — see the derivation in
`tests/expected/reference/expected.json`. A test that merely records what the
code produced would pass just as happily with a broken formula.

Scenarios, from the Factory brief:

    A  first project        end to end, quality PASS, history committed
    B  same file twice      no duplicate history, identical totals
    C  correction           old record updated, metrics change correctly
    D  bad file             quality FAIL, trusted history untouched
    E  incomplete meaning   prototype watermarked, production blocked
    F  missing dependency   fail closed, no reduced fallback
    G  approval bypass      blocked

E, F and G live in `tests/adversarial/` because they are about defending the
boundary rather than exercising the happy path.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from tools._common import REPO_ROOT

try:
    import duckdb  # noqa: F401
    HAS_DUCKDB = True
except ImportError:  # pragma: no cover - exercised on the portable CI tier
    HAS_DUCKDB = False

FIXTURES = REPO_ROOT / "tests" / "fixtures" / "reference"
EXPECTED = json.loads(
    (REPO_ROOT / "tests" / "expected" / "reference" / "expected.json").read_text("utf-8"))


def decimal_of(value) -> Decimal:
    return Decimal(str(value))


@unittest.skipUnless(HAS_DUCKDB, "duckdb is an application-tier dependency")
class ReferencePipelineTestCase(unittest.TestCase):
    """Shared harness: a fresh database per test, torn down afterwards."""

    def setUp(self) -> None:
        from app.data.database import Database
        from app.pipeline import Pipeline, ReportContract

        os.environ["ADAPTER_FIXTURE_ACK"] = "1"
        self._temp = tempfile.TemporaryDirectory()
        self.contract = ReportContract(REPO_ROOT / "reports" / "_REFERENCE")
        self.database = Database(Path(self._temp.name) / "reference.duckdb")
        self.pipeline = Pipeline(self.database, self.contract)
        self.pipeline.prepare()

    def tearDown(self) -> None:
        self.database.close()
        self._temp.cleanup()
        os.environ.pop("ADAPTER_FIXTURE_ACK", None)

    def run_fixture(self, filename: str, run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        path = FIXTURES / filename
        adapter = FixtureExtractionAdapter(path)
        adapter.open(str(path), {
            "report_id": self.contract.report_id,
            "run_id": run_id,
            "sheet": "Raw Data",
            "extraction": self.contract.report["extraction"],
        })
        return self.pipeline.run(run_id, adapter)

    # convenience readers -------------------------------------------------

    def produced_total(self) -> Decimal:
        return decimal_of(self.database.scalar(
            "SELECT COALESCE(SUM(produced_qty), 0) FROM analytics.history_production "
            "WHERE is_active = TRUE"))

    def defect_total(self) -> Decimal:
        return decimal_of(self.database.scalar(
            "SELECT COALESCE(SUM(defect_qty), 0) FROM analytics.history_production "
            "WHERE is_active = TRUE"))

    def active_rows(self) -> int:
        return int(self.database.scalar(
            "SELECT count(*) FROM analytics.history_production WHERE is_active = TRUE"))


class TestScenarioAFirstProject(ReferencePipelineTestCase):
    """A — a fresh project processes its first period successfully."""

    def test_first_period_completes_with_expected_totals(self):
        expected = EXPECTED["after_period_1"]
        outcome = self.run_fixture("period_1.csv", "RUN-20260818-001")

        self.assertEqual(outcome.status, "COMPLETE")
        self.assertEqual(outcome.quality_status, expected["quality_status"])
        self.assertEqual(outcome.rows_extracted, expected["rows_extracted"])
        self.assertEqual(outcome.history.inserted, expected["inserted"])
        self.assertEqual(outcome.history.updated, expected["updated"])
        self.assertEqual(self.produced_total(), decimal_of(expected["produced_total"]))
        self.assertEqual(self.defect_total(), decimal_of(expected["defect_total"]))
        self.assertEqual(self.active_rows(), expected["active_rows"])

    def test_control_total_difference_is_exactly_zero(self):
        # Part 9.4: not "approximately". Exactly zero, or the run fails.
        outcome = self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.assertTrue(outcome.control_totals)
        for control in outcome.control_totals:
            self.assertEqual(control.difference, Decimal(0))
            self.assertTrue(control.balances)

    def test_every_quality_check_ran(self):
        outcome = self.run_fixture("period_1.csv", "RUN-20260818-001")
        check_ids = {r.check_id for r in outcome.quality_report.results}
        for required in ("structural.required_columns", "row.business_key_not_blank",
                         "dataset.duplicate_business_key", "population.equation",
                         "control_total.produced_qty"):
            self.assertIn(required, check_ids)

    def test_output_is_watermarked_as_demo_data(self):
        # Part 44.3 rule 2: fixture output must never look production-ready.
        outcome = self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.assertTrue(outcome.demo_data)
        self.assertTrue(outcome.dashboard["demo_data"])

    def test_dashboard_package_validates_against_its_contract(self):
        outcome = self.run_fixture("period_1.csv", "RUN-20260818-001")
        dashboard = outcome.dashboard
        for key in ("schema_version", "report", "freshness", "quality",
                    "kpis", "charts", "lineage"):
            self.assertIn(key, dashboard)
        for chart in dashboard["charts"]:
            # Meaning must never depend on the picture alone (Part 22.9).
            self.assertTrue(chart["accessible_summary"].strip())
            self.assertTrue(chart["title"].endswith("?"),
                            "a chart title must be a plain-language question (Part 11.4)")


class TestScenarioBIdempotentRerun(ReferencePipelineTestCase):
    """B — running the same input twice changes nothing (rule 5)."""

    def test_same_file_twice_creates_no_duplicates(self):
        self.run_fixture("period_1.csv", "RUN-20260818-001")
        produced_before, rows_before = self.produced_total(), self.active_rows()

        second = self.run_fixture("period_1.csv", "RUN-20260818-002")

        self.assertEqual(second.history.inserted, 0)
        self.assertEqual(second.history.updated, 0)
        self.assertEqual(second.history.unchanged, 6)
        self.assertEqual(self.produced_total(), produced_before)
        self.assertEqual(self.active_rows(), rows_before)

    def test_rerun_after_correction_is_also_idempotent(self):
        expected = EXPECTED["idempotent_rerun"]
        self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.run_fixture("period_2.csv", "RUN-20260818-002")
        third = self.run_fixture("period_2.csv", "RUN-20260818-003")

        self.assertEqual(third.history.inserted, expected["inserted"])
        self.assertEqual(third.history.updated, expected["updated"])
        self.assertEqual(third.history.unchanged, expected["unchanged"])
        self.assertEqual(self.produced_total(), decimal_of(expected["produced_total"]))
        self.assertEqual(self.active_rows(), expected["active_rows"])


class TestScenarioCCorrection(ReferencePipelineTestCase):
    """C — a corrected historical record updates in place."""

    def setUp(self) -> None:
        super().setUp()
        self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.outcome = self.run_fixture("period_2.csv", "RUN-20260818-002")

    def test_totals_match_the_hand_derived_values(self):
        expected = EXPECTED["after_period_2"]
        self.assertEqual(self.outcome.quality_status, expected["quality_status"])
        self.assertEqual(self.produced_total(), decimal_of(expected["produced_total"]))
        self.assertEqual(self.defect_total(), decimal_of(expected["defect_total"]))
        self.assertEqual(self.active_rows(), expected["active_rows"])

    def test_correction_updates_the_existing_record_rather_than_inserting(self):
        expected = EXPECTED["after_period_2"]
        record = expected["corrected_record"]
        self.assertEqual(self.outcome.history.updated, expected["updated"])
        self.assertEqual(self.outcome.history.inserted, expected["inserted"])

        rows = self.database.query(
            "SELECT produced_qty FROM analytics.history_production "
            "WHERE order_number = ? AND is_active = TRUE", [record["order_number"]])
        self.assertEqual(len(rows), 1, "the correction must not create a second row")
        self.assertEqual(decimal_of(rows[0][0]),
                         decimal_of(record["produced_qty_after"]))

    def test_duplicate_row_is_filtered_and_named(self):
        expected = EXPECTED["after_period_2"]
        self.assertEqual(self.outcome.rows_filtered, expected["rows_filtered"])
        self.assertEqual(self.outcome.quarantine.get("EXACT_DUPLICATE"),
                         expected["quarantine"]["EXACT_DUPLICATE"])

    def test_negative_row_is_rejected_to_quarantine_not_dropped(self):
        # Part 9.5: nothing is ever silently dropped.
        expected = EXPECTED["after_period_2"]
        self.assertEqual(self.outcome.rows_rejected, expected["rows_rejected"])
        self.assertEqual(self.outcome.quarantine.get("NEGATIVE_MEASURE"),
                         expected["quarantine"]["NEGATIVE_MEASURE"])
        retained = self.database.scalar(
            "SELECT count(*) FROM quality.quarantine WHERE reason_code = ?",
            ["NEGATIVE_MEASURE"])
        self.assertEqual(int(retained), 1)

    def test_unexpected_category_warns_but_still_loads(self):
        warnings = [r for r in self.outcome.quality_report.results
                    if r.status == "WARNING"]
        self.assertTrue(any("category" in r.check_id for r in warnings))
        loaded = self.database.scalar(
            "SELECT count(*) FROM analytics.history_production "
            "WHERE category = 'trial' AND is_active = TRUE")
        self.assertEqual(int(loaded), 1)

    def test_population_equation_balances(self):
        # Part 25.3: source = accepted + rejected + filtered, always.
        population = [r for r in self.outcome.quality_report.results
                      if r.check_id == "population.equation"]
        self.assertEqual(len(population), 1)
        self.assertEqual(population[0].status, "PASS")


class TestScenarioDBadFilePreservesTruth(ReferencePipelineTestCase):
    """D — a blocking quality failure never touches trusted history."""

    def test_failure_leaves_history_and_last_good_output_intact(self):
        expected = EXPECTED["blocking_failure"]
        self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.run_fixture("period_2.csv", "RUN-20260818-002")
        produced_before, rows_before = self.produced_total(), self.active_rows()

        outcome = self.run_fixture("period_3_bad.csv", "RUN-20260818-004")

        self.assertEqual(outcome.status, expected["run_status"])
        self.assertEqual(outcome.quality_status, expected["quality_status"])
        self.assertEqual(outcome.error_code, expected["error_code"])
        # The golden rule: the dashboard keeps showing the last good data.
        self.assertEqual(self.produced_total(), produced_before)
        self.assertEqual(self.active_rows(), rows_before)
        self.assertEqual(self.produced_total(),
                         decimal_of(expected["produced_total_unchanged"]))

    def test_failure_error_code_is_in_the_registry(self):
        from app.errors import registry

        self.run_fixture("period_1.csv", "RUN-20260818-001")
        outcome = self.run_fixture("period_3_bad.csv", "RUN-20260818-002")
        self.assertIn(outcome.error_code, registry())
        # The operator is always told their data is safe (Part 22.8).
        self.assertTrue(registry()[outcome.error_code].preserves_history)


class TestReferenceMetrics(ReferencePipelineTestCase):
    """The calculated numbers a manager would actually look at."""

    def setUp(self) -> None:
        super().setUp()
        self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.outcome = self.run_fixture("period_2.csv", "RUN-20260818-002")

    def test_weighted_defect_rate_matches_hand_calculation(self):
        from app.analytics.runner import weighted_rate_ppm

        rate = weighted_rate_ppm(self.defect_total(), self.produced_total())
        self.assertEqual(
            rate.quantize(Decimal("0.01")),
            Decimal(EXPECTED["metrics"]["defect_rate_ppm_rounded_2dp"]))

    def test_trend_matches_hand_calculation(self):
        rows = self.pipeline.sql.run_named("metrics.sql", "trend_by_date")
        # Compare Decimals, not their text. Decimal("3000").normalize() renders
        # as "3E+3", which would fail for a value that is in fact correct.
        actual = [(str(row[0]), decimal_of(row[1])) for row in rows]
        expected = [(date, Decimal(value))
                    for date, value in EXPECTED["metrics"]["trend_produced_by_date"]]
        self.assertEqual(actual, expected)

    def test_pareto_ranks_contributors_correctly(self):
        rows = self.pipeline.sql.run_named("metrics.sql", "pareto_by_model")
        actual = [(row[0], decimal_of(row[1])) for row in rows]
        expected = [(model, Decimal(value))
                    for model, value in EXPECTED["metrics"]["pareto_defects_by_model"]]
        self.assertEqual(actual, expected)

    def test_pareto_cumulative_share_reaches_one_hundred(self):
        rows = self.pipeline.sql.run_named("metrics.sql", "pareto_by_model")
        self.assertAlmostEqual(float(rows[-1][2]), 100.0, places=6)

    def test_top_contributor_is_identified(self):
        rows = self.pipeline.sql.run_named("metrics.sql", "top_contributor")
        self.assertEqual(rows[0][0], EXPECTED["metrics"]["top_contributor"])
        self.assertEqual(decimal_of(rows[0][1]),
                         decimal_of(EXPECTED["metrics"]["top_contributor_defects"]))

    def test_insight_is_evidence_backed_and_avoids_causal_language(self):
        insights = self.outcome.dashboard["insights"]
        self.assertTrue(insights, "the reference must produce at least one insight")
        for insight in insights:
            self.assertTrue(insight["evidence_refs"],
                            "every insight links to its evidence (Part 10.3)")
            self.assertEqual(insight["confidence"], "verified")
            self.assertNotIn("root cause", insight["text"].lower(),
                             "contributors are not root causes (Part 26.12)")
        self.assertLessEqual(len(insights), 5, "at most five insights (Part 10.3)")

    def test_lineage_drill_through_reaches_source_rows(self):
        expected = EXPECTED["lineage_drill_through"]
        rows = self.pipeline.sql.run_named(
            "metrics.sql", "lineage_for_model", [expected["model_code"]])
        self.assertEqual(len(rows), expected["row_count"])
        self.assertEqual(sum(decimal_of(row[4]) for row in rows),
                         decimal_of(expected["produced_total"]))
        for row in rows:
            # Every number traces back to a source file and row (rule 8).
            self.assertTrue(row[6], "missing source file in lineage")
            self.assertIsNotNone(row[7], "missing source row number in lineage")

    def test_dashboard_filter_definitions_exist(self):
        definitions = self.outcome.dashboard["filters"]["definitions"]
        self.assertTrue(definitions)
        self.assertIn("model_code", {d["id"] for d in definitions})


class TestArchiveRebuild(ReferencePipelineTestCase):
    """Recovery: a fresh database rebuilds from the Parquet archive alone."""

    def test_history_rebuilds_from_archive_and_reconciles(self):
        from app.data.archive import archive_history, rebuild_history_from_archive

        self.run_fixture("period_1.csv", "RUN-20260818-001")
        self.run_fixture("period_2.csv", "RUN-20260818-002")
        produced_before, rows_before = self.produced_total(), self.active_rows()

        archive_root = Path(self._temp.name) / "archive"
        archive_history(
            self.database, history_table="analytics.history_production",
            report_id="_reference", archive_root=archive_root,
            event_date_column="production_date")

        self.database.execute("DELETE FROM analytics.history_production")
        self.assertEqual(self.active_rows(), 0)

        restored = rebuild_history_from_archive(
            self.database, history_table="analytics.history_production",
            archive_root=archive_root, report_id="_reference")

        self.assertEqual(restored, rows_before)
        self.assertEqual(self.produced_total(), produced_before)


if __name__ == "__main__":
    unittest.main()
