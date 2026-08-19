# Line downtime reuse proof

This is **Reference B** for project-centric reuse (V10 Part 34 / build program
S4). It is the same Maintenance downtime workflow proven at
`reports/line_downtime/`, migrated onto the project-centric contract
(`project.toml` + `sources.toml` + `dashboard.toml` + `business_rules/`)
instead of the legacy report contract.

One source role:

- `downtime` — transaction / upsert, with an unapproved-category warning path

Same fixtures as the legacy reference: `tests/fixtures/downtime/*.csv`. The
expected numbers (total 305.0000 minutes across 7 active rows after period 2,
one negative row rejected, one exact duplicate filtered, an "Utility" reason
warned-not-blocked) are the same hand-checked figures
`tests/golden/test_second_report_pipeline.py` already asserts against the
legacy path.

The legacy report's `data_area = "used_range"` is not carried forward: Part
7.2 forbids trusting `UsedRange` (it remembers deleted rows), and the project
contract's discovery has no `used_range` mode at all. `sources.toml` leaves
`table` unset, so a real COM run resolves through the bounded `discover`
strategy instead — a correctness improvement over the legacy configuration,
not a faithfulness gap, since this reference proves only the fixture path.

## What is new here versus the legacy report

Same `approved_categories` capability added for Reference A
(`projects/_REFERENCE_PRODUCTION_QUALITY/README.md`); this project is the
second real usage.

## Evidence status

**REFERENCE_PROVEN on the fixture extraction port**, mirroring the legacy
report's proof: `tests/golden/test_maintenance_downtime_project_pipeline.py`
runs periods 1 and 2 through `app.project_pipeline.ProjectPipeline` and
asserts the same hand-checked numbers as
`tests/golden/test_second_report_pipeline.py`.

This is **not** `ENVIRONMENT_PROVEN`. The proof runs through the fixture
adapter; real protected Excel/COM extraction is a separate environment-bound
gate (V10 Part 37).

The legacy `reports/line_downtime/` path is untouched and keeps working — V10
§0 forbids deleting a working compatibility path for conceptual cleanliness.
