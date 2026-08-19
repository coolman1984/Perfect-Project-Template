"""Negative probes against a real loopback listener (V10 Part 23 / Part 35.5).

Every test here tries to do something the local security boundary must refuse,
against a genuinely bound socket rather than a mocked transport. A boundary
that has only ever been tested with well-formed requests has not been tested.

Scope note: this file covers the probes that are reachable from a POSIX CI
runner — Host/Origin, launch-secret, CORS, response headers, path traversal and
the bind address. The Windows-only, clean-machine and protected-file probes
stay environment-bound gates and are not simulated here, because a fixture can
never advance them (V10 Part 37).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import socket
import tempfile
import unittest

_HAS_STACK = all(
    importlib.util.find_spec(name) for name in ("fastapi", "httpx", "uvicorn"))


@unittest.skipUnless(
    _HAS_STACK, "FastAPI/httpx/Uvicorn are application-tier bundled dependencies")
class TestLoopbackNegativeProbes(unittest.TestCase):
    def setUp(self):
        import httpx
        from app.local_transport import generate_launch_secret, start_listener
        from app.server import ServerContext, create_app

        self._temp = tempfile.TemporaryDirectory()
        self.addCleanup(self._temp.cleanup)
        root = Path(self._temp.name)
        (root / "web").mkdir()
        (root / "web" / "index.html").write_text(
            "<html><body></body></html>", encoding="utf-8")
        (root / "reports").mkdir()

        self.context = ServerContext(
            repo_root=root, launch_secret=generate_launch_secret())
        app = create_app(self.context)
        self.listener = start_listener(app, secret=self.context.launch_secret)
        self.context.listener = self.listener
        self.origin = f"http://{self.listener.host}:{self.listener.port}"
        self.client = httpx.Client(trust_env=False, timeout=5.0)
        self.addCleanup(self.client.close)
        self.addCleanup(self._stop)

    def _stop(self):
        from app.local_transport import shutdown

        try:
            shutdown(self.listener)
        except Exception:
            pass

    def _mutating(self, headers=None):
        """A POST is the strictest path: Origin and launch secret both required."""
        return self.client.post(
            self.origin + "/api/shutdown", headers=headers or {})

    # ------------------------------------------------------------- bind address
    def test_listener_is_bound_only_to_loopback(self):
        from app.local_transport import LOOPBACK_HOST

        self.assertEqual(self.listener.host, LOOPBACK_HOST)
        self.assertGreaterEqual(self.listener.port, 1024)

    def test_port_is_not_reachable_on_a_non_loopback_address(self):
        """No LAN binding: the port must not answer on a routable address.

        Connecting to this machine's own LAN address must fail rather than
        reach the listener. If it ever succeeds, the application has been
        exposed beyond the local user.
        """
        lan_address = socket.gethostbyname(socket.gethostname())
        if lan_address.startswith("127."):
            self.skipTest("runner has no non-loopback address to probe")
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.settimeout(2.0)
        try:
            result = probe.connect_ex((lan_address, self.listener.port))
        finally:
            probe.close()
        self.assertNotEqual(
            result, 0,
            f"the listener answered on {lan_address}: it is bound beyond "
            f"loopback (Part 23)")

    # --------------------------------------------------------------- Host/Origin
    def test_wrong_host_header_is_rejected(self):
        response = self.client.get(
            self.origin + "/api/health",
            headers={"Host": f"evil.example:{self.listener.port}"})
        self.assertEqual(response.status_code, 403)

    def test_wrong_port_in_host_header_is_rejected(self):
        response = self.client.get(
            self.origin + "/api/health",
            headers={"Host": f"127.0.0.1:{self.listener.port + 1}"})
        self.assertEqual(response.status_code, 403)

    def test_mutating_request_without_origin_is_rejected(self):
        self.assertEqual(self._mutating().status_code, 403)

    def test_mutating_request_with_foreign_origin_is_rejected(self):
        response = self._mutating({
            "Origin": "http://evil.example",
            "X-Launch-Secret": self.context.launch_secret,
        })
        self.assertEqual(response.status_code, 403)

    def test_mutating_request_with_null_origin_is_rejected(self):
        response = self._mutating({
            "Origin": "null",
            "X-Launch-Secret": self.context.launch_secret,
        })
        self.assertEqual(response.status_code, 403)

    # ------------------------------------------------------------- launch secret
    def test_mutating_request_without_the_launch_secret_is_rejected(self):
        response = self._mutating({"Origin": self.origin})
        self.assertEqual(response.status_code, 403)

    def test_mutating_request_with_a_wrong_launch_secret_is_rejected(self):
        response = self._mutating({
            "Origin": self.origin,
            "X-Launch-Secret": "not-the-secret",
        })
        self.assertEqual(response.status_code, 403)

    def test_launch_secret_of_a_different_launch_is_rejected(self):
        """A secret is per-launch, so yesterday's secret must not work today."""
        from app.local_transport import generate_launch_secret

        response = self._mutating({
            "Origin": self.origin,
            "X-Launch-Secret": generate_launch_secret(),
        })
        self.assertEqual(response.status_code, 403)

    def test_empty_launch_secret_is_rejected(self):
        response = self._mutating({
            "Origin": self.origin, "X-Launch-Secret": ""})
        self.assertEqual(response.status_code, 403)

    # -------------------------------------------------------------------- CORS
    def test_no_wildcard_cross_origin_header_is_ever_returned(self):
        """Part 23: no wildcard CORS. A `*` here would open the trusted API
        to any page the employee happens to have open."""
        for headers in (
            {},
            {"Origin": "http://evil.example"},
            {"Origin": self.origin},
        ):
            response = self.client.get(
                self.origin + "/api/health", headers=headers)
            allow = response.headers.get("access-control-allow-origin")
            self.assertNotEqual(allow, "*", f"wildcard CORS with {headers}")
            if allow is not None:
                self.assertNotIn("evil.example", allow)

    def test_security_headers_are_present_on_a_normal_response(self):
        response = self.client.get(self.origin + "/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("cache-control"), "no-store")
        self.assertEqual(
            response.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(response.headers.get("x-frame-options"), "DENY")
        self.assertEqual(
            response.headers.get("referrer-policy"), "no-referrer")

    # --------------------------------------------------------- path traversal
    def test_path_traversal_cannot_escape_the_web_directory(self):
        """The renderer serves web/ only; it is never a general file server."""
        secret_file = Path(self._temp.name) / "trusted_secret.txt"
        secret_file.write_text("trusted-data", encoding="utf-8")

        # Prove the static handler is actually live first. Without this the
        # traversal assertions below would pass just as happily against a
        # server that serves nothing at all.
        served = self.client.get(self.origin + "/")
        self.assertEqual(served.status_code, 200)
        self.assertIn("<html>", served.text.lower())

        for attempt in (
            "/../trusted_secret.txt",
            "/..%2ftrusted_secret.txt",
            "/%2e%2e/trusted_secret.txt",
            "/web/../trusted_secret.txt",
            "/....//trusted_secret.txt",
        ):
            response = self.client.get(self.origin + attempt)
            self.assertNotIn(
                "trusted-data", response.text,
                f"path traversal succeeded via {attempt!r}")

    def test_no_launch_secret_is_echoed_into_a_response_body(self):
        """The secret authorises mutations; it must not leak through the API."""
        for path in ("/api/health", "/", "/api/projects"):
            response = self.client.get(self.origin + path)
            self.assertNotIn(
                self.context.launch_secret, response.text,
                f"launch secret leaked in {path}")


if __name__ == "__main__":
    unittest.main()
