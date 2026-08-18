"""End-to-end proof for the project Python rule path (V10 Part 14.3, Phase I2).

The unit tests in `tests/unit/test_project_rules.py` fake the database and the
SQL runner to test the runner's own boundary in isolation. This test proves the
same path for real: a genuine one-source project, run through
`ProjectPipeline`, whose declared rule reads real trusted history through
`SqlRunner`, writes a real table through DuckDB, and whose result a dashboard
KPI can then read back — inside the same project transaction as everything
else.

The project built here is throwaway test fixture, not a new reference. It
exists only to exercise the rule path without touching the Supply Chain
reference, whose entire point is proving that a project needs none of this.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None

PROJECT_TOML = """
project_id = "rule_probe"
project_version = 1
mode = "prototype"
outputs = ["dashboard"]

[template]
template_id = "universal-excel-automation-engine"
template_version = "0.2.0-development"
baseline_digest = "PENDING_SEALED_TEMPLATE"

[business]
purpose = "Prove the project Python rule path end to end"
owner = "FIXTURE"
decision = "Does open demand look reasonable per item?"

[execution]
fixture_adapter = true
"""

SOURCES_TOML = """
[[sources]]
source_id = "orders"
role = "transaction"
required = true
grain = "One order line for one item"
business_key = ["order_id", "order_line"]
event_date = "order_date"

[sources.column_types]
order_id = "VARCHAR"
order_line = "INTEGER"
order_date = "DATE"
item_id = "VARCHAR"
ordered_qty = "DECIMAL(18,4)"
fulfilled_qty = "DECIMAL(18,4)"

[sources.match]
file_patterns = ["orders*.csv"]
[sources.discovery]
sheet = "Orders"
header_row = 1
[sources.history]
mode = "upsert"
lookback_days = 30
deletion_rule = "mark_inactive"
[sources.quality]
required_columns = ["order_id", "order_line", "order_date", "item_id", "ordered_qty", "fulfilled_qty"]
control_totals = ["ordered_qty", "fulfilled_qty"]
non_negative_columns = ["ordered_qty", "fulfilled_qty"]
"""

RELATIONSHIPS_TOML = "# no relationships: single-source project\n"

DASHBOARD_TOML = """
[meta]
title = "Rule Probe"
period_query = "latest_order_date"

[[kpis]]
id = "open_demand_i1"
label = "Open demand for I1"
query = "open_demand_i1"
format = "integer"
unit = "units"
"""

METRICS_TOML = """
[[python_rules]]
rule_id = "open_demand"
version = "1"
module = "open_demand"
entrypoint = "evaluate"
inputs = ["ordered_qty_lines"]
output_table = "analytics.rule_open_demand"

[[python_rules.output_schema]]
name = "item_id"
type = "VARCHAR"

[[python_rules.output_schema]]
name = "open_qty"
type = "DECIMAL(18,4)"
"""

METRICS_SQL = """
-- name: latest_order_date
SELECT max(order_date) FROM analytics.history_rule_probe_orders WHERE is_active;

-- name: ordered_qty_lines
SELECT item_id, ordered_qty, fulfilled_qty
FROM analytics.history_rule_probe_orders WHERE is_active;

-- name: open_demand_i1
SELECT open_qty FROM analytics.rule_open_demand WHERE item_id = 'I1';
"""

INSIGHTS_SQL = "-- no insights for this probe\n"

PYTHON_RULE = """
def evaluate(inputs):
    # Deliberately not natural SQL: open demand per item, floored at zero,
    # written as a Decimal-typed row pair the runner will validate.
    from decimal import Decimal
    from collections import defaultdict

    totals = defaultdict(lambda: [Decimal('0'), Decimal('0')])
    for item_id, ordered_qty, fulfilled_qty in inputs['ordered_qty_lines']:
        totals[item_id][0] += Decimal(str(ordered_qty))
        totals[item_id][1] += Decimal(str(fulfilled_qty))
    return [
        (item_id, max(ordered - fulfilled, Decimal('0')))
        for item_id, (ordered, fulfilled) in totals.items()
    ]
"""

ORDERS_CSV = """order_id,order_line,order_date,item_id,ordered_qty,fulfilled_qty
O1,1,2026-08-01,I1,100,80
O2,1,2026-08-01,I2,50,50
O3,1,2026-08-02,I1,40,30
"""


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestProjectPythonRuleEndToEnd(unittest.TestCase):
    def setUp(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project_dir = self._build_project()

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _build_project(self) -> Path:
        root = Path(self.temp.name) / "rule_probe"
        (root / "business_rules" / "python").mkdir(parents=True)
        (root / "project.toml").write_text(PROJECT_TOML, encoding="utf-8")
        (root / "sources.toml").write_text(SOURCES_TOML, encoding="utf-8")
        (root / "relationships.toml").write_text(
            RELATIONSHIPS_TOML, encoding="utf-8")
        (root / "dashboard.toml").write_text(DASHBOARD_TOML, encoding="utf-8")
        (root / "metrics.toml").write_text(METRICS_TOML, encoding="utf-8")
        (root / "business_rules" / "metrics.sql").write_text(
            METRICS_SQL, encoding="utf-8")
        (root / "business_rules" / "insights.sql").write_text(
            INSIGHTS_SQL, encoding="utf-8")
        (root / "business_rules" / "python" / "open_demand.py").write_text(
            PYTHON_RULE, encoding="utf-8")
        (root / "orders.csv").write_text(ORDERS_CSV, encoding="utf-8")
        return root

    def _port(self, run_id: str):
        from app.excel.fixture_adapter import FixtureExtractionAdapter

        path = self.project_dir / "orders.csv"
        adapter = FixtureExtractionAdapter(path)
        adapter.open(str(path), {
            "run_id": run_id,
            "report_id": "rule_probe",
            "sheet": "Orders",
            "schema_version": "1",
            "extraction": {
                "target_cells_per_chunk": 1000,
                "min_rows_per_chunk": 1,
                "max_rows_per_chunk": 100,
            },
        })
        return {"orders": adapter}

    def test_rule_result_is_queryable_by_dashboard_sql_in_the_same_run(self):
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        database = Database(Path(self.temp.name) / "project.duckdb")
        self.addCleanup(database.close)
        contract = load_project(self.project_dir)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()

        outcome = pipeline.run("RP-1", self._port("RP-1"))

        self.assertTrue(outcome.succeeded, outcome.error_message)
        self.assertEqual(outcome.rule_rows, {"open_demand": 2})

        rows = dict(database.query(
            "SELECT item_id, open_qty FROM analytics.rule_open_demand "
            "ORDER BY item_id"))
        self.assertEqual(rows["I1"], 30)
        self.assertEqual(rows["I2"], 0)

        # The rule's output is not a side channel: a dashboard KPI reads it
        # back through ordinary trusted SQL in the same run.
        kpis = {item["id"]: item["value"] for item in outcome.dashboard["kpis"]}
        self.assertEqual(kpis["open_demand_i1"], 30)

    def test_a_rule_that_raises_rolls_back_history_in_the_same_transaction(self):
        """Part 38 + Part 14.1: a rule failure aborts the project transaction.

        A rule runs after history is written but before COMMIT, so a raising
        rule must take that period's history down with it — exactly like a
        broken cross-source metric already does in
        `test_multisource_supply_chain.test_analytics_failure_rolls_back_*`.
        A silent partial commit here would mean the Python rule path sits
        outside the one project transaction the rest of the engine trusts.
        """
        from app.data.database import Database
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project

        broken_rule = self.project_dir / "business_rules" / "python" / "open_demand.py"
        broken_rule.write_text(
            "def evaluate(inputs):\n    raise ValueError('bad period')\n",
            encoding="utf-8")

        database = Database(Path(self.temp.name) / "project2.duckdb")
        self.addCleanup(database.close)
        contract = load_project(self.project_dir)
        pipeline = ProjectPipeline(database, contract, application_version="test")
        pipeline.prepare()

        with self.assertRaises(Exception) as caught:
            pipeline.run("RP-2", self._port("RP-2"))
        self.assertIn("bad period", str(caught.exception))

        run_row = database.query(
            "SELECT status FROM sys.run WHERE run_id = 'RP-2'")
        self.assertEqual(run_row, [("FAILED",)])
        history_rows = database.query(
            "SELECT count(*) FROM analytics.history_rule_probe_orders "
            "WHERE is_active")
        self.assertEqual(
            history_rows, [(0,)],
            "a raising rule must roll back the history written earlier in "
            "the same project transaction, not leave it committed")


if __name__ == "__main__":
    unittest.main()
