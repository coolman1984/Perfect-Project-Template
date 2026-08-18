"""Quality gate: the trust layer (Constitution Part 9).

Every run ends with exactly one verdict:

    PASS      safe to commit
    WARNING   continue; that rule is non-blocking
    FAIL      trusted history is NOT touched

Report-specific thresholds live in `quality.toml`. The rules themselves are
Factory Core and are the same for every report — that is what makes a new
report configuration rather than new engine code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.data.database import Database

PASS, WARNING, FAIL = "PASS", "WARNING", "FAIL"


@dataclass
class CheckResult:
    check_id: str
    scope: str
    severity: str          # "fail" | "warning"
    status: str            # PASS | WARNING | FAIL
    message: str
    expected: str = ""
    actual: str = ""
    difference: str = ""
    tolerance: str = ""
    evidence: str = ""


@dataclass
class QualityReport:
    run_id: str
    results: list[CheckResult] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    @property
    def status(self) -> str:
        if any(r.status == FAIL for r in self.results):
            return FAIL
        if any(r.status == WARNING for r in self.results):
            return WARNING
        return PASS

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == PASS)

    @property
    def warnings(self) -> int:
        return sum(1 for r in self.results if r.status == WARNING)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == FAIL)

    def blocking_failures(self) -> list[CheckResult]:
        return [r for r in self.results if r.status == FAIL]

    def persist(self, database: Database) -> None:
        now = datetime.now(timezone.utc)
        for result in self.results:
            database.execute(
                "INSERT INTO quality.check_result (run_id, check_id, scope, severity, "
                "status, expected, actual, difference, tolerance, message, evidence, "
                "checked_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [self.run_id, result.check_id, result.scope, result.severity,
                 result.status, result.expected, result.actual, result.difference,
                 result.tolerance, result.message, result.evidence, now],
            )


class QualityEngine:
    """Executes the configured checks against one run's staged data."""

    def __init__(self, database: Database, config: dict[str, Any]) -> None:
        self.database = database
        self.config = config
        self.quality_config = config.get("quality", {})

    # -- structural (Part 9.1) --------------------------------------------

    def check_required_columns(
        self, report: QualityReport, present: list[str], required: list[str]
    ) -> None:
        """A required column that is missing or renamed is a hard FAIL.

        Never fuzzy-match an important field: a confidently wrong column
        mapping is worse than a stopped run (Part 9.1).
        """
        missing = [column for column in required if column not in present]
        report.add(CheckResult(
            check_id="structural.required_columns",
            scope="structure",
            severity="fail",
            status=FAIL if missing else PASS,
            expected=", ".join(required),
            actual=", ".join(present),
            message=(f"required column(s) missing from the source: {', '.join(missing)}"
                     if missing else "all required columns present"),
        ))

    # -- row checks (Part 9.2) --------------------------------------------

    def check_no_blank_business_key(
        self, report: QualityReport, table: str, run_id: str, key_columns: list[str]
    ) -> None:
        condition = " OR ".join(
            f"{column} IS NULL OR trim({column}) = ''" for column in key_columns)
        blank = self.database.scalar(
            f"SELECT count(*) FROM {table} WHERE _run_id = ? AND ({condition})", [run_id])
        report.add(CheckResult(
            check_id="row.business_key_not_blank",
            scope="row",
            severity="fail",
            status=FAIL if blank else PASS,
            expected="0",
            actual=str(blank),
            message=f"{blank} row(s) have a blank business key" if blank
                    else "every row has a complete business key",
        ))

    def check_non_negative(
        self, report: QualityReport, table: str, run_id: str, columns: list[str]
    ) -> None:
        """Rejected rows are quarantined by the caller; here we only report."""
        for column in columns:
            negative = self.database.scalar(
                f"SELECT count(*) FROM {table} WHERE _run_id = ? "
                f"AND TRY_CAST({column} AS DECIMAL(18,4)) < 0", [run_id])
            report.add(CheckResult(
                check_id=f"row.non_negative.{column}",
                scope="row",
                severity="warning",
                status=WARNING if negative else PASS,
                expected="0",
                actual=str(negative),
                message=(f"{negative} row(s) had a negative {column} and were quarantined"
                         if negative else f"no negative {column}"),
            ))

    def check_category_allowed(
        self, report: QualityReport, table: str, run_id: str,
        column: str, allowed: list[str],
    ) -> None:
        if not allowed:
            return
        placeholders = ", ".join("?" for _ in allowed)
        unexpected = self.database.scalar(
            f"SELECT count(*) FROM {table} WHERE _run_id = ? "
            f"AND {column} IS NOT NULL AND {column} NOT IN ({placeholders})",
            [run_id, *allowed])
        report.add(CheckResult(
            check_id=f"row.category_allowed.{column}",
            scope="row",
            severity="warning",
            status=WARNING if unexpected else PASS,
            expected=", ".join(allowed),
            actual=str(unexpected),
            message=(f"{unexpected} row(s) use a {column} outside the approved list — "
                     f"loaded and flagged for review" if unexpected
                     else f"every {column} is in the approved list"),
        ))

    # -- dataset checks (Part 9.3) ----------------------------------------

    def check_duplicate_business_keys(
        self, report: QualityReport, table: str, run_id: str, key_columns: list[str]
    ) -> None:
        """Differing duplicates FAIL; identical duplicates are de-duplicated.

        This distinction matters. Two identical rows are a source-export
        artefact and safe to collapse with a counted, named reason. Two rows
        with the same key and *different* values are a genuine contradiction
        that no automation may resolve on its own.
        """
        keys = ", ".join(key_columns)
        conflicting = self.database.scalar(f"""
            SELECT count(*) FROM (
                SELECT {keys} FROM {table} WHERE _run_id = ?
                GROUP BY {keys} HAVING count(DISTINCT row_content_hash) > 1)
        """, [run_id])
        report.add(CheckResult(
            check_id="dataset.duplicate_business_key",
            scope="dataset",
            severity="fail",
            status=FAIL if conflicting else PASS,
            expected="0",
            actual=str(conflicting),
            message=(f"{conflicting} business key(s) appear more than once with "
                     f"different values — a human must decide which is correct"
                     if conflicting else "no conflicting duplicate business keys"),
        ))

    def check_row_count_movement(
        self, report: QualityReport, current: int, previous: int | None
    ) -> None:
        tolerance = self.quality_config.get("max_row_count_change_pct")
        if previous in (None, 0) or not isinstance(tolerance, (int, float)):
            report.add(CheckResult(
                check_id="dataset.row_count_change",
                scope="dataset", severity="warning", status=PASS,
                message="no prior run to compare row counts against",
            ))
            return
        change = abs(current - previous) / previous * 100
        exceeded = change > float(tolerance)
        report.add(CheckResult(
            check_id="dataset.row_count_change",
            scope="dataset",
            severity="warning",
            status=WARNING if exceeded else PASS,
            expected=f"<= {tolerance}%",
            actual=f"{change:.1f}%",
            tolerance=str(tolerance),
            message=(f"row count moved {change:.1f}% versus the previous run"
                     if exceeded else f"row count movement {change:.1f}% is within tolerance"),
        ))


def decimal_text(value: Decimal | int | float | None) -> str:
    return "" if value is None else str(value)
