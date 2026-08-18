# V10 Coding Plan

Nine work packages, named against the files and seams that exist in the
repository today. Companion to `docs/V10_BUILD_PROGRAM.md`, which covers
sequencing and gate evidence. Status: plan only — no repository code was
written to produce this document.

## The five open questions, answered

### 1. Supersede the constitution — do not reconcile it line by line

Freeze `constitution/EXCEL_AUTOMATION_CONSTITUTION.md` byte-for-byte as audit
history. Add `docs/V10_AUTHORITY_MAP.md` mapping each of its 45 Parts to one
of `V10 §n`, `SUPERSEDED`, or `STILL_BINDING`. Repoint
`tools/verify_constitution.py` at V10 plus that map.

Editing 3,787 lines in place is multi-week work that produces nothing an
employee ever sees, and the audit currently passes — so the risk of touching
it exceeds the risk of freezing it.

### 2. The V10 document lives under version control, committed

It is the authority document; it belongs under map control like every other
governed file. Untracked at the repo root it was the reason `doctor` failed
— an authority document that breaks the repo's own health check undermines
itself.

### 3. Keep the baseline's scope rules; demote only the seal

These are two different mechanisms sharing one file. `scope_rules` drives
`classify_scope()` and `core_change_guard()` — that is the classification
V10 §17 explicitly wants kept. The `sealed` flag is what makes
`template-baseline verify` return BLOCKED and drag `adaptation core-guard`
down with it.

Keep the rules, make the seal advisory outside a release build. Surgical,
and it matches §30's "keep integrity hashes as supporting release
capabilities".

### 4. Reference D stays Finance PPV, with source shape as the real requirement

What the proof actually needs is four sources with four genuinely different
behaviours: a transaction feed (append), a cost master (snapshot), a vendor
master (upsert) and a budget (replace-period). Finance PPV supplies exactly
that spread, which is why V10 §34 picked it.

If real finance files are not obtainable, substitute any department that
supplies the same four shapes. The subject is negotiable; the shape spread
is not — swapping it for four similar sources would prove nothing.

### 5. Fold all six defects into W0

The folder-resolution crash blocks W1 and W3 regardless, and W0's exit gate
is a green `doctor` with zero test errors — which cannot be reached while
any of them stands. Tracking them separately would mean W0 exits on a
known-red suite.

## Work packages

W0 → W1 → W2 are strictly serial: each removes a blocker the next depends
on. After W2, three tracks run in parallel. The environment track runs from
day one, independent of all of it.

### W0 — Truth

Green the repository and close six defects. Small, entirely mechanical, and
everything downstream is scheduled on its output.

| File | Kind | Change |
|---|---|---|
| factory/adaptation.py | edit | Resolve through `find_project_directory()` in `manifest_from_project` and `write_project_manifest`; stop joining `projects_root / project_id` |
| factory/reuse_report.py | edit | Take a resolved `directory: Path`; today one caller passes a folder name and the other a project_id |
| tools/adaptation_tool.py | edit | Move the `write_project_manifest` call inside the try/except so a contract error reports instead of tracebacks |
| app/server.py | edit | `_safe_report_id` rejects `.` and `..`; `/api/uploads` builds its path from the sanitized value, not the raw query param |
| app/server.py | edit | `_safe_upload_name` rejects Windows device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9), with or without extension |
| app/server.py | edit | Drop the `if runtime.port:` wrapper around the origin and launch-secret middleware; fail closed when port is 0 |
| app/server.py | edit | `_run_worker` emits a durable FAILED event instead of silently returning |
| app/locks.py | verify first | Replace the `os.kill(pid, 0)` liveness probe — see note below |
| app/orchestrator.py, app/project_orchestrator.py | edit | Construct `Database()` inside the lock scope; emit FAILED when the lock is refused so `/api/runs/{id}` stops returning 404 forever |
| acceptance/gates.yaml | edit | Re-audit all 43 gates against named commands; correct the stale entries in both directions |
| .ai/CURRENT_STATE.md | edit | Rewrite from evidence — settle whether Supply Chain execution is proven |
| docs/V10_MASTER_PLAN.md | new | Move the untracked root document here, then `map refresh` |
| .ai/test_run_out.txt | delete | Stray artifact; gitignore `projects/*/reuse_report.json` |
| tests/unit/test_project_resolution.py | test | The reference project resolves by `project_id` through every public entry point |
| tests/adversarial/test_path_sanitizers.py | test | `..`, `.`, device names, raw-versus-sanitized id |
| tests/unit/test_lock_liveness.py | test | Stale lock recovered, live lock not stolen, and the probe does not terminate its owner |
| tests/failure/test_lock_contention.py | test | A refused lock produces a terminal FAILED event and leaks no database handle |

**Verify before fixing.** On Windows, CPython maps `os.kill(pid, sig)` to
`TerminateProcess` for any signal that is not a console control event —
which would make this "liveness probe" kill the process holding the lock.
This was not confirmed empirically in this session, so W0 starts by proving
the behaviour against a disposable child process. If confirmed, the fix is a
ctypes `OpenProcess` + `GetExitCodeProcess` probe on win32; if not, the
ticket closes with a comment and a test.

**Exit gate:** PROJECT_TOOL doctor returns PASS · unittest reports 0 errors
· every gate status reproducible from a named command.

### W1 — Authority

One authority, and a core guard that warns instead of blocking. Mostly
deletion. This is what unblocks every reference proof that follows.

| File | Kind | Change |
|---|---|---|
| docs/V10_AUTHORITY_MAP.md | new | 45 Parts → `V10 §n` \| `SUPERSEDED` \| `STILL_BINDING` |
| decisions/register.json, contracts/decision_register.schema.json | new | D-001…D-014 from V10 §3, machine-checkable |
| tools/verify_constitution.py | edit | Audit V10 plus the authority map instead of the 3,787-line document |
| tools/template_baseline.py | edit | `verify(strict=False)`: unsealed becomes WARN + PASS; `--strict` reserved for release builds |
| tools/adaptation_tool.py | edit | `core_guard` stops inheriting the baseline exit code; reports core-owned files touched and demands justification per V10 §17 |
| factory/adaptation.py | edit | Wire the existing `core_change_guard(paths, reason=…)` into the CLI — the warn-and-justify logic already exists, unused |
| .ai/ADAPTATION_REPORT.md | new | The fifth §26 artifact; currently missing entirely |
| .ai/CONTRACTS.md, LESSONS.md, OPPORTUNITIES.md, READ_FIRST.md | fold in | 11 artifacts down to the 5 §26 permits; MAP_MANIFEST.json and MEMORY.jsonl stay as internal caches, which §26 allows |
| tools/project_map.py | edit | Update the artifact allow-list to match |
| tests/constitution/test_v10_authority.py | test | Every Part is classified; no Part is both superseded and binding |
| tests/factory/test_core_guard_warns.py | test | A justified core change proceeds; an unjustified one warns and names the files |

**Exit gate:** adaptation core-guard and adaptation validate both run clean
against the reference project · no surviving document contradicts V10.

### W2 — Contract

Complete the project contract and build the Python rule runner. The largest
package by far, and the only one containing genuinely new architecture. The
reference project ships 4 of the ~10 files V10 §16 describes, and the rule
runner of §14.3 has zero references anywhere in the repository.

One piece is smaller than it looks: `app/data/migrations.py` already
implements ordered, checksummed, immutable, transactional migrations.
Project migrations reuse that engine with a different directory and a
project-scoped ledger rather than a new implementation.

| File | Kind | Change |
|---|---|---|
| contracts/quality.schema.json, metrics.schema.json, output.schema.json | new | The three missing §16 contracts, beside the existing project/sources/relationships schemas |
| contracts/python_rule.schema.json | new | rule_id, version, input_tables, input_columns, output_schema, deterministic, allowed_dependencies, error_behavior |
| factory/project_contract.py | edit | Add `QualitySpec`, `MetricSpec`, `OutputSpec`, `RuleSpec`; `load_project` loads the three new files as optional — §16 says not every project needs every file |
| app/rules/contract.py | new | Rule declaration parsing and validation |
| app/rules/runner.py | new | `ProjectRuleRunner` — loads only rules named in `metrics.toml`, from `projects/<id>/business_rules/python/`, writing only to declared output tables inside the caller's transaction |
| app/rules/sandbox.py | new | Static AST check at load plus a `sys.addaudithook` guard: no socket, no urllib, no open outside declared outputs, import allow-list |
| app/project_pipeline.py | edit | Hook the runner inside `with self.database.transaction():` — after the history loop and `self.analytics.run()`, before `project_json_builder.build()`. That is V10 §11 steps 14–15, and it keeps a failed rule inside the rollback boundary |
| app/data/project_migrations.py | new | Reuse the `migrations.py` engine with `directory=projects/<id>/migrations` and a `sys.project_schema_migration` ledger keyed by project |
| app/rebuild.py | new | The §18 decision table: declared dependencies versus the bundled lock → `reuse_runtime` \| `rebuild_minimum` \| `full_regression` |
| tools/project_tool.py | edit | New `rules` group: `list`, `verify`, `run` — one parser block and one `_dispatch` branch |
| tests/unit/test_rule_runner.py | test | Determinism, declared-output enforcement, undeclared table access rejected |
| tests/adversarial/test_rule_sandbox.py | test | Network blocked, arbitrary file read blocked, unlisted rule never loads, rule cannot bypass quality or the transaction |
| tests/unit/test_project_migrations.py | test | Forward apply, immutability after apply, failed migration preserves the last trusted database |
| tests/factory/test_rebuild_detection.py | test | Each row of the §18 table returns the documented verdict |

**Exit gate:** one config-only adaptation and one Python-rule adaptation
both pass end to end · every project file validates against a schema.

### W3 — Reference C (Supply Chain)

Close the multi-source foundation. Begin by establishing what is already
proven — `tests/golden/test_multisource_supply_chain.py` passes today while
`CURRENT_STATE.md` calls this path unproven. Build only the genuine gaps.

| File | Kind | Change |
|---|---|---|
| tests/golden/test_multisource_supply_chain.py | extend | Name one test per I3 property: independent history modes, relationship validation, downstream failure rolls back all sources, identical rerun is idempotent, archive rebuild reconciles |
| projects/_REFERENCE_SUPPLY_CHAIN/ | new | Add `quality.toml`, `metrics.toml`, `output.toml`, `setup_answers.json`, `migrations/`, `tests/` so the reference demonstrates the full §16 surface rather than a third of it |

**Exit gate:** each of the six I3 properties maps to a named passing test.

### W4 — References A and B

Migrate Production Quality and Maintenance onto the project surface. Reuse
cannot be measured while two of four references run through a different
pipeline. Runs in parallel with W3.

| File | Kind | Change |
|---|---|---|
| projects/production_quality/ | new | Ported from `reports/_REFERENCE` |
| projects/line_downtime/ | new | Ported from `reports/line_downtime` |
| app/server.py | edit | Keep `/api/reports`, `/api/uploads`, `/api/runs` working; add a deprecation header and a dated retirement note. V10 §0 forbids deleting working compatibility paths for tidiness |
| tests/golden/test_reference_pipeline.py, test_second_report_pipeline.py | port | Duplicate onto the project pipeline; keep the legacy tests until the retirement date |

**Exit gate:** References A, B and C all execute through the project
pipeline · legacy endpoints dated for retirement.

### W5 — Reference D (Finance PPV)

The reuse proof, built the employee way. Everything before this is
foundation. This is the package that tests whether the foundation was worth
building. It must go through `PROJECT_TOOL adaptation new` and the
questionnaire — no hand-built architecture, or the proof is void.

```
projects/finance_ppv/
    sources.toml
        purchase_transactions   append           transaction
        standard_cost           snapshot         master
        vendor_master           upsert           master
        budget_target           replace_period   target
    relationships.toml
        txn_to_item · txn_to_vendor · txn_to_budget_period
    business_rules/metrics.sql
    reuse_report.json
```

Record the full §4 reuse report: shared files changed, configuration
changed, project SQL and Python, tests reused versus added, rebuild
required, context size, operator effort. Any shared-engine change is treated
as a defect in the abstraction — fix upstream in W2 and repeat. Budget for
at least one repeat; §I4 anticipates it.

**Exit gate:** Finance PPV runs with zero or individually justified
shared-engine changes, evidenced by the reuse report.

### W6 — Experience

Finish the employee-facing flow. Depends only on W2's contracts, not on the
references — so it runs in parallel with W3, W4 and W5. Closes four of the
twenty outstanding block gates.

| File | Kind | Change |
|---|---|---|
| web/index.html, styles.css | edit | One-page grid per §26.11 — `GATE_ONE_PAGE_DESIGN` |
| web/app.js | edit | Typed shared filter-state object; cross-filter, drill-through and reset all reconcile — `GATE_FILTER_RECONCILIATION` |
| web/i18n/en.json, ar.json | new | Dictionaries plus RTL layout — `GATE_BILINGUAL_RTL` |
| web/app.js, styles.css | edit | Keyboard, focus, labels, WCAG 2.2 AA contrast, reduced motion — `GATE_ACCESSIBILITY` |
| app/dashboard/verifier.py | edit | Static check over `web/` proving no trusted KPI arithmetic in JavaScript — `GATE_NO_BROWSER_ARITHMETIC` |
| tests/browser/ | test | Currently an empty package; needs Playwright from the `qa` extra |

**Exit gate:** a first-time operator reaches a published dashboard without
reading documentation.

### W7 — Pilot

Package, and prove it on real corporate hardware. Where the environment
track opened at W0 is finally consumed. Note the hard dependency:
`web/vendor/` holds only a 6-byte version stamp, so `GATE_BROWSER_OFFLINE`
cannot pass until the pinned ECharts binary is actually vendored — no amount
of code quality substitutes.

| Item | Kind | Change |
|---|---|---|
| web/vendor/echarts.min.js | new | Vendor the pinned binary matching the existing version stamp |
| BUILD_RELEASE | edit | Runtime, assets, SBOM, licences, checksums, repair path; then `architecture verify --release` |
| Environment proofs | external | Clean offline PC · standard non-admin user · real protected Excel read twice with unchanged hash · two stable runs · operator handoff |

**Exit gate:** V10 §43 definition of done · all 20 block-severity gates pass
or are documented not-applicable.

### W8 — Deferred (not scheduled)

Optional connectors — named, not scheduled. Watched folder, Data Hub, RPA,
database and API, Gauss review, company-server mode. Zero references in the
repository today, and decision D-014 is explicit that the local product
finishes first.

When they are built, each adapter must produce the same source manifest and
pass the same reconciliation contract as manual upload before it counts as
supported. Gauss additionally needs the official company API contract
verified, and may never calculate a trusted KPI.

**Not scheduled** — revisit only after a successful W7 pilot.

## Order of work

```
W0 -> W1 -> W2 -+-> W3 -+
                |        +-> W5 -> W7
                +-> W4 --+        ^
                +-> W6 -----------+

environment track ------------------+
  opened at W0, consumed at W7
```

W0, W1 and W2 are serial because each removes a blocker the next depends on:
the crash blocks the guard, the guard blocks the contract work. After W2,
W3, W4 and W6 are independent. W5 needs W3 and W4 finished, because a reuse
measurement taken against a half-migrated reference set means nothing.

The environment track is not engineering work and does not consume
developer time — but it has the longest lead time in the program and is the
most likely cause of a late slip.

## Scope of this document

Plan only. No repository code was written to produce it. Every file path,
function name and seam above was read from the repository at the time of
writing — the hook point in `project_pipeline.py`, the reusable migration
engine, the `core_change_guard` that already exists unused, and the exact
line where the seal drags `core-guard` down.
