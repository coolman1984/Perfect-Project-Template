"""Loopback transport: bind, secret, origin checks, lifecycle (Parts 0.9, 22.10, 25.5.1).

This module is the security boundary of the whole product, so its rules are
written out in full rather than summarized.

**"No external server" does not mean "no local server."** It means no cloud
host, no shared web server, no remote API and no office-network dependency.
The bundled FastAPI/Uvicorn process stays. Removing it to avoid administrator
rights is a Part 27.6 architecture violation — a user-mode loopback socket has
never required elevation.

Startup sequence (Part 25.5.1)::

    verify package hashes and asInvoker execution level
    -> acquire the per-user single-instance lock
    -> choose an OS-assigned port (port 0) or a bounded approved high port
    -> generate a per-launch secret IN MEMORY
    -> start Uvicorn on 127.0.0.1 only
    -> health check the exact process, address and port
    -> open the renderer with a one-time bootstrap handshake
    -> on exit: reject new work, finish or roll back at a safe boundary,
       stop the listener, release the lock

Mandatory invariants:

1. The executable runs under the invoking standard user's token; its manifest is
   `asInvoker`; no child process self-elevates.
2. The launcher never uses `runas`; code never installs a service and never
   invokes `netsh` for a URL reservation or firewall rule.
3. The socket's **actual bound address** is verified as `127.0.0.1`. A host
   string in configuration is not proof — read it back from the socket.
4. The API accepts only the exact launch session and the expected loopback
   origin and host. Wildcard CORS is forbidden.
5. Port-conflict recovery changes only the local port, within the approved
   algorithm, and updates the exact URL the launcher opens. Never "fix" a bind
   failure by elevating.
6. A browser refresh reconnects to durable state by `run_id` and event sequence.
   The renderer never becomes the source of truth.
7. Startup fails closed with a stable code — `LOCAL_LOOPBACK_BIND_FAILED`,
   `LOCAL_ORIGIN_REJECTED`, `LOCAL_TRANSPORT_INTEGRITY_FAILED`,
   `ELEVATION_FORBIDDEN` — and writes diagnostic evidence.
8. The per-launch secret lives in process memory only: never on disk, never in
   a log, never in a URL, never in browser history, never in a run manifest
   (Part 43).

If corporate endpoint policy blocks the loopback socket, that is an
environmental compatibility failure to diagnose and document with IT. It is not
permission to request administrator rights, add a firewall exclusion, bind to
the LAN, or delete the local API (Part 22.10).
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass

#: Bind address. IPv4 loopback only — never 0.0.0.0, ::, a hostname, a LAN
#: address, or any public interface (Part 22.10).
LOOPBACK_HOST = "127.0.0.1"

#: 0 asks the OS for a free port, which is the preferred strategy. The bounded
#: list is the fallback when a deterministic port is operationally required.
OS_ASSIGNED_PORT = 0
APPROVED_FALLBACK_PORTS = (49731, 49732, 49733, 49734, 49735)

#: Ports the application must never bind (Part 22.10).
FORBIDDEN_PORTS = frozenset({80, 443})


@dataclass(frozen=True)
class TransportEvidence:
    """Written to release/LOCAL_TRANSPORT_EVIDENCE.json (Part 23.10)."""

    user_identity_class: str          # "standard" — never "administrator"
    manifest_execution_level: str     # "asInvoker"
    bound_address: str                # read back from the socket, not config
    bound_port: int
    listener_process_id: int
    rejected_probes: tuple[str, ...]  # wrong Host/Origin/secret, non-loopback
    created_service: bool             # must be False
    created_firewall_rule: bool       # must be False
    created_url_reservation: bool     # must be False
    lifecycle_clean_shutdown: bool


def generate_launch_secret() -> str:
    """A cryptographically random per-launch secret (Part 22.10).

    Held in memory for exactly one launch. Never persisted, logged, placed in a
    URL, or written to a manifest — a secret in a URL ends up in browser
    history, which is why the handshake is one-time and header-based.
    """
    return secrets.token_urlsafe(32)


def is_loopback_bind_legal(host: str, port: int) -> bool:
    """Pure predicate, so the rule is unit-testable without a socket.

    >>> is_loopback_bind_legal("127.0.0.1", 49731)
    True
    >>> is_loopback_bind_legal("0.0.0.0", 49731)
    False
    >>> is_loopback_bind_legal("127.0.0.1", 443)
    False
    """
    if host != LOOPBACK_HOST:
        return False
    if port in FORBIDDEN_PORTS:
        return False
    return port == OS_ASSIGNED_PORT or 1024 <= port <= 65535


def start_listener(*_args: object, **_kwargs: object):
    raise NotImplementedError(
        "Implement the Part 25.5.1 startup sequence. Verify the bound address "
        "by reading it back from the socket — a host string in configuration "
        "is not proof (invariant 3).")


def verify_origin(*_args: object, **_kwargs: object):
    raise NotImplementedError(
        "Validate Host and Origin against the exact current loopback origin. "
        "Reject everything else with LOCAL_ORIGIN_REJECTED. Wildcard CORS and "
        "credentials-to-wildcard are forbidden (Part 22.10).")


def shutdown(*_args: object, **_kwargs: object):
    raise NotImplementedError(
        "Reject new work, finish or roll back at a safe boundary, stop the "
        "listener, release the single-instance lock (Part 25.5.1).")
