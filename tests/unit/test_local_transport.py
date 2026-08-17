"""Loopback bind rules (Constitution Parts 0.9, 22.10).

These are pure predicates so the security rule is testable without a socket.
The runtime must ALSO verify the actual bound address by reading it back from
the socket — a host string in configuration is not proof (Part 25.5.1 rule 3).
"""

from __future__ import annotations

import unittest

from app.local_transport import (
    APPROVED_FALLBACK_PORTS, FORBIDDEN_PORTS, LOOPBACK_HOST, OS_ASSIGNED_PORT,
    generate_launch_secret, is_loopback_bind_legal,
)


class TestLoopbackBindRules(unittest.TestCase):
    def test_loopback_high_port_is_legal(self):
        self.assertTrue(is_loopback_bind_legal(LOOPBACK_HOST, 49731))

    def test_os_assigned_port_is_legal(self):
        self.assertTrue(is_loopback_bind_legal(LOOPBACK_HOST, OS_ASSIGNED_PORT))

    def test_every_approved_fallback_port_is_legal(self):
        for port in APPROVED_FALLBACK_PORTS:
            self.assertTrue(is_loopback_bind_legal(LOOPBACK_HOST, port))

    def test_non_loopback_addresses_are_rejected(self):
        # Part 22.10: never the LAN, never a public interface, never a hostname.
        for host in ("0.0.0.0", "::", "[::]", "192.168.1.10", "localhost", "example.local"):
            self.assertFalse(is_loopback_bind_legal(host, 49731),
                             f"{host} must be rejected")

    def test_privileged_web_ports_are_rejected(self):
        for port in FORBIDDEN_PORTS:
            self.assertFalse(is_loopback_bind_legal(LOOPBACK_HOST, port))

    def test_reserved_low_ports_are_rejected(self):
        self.assertFalse(is_loopback_bind_legal(LOOPBACK_HOST, 22))


class TestLaunchSecret(unittest.TestCase):
    def test_secret_is_long_and_unique_per_launch(self):
        first, second = generate_launch_secret(), generate_launch_secret()
        self.assertNotEqual(first, second)
        self.assertGreaterEqual(len(first), 32)

    def test_secret_is_url_safe_but_still_must_not_go_in_a_url(self):
        # URL-safe encoding is for header transport. Part 43 forbids putting the
        # secret in a URL, where it would land in browser history.
        secret = generate_launch_secret()
        self.assertTrue(all(character.isalnum() or character in "-_" for character in secret))


if __name__ == "__main__":
    unittest.main()
