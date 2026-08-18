"""Control totals and the population equation (Constitution Parts 9.4, 25.3).

The strongest check in the system, and the one that converts "a nice dashboard"
into "a number I can present to management".

    Excel total of produced_qty : 4,812,300
    Database total              : 4,812,300
    Difference                  : 0        -> PASS

Not "approximately". **Exactly zero** at the defined decimal precision. If it is
not zero the run FAILS, trusted history is untouched, and the dashboard keeps
showing the last good data.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.data.database import Database
from app.quality.engine import FAIL, PASS, CheckResult, QualityReport


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
    """Part 25.3: filters are named evidence, never balancing figures."""

    source_rows: int
    accepted_rows: int
    rejected_rows: int
    intentionally_filtered_rows: int
    filter_reasons: tuple[tuple[str, int], ...] = ()

    @property
    def balances(self) -> bool:
        return self.source_rows == (
            self.accepted_rows + self.rejected_rows + self.intentionally_filtered_rows)

    @property
    def shortfall(self) -> int:
        return self.source_rows - (
            self.accepted_rows + self.rejected_rows + self.intentionally_filtered_rows)


def check_control_total(
    report: QualityReport, control: ControlTotal, *, severity: str = "fail"
) -> None:
    report.add(CheckResult(
        check_id=f"control_total.{control.name}",
        scope="dataset",
        severity=severity,
        status=PASS if control.balances else FAIL,
        expected=str(control.source_value),
        actual=str(control.database_value),
        difference=str(control.difference),
        tolerance="0",
        message=(f"{control.name}: source and database agree exactly"
                 if control.balances else
                 f"{control.name}: source {control.source_value} vs database "
                 f"{control.database_value}, difference {control.difference}"),
        evidence=f"control_total:{control.name}",
    ))


def check_population(report: QualityReport, population: Population) -> None:
    detail = ", ".join(f"{reason}={count}" for reason, count in population.filter_reasons)
    report.add(CheckResult(
        check_id="population.equation",
        scope="dataset",
        severity="fail",
        status=PASS if population.balances else FAIL,
        expected=str(population.source_rows),
        actual=str(population.accepted_rows + population.rejected_rows
                   + population.intentionally_filtered_rows),
        difference=str(population.shortfall),
        message=("source rows = accepted + rejected + filtered"
                 if population.balances else
                 f"population does not balance: {population.shortfall} row(s) "
                 f"unaccounted for — every row must be explained"),
        evidence=f"accepted={population.accepted_rows} rejected={population.rejected_rows} "
                 f"filtered={population.intentionally_filtered_rows} [{detail}]",
    ))


def source_total(database: Database, table: str, run_id: str, column: str) -> Decimal:
    """Sum the raw staged column exactly as the source presented it."""
    value = database.scalar(
        f"SELECT COALESCE(SUM(TRY_CAST({column} AS DECIMAL(18,4))), 0) "
        f"FROM {table} WHERE _run_id = ?", [run_id])
    return Decimal(str(value or 0))


def accepted_total(database: Database, table: str, run_id: str, column: str) -> Decimal:
    value = database.scalar(
        f"SELECT COALESCE(SUM({column}), 0) FROM {table} WHERE _run_id = ?", [run_id])
    return Decimal(str(value or 0))
