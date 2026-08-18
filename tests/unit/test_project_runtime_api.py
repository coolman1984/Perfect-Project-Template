from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_HAS_WEB_STACK = bool(
    importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx"))


@unittest.skipUnless(
    _HAS_WEB_STACK,
    "FastAPI/httpx are application-tier bundled dependencies")
class TestProjectRuntimeApi(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from app.server import ServerContext, create_app

        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        project = root / "projects" / "employee_demo"
        project.mkdir(parents=True)
        (project / "project.toml").write_text(
            """project_id = "employee_demo"
project_version = 1
mode = "prototype"
[template]
template_id = "universal-excel-automation-engine"
template_version = "test"
[business]
purpose = "API readiness proof"
owner = "Fixture Owner"
decision = "See whether orders are covered by inventory"
[execution]
fixture_adapter = true
""",
            encoding="utf-8",
        )
        (project / "sources.toml").write_text(
            """[[sources]]
source_id = "orders"
role = "transaction"
required = true
grain = "One order line"
business_key = ["order_id"]
event_date = "order_date"
[sources.column_types]
order_id = "VARCHAR"
order_date = "DATE"
item_id = "VARCHAR"
qty = "DECIMAL(18,4)"
[sources.match]
file_patterns = ["orders*.csv"]
[sources.discovery]
sheet = "Orders"
header_row = 1
[sources.history]
mode = "upsert"
lookback_days = 30
deletion_rule = "ignore"
[sources.quality]
required_columns = ["order_id", "order_date", "item_id", "qty"]
control_totals = ["qty"]
non_negative_columns = ["qty"]

[[sources]]
source_id = "inventory"
role = "snapshot"
required = true
grain = "One item balance"
business_key = ["snapshot_date", "item_id"]
event_date = "snapshot_date"
[sources.column_types]
snapshot_date = "DATE"
item_id = "VARCHAR"
on_hand = "DECIMAL(18,4)"
[sources.match]
file_patterns = ["inventory*.csv"]
[sources.discovery]
sheet = "Inventory"
header_row = 1
[sources.history]
mode = "snapshot"
lookback_days = 0
deletion_rule = "ignore"
[sources.quality]
required_columns = ["snapshot_date", "item_id", "on_hand"]
control_totals = ["on_hand"]
non_negative_columns = ["on_hand"]
""",
            encoding="utf-8",
        )
        (project / "relationships.toml").write_text(
            "relationships = []\n", encoding="utf-8")
        (project / "dashboard.toml").write_text(
            '[meta]\ntitle="Demo"\n', encoding="utf-8")
        (project / "business_rules").mkdir()
        (project / "business_rules" / "metrics.sql").write_text(
            "-- name: no_metric\nSELECT 1;\n", encoding="utf-8")
        (project / "business_rules" / "insights.sql").write_text(
            "-- name: no_insight\nSELECT 1 WHERE FALSE;\n", encoding="utf-8")

        (root / "web").mkdir()
        (root / "web" / "index.html").write_text(
            '<html><body><script type="module" src="app.js"></script></body></html>',
            encoding="utf-8",
        )
        (root / "web" / "app.js").write_text("", encoding="utf-8")

        self.root = root
        self.context = ServerContext(root, "project-api-secret", 49731)
        self.client = TestClient(
            create_app(self.context),
            base_url="http://127.0.0.1:49731")
        self.auth = {
            "Origin": "http://127.0.0.1:49731",
            "X-Launch-Secret": "project-api-secret",
        }

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def _upload(self, source_id: str, name: str, body: bytes):
        headers = {
            **self.auth,
            "X-File-Name": name,
            "Content-Type": "application/octet-stream",
        }
        return self.client.post(
            "/api/project-uploads"
            f"?project_id=employee_demo&source_id={source_id}",
            headers=headers,
            content=body,
        )

    def test_project_discovery_exposes_source_roles_and_history_modes(self):
        projects = self.client.get("/api/projects")
        self.assertEqual(projects.status_code, 200)
        self.assertEqual(projects.json()[0]["project_id"], "employee_demo")
        self.assertEqual(projects.json()[0]["required_source_count"], 2)

        detail = self.client.get("/api/projects/employee_demo")
        self.assertEqual(detail.status_code, 200)
        sources = {item["source_id"]: item for item in detail.json()["sources"]}
        self.assertEqual(sources["orders"]["history_mode"], "upsert")
        self.assertEqual(sources["inventory"]["history_mode"], "snapshot")

    def test_project_run_refuses_missing_required_source_before_background_work(self):
        orders = self._upload(
            "orders", "orders_week.csv",
            b"order_id,order_date,item_id,qty\nO1,2026-08-01,I1,10\n")
        self.assertEqual(orders.status_code, 200, orders.text)
        response = self.client.post(
            "/api/project-runs",
            headers={**self.auth, "Content-Type": "application/json"},
            json={
                "project_id": "employee_demo",
                "uploads": {"orders": orders.json()["upload_id"]},
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("required source", response.json()["support_detail"].lower())

    def test_upload_identity_cannot_be_relabelled_as_another_source(self):
        orders = self._upload(
            "orders", "orders_week.csv",
            b"order_id,order_date,item_id,qty\nO1,2026-08-01,I1,10\n")
        upload_id = orders.json()["upload_id"]
        inventory = self._upload(
            "inventory", "inventory_week.csv",
            b"snapshot_date,item_id,on_hand\n2026-08-01,I1,8\n")
        self.assertEqual(inventory.status_code, 200)
        response = self.client.post(
            "/api/project-runs",
            headers={**self.auth, "Content-Type": "application/json"},
            json={
                "project_id": "employee_demo",
                "uploads": {
                    "orders": upload_id,
                    # Deliberately try to reuse the orders upload id under the
                    # inventory source role. Its source-scoped path must fail.
                    "inventory": upload_id,
                },
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_fixture_csv_is_explicit_project_policy_not_global_fallback(self):
        response = self._upload(
            "orders", "orders_week.csv",
            b"order_id,order_date,item_id,qty\nO1,2026-08-01,I1,10\n")
        self.assertEqual(response.status_code, 200)
        meta = (
            self.root / "inbox" / "projects" / "employee_demo" / "orders"
            / response.json()["upload_id"] / "upload.json")
        self.assertTrue(meta.exists())


if __name__ == "__main__":
    unittest.main()
