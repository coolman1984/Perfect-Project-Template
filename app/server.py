"""Local loopback API — the renderer-to-application boundary (Parts 0.9, 25.5).

Task contract (Part 17.1):

    LAYER             transport / API
    INPUTS            HTTP requests from the local renderer, on 127.0.0.1 only
    OUTPUTS           typed responses, durable events, approved local outputs
    VALIDATION        every route validates its input; every state-changing
                      route requires the per-launch secret and an exact origin
    FAILURE BEHAVIOR  fail closed with a registry error code; trusted history
                      and the last approved dashboard are never disturbed

This API **owns** validated uploads, run creation, durable progress and events,
quality results, approved history, dashboard data, exports, cancellation and
safe shutdown.

Browser JavaScript may not automate Excel COM, open DuckDB, read arbitrary
files, or bypass this boundary in any other way (Part 0.9). A proposal called
"direct Windows connection", "native connection", "no-server mode" or "static
local mode" is an architecture deviation under Part 0.7 — not a packaging
detail, and not something to rename and implement quietly.

Route contract — the full table lives in `.ai/CONTRACTS.md` and Part 25.5::

    GET  /api/health                  runtime and database readiness
    GET  /api/reports                 configured reports and requirements
    POST /api/uploads                 copy files into intake, validated
    POST /api/runs                    start one run; idempotency key + lock
    GET  /api/runs/{id}               current durable state
    GET  /api/runs/{id}/events        ordered, replayable progress
    POST /api/runs/{id}/answer        answer a waiting question
    POST /api/runs/{id}/cancel        safe-boundary cancellation only
    GET  /api/dashboard               latest APPROVED dashboard JSON
    GET  /api/history                 weekly approved history, paginated
    GET  /api/quality/{id}            checks, exceptions, reconciliation
    GET  /outputs/{file}              approved output; path allow-list only

Security requirements on every request (Part 22.10):

    - run as the same standard interactive user as Excel and the renderer
    - require the per-launch secret on state-changing requests
    - validate Host and Origin; allow only the exact loopback origin
    - no wildcard CORS; no credentials-to-wildcard combination
    - SameSite=Strict and secure attributes when cookies are used
    - request, upload, body, file-count, extension and signature limits
    - rate and concurrency limits
    - canonicalized, allow-listed output paths; per-run folders
    - developer documentation and debug endpoints disabled in the employee
      release unless explicitly required and protected
    - start only after integrity verification; stop cleanly with the app
"""

from __future__ import annotations


def create_app():
    """Build the FastAPI application with its security middleware.

    Wire, in this order: integrity verification -> origin/host validation ->
    launch-secret check -> size and rate limits -> routes. A route registered
    before the security middleware is a defect, not a shortcut.
    """
    raise NotImplementedError(
        "Implement in Phase 2 (vertical slice). Keep the bundled FastAPI/"
        "Uvicorn stack: it is a locked component (Part 23.8) and removing it "
        "requires an explicitly approved Part 0.7 deviation.")


def main() -> None:
    """Entry point used by the packaged executable and START_APP.bat."""
    raise NotImplementedError(
        "Implement the Part 25.5.1 startup sequence via app.local_transport.")
