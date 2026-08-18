"""Executes approved SQL only (Constitution Part 10.2).

Layer 8. **All trusted business metric and reconciliation logic lives in
versioned `.sql` files.** Python orchestrates, validates, converts and formats;
it never holds a second copy of a KPI formula. JavaScript renders and filters
approved pre-aggregations; it never calculates either.

That single rule is what makes "one place to fix the logic" true, and it is why
`metrics.sql` is a report variation point while this runner is Factory Core.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

from app.data.database import Database

#: `-- name: <metric_id>` marks the start of a named statement inside a .sql file.
NAME_MARKER = re.compile(r"^--\s*name:\s*([a-z][a-z0-9_]*)\s*$", re.MULTILINE)


class MetricError(RuntimeError):
    """A metric was requested that no approved SQL file defines."""


@dataclass(frozen=True)
class NamedStatement:
    name: str
    sql: str


def parse_named_statements(text: str) -> dict[str, NamedStatement]:
    """Split a .sql file into `-- name: x` blocks.

    Anything before the first marker is treated as shared preamble and ignored,
    so a file can carry a header comment without becoming an unnamed statement.
    """
    matches = list(NAME_MARKER.finditer(text))
    statements: dict[str, NamedStatement] = {}
    for index, match in enumerate(matches):
        name = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if body:
            statements[name] = NamedStatement(name=name, sql=body)
    return statements


class SqlRunner:
    """Loads a report's approved SQL and executes named statements by id."""

    def __init__(self, database: Database, sql_directory: Path) -> None:
        self.database = database
        self.sql_directory = Path(sql_directory)
        self._cache: dict[str, dict[str, NamedStatement]] = {}

    def statements(self, filename: str) -> dict[str, NamedStatement]:
        if filename not in self._cache:
            path = self.sql_directory / filename
            if not path.exists():
                raise MetricError(f"missing approved SQL file: {path}")
            self._cache[filename] = parse_named_statements(
                path.read_text(encoding="utf-8"))
        return self._cache[filename]

    def run_named(
        self, filename: str, name: str, parameters: list[Any] | None = None
    ) -> list[tuple]:
        available = self.statements(filename)
        if name not in available:
            raise MetricError(
                f"'{name}' is not defined in {filename}. Approved metric SQL is "
                f"the only place a trusted number may be calculated (Part 10.2). "
                f"Defined here: {sorted(available)}")
        return self.database.query(available[name].sql, parameters)

    def run_script(self, filename: str, name: str, parameters: list[Any] | None = None) -> None:
        available = self.statements(filename)
        if name not in available:
            raise MetricError(f"'{name}' is not defined in {filename}")
        self.database.execute(available[name].sql, parameters)

    def scalar(
        self, filename: str, name: str, parameters: list[Any] | None = None
    ) -> Any:
        rows = self.run_named(filename, name, parameters)
        return rows[0][0] if rows and rows[0] else None


def as_decimal(value: Any) -> Decimal:
    return Decimal(str(value if value is not None else 0))


def weighted_rate_ppm(numerator: Any, denominator: Any) -> Decimal | None:
    """Weighted rate from summed numerator/denominator (Part 26.5).

    Never the average of row percentages, and never a false zero: a zero
    denominator yields None, which the dashboard shows as an em dash.
    """
    denominator_value = as_decimal(denominator)
    if denominator_value == 0:
        return None
    return as_decimal(numerator) / denominator_value * Decimal(1_000_000)
