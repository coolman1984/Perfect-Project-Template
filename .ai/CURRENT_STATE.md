# CURRENT STATE

## Product identity

This repository is evolving into a **Universal Excel Automation Engine + Adaptation Template**.

**The application already exists. New department projects adapt configuration and business logic; they do not rebuild the application.**

## Proven reusable foundation in this branch

- Golden Reference executes extract → stage → quality → clean → history → archive → SQL analytics → evidence insights → dashboard JSON against synthetic fixtures.
- A genuinely different Maintenance downtime report executes through the same Universal Core with different columns, keys, KPIs, charts, quality rules and fixtures.
- History supports append/upsert/snapshot/replace-period and idempotent reruns.
- Shared analytics and dashboard meaning are configuration-driven through each report's `dashboard.toml` and versioned SQL.
- Compact source profiling omits raw samples by default; adaptation manifests/core-change guards keep future agents focused on variation points.
- A reusable FastAPI/Uvicorn loopback runtime now provides verified `127.0.0.1` startup/shutdown, launch-secret + Host/Origin controls, durable run events, report locks, local hashed intake, run start/status/events, dashboard/history/quality endpoints and the shared web shell.
- Windows CI exercises BAT launchers, portable tests, application tests and a workspace path containing spaces plus Arabic characters.
- The standalone HTML builder is self-contained and fails closed when the pinned local ECharts asset is missing; static verification never pretends to be a browser proof.

## Explicit remaining gaps

- `app/excel/com_adapter.py` production COM extraction is still an implementation/proof gap; real protected Excel/DRM proof can only close on the authorized corporate Windows environment.
- Employee run orchestration currently accepts one source file. Multiple workbooks with different business roles still need an explicit multi-source composition contract; the engine intentionally does not concatenate unrelated schemas.
- The actual pinned `web/vendor/echarts.min.js` binary is not stored in this repository yet. Target version is recorded as 6.1.0; release packaging must include and hash-verify it.
- Full headless-browser proof (zero network requests/JS errors plus theme/RTL/print/filter checks) is not yet wired to release publication.
- Final offline executable/runtime/wheelhouse packaging is not complete.
- GitHub server settings such as default branch `main` and branch protection must be enabled in GitHub Settings; repository files cannot truthfully claim those settings were changed.

Environment-bound gates remain conditional even when Linux and Windows CI are green.
