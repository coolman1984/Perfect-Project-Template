"""Quality gate: the trust layer.

Canonical quality verdicts are PASS / WARNING / BLOCK. A BLOCK verdict means
trusted history must not be touched. The execution run may then enter state
FAILED; quality verdict and run state are deliberately different concepts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from app.data.database import Database

PASS, WARNING, BLOCK = "PASS", "WARNING", "BLOCK"
# Compatibility symbol for older imports while the repository is migrated.
# It intentionally resolves to BLOCK so no second persisted quality vocabulary exists.
FAIL = BLOCK

@dataclass
class CheckResult:
    check_id: str; scope: str; severity: str; status: str; message: str
    expected: str = ""; actual: str = ""; difference: str = ""; tolerance: str = ""; evidence: str = ""

@dataclass
class QualityReport:
    run_id: str
    results: list[CheckResult] = field(default_factory=list)
    def add(self, result: CheckResult) -> None: self.results.append(result)
    @property
    def status(self) -> str:
        if any(r.status == BLOCK for r in self.results): return BLOCK
        if any(r.status == WARNING for r in self.results): return WARNING
        return PASS
    @property
    def passed(self) -> int: return sum(1 for r in self.results if r.status == PASS)
    @property
    def warnings(self) -> int: return sum(1 for r in self.results if r.status == WARNING)
    @property
    def failed(self) -> int: return sum(1 for r in self.results if r.status == BLOCK)
    def blocking_failures(self) -> list[CheckResult]: return [r for r in self.results if r.status == BLOCK]
    def persist(self, database: Database) -> None:
        now = datetime.now(timezone.utc)
        for result in self.results:
            database.execute("INSERT INTO quality.check_result (run_id, check_id, scope, severity, status, expected, actual, difference, tolerance, message, evidence, checked_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [self.run_id, result.check_id, result.scope, result.severity, result.status, result.expected, result.actual, result.difference, result.tolerance, result.message, result.evidence, now])

class QualityEngine:
    def __init__(self, database: Database, config: dict[str, Any]) -> None:
        self.database = database; self.config = config; self.quality_config = config.get("quality", {})
    def check_required_columns(self, report: QualityReport, present: list[str], required: list[str]) -> None:
        missing = [column for column in required if column not in present]
        report.add(CheckResult("structural.required_columns", "structure", "block", BLOCK if missing else PASS, f"required column(s) missing from the source: {', '.join(missing)}" if missing else "all required columns present", ", ".join(required), ", ".join(present)))
    def check_no_blank_business_key(self, report: QualityReport, table: str, run_id: str, key_columns: list[str]) -> None:
        condition = " OR ".join(f"{column} IS NULL OR trim({column}) = ''" for column in key_columns)
        blank = self.database.scalar(f"SELECT count(*) FROM {table} WHERE _run_id = ? AND ({condition})", [run_id])
        report.add(CheckResult("row.business_key_not_blank", "row", "block", BLOCK if blank else PASS, f"{blank} row(s) have a blank business key" if blank else "every row has a complete business key", "0", str(blank)))
    def check_non_negative(self, report: QualityReport, table: str, run_id: str, columns: list[str]) -> None:
        for column in columns:
            negative = self.database.scalar(f"SELECT count(*) FROM {table} WHERE _run_id = ? AND TRY_CAST({column} AS DECIMAL(18,4)) < 0", [run_id])
            report.add(CheckResult(f"row.non_negative.{column}", "row", "warning", WARNING if negative else PASS, f"{negative} row(s) had a negative {column} and were quarantined" if negative else f"no negative {column}", "0", str(negative)))
    def check_category_allowed(self, report: QualityReport, table: str, run_id: str, column: str, allowed: list[str]) -> None:
        if not allowed: return
        placeholders = ", ".join("?" for _ in allowed)
        unexpected = self.database.scalar(f"SELECT count(*) FROM {table} WHERE _run_id = ? AND {column} IS NOT NULL AND {column} NOT IN ({placeholders})", [run_id, *allowed])
        report.add(CheckResult(f"row.category_allowed.{column}", "row", "warning", WARNING if unexpected else PASS, f"{unexpected} row(s) use a {column} outside the approved list — loaded and flagged for review" if unexpected else f"every {column} is in the approved list", ", ".join(allowed), str(unexpected)))
    def check_duplicate_business_keys(self, report: QualityReport, table: str, run_id: str, key_columns: list[str]) -> None:
        keys = ", ".join(key_columns)
        conflicting = self.database.scalar(f"SELECT count(*) FROM (SELECT {keys} FROM {table} WHERE _run_id = ? GROUP BY {keys} HAVING count(DISTINCT row_content_hash) > 1)", [run_id])
        report.add(CheckResult("dataset.duplicate_business_key", "dataset", "block", BLOCK if conflicting else PASS, f"{conflicting} business key(s) appear more than once with different values — a human must decide which is correct" if conflicting else "no conflicting duplicate business keys", "0", str(conflicting)))
    def check_row_count_movement(self, report: QualityReport, current: int, previous: int | None) -> None:
        tolerance = self.quality_config.get("max_row_count_change_pct")
        if previous in (None, 0) or not isinstance(tolerance, (int, float)):
            report.add(CheckResult("dataset.row_count_change", "dataset", "warning", PASS, "no prior run to compare row counts against")); return
        change = abs(current - previous) / previous * 100; exceeded = change > float(tolerance)
        report.add(CheckResult("dataset.row_count_change", "dataset", "warning", WARNING if exceeded else PASS, f"row count moved {change:.1f}% versus the previous run" if exceeded else f"row count movement {change:.1f}% is within tolerance", f"<= {tolerance}%", f"{change:.1f}%", tolerance=str(tolerance)))

def decimal_text(value: Decimal | int | float | None) -> str: return "" if value is None else str(value)
