"""Secure user-mode loopback transport for the offline local web application.

The listener binds only to IPv4 loopback, uses an OS-assigned/high port, reads
back the actual bound address, starts Uvicorn in-process and shuts it down
cleanly. No service, elevation, URL reservation or firewall change is needed.
"""
from __future__ import annotations

import socket
import threading
import time
from dataclasses import dataclass
from typing import Any

from app.errors import AppError

LOOPBACK_HOST = "127.0.0.1"
OS_ASSIGNED_PORT = 0
APPROVED_FALLBACK_PORTS = (49731, 49732, 49733, 49734, 49735)
FORBIDDEN_PORTS = frozenset({80, 443})


@dataclass(frozen=True)
class TransportEvidence:
    user_identity_class: str
    manifest_execution_level: str
    bound_address: str
    bound_port: int
    listener_process_id: int
    rejected_probes: tuple[str, ...]
    created_service: bool
    created_firewall_rule: bool
    created_url_reservation: bool
    lifecycle_clean_shutdown: bool


@dataclass
class LoopbackListener:
    host: str
    port: int
    launch_secret: str
    server: Any
    thread: threading.Thread
    socket: socket.socket


def generate_launch_secret() -> str:
    import secrets
    return secrets.token_urlsafe(32)


def is_loopback_bind_legal(host: str, port: int) -> bool:
    if host != LOOPBACK_HOST:
        return False
    if port in FORBIDDEN_PORTS:
        return False
    return port == OS_ASSIGNED_PORT or 1024 <= port <= 65535


def expected_origin(port: int) -> str:
    if not is_loopback_bind_legal(LOOPBACK_HOST, port) or port == 0:
        raise ValueError("an actual high loopback port is required")
    return f"http://{LOOPBACK_HOST}:{port}"


def verify_origin(host_header: str | None, origin_header: str | None, port: int, *, require_origin: bool = False) -> bool:
    """Validate exact Host and, when present/required, exact loopback Origin."""
    origin = expected_origin(port)
    expected_host = f"{LOOPBACK_HOST}:{port}"
    if (host_header or "").strip().lower() != expected_host:
        return False
    if require_origin and not origin_header:
        return False
    if origin_header and origin_header.rstrip("/").lower() != origin:
        return False
    return True


def start_listener(
    app: Any, *, port: int = OS_ASSIGNED_PORT, secret: str | None = None,
    startup_timeout: float = 10.0,
) -> LoopbackListener:
    """Bind first, verify the real socket, then hand that socket to Uvicorn."""
    if not is_loopback_bind_legal(LOOPBACK_HOST, port):
        raise AppError("LOCAL_LOOPBACK_BIND_FAILED", support_detail=f"illegal requested port {port}")
    try:
        import uvicorn
    except ImportError as error:
        raise AppError("PACKAGE_COMPONENT_MISSING", support_detail="uvicorn is not bundled") from error

    listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        listener_socket.bind((LOOPBACK_HOST, port))
        listener_socket.listen(128)
        bound_host, bound_port = listener_socket.getsockname()[:2]
        if bound_host != LOOPBACK_HOST or not is_loopback_bind_legal(bound_host, int(bound_port)) or int(bound_port) == 0:
            raise AppError("LOCAL_TRANSPORT_INTEGRITY_FAILED", support_detail=f"actual_bind={bound_host}:{bound_port}")
        launch_secret = secret or generate_launch_secret()
        context = getattr(getattr(app, "state", None), "context", None)
        if context is not None:
            context.port = int(bound_port)
            context.launch_secret = launch_secret

        config = uvicorn.Config(
            app, host=LOOPBACK_HOST, port=int(bound_port), log_level="warning",
            access_log=False, proxy_headers=False, server_header=False,
            date_header=False, workers=1,
        )
        server = uvicorn.Server(config)
        thread = threading.Thread(
            target=server.run, kwargs={"sockets": [listener_socket]},
            name="excel-intelligence-loopback", daemon=True,
        )
        thread.start()
        deadline = time.monotonic() + startup_timeout
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(0.02)
        if not server.started:
            server.should_exit = True
            thread.join(timeout=1.0)
            raise AppError("LOCAL_LOOPBACK_BIND_FAILED", support_detail="Uvicorn did not reach started state")
        return LoopbackListener(LOOPBACK_HOST, int(bound_port), launch_secret, server, thread, listener_socket)
    except Exception:
        try:
            listener_socket.close()
        except OSError:
            pass
        raise


def shutdown(listener: LoopbackListener, *, timeout: float = 10.0) -> None:
    """Request graceful ASGI shutdown, then release the pre-bound socket."""
    listener.server.should_exit = True
    if threading.current_thread() is not listener.thread:
        listener.thread.join(timeout=timeout)
    try:
        listener.socket.close()
    except OSError:
        pass
