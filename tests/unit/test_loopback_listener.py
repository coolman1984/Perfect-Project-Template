from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

_HAS_STACK = all(importlib.util.find_spec(name) for name in ("fastapi", "httpx", "uvicorn"))


@unittest.skipUnless(_HAS_STACK, "FastAPI/httpx/Uvicorn are application-tier bundled dependencies")
class TestRealLoopbackListener(unittest.TestCase):
    def test_real_socket_is_loopback_high_port_and_stops_cleanly(self):
        import httpx
        from app.local_transport import LOOPBACK_HOST, shutdown, start_listener
        from app.server import ServerContext, create_app

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "web").mkdir()
            (root / "web" / "index.html").write_text(
                '<html><body><script type="module" src="app.js"></script></body></html>',
                encoding="utf-8",
            )
            (root / "web" / "app.js").write_text("", encoding="utf-8")
            (root / "reports").mkdir()
            context = ServerContext(repo_root=root, launch_secret="listener-secret")
            app = create_app(context)
            listener = start_listener(app, secret=context.launch_secret)
            context.listener = listener
            try:
                self.assertEqual(listener.host, LOOPBACK_HOST)
                self.assertGreaterEqual(listener.port, 1024)
                self.assertEqual(context.port, listener.port)
                origin = f"http://{listener.host}:{listener.port}"
                with httpx.Client(trust_env=False, timeout=5.0) as client:
                    response = client.get(origin + "/api/health")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json()["host"], LOOPBACK_HOST)
                    wrong_host = client.get(
                        origin + "/api/health",
                        headers={"Host": f"localhost:{listener.port}"},  # FORBIDDEN negative test input
                    )
                    self.assertEqual(wrong_host.status_code, 403)
                    shutdown_response = client.post(
                        origin + "/api/shutdown",
                        headers={"Origin": origin, "X-Launch-Secret": context.launch_secret},
                    )
                    self.assertEqual(shutdown_response.status_code, 200)
            finally:
                shutdown(listener)
            self.assertFalse(listener.thread.is_alive())


if __name__ == "__main__":
    unittest.main()
