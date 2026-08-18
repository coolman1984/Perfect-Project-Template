# CURRENT STATE

## Product identity

**Universal Excel Automation Engine + Adaptation Template, under V8.1 deep-audit remediation.**

The ready application is the product. Employee agents should adapt project configuration and isolated business logic rather than rebuild technical foundations.

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
- Canonical quality semantics are PASS/WARNING/BLOCK; run state remains FAILED on a block.
- Normal history behavior is Universal Core, not per-report `history.sql`.

## Explicit blockers before employee distribution

1. No independent adaptation proof yet. V10 Phase I4 requires a Finance Purchase
   Price Variance project built through the normal employee workflow to show
   low-change reuse. Until it exists, reuse is asserted rather than measured.
2. Project generation/UI still has legacy report-centric compatibility paths that must be migrated.
3. `TEMPLATE_BASELINE.json` is intentionally development-unsealed until master-core work stabilizes.
4. Template upgrade/migration/rollback is defined as a contract but not yet executed/proven.
5. Real protected Excel COM/DRM proof requires the authorized corporate Windows + Excel environment.
6. Actual pinned ECharts binary, full browser/offline/accessibility/RTL proof and final sealed offline package remain open.
7. `requirements-lock.txt` is still an unpopulated template, so the offline
   wheelhouse and GATE_ARCHITECTURE_BASELINE cannot be satisfied. DuckDB,
   FastAPI, Uvicorn and httpx are installed ad hoc in CI instead of pinned.
8. The legacy 225k-line constitution still needs a mechanical reconciliation with the V8.1 authority addendum.

**Current approval verdict: NOT READY FOR EMPLOYEE DISTRIBUTION.**

Detailed finding-by-finding status: `docs/V8_1_AUDIT_REMEDIATION.md`.
