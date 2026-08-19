# Perfect Project Template — Universal Excel Automation Engine

One reusable offline Excel automation application that ChatGPT Work **adapts**
to new departments and Excel files instead of rebuilding the same software.

## The whole product

```text
Template ZIP + Excel files + business explanation
→ ChatGPT Work reuses and configures the existing engine
→ tests, reconciles and builds ProjectName.zip
→ employee extracts, double-clicks START and uses the local browser app
```

The operator ZIP exposes only `START.bat`, `QUICK_START.html` and
`Application/`. Python, databases, packages, terminals, Git, configuration,
migrations, ports and build tools remain internal. See `docs/PRODUCT_GOAL.md`.

```text
Employee gives Excel files + business meaning
→ AI profiles structure with small context
→ AI maps to existing capabilities
→ AI changes configuration + small report SQL
→ existing engine extracts, validates, stores, updates, calculates and renders
→ tests + reconciliation prove the result
```

The application is the reusable asset. The agent is mainly the adapter.

## Agent start

`AGENTS.md → PROJECT_SKILL.md → UNIVERSAL_ENGINE_SKILL.md → .ai/READ_FIRST.md → PROJECT_TOOL doctor → map context`

Do not broad-read the repository or huge workbooks into context.

## Reusable foundation

Authorized desktop Excel COM/Value2 extraction, chunked staging/lineage, DuckDB + Parquet history, four update modes, idempotent reruns, quality/quarantine/reconciliation, versioned SQL analytics, reusable evidence patterns, configuration-driven dashboard JSON, shared web architecture, FastAPI/Uvicorn loopback, offline packaging, map/context controls, approvals and gates.

A normal project should mostly change `reports/<id>/`, its additive migration and focused tests.

## Two executable references

`reports/_REFERENCE/` is the first full reference. `reports/line_downtime/` is deliberately different: Maintenance event records, downtime KPIs and a different business key. It exists to prove shared Python is not secretly a Production Quality application.

## Locked production shape

`Windows → authorized desktop Excel → COM/Value2 → ExtractionPort → staging → quality → clean/history → DuckDB/Parquet → versioned SQL → dashboard JSON → local FastAPI/Uvicorn web app`

Offline means dependencies are bundled. It does not mean dependencies disappear and Windows performs interpretive dance in their place.

Humans approve business meaning. AI adapts the proven engine and may suggest mappings, but it cannot invent approvals or redesign settled architecture.

Reuse is judged by smaller change surface, less new code, less context and fewer defects. `factory/adaptation.py` records a capability-level reuse indicator but does not pretend it is mathematically exact source-code reuse.

Linux and Windows CI provide portable/build-machine evidence. Real protected-file + Excel COM proof remains an environment-bound gate on the authorized corporate Windows PC.

See `docs/GITHUB_GOVERNANCE.md` and `UNIVERSAL_ENGINE_SKILL.md`.
