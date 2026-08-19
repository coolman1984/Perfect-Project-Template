# CURRENT STATE

## Product identity

**Universal Excel Automation Engine + Adaptation Template, under V8.1 deep-audit remediation.**

The ready application is the product. Employee agents should adapt project configuration and isolated business logic rather than rebuild technical foundations.

> **Read this before believing any "ready" claim.** Everything downstream of
> extraction is built and proven. The extraction adapter itself — the door into
> real protected Excel workbooks — is **not written** (blocker 1). The engine
> currently ingests only through the test-only fixture port, so no employee can
> yet point it at a real workbook.

## Proven reusable foundation

- Single-source Golden Production Quality pipeline executes through extraction-port fixture → staging → quality/reconciliation → clean → universal history → DuckDB/Parquet → SQL analytics → evidence insights → dashboard JSON.
- A genuinely different single-source Maintenance downtime project executes through the same Universal Core.
- Reusable FastAPI/Uvicorn loopback runtime, launch-secret/Host/Origin controls, durable events, locks, local intake, last-good dashboard publication and standalone HTML builder have Linux/Windows CI proof.
- Compact source profiling omits raw sample values by default.
- The three-source Supply Chain project (orders + inventory + item master)
  executes end to end through the same Universal Core: independent per-source
  history modes, validated relationships, cross-source trusted SQL, idempotent
  rerun, whole-project rollback on downstream failure, and Parquet archive
  rebuild of every source. Proof: `tests/golden/test_multisource_supply_chain.py`
  and `acceptance/evidence/multisource-archive-rebuild-2026-08-18.txt`.
- The project contract (V10 Phase I2) is complete: a project may declare a
  Python business rule (`app/rules/runner.py`, `metrics.toml`
  `[[python_rules]]`) that runs inside the same project transaction as
  history and analytics, with a declared output schema enforced at
  materialization and an import allowlist enforced at both parse and
  execution time; and a project may declare additive schema migrations
  (`app/data/project_migrations.py`, `projects/<id>/migrations/*.sql`)
  tracked in their own per-project ledger, ordered before table creation so a
  fresh database and an evolving one reach the same validated shape. Proof:
  `tests/golden/test_project_python_rule.py`,
  `tests/golden/test_project_migration.py`,
  `tests/unit/test_project_rules.py`, `tests/unit/test_project_migrations.py`
  and `acceptance/evidence/project-python-rule-and-migrations-2026-08-18.txt`.
  Both paths are proven on the fixture port only, and both are unused by
  every existing reference — none needed them, which is itself evidence SQL
  configuration covers the ordinary case.

## V8.1 remediation now present

- Project-centric `projects/<project_id>/` contract.
- Explicit multi-source source registry, per-source keys/history/quality and relationship contract.
- Git-independent `TEMPLATE_BASELINE.json` with machine path ownership and seal/verify tooling.
- Capability registry and dashboard component catalog.
- IT-owned security policy with metadata-only AI profiling default.
- Machine schemas for baseline/project/sources/relationships/adaptation/reuse/source-profile/capability contracts.
- Supply Chain reference contract for orders + inventory + item master with different history modes.
- Independent adaptation proven (V10 Reference D / Phase I4):
  `projects/_REFERENCE_FINANCE_PPV/` adds a whole finance department — four
  sources including an optional `target` source, an optional relationship and
  `replace_period` history — with **zero Universal Core files changed**. The
  claim is machine-checked by `tests/golden/test_reference_reuse_boundary.py`
  against `TEMPLATE_BASELINE.json` (the same authority the core-change guard
  uses) and recorded in that project's `reuse_report.json`. All four V10 load
  modes and both required and optional relationship semantics are now covered
  by references.
- Canonical quality semantics are PASS/WARNING/BLOCK; run state remains FAILED on a block.
- Normal history behavior is Universal Core, not per-report `history.sql`.

## Explicit blockers before employee distribution

Architecture is no longer the blocker. Everything below is environment-bound,
release-mechanical or documentation debt.

1. **The COM binding layer of Excel extraction is NOT WRITTEN.** This is the
   largest remaining gap and it is a code gap, not only an environment one.
   Within `app/excel/`, four modules are documented stubs whose every entry
   point raises `NotImplementedError`:

   | Module | Status |
   |---|---|
   | `conversion.py` | **real** — dates/serials, separators, percentages, currency, leading zeros, errors, blanks (V10 Part 9 value rules) |
   | `port.py` | **real** — ExtractionPort contract and adaptive `rows_per_chunk` |
   | `identity.py` | **real** — exact-path workbook matching; a similar-but-wrong workbook is refused |
   | `fixture_adapter.py` | **real** — test-only, never ships |
   | `session.py` | **stub** — acquire/attach an Excel session |
   | `discovery.py` | **stub** — table → named range → header row |
   | `extractor.py` | **stub** — drive block reads into staging |
   | `com_adapter.py` | **stub** — the production ExtractionPort itself |

   So the hard, testable logic is done; what is missing is the Windows COM
   binding that calls it. The engine today ingests only through the test-only
   fixture port, so no employee can yet point it at a real workbook.
   Everything downstream of extraction (staging, quality, history, analytics,
   dashboard, runtime) is real and proven. Writing the missing layer needs the
   authorized Windows + Excel machine, so it is both unwritten and
   environment-bound. `tests/architecture/test_no_cell_by_cell_extraction.py`
   pins this status and fails the moment it changes.
2. **Environment-bound (cannot be closed from CI even once the code exists).**
   Protected-file DRM proof, clean-offline-machine and standard-user startup
   runs all need the corporate Windows machine; the non-technical operator
   handoff needs a person. Fixture execution is never evidence for any of
   these (V10 Part 37).
2. `requirements-lock.txt` is still an unpopulated template, so the offline
   wheelhouse and GATE_ARCHITECTURE_BASELINE cannot be satisfied. DuckDB,
   FastAPI, Uvicorn and httpx are installed ad hoc in CI instead of pinned.
3. Actual pinned ECharts binary, full browser/offline/accessibility/RTL proof
   and the final sealed offline package remain open.
4. Project generation/UI still has legacy report-centric compatibility paths
   that must be migrated (V10 Phase I5).
5. `TEMPLATE_BASELINE.json` is intentionally development-unsealed until
   master-core work stabilizes.
6. Template upgrade/migration/rollback is defined as a contract but not yet
   executed/proven.
7. The legacy 225k-line constitution still needs a mechanical reconciliation
   with the V8.1 authority addendum, and V8.1 reference letters (A/B) need
   aligning with the V10 letters (A/B/C/D) wherever they still disagree.
8. One canonical branch has not been chosen (V10 Part 28). `main` and
   `agent/universal-excel-automation-engine` are still unreconciled; this is a
   repository-owner decision, not an engineering one.

**Current approval verdict: NOT READY FOR EMPLOYEE DISTRIBUTION.**

Detailed finding-by-finding status: `docs/V8_1_AUDIT_REMEDIATION.md`.
