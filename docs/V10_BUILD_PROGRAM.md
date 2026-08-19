# V10 Build Program

Sequencing for the V10 master plan, ordered against verified repository state
rather than what the plan's own documents claim. Companion to
`docs/V10_CODING_PLAN.md`, which names the files and seams for each stage.

Source: `ULTIMATE_EXCEL_AUTOMATION_V10_UNIFIED_APPROVED_MASTER_PLAN.md`, 2,014
lines. Repo state checked against `main`. Status: plan only — no repository
code was written to produce this document.

## Read this first

V10 §0 and §28 instruct: freeze merges, do not rewrite repository code, choose
one canonical branch only after the documentation and gate audit. `main` was
already fast-forwarded to `agent/universal-excel-automation-engine` (93
commits) and pushed. That freeze is spent and the branch decision is made.
This plan treats Phase P0 ("freeze and inventory") and the branch half of
Phase I0 as settled facts and reallocates that effort to what is genuinely
outstanding: making the repository's own status reporting true.

## Where the repository actually is

Every row below is a command run against the repository, not a claim copied
from a document. Two of these contradict what the repository says about
itself.

| Check | Result | Detail |
|---|---|---|
| Test suite | 1 error | 243 tests, 62s. `test_project_build_brief` raises `ProjectContractError` |
| PROJECT_TOOL doctor | fail | 7 of 8 checks pass; `map verify` fails |
| map verify | fail | The untracked V10 document at repo root is not in the manifest |
| architecture --baseline | pass | 14 required components, 0 approved deviations |
| architecture --source-scan | pass | 134 runtime files, 4 warnings (loopback URL patterns) |
| constitution audit | pass | 45 Parts, 32 cross-references all resolve |
| adaptation core-guard | blocked | `TEMPLATE_BASELINE.json` is `development_unsealed` |
| adaptation validate | crash | Unhandled traceback on the shipped reference project |
| Python rule runner | absent | V10 §14.3 — zero references anywhere in the repo |
| Project migrations | absent | V10 §15 — no `projects/<id>/migrations/` |
| ECharts binary | absent | `web/vendor/` holds a 6-byte version stamp and a README |
| Connectors | absent | Watched folder, Data Hub, RPA, Gauss — zero references |

The acceptance ledger (`acceptance/gates.yaml`) holds **43 gates**, of which
**20 block-severity gates** are outstanding: 17 pass, 22 not started, 3
conditional (need a real Windows target), 1 not applicable.

## Three corrections to V10's sequence

### 1. The gate ledger is wrong in both directions

`GATE_LOOPBACK_TRANSPORT` is `not_started` with next action "Implement
app/local_transport.py" — that file exists and
`tests/unit/test_loopback_listener.py` passes against a real bound socket.
`GATE_LOOPBACK_SECURITY` is `not_started` although `test_runtime_core.py`
already proves wrong-Host, wrong-Origin and launch-secret rejection.
`GATE_ARCHITECTURE_BASELINE` is `not_started` although its verifier passes
today. In the other direction, `GATE_MAP_FRESHNESS` is recorded `pass` while
`map verify` fails.

V10 acceptance item 22 — "no critical plan/code/gate contradiction remains" —
fails on day one. Re-auditing all 43 gates against machine evidence is the
true first task, and it will most likely *shorten* the remaining roadmap
rather than lengthen it.

### 2. Governance currently blocks the proof V10 asks for

V10 §30 says retire the immutable core firewall and demote mandatory upgrade
machinery from the employee path. Today the opposite holds:
`adaptation core-guard` returns BLOCKED because the template baseline is
unsealed, and `adaptation validate --project reference_supply_chain` dies
with an unhandled traceback.

The cause is a folder-resolution defect. `find_project_directory()` exists
precisely so a project is found by its `project_id` and never by a guessed
folder name, but `manifest_from_project()` joins `projects_root / project_id`
directly — so the shipped `_REFERENCE_SUPPLY_CHAIN` folder is never found.
The adaptation toolchain cannot be run against the very reference project
Phase I3 depends on. Simplification (I1) must therefore come *before*
contract work (I2), not beside it.

### 3. The long-lead items sit at the end of V10's roadmap but must start now

Five gates need written IT approval, a named business owner, a corporate
Windows PC with Excel and DRM-protected files, a standard non-admin account,
and a scheduled session with a non-technical operator. None can ever be
advanced from a development workspace, and V10 §37 is explicit that fixtures
can never satisfy them. They are consumed at Stage 7 but have lead times
measured in weeks. Requesting them at Stage 0 is the single highest-leverage
scheduling change in this plan.

## The plan

Nine stages. The codes are sequential because the dependencies are real —
each stage's exit gate is the next stage's entry condition. Stages 0 through
7 are the path to a controlled employee pilot; Stage 8 is deliberately
unscheduled.

### S0 — Truth

Make the repository's self-reporting true. Nothing downstream can be
scheduled honestly while `doctor` fails and the gate ledger disagrees with
the code in both directions.

- Decide where the V10 document lives — it currently breaks `map verify` and
  so fails `doctor` outright.
- Fix `manifest_from_project` and `write_project_manifest` to resolve
  through `find_project_directory`; one call site passes a folder name and
  the other a `project_id`, and only one of them works.
- Re-audit all 43 gates against named commands. Move the understated ones up
  with real evidence files; move `GATE_MAP_FRESHNESS` down until doctor is
  green.
- Rewrite `.ai/CURRENT_STATE.md` from evidence. It calls the Supply Chain
  multi-source path "EXECUTION NOT YET PROVEN", but
  `tests/golden/test_multisource_supply_chain.py` runs and passes today —
  settle which is true before scheduling S3.
- Remove stray artifacts: `.ai/test_run_out.txt`, generated
  `reuse_report.json`.
- **Open the long-lead requests now** — IT storage approval, the named
  business owner, the corporate Windows machine, the operator session.

**Exit gate:** doctor returns PASS · every gate status reproducible from a
named command · zero test errors.

### S1 — Authority

One authority, and a core guard that warns instead of blocking. V10 P1 and
I1 combined. This is mostly deletion, and it is what unblocks every
reference proof that follows.

- Adopt V10 as source-of-truth #1 per §40; turn the §3 decision table
  (D-001…D-014) into a machine-checkable register.
- Reconcile the 3,787-line `constitution/EXCEL_AUTOMATION_CONSTITUTION.md`
  against the 49 KB V10 — the largest documentation item in the program.
- Convert the Core Change Guard to warn-and-justify (§17). Stop `core-guard`
  returning BLOCKED for an unsealed development baseline; keep sealing as an
  optional release capability only (§30).
- Reduce `.ai/` from 11 artifacts to the 5 permitted by §26, and add the
  missing `ADAPTATION_REPORT.md`.

**Exit gate:** core-guard and adaptation validate both run clean against the
reference project · no surviving document contradicts V10.

### S2 — Contract

Complete the project contract and build the Python rule runner. V10 I2. The
reference project has 4 of the roughly 10 files §16 describes. The rule
runner does not exist at all — this is the largest genuinely new engineering
item in the program.

- Add `quality.toml`, `metrics.toml` and `output.toml` contracts, loaders
  and JSON schemas beside the existing project / sources / relationships
  schemas.
- Build the §14.3 rule runner: rule ID and version, declared input tables
  and columns, output schema, determinism, allow-listed dependencies, no
  network and no arbitrary file access, per-rule tests. Only rules named in
  project configuration may load.
- Add `projects/<id>/migrations/` and its transactional runner (§15).
- Implement the §18 rebuild-detection table so the runtime can state whether
  a rule requires a repackage instead of guessing.

**Exit gate:** one config-only adaptation and one Python-rule adaptation
both pass end to end · every project file validates against a schema.

### S3 — Reference C (Supply Chain)

Settle and close the multi-source foundation. V10 I3. Start by establishing
what is already proven — the golden test passes today, so part of this stage
may already be done.

- Map the existing Supply Chain golden test against I3's six required
  properties: independent histories, validated relationships, injected
  downstream failure, complete rollback, identical rerun, archive rebuild.
- Build only whichever of the six is genuinely missing.

**Exit gate:** each of the six I3 properties maps to a named passing test.

### S4 — References A and B — DONE (2026-08-19)

Migrate Production Quality and Maintenance onto the project surface. Not a
numbered V10 phase, but required by §16 and §34 before reuse can be measured
honestly.

- `projects/_REFERENCE_PRODUCTION_QUALITY/` (Reference A) and
  `projects/_REFERENCE_MAINTENANCE_DOWNTIME/` (Reference B) now run the same
  fixtures and hand-checked numbers through `app.project_pipeline.ProjectPipeline`
  as the legacy `reports/_REFERENCE` and `reports/line_downtime` do through
  `app.pipeline.Pipeline`. Proof:
  `tests/golden/test_reference_project_pipeline.py`,
  `tests/golden/test_maintenance_downtime_project_pipeline.py`.
- The legacy report contract had one quality capability the project contract
  did not: `approved_categories` (a column value outside an approved list
  loads and warns, per Part 9). This was a real faithfulness gap, not a
  cosmetic one, so it was added as a small reusable capability
  (`contracts/source_registry.schema.json`, `factory/project_contract.py`,
  `app/project_pipeline.py`) rather than dropped. Both new references use it;
  Supply Chain and Finance PPV are unaffected (the field is optional).
- `reports/_REFERENCE` and `reports/line_downtime` are untouched and keep
  working — V10 §0 forbids deleting a working compatibility path for
  conceptual cleanliness. Not yet marked for retirement with a date; that is
  a product decision, not an engineering one.

**Exit gate:** References A, B and C all execute through the project
pipeline · legacy endpoints dated for retirement.

The first half is done. The second half — dating the legacy endpoints for
retirement — is a product/ownership decision still open.

### S5 — Reference D (Finance PPV)

The actual reuse proof. V10 I4. Everything before this stage is foundation;
this is the stage that tests whether the foundation is worth anything.

- Build it through the normal employee adaptation workflow only (§34):
  interview, profile, configure, test. No hand-built architecture changes.
- Record the full §4 reuse report — shared files changed, configuration
  changed, project SQL and Python, tests reused versus added, rebuild
  required, context size, operator effort.
- Budget for at least one repeat. §I4 is explicit: if major shared
  rebuilding is required, improve the abstraction and do it again.

**Exit gate:** Finance PPV runs with zero or individually justified
shared-engine changes, evidenced by the reuse report.

### S6 — Experience — IN PROGRESS (2026-08-19)

Finish the employee-facing flow. V10 I5. Project discovery, business
questionnaire, source-role assignment, guided upload, durable progress,
quality explanation, dashboard, history, export, friendly recovery.

- Closes `GATE_ONE_PAGE_DESIGN`, `GATE_FILTER_RECONCILIATION`,
  `GATE_ACCESSIBILITY` and `GATE_BILINGUAL_RTL` — four of the outstanding
  block/major gates. `GATE_BILINGUAL_RTL` now fully passes; the other three
  moved from not_started to in_progress with real, browser-tested progress
  (see acceptance/gates.yaml for what remains on each).
- Built: the sticky filter ribbon and hero/insight grid region
  (`web/index.html`, `web/styles.css`); `web/filters.js`'s FilterState and
  verifyReconciliation — written earlier but never imported anywhere — wired
  into `web/app.js` for real client-side chart filtering, chips and reset;
  `web/i18n.js` (new) driving real `lang`/`dir` switching and text
  translation from the pre-existing but unused `web/i18n/en.json` /
  `ar.json`; a conditional action-table region. Proof:
  `tests/browser/test_local_app_browser.py` (new), 10 tests against a real
  loopback server in real Chromium.
- Still open: cross-filter (click a chart mark) and drill-through, WCAG
  contrast/keyboard-reachability assertions for the local app's larger
  control set, and the business questionnaire / guided-upload onboarding
  flow this stage's title names but which was out of scope for this pass.
- Progress must be driven by durable events, never decorative animation
  (§22).

**Exit gate:** a first-time operator reaches a published dashboard without
reading documentation.

### S7 — Pilot

Package, and prove it on real corporate hardware. V10 I6 — the first
employee pilot target, and where the long-lead track opened at S0 is finally
consumed.

- Bundle the ECharts binary. `web/vendor/` currently holds only a version
  stamp, so `GATE_BROWSER_OFFLINE` cannot pass regardless of code quality.
- Build the release: runtime, assets, SBOM, licences, checksums, repair
  path.
- Run the environment proofs — clean offline PC, standard non-admin user,
  real protected Excel read twice with an unchanged hash, two stable runs,
  operator handoff.

**Exit gate:** V10 §43 definition of done · all 20 block-severity gates pass
or are documented not-applicable.

### S8 — Deferred (not scheduled)

Optional connectors — named, costed, not scheduled. V10 I7, I8 and I9:
watched folder, Data Hub, RPA, database and API, Gauss review, company-server
mode. None exist in the repository today.

- Decision D-014 is explicit — finish the reusable local product before
  optional enterprise connectors dominate the roadmap.
- Each adapter must pass the same source-manifest and reconciliation
  contract as manual upload before it counts as supported.
- Gauss needs the official company API contract verified first; it may
  never calculate a trusted KPI (§21).

**Not scheduled** — revisit only after a successful S7 pilot.

## Defects found and folded into S0

Found while reviewing the newly merged code.

| Where | Confidence | Problem |
|---|---|---|
| factory/adaptation.py | reproduced | Guesses the folder name from `project_id`; crashes on the shipped reference project |
| app/server.py | reproduced | `_safe_report_id("..")` is accepted and resolves outside the reports root |
| app/server.py | reproduced | `_safe_upload_name` accepts Windows device names such as `CON` |
| app/locks.py | unverified | `_pid_alive` uses `os.kill(pid, 0)`, which on Windows maps to `TerminateProcess` rather than a liveness probe |
| app/server.py | unverified | Origin and launch-secret checks sit inside `if runtime.port:`, and `port` defaults to `0` |
| app/*orchestrator.py | unverified | `Database()` is constructed before the lock is acquired, so a REPORT_LOCKED failure skips `database.close()` |

## Decisions resolved

| # | Question | Resolution |
|---|---|---|
| 1 | What happens to the 3,787-line constitution? | Supersede it with a mapping table; keep as audit history per §32 P1 |
| 2 | Where does the V10 document live? | Committed under version control, referenced by the project map |
| 3 | Is template sealing retired, or kept as an optional release capability? | Keep the tooling, remove it from every blocking path |
| 4 | Does Reference D stay Finance PPV? | Yes — any department supplying four real, differently-shaped sources works; the shape spread is what matters |
| 5 | Fold the six defects into S0, or track separately? | Folded into S0 — they are small, and S0's exit gate is a green doctor anyway |

## Scope of this document

Plan only. No repository files were modified to produce it, and no stage
above has been started when it was written. Effort is expressed as sequence
and exit gates rather than dates. The one thing worth starting immediately
regardless of remaining decisions: the long-lead external requests in S0.
