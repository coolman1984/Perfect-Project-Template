# Production Quality golden reference

This is **Reference A** for project-centric reuse (V10 Part 34 / build program
S4). It is the same Golden Production Quality workflow proven at
`reports/_REFERENCE/`, migrated onto the project-centric contract
(`project.toml` + `sources.toml` + `dashboard.toml` + `business_rules/`)
instead of the legacy report contract (`report.toml` + `pipeline.toml` +
`sql/`).

One source role:

- `production` — transaction / upsert, with corrections and quarantine

Same fixtures, same hand-derived expected numbers as the legacy reference:
`tests/fixtures/reference/*.csv` and `tests/expected/reference/expected.json`.
Only the table names differ (project-prefixed:
`analytics.history_reference_production_quality_production` instead of
`analytics.history_production`), because the project pipeline namespaces every
source's tables by `{project_id}_{source_id}` so multiple projects can share
one database safely.

## What is new here versus the legacy report

The legacy report's `approved_categories` check (Part 9, "loaded and flagged
for review") had no equivalent in the project contract — `source_registry`
only supported `required_columns`, `control_totals` and
`non_negative_columns`. Migrating this reference faithfully required adding it
as a genuine, small, reusable capability (`contracts/source_registry.schema.json`,
`factory/project_contract.py`, `app/project_pipeline.py`), not dropping the
check. It is optional and unused by every other reference, so nothing else
changes behaviour.

## Evidence status

**REFERENCE_PROVEN on the fixture extraction port**, mirroring the legacy
report's proof: `tests/golden/test_reference_project_pipeline.py` runs periods
1, 2 and the bad period 3 through `app.project_orchestrator.run_project` and
asserts the same hand-derived numbers as `tests/expected/reference/expected.json`.

This is **not** `ENVIRONMENT_PROVEN`. The proof runs through the fixture
adapter; real protected Excel/COM extraction is a separate environment-bound
gate (V10 Part 37).

The legacy `reports/_REFERENCE/` path is untouched and keeps working — V10 §0
forbids deleting a working compatibility path for conceptual cleanliness.
