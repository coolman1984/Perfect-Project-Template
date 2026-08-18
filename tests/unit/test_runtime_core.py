from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

from app import events
from app.errors import AppError
from app.local_transport import verify_origin
from app.locks import acquire_report_lock


class TestDurableEvents(unittest.TestCase):
    def test_events_are_persisted_before_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = events.emit("RUN-1", "STARTING", root=root, progress=0)
            second = events.emit("RUN-1", "COMPLETE", root=root, progress=100)
            self.assertEqual((first["sequence"], second["sequence"]), (0, 1))
            replay = events.since("RUN-1", 0, root=root)
            self.assertEqual([item["stage"] for item in replay], ["COMPLETE"])
            self.assertTrue((root / "RUN-1" / "events.jsonl").exists())


class TestReportLocks(unittest.TestCase):
    def test_live_lock_is_not_stolen(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock = acquire_report_lock("quality", root=root)
            try:
                with self.assertRaises(AppError) as caught:
                    acquire_report_lock("quality", root=root)
                self.assertEqual(caught.exception.code, "REPORT_LOCKED")
            finally:
                lock.release()

    def test_stale_lock_is_recovered(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); root.mkdir(exist_ok=True)
            path = root / "quality.lock"
            path.write_text(json.dumps({"pid": 99999999}), encoding="utf-8")
            lock = acquire_report_lock("quality", root=root)
            try:
                self.assertTrue(path.exists())
                self.assertEqual(json.loads(path.read_text("utf-8"))["pid"], os.getpid())
            finally:
                lock.release()


class TestOriginRules(unittest.TestCase):
    def test_exact_loopback_origin(self):
        self.assertTrue(verify_origin("127.0.0.1:49731", "http://127.0.0.1:49731", 49731, require_origin=True))
        self.assertTrue(verify_origin("127.0.0.1:49731", None, 49731))
        self.assertFalse(verify_origin("localhost:49731", "http://127.0.0.1:49731", 49731, require_origin=True))
        self.assertFalse(verify_origin("127.0.0.1:49731", None, 49731, require_origin=True))


_HAS_WEB_STACK = bool(importlib.util.find_spec("fastapi") and importlib.util.find_spec("httpx"))


@unittest.skipUnless(_HAS_WEB_STACK, "FastAPI/httpx are application-tier bundled dependencies")
class TestLocalApi(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from app.server import ServerContext, create_app
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "reports" / "demo").mkdir(parents=True)
        (root / "reports" / "demo" / "report.toml").write_text(
            'report_id="demo"\nmode="prototype"\n[excel]\nadapter="fixture"\n', encoding="utf-8")
        (root / "web").mkdir()
        (root / "web" / "index.html").write_text(
            '<html><body><script type="module" src="app.js"></script></body></html>', encoding="utf-8")
        (root / "web" / "app.js").write_text("", encoding="utf-8")
        self.context = ServerContext(root, "secret-123", 49731)
        self.client = TestClient(create_app(self.context), base_url="http://127.0.0.1:49731")

    def tearDown(self):
        self.client.close(); self.temp.cleanup()

    def test_health_and_report_discovery(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        self.assertEqual(self.client.get("/api/reports").json()[0]["report_id"], "demo")

    def test_wrong_host_is_rejected(self):
        response = self.client.get("/api/health", headers={"Host": "localhost:49731"})
        self.assertEqual(response.status_code, 403)

    def test_mutation_requires_origin_and_launch_secret(self):
        origin = "http://127.0.0.1:49731"
        self.assertEqual(self.client.post("/api/shutdown", headers={"Origin": origin}).status_code, 403)
        response = self.client.post("/api/shutdown", headers={"Origin": origin, "X-Launch-Secret": "secret-123"})
        self.assertEqual(response.status_code, 200)

    def test_root_injects_secret_in_memory_and_disables_docs(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("window.__launchSecret", response.text)
        self.assertEqual(self.client.get("/docs").status_code, 404)
