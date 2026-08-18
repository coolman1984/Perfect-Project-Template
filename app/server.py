"""FastAPI loopback control plane for the reusable offline application.

This module owns the employee-facing local boundary once. Department reports
supply configuration and SQL; they do not create their own upload/run server.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
import threading
import tomllib
import uuid
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from app import events, orchestrator
from app.data.database import Database
from app.errors import AppError
from app.local_transport import LOOPBACK_HOST, generate_launch_secret, shutdown, start_listener, verify_origin
from app.locks import acquire_report_lock

REPO_ROOT = Path(__file__).resolve().parent.parent
EXCEL_EXTENSIONS = frozenset({".xlsx", ".xlsm", ".xlsb", ".xls"})
FIXTURE_EXTENSIONS = frozenset({".csv"})
MAX_UPLOAD_BYTES = 512 * 1024 * 1024


@dataclass
class ServerContext:
    repo_root: Path = REPO_ROOT
    launch_secret: str = ""
    port: int = 0
    listener: Any = None

    @property
    def reports_root(self) -> Path:
        return self.repo_root / "reports"

    @property
    def web_root(self) -> Path:
        return self.repo_root / "web"

    @property
    def output_root(self) -> Path:
        return self.repo_root / "output"

    @property
    def inbox_root(self) -> Path:
        return self.repo_root / "inbox"

    @property
    def runs_root(self) -> Path:
        return self.repo_root / "runs"

    @property
    def database_path(self) -> Path:
        return self.repo_root / "data" / "warehouse.duckdb"


def _operator_error(error: AppError) -> dict[str, object]:
    return error.operator_screen("en")


def _safe_report_id(value: str) -> str:
    if not value or len(value) > 120 or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-" for ch in value):
        raise ValueError("invalid report_id")
    return value


def _report_config(context: ServerContext, report_id: str) -> dict[str, Any]:
    report_id = _safe_report_id(report_id)
    path = context.reports_root / report_id / "report.toml"
    if not path.exists():
        raise AppError("SRC_NOT_FOUND", support_detail=f"unknown report_id={report_id}")
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _safe_upload_name(encoded_name: str) -> str:
    name = unquote(encoded_name or "").strip()
    if not name or name in {".", ".."} or Path(name).name != name:
        raise ValueError("invalid file name")
    if any(ord(ch) < 32 for ch in name) or len(name) > 220:
        raise ValueError("invalid file name")
    return name


def _upload_meta_path(context: ServerContext, report_id: str, upload_id: str) -> Path:
    if not upload_id or len(upload_id) != 32 or any(ch not in "0123456789abcdef" for ch in upload_id):
        raise ValueError("invalid upload_id")
    return context.inbox_root / _safe_report_id(report_id) / upload_id / "upload.json"


def _load_upload(context: ServerContext, report_id: str, upload_id: str) -> dict[str, Any]:
    path = _upload_meta_path(context, report_id, upload_id)
    if not path.exists():
        raise AppError("SRC_NOT_FOUND", support_detail=f"upload_id={upload_id}")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    source = Path(metadata["stored_path"]).resolve()
    allowed = (context.inbox_root / report_id / upload_id).resolve()
    if allowed not in source.parents or not source.is_file():
        raise AppError("LOCAL_TRANSPORT_INTEGRITY_FAILED", support_detail="upload path escaped its allow-listed directory")
    return metadata


def _run_worker(context: ServerContext, report_id: str, source: Path, run_id: str) -> None:
    try:
        orchestrator.run(
            report_id, source, run_id=run_id, repo_root=context.repo_root,
            database_path=context.database_path,
        )
    except Exception:
        # Orchestrator already stores a durable FAILED event. Never put a stack
        # trace, workbook row or secret in the browser delivery channel.
        return


def create_app(context: ServerContext | None = None):
    """Create the same-origin FastAPI app used by every department project."""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as error:
        raise AppError("PACKAGE_COMPONENT_MISSING", support_detail="FastAPI/Starlette is not bundled") from error

    runtime = context or ServerContext(launch_secret=generate_launch_secret())
    if not runtime.launch_secret:
        runtime.launch_secret = generate_launch_secret()
    app = FastAPI(title="Excel Intelligence Local API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.context = runtime

    @app.middleware("http")
    async def local_security(request: Request, call_next):
        if runtime.port:
            mutating = request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}
            if not verify_origin(
                request.headers.get("host"), request.headers.get("origin"),
                runtime.port, require_origin=mutating,
            ):
                error = AppError("LOCAL_ORIGIN_REJECTED", support_detail="Host/Origin did not match this launch")
                return JSONResponse(_operator_error(error), status_code=403)
            if mutating:
                supplied = request.headers.get("x-launch-secret", "")
                if not supplied or not secrets.compare_digest(supplied, runtime.launch_secret):
                    error = AppError("LOCAL_ORIGIN_REJECTED", support_detail="launch secret missing or invalid")
                    return JSONResponse(_operator_error(error), status_code=403)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(_request: Request, error: AppError):
        return JSONResponse(_operator_error(error), status_code=400)

    @app.get("/api/health")
    async def health():
        return {
            "status": "ok", "offline": True, "host": LOOPBACK_HOST,
            "port": runtime.port,
            "dashboard_available": (runtime.output_root / "latest_dashboard.json").exists(),
        }

    @app.get("/api/reports")
    async def reports():
        configured = []
        if runtime.reports_root.exists():
            for directory in sorted(runtime.reports_root.iterdir()):
                config_path = directory / "report.toml"
                if not directory.is_dir() or not config_path.exists() or directory.name.startswith("_"):
                    continue
                config = tomllib.loads(config_path.read_text(encoding="utf-8"))
                configured.append({
                    "report_id": config.get("report_id", directory.name),
                    "mode": config.get("mode", "prototype"),
                    "adapter": config.get("excel", {}).get("adapter", "unknown"),
                    "sheet": config.get("excel", {}).get("sheet", ""),
                })
        return configured

    @app.post("/api/uploads")
    async def upload(request: Request, report_id: str):
        config = _report_config(runtime, report_id)
        try:
            file_name = _safe_upload_name(request.headers.get("x-file-name", ""))
        except ValueError as error:
            raise AppError("SRC_NOT_FOUND", support_detail=str(error)) from error
        adapter = str(config.get("excel", {}).get("adapter", "com"))
        allowed_extensions = FIXTURE_EXTENSIONS if adapter == "fixture" else EXCEL_EXTENSIONS
        if Path(file_name).suffix.lower() not in allowed_extensions:
            raise AppError(
                "SRC_NOT_FOUND",
                support_detail=f"extension {Path(file_name).suffix!r} is not allowed for adapter {adapter}",
            )
        upload_id = uuid.uuid4().hex
        directory = runtime.inbox_root / report_id / upload_id
        directory.mkdir(parents=True, exist_ok=False)
        target = directory / file_name
        digest = hashlib.sha256()
        size = 0
        try:
            with target.open("xb") as handle:
                async for chunk in request.stream():
                    if not chunk:
                        continue
                    size += len(chunk)
                    if size > MAX_UPLOAD_BYTES:
                        raise AppError("RESOURCE_DISK_LOW", support_detail="upload exceeds the configured 512 MiB safety limit")
                    digest.update(chunk)
                    handle.write(chunk)
        except Exception:
            try:
                target.unlink()
            except FileNotFoundError:
                pass
            raise
        metadata = {
            "upload_id": upload_id, "report_id": report_id, "file_name": file_name,
            "stored_path": str(target.resolve()), "size": size, "sha256": digest.hexdigest(),
        }
        (directory / "upload.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {key: metadata[key] for key in ("upload_id", "report_id", "file_name", "size", "sha256")}

    @app.post("/api/runs")
    async def start_run(request: Request):
        payload = await request.json()
        report_id = _safe_report_id(str(payload.get("report_id", "")))
        _report_config(runtime, report_id)
        upload_id = str(payload.get("upload_id", ""))
        metadata = _load_upload(runtime, report_id, upload_id)
        run_id = orchestrator.new_run_id()
        thread = threading.Thread(
            target=_run_worker,
            args=(runtime, report_id, Path(metadata["stored_path"]), run_id),
            name=f"excel-run-{run_id}", daemon=True,
        )
        thread.start()
        return {"run_id": run_id, "report_id": report_id, "status": "STARTING"}

    @app.get("/api/runs/{run_id}")
    async def run_status(run_id: str):
        batch = events.since(run_id, -1, root=runtime.runs_root)
        if not batch:
            return JSONResponse({"run_id": run_id, "status": "NOT_FOUND"}, status_code=404)
        latest = batch[-1]
        return {"run_id": run_id, "status": latest["stage"], "sequence": latest["sequence"], "event": latest}

    @app.get("/api/runs/{run_id}/events")
    async def run_events(request: Request, run_id: str, since: int = -1):
        if "text/event-stream" not in request.headers.get("accept", ""):
            return events.since(run_id, since, root=runtime.runs_root)

        async def stream():
            sequence = since
            while True:
                batch = events.since(run_id, sequence, root=runtime.runs_root)
                for event in batch:
                    sequence = event["sequence"]
                    yield "data: " + json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n\n"
                    if event["stage"] in {"COMPLETE", "FAILED", "CANCELLED"}:
                        return
                if await request.is_disconnected():
                    return
                await asyncio.sleep(0.4)
        return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

    @app.get("/api/dashboard")
    async def dashboard():
        path = runtime.output_root / "latest_dashboard.json"
        if not path.exists():
            return JSONResponse({"status": "NO_DASHBOARD", "message": "No successful report has been published yet."}, status_code=404)
        return json.loads(path.read_text(encoding="utf-8"))

    @app.get("/api/history")
    async def history(limit: int = 50):
        if not runtime.database_path.exists():
            return []
        limit = max(1, min(int(limit), 200))
        database = Database(runtime.database_path, read_only=True)
        try:
            rows = database.query(
                "SELECT run_id, report_id, status, started_at, finished_at, rows_extracted, rows_rejected, rows_inserted, rows_updated, quality_status, demo_data FROM sys.run ORDER BY started_at DESC LIMIT ?",
                [limit],
            )
            keys = ("run_id", "report_id", "status", "started_at", "finished_at", "rows_extracted", "rows_rejected", "rows_inserted", "rows_updated", "quality_status", "demo_data")
            return [dict(zip(keys, row)) for row in rows]
        finally:
            database.close()

    @app.get("/api/quality/{run_id}")
    async def quality(run_id: str):
        if not runtime.database_path.exists():
            return []
        database = Database(runtime.database_path, read_only=True)
        try:
            rows = database.query(
                "SELECT check_id, scope, severity, status, expected, actual, difference, tolerance, message, evidence, checked_at FROM quality.check_result WHERE run_id=? ORDER BY checked_at, check_id",
                [run_id],
            )
            keys = ("check_id", "scope", "severity", "status", "expected", "actual", "difference", "tolerance", "message", "evidence", "checked_at")
            return [dict(zip(keys, row)) for row in rows]
        finally:
            database.close()

    @app.get("/outputs/{file_name}")
    async def output_file(file_name: str):
        safe_name = _safe_upload_name(file_name)
        path = (runtime.output_root / safe_name).resolve()
        if path.parent != runtime.output_root.resolve() or not path.is_file():
            raise AppError("SRC_NOT_FOUND", support_detail="output is not allow-listed")
        return FileResponse(path)

    @app.post("/api/shutdown")
    async def request_shutdown():
        if runtime.listener is not None:
            runtime.listener.server.should_exit = True
        return {"status": "shutting_down"}

    @app.get("/", response_class=HTMLResponse)
    async def index():
        path = runtime.web_root / "index.html"
        if not path.exists():
            raise AppError("PACKAGE_COMPONENT_MISSING", support_detail="web/index.html is missing")
        nonce = secrets.token_urlsafe(18)
        secret_literal = json.dumps(runtime.launch_secret)
        bootstrap = f'<script nonce="{nonce}">window.__launchSecret={secret_literal};</script>'
        html = path.read_text(encoding="utf-8").replace(
            '<script type="module" src="app.js"></script>',
            bootstrap + '\n  <script type="module" src="app.js"></script>',
        )
        headers = {
            "Content-Security-Policy": (
                "default-src 'self'; script-src 'self' 'nonce-" + nonce + "'; "
                "style-src 'self'; img-src 'self' data:; connect-src 'self'; "
                "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
            )
        }
        return HTMLResponse(html, headers=headers)

    app.mount("/", StaticFiles(directory=str(runtime.web_root), html=False), name="web")
    return app


def main() -> None:
    context = ServerContext(launch_secret=generate_launch_secret())
    with acquire_report_lock("_application"):
        app = create_app(context)
        listener = start_listener(app, secret=context.launch_secret)
        context.listener = listener
        url = f"http://{listener.host}:{listener.port}/"
        webbrowser.open(url, new=1, autoraise=True)
        try:
            listener.thread.join()
        except KeyboardInterrupt:
            pass
        finally:
            shutdown(listener)


if __name__ == "__main__":
    main()
