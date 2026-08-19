"""Every number the browser receives already equals the trusted SQL result.

This is the substantive half of GATE_NO_BROWSER_ARITHMETIC and of V10 Part 36
item 13 ("dashboard equals trusted results"). The static check in
`tests/architecture/test_no_browser_arithmetic.py` guards the source of the
renderer; this one proves the property that actually matters: by the time the
dashboard package leaves the engine, there is nothing left for the browser to
compute.

It runs against every reference project that ships a dashboard, so a new
reference cannot quietly opt out.
"""

from __future__ import annotations

from decimal import Decimal
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

_HAS_DUCKDB = importlib.util.find_spec("duckdb") is not None

#: project directory -> {source_id: fixture filename}, plus any approved period.
REFERENCE_RUNS = {
    "_REFERENCE_SUPPLY_CHAIN": {
        "fixtures": "supply_chain",
        "files": {
            "orders": "orders_p1.csv",
            "inventory": "inventory_p1.csv",
            "item_master": "item_master_p1.csv",
        },
        "periods": {},
    },
    "_REFERENCE_FINANCE_PPV": {
        "fixtures": "finance_ppv",
        "files": {
            "purchases": "purchases_p1.csv",
            "standard_cost": "standard_cost_p1.csv",
            "vendors": "vendors_p1.csv",
            "ppv_budget": "ppv_budget_p1.csv",
        },
        "periods": {"ppv_budget": "2026-08"},
    },
}


@unittest.skipUnless(
    _HAS_DUCKDB, "DuckDB is an application-tier bundled dependency")
class TestDashboardEqualsTrustedSql(unittest.TestCase):
    def setUp(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        self._old_ack = os.environ.get(ACK_VARIABLE)
        os.environ[ACK_VARIABLE] = "1"

    def tearDown(self):
        from app.excel.fixture_adapter import ACK_VARIABLE

        if self._old_ack is None:
            os.environ.pop(ACK_VARIABLE, None)
        else:
            os.environ[ACK_VARIABLE] = self._old_ack

    def _run_reference(self, directory_name, spec, temp):
        from app.data.database import Database
        from app.excel.fixture_adapter import FixtureExtractionAdapter
        from app.project_pipeline import ProjectPipeline
        from factory.project_contract import load_project
        from tools._common import REPO_ROOT

        contract = load_project(REPO_ROOT / "projects" / directory_name)
        database = Database(Path(temp) / f"{contract.project_id}.duckdb")
        self.addCleanup(database.close)
        pipeline = ProjectPipeline(
            database, contract, application_version="test")
        pipeline.prepare()

        run_id = "DASH-1"
        ports = {}
        for source_id, filename in spec["files"].items():
            source = contract.source(source_id)
            path = REPO_ROOT / "tests/fixtures" / spec["fixtures"] / filename
            adapter = FixtureExtractionAdapter(path)
            adapter.open(str(path), {
                "run_id": run_id,
                "report_id": contract.project_id,
                "sheet": source.sheet,
                "schema_version": "1",
                "extraction": {
                    "target_cells_per_chunk": 1000,
                    "min_rows_per_chunk": 1,
                    "max_rows_per_chunk": 100,
                },
            })
            ports[source_id] = adapter

        outcome = pipeline.run(
            run_id, ports, requested_periods=spec["periods"])
        self.assertTrue(outcome.succeeded, outcome.error_message)
        return contract, database, outcome

    @staticmethod
    def _as_number(value):
        if value is None:
            return None
        return Decimal(str(value))

    def test_every_reference_kpi_equals_its_trusted_sql_result(self):
        from app.analytics.runner import SqlRunner

        for directory_name, spec in REFERENCE_RUNS.items():
            with self.subTest(project=directory_name), \
                    tempfile.TemporaryDirectory() as temp:
                contract, database, outcome = self._run_reference(
                    directory_name, spec, temp)
                runner = SqlRunner(
                    database, contract.directory / "business_rules")
                config = outcome.dashboard

                kpi_specs = {
                    str(item["id"]): str(item.get("query", item["id"]))
                    for item in pipeline_kpi_specs(contract)
                }
                self.assertTrue(kpi_specs, f"{directory_name} declares no KPIs")

                for item in config["kpis"]:
                    kpi_id = item["id"]
                    query = kpi_specs[kpi_id]
                    rows = runner.run_named("metrics.sql", query)
                    sql_value = self._as_number(rows[0][0] if rows else None)
                    package_value = self._as_number(item["value"])
                    self.assertEqual(
                        package_value, sql_value,
                        f"{directory_name}/{kpi_id}: dashboard value "
                        f"{item['value']!r} does not equal trusted SQL "
                        f"{sql_value!r}; the browser would be showing a number "
                        f"the engine did not compute")

    def test_every_reference_chart_point_equals_its_trusted_sql_rows(self):
        from app.analytics.runner import SqlRunner

        for directory_name, spec in REFERENCE_RUNS.items():
            with self.subTest(project=directory_name), \
                    tempfile.TemporaryDirectory() as temp:
                contract, database, outcome = self._run_reference(
                    directory_name, spec, temp)
                runner = SqlRunner(
                    database, contract.directory / "business_rules")

                chart_specs = {
                    str(item["id"]): item
                    for item in pipeline_chart_specs(contract)
                }
                for chart in outcome.dashboard["charts"]:
                    spec_entry = chart_specs[chart["id"]]
                    rows = runner.run_named(
                        "metrics.sql", str(spec_entry["query"]))
                    x_index = int(spec_entry.get("x_index", 0))
                    y_index = int(spec_entry.get("y_index", 1))
                    expected = [
                        (row[x_index], self._as_number(row[y_index]))
                        for row in rows
                    ]
                    actual = [
                        (point["x"], self._as_number(point["y"]))
                        for point in chart["series"][0]["points"]
                    ]
                    self.assertEqual(
                        actual, expected,
                        f"{directory_name}/{chart['id']}: chart points differ "
                        f"from the trusted SQL rows")


def _dashboard_config(contract):
    from app.analytics.configured import load_dashboard_config

    return load_dashboard_config(contract.directory / "dashboard.toml")


def pipeline_kpi_specs(contract):
    return _dashboard_config(contract).get("kpis", [])


def pipeline_chart_specs(contract):
    return _dashboard_config(contract).get("charts", [])


if __name__ == "__main__":
    unittest.main()
