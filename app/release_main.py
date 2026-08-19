"""Entry point for the sealed Windows one-folder release."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import urllib.request
import webbrowser
from pathlib import Path


def release_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parent.parent


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_package(root: Path) -> list[str]:
    manifest = root / "checksums.sha256"
    if not manifest.is_file():
        return ["checksums.sha256 is missing"]
    failures: list[str] = []
    for number, line in enumerate(manifest.read_text("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            expected, relative = line.split(" *", 1)
        except ValueError:
            failures.append(f"invalid manifest line {number}")
            continue
        path = root / Path(relative)
        if not path.is_file():
            failures.append(f"missing {relative}")
            continue
        actual = _sha256(path)
        if actual != expected:
            failures.append(f"checksum mismatch {relative}")
    return failures


def self_test(root: Path) -> dict[str, object]:
    import duckdb
    import fastapi
    import uvicorn
    from app.excel import session as excel_session
    from app.local_transport import generate_launch_secret, shutdown, start_listener
    from app.server import ServerContext, create_app

    excel_session.verify_com_binding()

    with tempfile.TemporaryDirectory() as temporary:
        database = duckdb.connect(str(Path(temporary) / "smoke.duckdb"))
        try:
            value = database.execute("SELECT 42").fetchone()[0]
        finally:
            database.close()
    context = ServerContext(repo_root=root, launch_secret=generate_launch_secret())
    listener = start_listener(create_app(context), secret=context.launch_secret)
    context.listener = listener
    try:
        with urllib.request.urlopen(
            f"http://{listener.host}:{listener.port}/api/health", timeout=10
        ) as response:
            health = json.loads(response.read().decode("utf-8"))
    finally:
        shutdown(listener)
    return {
        "status": "PASS",
        "database_value": value,
        "fastapi": fastapi.__version__,
        "uvicorn": uvicorn.__version__,
        "loopback_health": health.get("status"),
        "host": listener.host,
    }


def start(root: Path) -> int:
    from app.local_transport import generate_launch_secret, shutdown, start_listener
    from app.locks import acquire_report_lock
    from app.server import ServerContext, create_app

    failures = verify_package(root)
    if failures:
        print("PACKAGE_COMPONENT_MISSING")
        for failure in failures:
            print(f"  {failure}")
        return 1
    context = ServerContext(repo_root=root, launch_secret=generate_launch_secret())
    with acquire_report_lock("_application", root=root / "runs" / "locks"):
        listener = start_listener(create_app(context), secret=context.launch_secret)
        context.listener = listener
        webbrowser.open(f"http://{listener.host}:{listener.port}/", new=1)
        try:
            listener.thread.join()
        except KeyboardInterrupt:
            pass
        finally:
            shutdown(listener)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--verify-package", action="store_true")
    args = parser.parse_args()
    root = release_root()
    if args.self_test:
        print(json.dumps(self_test(root), sort_keys=True))
        return 0
    if args.verify_package:
        failures = verify_package(root)
        print(json.dumps({"status": "FAIL" if failures else "PASS", "failures": failures}))
        return 1 if failures else 0
    return start(root)


if __name__ == "__main__":
    raise SystemExit(main())
