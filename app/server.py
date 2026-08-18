"""FastAPI loopback control plane for the reusable offline application."""
from __future__ import annotations

import json
import secrets
import tomllib
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.errors import AppError
from app.local_transport import LOOPBACK_HOST, generate_launch_secret, shutdown, start_listener, verify_origin
from app.locks import acquire_report_lock

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def _operator_error(error: AppError) -> dict[str, object]:
    return error.operator_screen("en")


def create_app(context: ServerContext | None = None):
    """Create the same-origin FastAPI app used by every department project."""
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import HTMLResponse, JSONResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as error:
        raise AppError("PACKAGE_COMPONENT_MISSING", support_detail="FastAPI/Starlette is not bundled") from error

    runtime = context or ServerContext(launch_secret=generate_launch_secret())
    if not runtime.launch_secret:
        runtime.launch_secret = generate_launch_secret()
    app = FastAPI(
        title="Excel Intelligence Local API", docs_url=None, redoc_url=None,
        openapi_url=None,
    )
    app.state.context = runtime

    @app.middleware("http")
    async def local_security(request: Request, call_next):
        # Port is filled with the actual bound socket before Uvicorn serves requests.
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
            "status": "ok",
            "offline": True,
            "host": LOOPBACK_HOST,
            "port": runtime.port,
            "dashboard_available": (runtime.output_root / "latest_dashboard.json").exists(),
        }

    @app.get("/api/reports")
    async def reports():
        configured = []
        if runtime.reports_root.exists():
            for directory in sorted(runtime.reports_root.iterdir()):
                config_path = directory / "report.toml"
                if not directory.is_dir() or not config_path.exists():
                    continue
                config = tomllib.loads(config_path.read_text(encoding="utf-8"))
                configured.append({
                    "report_id": config.get("report_id", directory.name),
                    "mode": config.get("mode", "prototype"),
                    "adapter": config.get("excel", {}).get("adapter", "unknown"),
                })
        return configured

    @app.get("/api/dashboard")
    async def dashboard():
        path = runtime.output_root / "latest_dashboard.json"
        if not path.exists():
            return JSONResponse({"status": "NO_DASHBOARD", "message": "No successful report has been published yet."}, status_code=404)
        return json.loads(path.read_text(encoding="utf-8"))

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

    # API routes above take precedence; the mounted app serves only bundled files.
    app.mount("/", StaticFiles(directory=str(runtime.web_root), html=False), name="web")
    return app


def main() -> None:
    """Start one standard-user loopback session and open its exact local URL."""
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
