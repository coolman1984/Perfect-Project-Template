---
name: universal-excel-automation-adapter
description: Adapt this already-built offline Excel automation engine into an employee-specific multi-source project with minimal core change and minimal repository reading.
---

# PROJECT SKILL — mandatory first read

## 1. What this repository is

This repository is the **Universal Excel Automation Engine + Adaptation Template**. It is not a blank scaffold and a normal employee agent is not an application architect.

The employee supplies Excel files and business meaning. The repository supplies extraction, staging, quality, history, database, analytics, local API, dashboard framework, offline runtime, security controls, tests, map and packaging foundations.

Canonical work order:

```text
UNDERSTAND BUSINESS
→ PROFILE SOURCES
→ MAP TO EXISTING CAPABILITIES
→ REUSE AS-IS
→ CONFIGURE DIFFERENCES
→ ADD ISOLATED PROJECT-SPECIFIC BUSINESS LOGIC ONLY WHEN NEEDED
→ TEST / RECONCILE
→ DELIVER PROJECT PACK WITH THE SEALED RUNTIME
```

## 2. 90-second start

```text
PROJECT_TOOL doctor
PROJECT_TOOL map verify
PROJECT_TOOL map context --task "<exact task>" --budget 4000
```

Then read `.ai/CURRENT_STATE.md`, `.ai/CONTEXT_PACK.md`, the relevant `projects/<id>/` contracts, and only the routed implementation/tests. Do not broad-scan the repository.

For an **employee adaptation**, also run:

```text
PROJECT_TOOL template-baseline verify
PROJECT_TOOL adaptation core-guard --project <project_id>
```

If the template baseline is missing/unsealed/changed, stop employee release work. A copied employee agent verifies foundational tooling; it does not recreate the Universal Core on the PC.

For **master-core development**, an unsealed development baseline is expected until the core is ready to release. Only master-core release work may seal a new baseline.

## 3. Project, not report

The adaptation unit is `projects/<project_id>/`.

```text
project.toml          identity + template lineage + business purpose
sources.toml          every independent workbook/sheet/source role
relationships.toml    explicit joins/cardinality/approval state
dashboard.toml        presentation composition
quality.toml          project/cross-source controls when needed
metrics.toml          reusable metric bindings when needed
business_rules/       isolated genuinely project-specific SQL/Python
reports/              optional report/export definitions inside the project
```

Legacy `reports/` exists only while older executable reference tests are migrated. Never use that legacy location as proof that the architecture is report-centric.

Each source independently owns its file pattern, discovery rule, grain, business key, event date, load/update strategy, deletion behavior and quality controls. Orders may upsert while inventory snapshots and a master file upserts. Do not force one project-wide load mode onto unrelated sources.

## 4. Requirement classification

Every requirement is exactly one of:

```text
REUSE_AS_IS
CONFIGURE
PROJECT_SPECIFIC_BUSINESS_LOGIC
NEW_REUSABLE_CAPABILITY_CANDIDATE
```

The fourth is exceptional. Employee copies may create a candidate package; they do not promote themselves into a new master core. Central master-template work reviews/promotes a candidate and issues a new template version.

Use `capabilities/registry.json` before opening implementation files. It tells you what already exists, how to configure it, the extension point, tests and limitations.

## 5. Core ownership

`TEMPLATE_BASELINE.json` is the machine authority for path scope and, when sealed, core hashes. The baseline works even when the employee received a ZIP and Git is unavailable.

Normal employee changes belong to project configuration, presentation or project business rules. A Universal Core edit requires evidence that configuration/extension points cannot express the need, regression proof across references, and master-core review.

Do not use a reuse percentage as the main proof. Report instead:

```text
core files changed
project config files changed
business-rule files changed / size
reused capabilities
reused tests
new architecture decisions
context files/bytes/estimated tokens
provider token count only when actually available
```

## 6. Human and security boundary

Ask the employee business questions only:

- What does each source/file mean?
- What does one row mean in each source?
- Which values identify the same business record?
- Can old records change later?
- Which trusted totals prove correctness?
- Which source wins when business sources disagree?
- What KPI/decision/exception matters?
- Who owns and approves the business meaning?

Do **not** ask a non-technical employee to choose database, API, folder architecture, ports, packaging, security model, retention policy or external-AI disclosure policy. Corporate security policy is preloaded in `policy/security_policy.toml`; unresolved policy goes to IT/Security.

Source profiling is metadata-only by default. Protected/raw sample values do not enter AI context unless the policy explicitly permits them.

## 7. Trusted calculations and quality

Trusted calculations live once. Prefer deterministic versioned SQL. Isolated tested Python is allowed only when SQL would be unsafe or materially less clear. Never duplicate a trusted formula in SQL/Python/browser. JavaScript renders results and interactions; it is not the trusted business-calculation engine.

Canonical quality verdicts:

```text
PASS     trusted checks passed
WARNING  non-blocking anomaly; visible to user
BLOCK    trusted data must not be published/committed
```

A `BLOCK` quality verdict makes the execution run state `FAILED`. Do not create a second quality vocabulary called FAIL.

## 8. Universal history

`app/data/history.py` implements append/upsert/snapshot/replace-period and correction/deletion semantics. A project selects those behaviors per source/entity. Normal adaptations must not carry `sql/history.sql` implementations.

If a new business case needs history semantics the engine truly cannot express, classify it as a reusable-capability candidate and handle it through master-core evolution.

## 9. Dashboard and web app

The employee's work surface remains one offline local web application:

```text
Add all required source files
→ see detected roles/readiness
→ process with durable progress
→ review quality/reconciliation
→ use interactive dashboard/history
→ export approved standalone report
```

Presentation comes from project configuration and the reusable component catalog. Do not copy or rewrite frontend architecture for each department.

## 10. Offline/runtime rules that remain locked

- Windows + authorized desktop Excel are the approved external prerequisites.
- The complete private runtime/dependencies/assets are bundled. Offline never means dependency-free.
- FastAPI/Uvicorn loopback remains bound only to `127.0.0.1` as a standard-user process.
- No service, IIS, URL reservation, firewall rule, elevation, LAN bind, CDN, telemetry or runtime download.
- Excel is the authorized door to protected data, not the database or calculation engine.
- DuckDB is local truth; Parquet is approved recovery/history archive; SQL Server is optional when enabled/approved.
- A failure preserves trusted history and last-good output.

## 11. Packaging and upgrades

A normal project adaptation does **not** rebuild/freeze the entire runtime when Universal Core is unchanged. It reuses the sealed approved runtime and validates/packages the employee project pack.

A core/runtime change is master-template release work: rebuild the full release, seal a new baseline/version, migrate compatible project packs, verify, and preserve rollback.

Core-owned paths may be replaced/migrated by a template upgrade. Project-owned paths must be preserved unless an explicit project migration says otherwise.

## 12. References and current honesty

- Legacy single-source Golden Reference: `reports/_REFERENCE/`.
- Legacy second-domain single-source proof: `reports/line_downtime/`.
- Required multi-source project reference: `projects/_REFERENCE_SUPPLY_CHAIN/`.

The Supply Chain reference proves both the **contract and the execution** for
orders + inventory + item master: independent history modes, validated
relationships, cross-source trusted SQL, idempotent rerun, whole-project rollback
and per-source Parquet archive rebuild all pass in
`tests/golden/test_multisource_supply_chain.py`.

That proof runs through the fixture extraction port. It is REFERENCE_PROVEN, not
ENVIRONMENT_PROVEN — real protected Excel/COM on the authorized corporate PC
remains a separate open gate, and fixture execution is never evidence for it.

The outstanding universality question is now **independent adaptation** (V10
Reference D / Phase I4), not multi-source execution.

Detailed finding/status ledger: `docs/V8_1_AUDIT_REMEDIATION.md`.
Controlling adaptation addendum: `constitution/V8_1_ADAPTATION_AUTHORITY.md`.

## 13. Completion declaration

Every adaptation/evolution report ends with:

```text
mode: EMPLOYEE_ADAPTATION / MASTER_CORE
project: <id>
template baseline: SEALED+PASS / DEVELOPMENT_UNSEALED / BLOCKED
sources + roles: <count/list>
relationships confirmed/pending: <count>
requirements: reuse/config/project-logic/candidate counts
core files changed: NONE / justified list
security policy: PASS / IT ACTION REQUIRED
quality vocabulary: PASS/WARNING/BLOCK
reference A: PASS / BLOCKED
reference B multi-source: CONTRACT_ONLY / EXECUTION_PASS / BLOCKED
offline/browser/COM gates: exact evidence or CONDITIONAL
map/context metrics: files + bytes + estimated tokens (+ actual tokens only if exposed)
```

Do not claim employee-ready while a critical V8.1 audit item or release/environment gate remains open.
