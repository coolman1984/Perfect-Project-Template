"""The one approved way a project runs its own Python business rule.

V10 Part 14.1 puts Python last in the rule order: configuration, then an
existing reusable SQL pattern, then project-owned SQL, and only then a
project-owned Python rule. This module is that last step and nothing more. It
exists so a project with a genuinely awkward calculation has a tested, declared
path that does not become "edit the shared engine".

The contract a rule author gets (Part 14.3):

- the runtime loads **only** rules named in project configuration;
- a rule receives already-queried rows, never a database handle, so it cannot
  bypass quality gates, escape the caller's transaction, or write a trusted
  table the contract did not declare;
- a rule declares its inputs and its output schema, and a result that does not
  match the declaration fails the run instead of being coerced into place;
- a rule may import only a small deterministic allowlist.

Honest limitation: the import allowlist and restricted builtins below are a
guard against accident and casual misuse, not a security sandbox. Python cannot
contain hostile in-process code, and pretending otherwise would be exactly the
kind of claim Part 37 forbids. The real boundary is that project rules are
authored in the repository and reviewed like any other code.
"""

from __future__ import annotations

import ast
import builtins
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable

#: Deterministic, offline-safe modules a project rule may import. Anything that
#: reaches the network, the filesystem, the process table or the clock is absent
#: on purpose: a trusted calculation must produce the same answer on every run
#: from the same inputs (Part 11).
ALLOWED_IMPORTS = frozenset({
    "collections", "dataclasses", "decimal", "enum", "fractions", "functools",
    "itertools", "math", "operator", "re", "statistics", "typing",
})

#: Builtins a rule body may use. `open`, `__import__`, `eval`, `exec`,
#: `compile`, `input`, `globals` and `vars` are withheld so the obvious escapes
#: are not one keystroke away.
SAFE_BUILTINS = {
    name: getattr(builtins, name)
    for name in (
        "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "filter",
        "float", "frozenset", "int", "isinstance", "len", "list", "map", "max",
        "min", "range", "reversed", "round", "set", "sorted", "str", "sum",
        "tuple", "zip", "ValueError", "TypeError", "KeyError", "ZeroDivisionError",
    )
}

#: Output column types a rule may declare, matching the source vocabulary so a
#: rule result is materialized exactly like any other trusted table.
ALLOWED_OUTPUT_TYPES = frozenset({
    "VARCHAR", "DATE", "INTEGER", "BIGINT", "BOOLEAN",
    "DECIMAL(18,4)", "DECIMAL(18,2)",
})


class ProjectRuleError(RuntimeError):
    """A declared rule is missing, unsafe, or produced an undeclared shape."""


def _guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Enforce the allowlist at execution time as well as at parse time.

    The AST check in `_reject_unsafe_source` catches the import statements a
    rule declares. This catches the ones it computes, so a dynamic import
    cannot reach past a check that only ever read the source.
    """
    if level or name.split(".")[0] not in ALLOWED_IMPORTS:
        raise ProjectRuleError(
            f"import {name!r} is outside the deterministic allowlist "
            f"{sorted(ALLOWED_IMPORTS)}")
    return builtins.__import__(name, globals, locals, fromlist, level)


@dataclass(frozen=True)
class RuleColumn:
    name: str
    sql_type: str


@dataclass(frozen=True)
class PythonRuleSpec:
    """One declared project rule (Part 14.3 declaration fields)."""

    rule_id: str
    version: str
    module: str
    entrypoint: str
    inputs: tuple[str, ...]
    output_table: str
    output_schema: tuple[RuleColumn, ...]

    @property
    def output_columns(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.output_schema)


def parse_rule_specs(document: dict[str, Any]) -> tuple[PythonRuleSpec, ...]:
    """Read `[[python_rules]]` from a project's metrics/rules configuration."""
    specs: list[PythonRuleSpec] = []
    seen: set[str] = set()
    for raw in document.get("python_rules", []):
        rule_id = str(raw.get("rule_id", "")).strip()
        if not rule_id:
            raise ProjectRuleError("a python rule must declare rule_id")
        if rule_id in seen:
            raise ProjectRuleError(f"duplicate python rule_id: {rule_id}")
        seen.add(rule_id)

        for field in ("version", "module", "output_table"):
            if not str(raw.get(field, "")).strip():
                raise ProjectRuleError(f"{rule_id}: {field} is required")

        columns: list[RuleColumn] = []
        for column in raw.get("output_schema", []):
            name = str(column.get("name", "")).strip()
            sql_type = str(column.get("type", "")).strip()
            if not name:
                raise ProjectRuleError(f"{rule_id}: output column needs a name")
            if sql_type not in ALLOWED_OUTPUT_TYPES:
                raise ProjectRuleError(
                    f"{rule_id}: unsupported output type {sql_type!r} for "
                    f"{name!r}")
            columns.append(RuleColumn(name, sql_type))
        if not columns:
            raise ProjectRuleError(
                f"{rule_id}: output_schema is required; an undeclared result "
                f"cannot be validated and must not reach a trusted table")

        inputs = tuple(str(item) for item in raw.get("inputs", []))
        if not inputs:
            raise ProjectRuleError(
                f"{rule_id}: declare the named SQL inputs the rule reads")

        specs.append(PythonRuleSpec(
            rule_id=rule_id,
            version=str(raw["version"]),
            module=str(raw["module"]),
            entrypoint=str(raw.get("entrypoint", "evaluate")),
            inputs=inputs,
            output_table=str(raw["output_table"]),
            output_schema=tuple(columns),
        ))
    return tuple(specs)


def _reject_unsafe_source(spec: PythonRuleSpec, source: str, path: Path) -> ast.Module:
    """Fail closed before executing anything the allowlist does not cover."""
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as error:
        raise ProjectRuleError(f"{spec.rule_id}: cannot parse rule ({error})") from error

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                raise ProjectRuleError(
                    f"{spec.rule_id}: relative imports are not available to a "
                    f"project rule")
            modules = [node.module or ""]
        else:
            continue
        for module in modules:
            if module.split(".")[0] not in ALLOWED_IMPORTS:
                raise ProjectRuleError(
                    f"{spec.rule_id}: import {module!r} is outside the "
                    f"deterministic allowlist {sorted(ALLOWED_IMPORTS)}")
    return tree


def load_rule_callable(spec: PythonRuleSpec, *, rules_root: Path) -> Callable:
    """Load one declared rule from `business_rules/python/<module>.py`."""
    path = Path(rules_root) / f"{spec.module}.py"
    if not path.is_file():
        raise ProjectRuleError(
            f"{spec.rule_id}: declared module is missing: {path}")

    source = path.read_text(encoding="utf-8")
    tree = _reject_unsafe_source(spec, source, path)

    namespace: dict[str, Any] = {
        "__builtins__": {**SAFE_BUILTINS, "__import__": _guarded_import},
        "__name__": f"project_rule_{spec.rule_id}",
        "__file__": str(path),
    }
    exec(compile(tree, filename=str(path), mode="exec"), namespace)  # noqa: S102

    entrypoint = namespace.get(spec.entrypoint)
    if not callable(entrypoint):
        raise ProjectRuleError(
            f"{spec.rule_id}: module {spec.module!r} defines no callable "
            f"{spec.entrypoint!r}")
    return entrypoint


def _coerce(spec: PythonRuleSpec, column: RuleColumn, value: Any) -> Any:
    """Validate one produced value against its declared type."""
    if value is None:
        return None
    kind = column.sql_type
    try:
        if kind.startswith("DECIMAL"):
            return Decimal(str(value))
        if kind in ("INTEGER", "BIGINT"):
            if isinstance(value, bool):
                raise ValueError("boolean is not an integer measure")
            return int(value)
        if kind == "BOOLEAN":
            if not isinstance(value, bool):
                raise ValueError("expected a real boolean")
            return value
    except (ValueError, TypeError, ArithmeticError, InvalidOperation) as error:
        raise ProjectRuleError(
            f"{spec.rule_id}: column {column.name!r} declared {kind} received "
            f"{value!r}") from error
    return value


def validate_rows(spec: PythonRuleSpec, rows: Iterable[Any]) -> list[tuple]:
    """Reject anything that does not match the declared output schema."""
    if isinstance(rows, (str, bytes)) or rows is None:
        raise ProjectRuleError(
            f"{spec.rule_id}: rule must return a sequence of rows")
    width = len(spec.output_schema)
    validated: list[tuple] = []
    for index, row in enumerate(rows):
        if isinstance(row, (str, bytes)) or not isinstance(row, (tuple, list)):
            raise ProjectRuleError(
                f"{spec.rule_id}: row {index} is not a tuple of "
                f"{width} declared columns")
        if len(row) != width:
            raise ProjectRuleError(
                f"{spec.rule_id}: row {index} has {len(row)} values but the "
                f"declared output schema has {width}")
        validated.append(tuple(
            _coerce(spec, column, value)
            for column, value in zip(spec.output_schema, row)))
    return validated


class ProjectRuleRunner:
    """Execute a project's declared Python rules inside the caller's transaction.

    The runner is deliberately the only component that talks to both the rule
    and the database. A rule sees rows and returns rows; materializing the
    result stays here, where the declared schema is enforced.
    """

    def __init__(self, database: Any, sql_runner: Any, *, rules_root: Path,
                 metrics_file: str = "metrics.sql") -> None:
        self.database = database
        self.sql_runner = sql_runner
        self.rules_root = Path(rules_root)
        self.metrics_file = metrics_file

    def _inputs_for(self, spec: PythonRuleSpec) -> dict[str, list[tuple]]:
        return {
            name: self.sql_runner.run_named(self.metrics_file, name)
            for name in spec.inputs
        }

    def materialize(self, spec: PythonRuleSpec, rows: list[tuple]) -> None:
        columns = ",\n                ".join(
            f"{column.name} {column.sql_type}" for column in spec.output_schema)
        self.database.execute(
            f"CREATE TABLE IF NOT EXISTS {spec.output_table} (\n"
            f"                {columns}\n            )")
        self.database.execute(f"DELETE FROM {spec.output_table}")
        if not rows:
            return
        placeholders = ", ".join("?" for _ in spec.output_schema)
        target = ", ".join(spec.output_columns)
        for row in rows:
            self.database.execute(
                f"INSERT INTO {spec.output_table} ({target}) "
                f"VALUES ({placeholders})", list(row))

    def run(self, specs: Iterable[PythonRuleSpec]) -> dict[str, int]:
        """Run every declared rule and return rows written per rule_id."""
        written: dict[str, int] = {}
        for spec in specs:
            entrypoint = load_rule_callable(spec, rules_root=self.rules_root)
            try:
                produced = entrypoint(self._inputs_for(spec))
            except ProjectRuleError:
                raise
            except Exception as error:
                # Part 38: a failing rule fails the run. It never degrades to a
                # partial trusted result.
                raise ProjectRuleError(
                    f"{spec.rule_id}: rule raised {type(error).__name__}: "
                    f"{error}") from error
            rows = validate_rows(spec, produced)
            self.materialize(spec, rows)
            written[spec.rule_id] = len(rows)
        return written
