"""The project Python rule interface must hold its declared boundary.

Every claim in `app/rules/runner.py` is tested here as a boundary, not as a
happy path: an undeclared shape, a forbidden import and a raising rule all have
to fail the run rather than quietly produce a trusted table.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import tempfile
import unittest

from app.rules.runner import (
    ProjectRuleError, ProjectRuleRunner, PythonRuleSpec, RuleColumn,
    load_rule_callable, parse_rule_specs, validate_rows,
)

SPEC = PythonRuleSpec(
    rule_id="open_demand",
    version="1",
    module="open_demand",
    entrypoint="evaluate",
    inputs=("ordered_qty",),
    output_table="analytics.rule_open_demand",
    output_schema=(
        RuleColumn("item_id", "VARCHAR"),
        RuleColumn("open_qty", "DECIMAL(18,4)"),
    ),
)


def _write(directory: Path, name: str, body: str) -> Path:
    path = directory / f"{name}.py"
    path.write_text(body, encoding="utf-8")
    return path


class TestRuleDeclaration(unittest.TestCase):
    def test_output_schema_is_mandatory(self):
        with self.assertRaises(ProjectRuleError):
            parse_rule_specs({"python_rules": [{
                "rule_id": "r", "version": "1", "module": "m",
                "output_table": "analytics.r", "inputs": ["q"],
            }]})

    def test_inputs_are_mandatory(self):
        with self.assertRaises(ProjectRuleError):
            parse_rule_specs({"python_rules": [{
                "rule_id": "r", "version": "1", "module": "m",
                "output_table": "analytics.r",
                "output_schema": [{"name": "a", "type": "VARCHAR"}],
            }]})

    def test_unsupported_output_type_is_rejected(self):
        with self.assertRaises(ProjectRuleError):
            parse_rule_specs({"python_rules": [{
                "rule_id": "r", "version": "1", "module": "m",
                "output_table": "analytics.r", "inputs": ["q"],
                "output_schema": [{"name": "a", "type": "BLOB"}],
            }]})

    def test_duplicate_rule_id_is_rejected(self):
        entry = {
            "rule_id": "r", "version": "1", "module": "m",
            "output_table": "analytics.r", "inputs": ["q"],
            "output_schema": [{"name": "a", "type": "VARCHAR"}],
        }
        with self.assertRaises(ProjectRuleError):
            parse_rule_specs({"python_rules": [entry, dict(entry)]})

    def test_a_complete_declaration_parses(self):
        specs = parse_rule_specs({"python_rules": [{
            "rule_id": "r", "version": "2", "module": "m",
            "output_table": "analytics.r", "inputs": ["q"],
            "output_schema": [{"name": "a", "type": "DECIMAL(18,4)"}],
        }]})
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0].entrypoint, "evaluate")
        self.assertEqual(specs[0].output_columns, ("a",))


class TestRuleLoadingRefusesUnsafeCode(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)

    def test_network_import_is_refused(self):
        _write(self.root, "open_demand",
               "import socket\ndef evaluate(inputs):\n    return []\n")
        with self.assertRaises(ProjectRuleError) as caught:
            load_rule_callable(SPEC, rules_root=self.root)
        self.assertIn("allowlist", str(caught.exception))

    def test_filesystem_import_is_refused(self):
        _write(self.root, "open_demand",
               "from pathlib import Path\ndef evaluate(inputs):\n    return []\n")
        with self.assertRaises(ProjectRuleError):
            load_rule_callable(SPEC, rules_root=self.root)

    def test_subprocess_import_is_refused(self):
        _write(self.root, "open_demand",
               "import subprocess\ndef evaluate(inputs):\n    return []\n")
        with self.assertRaises(ProjectRuleError):
            load_rule_callable(SPEC, rules_root=self.root)

    def test_open_builtin_is_not_reachable(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n    return open('/etc/hostname').read()\n")
        rule = load_rule_callable(SPEC, rules_root=self.root)
        with self.assertRaises(NameError):
            rule({})

    def test_computed_import_cannot_slip_past_the_static_check(self):
        """The AST check reads declared imports; this one is built at runtime."""
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n"
               "    return __import__('so' + 'cket')\n")
        rule = load_rule_callable(SPEC, rules_root=self.root)
        with self.assertRaises(ProjectRuleError) as caught:
            rule({})
        self.assertIn("allowlist", str(caught.exception))

    def test_deterministic_import_is_allowed(self):
        _write(self.root, "open_demand",
               "from decimal import Decimal\n"
               "def evaluate(inputs):\n    return [('I1', Decimal('1'))]\n")
        rule = load_rule_callable(SPEC, rules_root=self.root)
        self.assertEqual(rule({}), [("I1", Decimal("1"))])

    def test_missing_module_is_named(self):
        with self.assertRaises(ProjectRuleError) as caught:
            load_rule_callable(SPEC, rules_root=self.root)
        self.assertIn("open_demand", str(caught.exception))

    def test_missing_entrypoint_is_named(self):
        _write(self.root, "open_demand", "def other(inputs):\n    return []\n")
        with self.assertRaises(ProjectRuleError) as caught:
            load_rule_callable(SPEC, rules_root=self.root)
        self.assertIn("evaluate", str(caught.exception))


class TestOutputValidation(unittest.TestCase):
    def test_wrong_arity_is_rejected(self):
        with self.assertRaises(ProjectRuleError) as caught:
            validate_rows(SPEC, [("I1",)])
        self.assertIn("declared output schema", str(caught.exception))

    def test_non_row_is_rejected(self):
        with self.assertRaises(ProjectRuleError):
            validate_rows(SPEC, ["I1"])

    def test_undecimalizable_measure_is_rejected(self):
        with self.assertRaises(ProjectRuleError) as caught:
            validate_rows(SPEC, [("I1", "not-a-number")])
        self.assertIn("open_qty", str(caught.exception))

    def test_nulls_survive(self):
        self.assertEqual(validate_rows(SPEC, [("I1", None)]), [("I1", None)])

    def test_declared_row_is_coerced_to_its_type(self):
        self.assertEqual(
            validate_rows(SPEC, [("I1", "2.5")]), [("I1", Decimal("2.5"))])


class _FakeDatabase:
    def __init__(self):
        self.statements: list[str] = []
        self.rows: list[list] = []

    def execute(self, sql, parameters=None):
        self.statements.append(sql.strip().split()[0].upper())
        if sql.strip().upper().startswith("INSERT"):
            self.rows.append(list(parameters))
        if sql.strip().upper().startswith("DELETE"):
            self.rows.clear()


class _FakeSqlRunner:
    def __init__(self, results):
        self.results = results
        self.asked: list[str] = []

    def run_named(self, filename, name):
        self.asked.append(name)
        return self.results[name]


class TestRunnerBoundary(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)
        self.database = _FakeDatabase()
        self.sql = _FakeSqlRunner({"ordered_qty": [("I1", 10), ("I2", 4)]})

    def _runner(self):
        return ProjectRuleRunner(
            self.database, self.sql, rules_root=self.root)

    def test_rule_receives_declared_inputs_only(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n"
               "    assert list(inputs) == ['ordered_qty']\n"
               "    return [(item, qty) for item, qty in inputs['ordered_qty']]\n")
        written = self._runner().run([SPEC])
        self.assertEqual(written, {"open_demand": 2})
        self.assertEqual(self.sql.asked, ["ordered_qty"])

    def test_rule_never_receives_a_database_handle(self):
        """A rule sees rows. It cannot reach the connection to bypass controls."""
        payload = self._runner()._inputs_for(SPEC)
        self.assertIsInstance(payload, dict)
        self.assertEqual(set(payload), {"ordered_qty"})
        self.assertEqual(payload["ordered_qty"], [("I1", 10), ("I2", 4)])
        for value in payload.values():
            self.assertIsInstance(value, list)
            self.assertFalse(hasattr(value, "execute"))

    def test_materialized_rows_match_the_declaration(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n    return [('I1', '7.5')]\n")
        self._runner().run([SPEC])
        self.assertEqual(self.database.rows, [["I1", Decimal("7.5")]])

    def test_a_raising_rule_fails_the_run(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n    raise ValueError('bad period')\n")
        with self.assertRaises(ProjectRuleError) as caught:
            self._runner().run([SPEC])
        self.assertIn("bad period", str(caught.exception))

    def test_an_undeclared_result_never_reaches_the_table(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n    return [('I1', 1, 'extra')]\n")
        with self.assertRaises(ProjectRuleError):
            self._runner().run([SPEC])
        self.assertEqual(self.database.rows, [])

    def test_only_declared_rules_run(self):
        _write(self.root, "open_demand",
               "def evaluate(inputs):\n    return []\n")
        _write(self.root, "undeclared",
               "def evaluate(inputs):\n    raise AssertionError('must not run')\n")
        self.assertEqual(self._runner().run([SPEC]), {"open_demand": 0})


if __name__ == "__main__":
    unittest.main()
