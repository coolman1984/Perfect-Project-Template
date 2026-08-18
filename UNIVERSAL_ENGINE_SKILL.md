# Universal Excel Automation Engine — Adaptation Skill

**The application is already built. Adapt the differences. Do not rebuild the application.**

The target is that a normal new Excel automation reuses roughly 70–80% or more of the proven system. Never game a percentage; the real measures are fewer core files changed, less new code, less context, fewer architecture decisions and fewer defects.

## What the employee supplies

The employee supplies Excel files and business knowledge: what one row means, relationships, calculations, KPIs, trusted totals, correction behavior and ownership. Do not ask the employee to choose DuckDB, FastAPI, COM, Parquet, ports, services or packaging technology. Those are already governed.

## Required work order

`UNDERSTAND -> PROFILE -> MAP -> CONFIGURE -> SMALL BUSINESS LOGIC -> TEST -> DELIVER`

1. Understand the business request.
2. Profile Excel structure compactly. Do not pour a giant workbook into model context.
3. Run the project-map router for the exact task.
4. Classify needs as reuse-as-is, configuration, report business logic, or genuinely missing reusable capability.
5. Configure the existing engine first.
6. Put unique business formulas in report SQL/configuration.
7. Change Universal Core only for a genuinely reusable missing capability.
8. Test idempotency, corrections, reconciliation, quality failure and dashboard results.
9. Record adaptation/map/state evidence.

## Universal Core, normally unchanged

Authorized desktop Excel COM/Value2 extraction; chunked staging/lineage; DuckDB; Parquet archive; history/idempotency; quality/quarantine/reconciliation; configured SQL analytics; reusable insight patterns; configured dashboard JSON; shared UI; FastAPI/Uvicorn loopback on 127.0.0.1; offline packaging; project map; approvals and gates.

## Normal variation points

Prefer `reports/<id>/` plus its additive migration and focused tests: `report.toml`, `pipeline.toml`, `dashboard.toml`, `sql/clean.sql`, `sql/checks.sql`, `sql/metrics.sql`, `sql/insights.sql`, fixtures and expected values.

Business formulas stay in versioned SQL. JavaScript renders; it does not become a second calculation engine.

## Never hardcode one department into Universal Core

Shared Python must not contain concepts such as defect rate, sales revenue, headcount, inventory shortage, budget variance, model code or downtime minutes. Those belong to report configuration/SQL.

## Low-token source understanding

Use structural profiles: sheet identity, row/column counts, column names, probable types, null/distinct counts, candidate keys, date-like fields and schema drift. `factory/source_profile.py` omits raw samples by default. Never place hundreds of thousands of rows into AI context.

## Human boundary

AI may infer and suggest. It may not silently approve uncertain business meaning. Humans approve record identity, correction behavior, trusted totals, KPI meaning and storage policy. Technical architecture is already governed.

## Two executable references

`reports/_REFERENCE/` proves the first full pipeline. `reports/line_downtime/` proves a different Maintenance-style data shape and KPI set through the same Universal Core. Copy patterns, not business columns.

## Core-change rule

Before changing shared engine code ask: can configuration express this, does an extension point exist, is this truly common, and can it be added once without department meaning? A justified core improvement needs regression evidence across both references.

A good new project feels like: **the agent taught the existing application what this department's Excel process means.**
