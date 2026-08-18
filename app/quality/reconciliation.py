"""Population and control-total reconciliation.

Quality verdicts are PASS / WARNING / BLOCK. A BLOCK verdict means the run must
not update trusted history. The execution state can then become FAILED; the two
vocabularies are intentionally separate.

The public helper API is intentionally backward-compatible with the original
golden reference: `balances`, `shortfall`, `source_total()` and
`accepted_total()` remain available while status vocabulary is canonicalized.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.data.database import Database
from app.quality.engine import BLOCK, PASS, CheckResult, QualityReport


@dataclass(frozen=True)
class ControlTotal:
    name: str
    source_value: Decimal
    database_value: Decimal

    @property
    def difference(self) -> Decimal:
        return self.source_value - self.database_value

    @property
    def balances(self) -> bool:
        return self.difference == 0


@dataclass(frozen=True)
class Population:
    source_rows: int
    accepted_rows: int
    rejected_rows: int
    intentionally_filtered_rows: int
    filter_reasons: tuple[tuple[str, int], ...] = ()

    @property
    def difference(self) -> int:
        return self.source_rows - (
            self.accepted_rows + self.rejected_rows
            + self.intentionally_filtered_rows)

    @property
    def shortfall(self) -> int:
        return self.difference

    @property
    def balances(self) -> bool:
        return self.difference == 0


def check_population(
    report: QualityReport, population: Population
) -> CheckResult:
    status = PASS if population.balances else BLOCK
    reasons = ", ".join(
        f"{name}={count}" for name, count in population.filter_reasons) or "none"
    result = CheckResult(
        "population.equation",
        "dataset",
        "block",
        status,
        ("source rows reconcile to accepted + rejected + explicitly filtered"
         if status == PASS
         else "row population does not reconcile — publishing is blocked"),
        str(population.source_rows),
        (f"accepted={population.accepted_rows}; rejected={population.rejected_rows}; "
         f"filtered={population.intentionally_filtered_rows}; reasons={reasons}"),
        str(population.difference),
        "0",
        evidence=(f"accepted={population.accepted_rows} "
                  f"rejected={population.rejected_rows} "
                  f"filtered={population.intentionally_filtered_rows} "
                  f"[{reasons}]"),
    )
    report.add(result)
    return result


def check_control_total(
    report: QualityReport,
    control: ControlTotal,
    *,
    tolerance: Decimal = Decimal(0),
    severity: str = "block",
) -> CheckResult:
    within = abs(control.difference) <= tolerance
    status = PASS if within else BLOCK
    result = CheckResult(
        f"control_total.{control.name}",
        "dataset",
        severity,
        status,
        (f"{control.name} reconciles"
         if within
         else f"{control.name} differs by {control.difference} — publishing is blocked"),
        str(control.source_value),
        str(control.database_value),
        str(control.difference),
        str(tolerance),
        evidence=f"control_total:{control.name}",
    )
    report.add(result)
    return result


def source_total(
    database: Database, table: str, run_id: str, column: str
) -> Decimal:
    """Sum the raw staged column exactly as the source presented it."""
    value = database.scalar(
        f"SELECT COALESCE(SUM(TRY_CAST({column} AS DECIMAL(18,4))), 0) "
        f"FROM {table} WHERE _run_id = ?",
        [run_id],
    )
    return Decimal(str(value or 0))


def accepted_total(
    database: Database, table: str, run_id: str, column: str
) -> Decimal:
    value = database.scalar(
        f"SELECT COALESCE(SUM({column}), 0) FROM {table} WHERE _run_id = ?",
        [run_id],
    )
    return Decimal(str(value or 0))
