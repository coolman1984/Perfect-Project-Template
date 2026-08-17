---
name: excel-intelligence-project-operator
description: Build, run, diagnose, verify, and evolve this exact offline Excel intelligence project using its verified task-ranked project map. Use whenever an AI agent enters this repository or changes extraction, data, analytics, dashboard, packaging, tests, or project memory.
---

# PROJECT SKILL — the mandatory first read

> **Template status.** This file ships as a template. Phase −2 instantiation
> (Part 39) replaces `<project_slug>`, `<REPORT_ID>` and the CURRENT TRUTH
> section with real values. Sections marked *generated* are owned by
> `PROJECT_TOOL map refresh`; everything else is written by humans and agents
> and preserved across refreshes (Part 24.2 rule 1).

---

## 1. READ THIS FIRST

```text
PROJECT_TOOL doctor
PROJECT_TOOL map context --task "<your task>" --budget 4000
```

Then read `.ai/CURRENT_STATE.md` and `.ai/CONTEXT_PACK.md`. Open only the files
the router names. **Do not scan the repository** (Part 0.1).

Windows: `PROJECT_TOOL.bat`. Linux/macOS: `./project_tool.sh`. Same tool (Part 37.2).

**Stop conditions — stop and ask, do not guess:**

| Condition | Why |
|---|---|
| A business rule is unknown (grain, key, formula, threshold, deletion, currency, timezone) | Part 3.1 reserves these to a named human. A guessed rule is the most expensive bug in this system. |
| A locked component seems incompatible or hard to package | Part 0.7 deviation request, explicit approval required. Difficulty is not permission to delete a component. |
| You want a "simpler" architecture or a new external prerequisite | Same. Describing a downgrade as "more portable" or "native" is itself evidence of non-compliance (Part 34.4). |
| `doctor` reports BLOCKED | Something was **not verified**. Never report it as a pass (Part 37.4). |
| The map contradicts the code | Code and executable evidence win temporarily; repair the map in the same task (Part 27.8). |

Stopping is correct behaviour, not failure.

---

## 2. PRODUCT

| | |
|---|---|
| **User** | A non-technical employee. No editor, terminal, database tool or file-system inspection. |
| **Decision supported** | `PENDING_APPROVAL` — name the one decision this dashboard drives (Part 26.1). |
| **Sources** | Protected Excel workbooks, opened through the employee's own authorized Excel session. Never DRM bypass. |
| **Outputs** | One-page local web app (the operating product) + a standalone portable HTML report (the export). |
| **Security boundary** | Loopback only, `127.0.0.1`, standard user, `asInvoker`, no elevation, no service, no firewall change. |
| **Flow** | `Open app → add data → process → see quality → use dashboard → act/export` |

⚠️ Extracted DuckDB, Parquet, JSON, HTML, exports, logs and backups contain the
same data as the protected Excel files **without** the DRM wrapper. That is a
real change in security posture and needs written IT approval (Part 13.5).

---

## 3. CURRENT TRUTH

<!-- HUMAN:BEGIN current-truth — preserved across map refresh -->

| | |
|---|---|
| **Phase** | −2 (template, not yet instantiated) |
| **Application version** | 0.0.0 |
| **Proven features** | None. This is a scaffold. |
| **Conditional gates** | Every Windows/Excel gate — see `acceptance/gates.yaml` |
| **Known limits** | No report configured; no business meaning approved; no release built |

Authoritative live status is `acceptance/gates.yaml` (`PROJECT_TOOL gates status`),
not this paragraph. Update both in the same change set.

<!-- HUMAN:END current-truth -->

---

## 4. ARCHITECTURE

```text
DRM-PROTECTED EXCEL  →  Excel desktop (authorized session)
   → ExtractionPort (COM adapter, Value2 blocks)
   → RAW STAGING  →  QUALITY GATE  →  CLEAN
   → HISTORY ENGINE ── DuckDB (brain) · Parquet (archive) · SQL Server (optional)
   → ANALYTICS (versioned SQL)  →  INSIGHTS (evidence objects)
   → DASHBOARD JSON  →  one-page local web app + standalone HTML  →  VERIFY
```

Dependency direction (Part 24.1) — circular dependencies are forbidden:

```text
web → local API → orchestrator → components
configuration and contracts point inward; business logic never leaks into UI
tests may depend on all layers; production layers never depend on tests
```

**Golden sentence:** *Excel is the authorized door to the data — Excel is not
the calculation engine.*

---

## 5. COMPACT PROJECT MAP

| Path | Purpose | Owner | Risk |
|---|---|---|---|
| `constitution/` | The law. Read once; afterwards route by Part number. | platform | critical |
| `app/excel/` | Session, discovery, extraction, conversion, identity | platform | critical |
| `app/data/` | DuckDB, staging, history, archive, migrations, optional SQL sync | data | critical |
| `app/quality/` | Checks, reconciliation, drift, quarantine | data/report | critical |
| `app/analytics/` | Metric registry, SQL runner, insights, calendar | business/data | critical |
| `app/dashboard/` | JSON builder, HTML builder, verifier | product | high |
| `app/server.py`, `app/local_transport.py` | Loopback API and its security boundary | platform | critical |
| `web/` | One-page shell, filters, charts, story, i18n, vendor assets | UI | high |
| `reports/<id>/` | Business meaning, config, mappings, metrics, quality, SQL | business | critical |
| `contracts/` | Config, dashboard, event, manifest schemas; error codes; run states | platform | critical |
| `acceptance/gates.yaml` | What is actually proven (Part 38) | platform | high |
| `tools/` | Map, memory, verifiers, gate ledger — dev only, never imported by `app/` | platform | medium |
| `.ai/` | Map, state, contracts, lessons, opportunities, memory | platform | medium |

Exhaustive catalog: `.ai/PROJECT_MAP.md` (generated). Do not load it whole —
search it by section.

---

## 6. TASK ROUTER

| Task | Read first | Usually edit | Must test | Must update |
|---|---|---|---|---|
| Excel will not open | `app/excel/session.py`, source config, last failure event | Excel adapter/config only | protected-file fixture + cleanup | map if behaviour changed |
| New or renamed column | report definition, `mappings.toml`, schema contract | mapping/config/migration | drift + reconciliation + golden | contracts, state, map |
| New KPI | `metrics.toml`, source fields, calendar rule | `sql/metrics.sql` + registry + JSON builder | unit + golden + dashboard | contract if public shape changes |
| New chart | `contracts/dashboard.schema.json`, Part 26.2 selection map | chart spec/template | browser + accessibility + print | map / UI contract |
| History duplicates | load-mode config, key rules, `sql/history.sql` | `app/data/history.py` + migration | same-input rerun + correction | decision record + lessons |
| SQL Server outage | `sys.sync_queue`, retry policy | connector only if a defect exists | disconnect/retry/reconcile | state if the limitation changed |
| Slow large file | profile, projection, chunk logic | extractor/config | representative benchmark | performance evidence + map |
| Text/UI change | `web/i18n/*.json`, component, accessibility rules | UI assets | keyboard + responsive + RTL + print | map only if structure changed |
| New report | Part 4, `reports/_TEMPLATE/` | `PROJECT_TOOL report new --id <id>` | report validate | gates, state, map |
| Gate evidence | `acceptance/gates.yaml` | `PROJECT_TOOL gates set` | the gate's own proof | state |

Route not listed? Add it here in the same change set (Part 20.4).

---

## 7. BUSINESS INVARIANTS

<!-- HUMAN:BEGIN invariants — never generated; a named human owns every line -->

| Invariant | Value | Approved by |
|---|---|---|
| Grain (what ONE ROW means) | `PENDING_APPROVAL` | — |
| Business key | `PENDING_APPROVAL` | — |
| Load mode | `PENDING_APPROVAL` | — |
| Lookback window | `PENDING_APPROVAL` | — |
| Deletion behaviour | `PENDING_APPROVAL` | — |
| Control total column | `PENDING_APPROVAL` | — |
| Currency / units | `PENDING_APPROVAL` | — |
| Timezone / fiscal calendar | `PENDING_APPROVAL` | — |
| Approved storage locations | `PENDING_APPROVAL` | — |
| AI narrative permitted? | `PENDING_APPROVAL` | — |

**An agent may create these sentinels. An agent may never resolve one.**
Resolution needs a named person, a UTC timestamp and an evidence reference
(Part 41.2).

<!-- HUMAN:END invariants -->

Permanent invariants that need no approval because the constitution fixes them:

- Running the same input twice changes nothing (idempotent, rule 5).
- A failure never corrupts trusted history (rule 9).
- Every row traces to source file, sheet and row number (rule 8).
- Control-total difference is exactly zero, not approximately (Part 9.4).
- Rejected rows are quarantined, never silently dropped (Part 9.5).

---

## 8. OPERATING RUNBOOK

| Action | Employee does | Behind the scenes |
|---|---|---|
| Start | `START_APP.bat` | integrity check → single-instance lock → bind `127.0.0.1` → health check → open renderer |
| Add data | drag files onto the page | stability check, role detection, hash, intake copy; source never modified |
| Process | press Process | the 26-step run cycle (Part 12.1); durable events drive the progress UI |
| Protected file prompt | open it in Excel, leave it open, press Retry | run sits in `WAITING_FOR_USER` with its checkpoint intact |
| Review | read PASS / WARNING / FAIL | FAIL leaves trusted history and the last dashboard untouched |
| Recover | follow the on-screen instruction | four-part error screen from `contracts/error_codes.json` |
| Back up | `BACKUP.bat` | copies database, archive, config, output and evidence to the approved destination |

**Golden operating rule:** if a run fails, the dashboard keeps showing the last
good data — and says so on screen. Never broken numbers. Never a blank page
(Part 12.6).

---

## 9. CHANGE PROTOCOL

```text
verify map + architecture baseline
→ classify the work mode and rewrite the eight-question task contract (Part 19.3)
→ resolve only true business/security/deviation blockers
→ reproduce current behaviour or the defect
→ write the failing test first
→ make the smallest clean change inside one layer
→ run focused, then integration/golden/failure/browser/architecture tests
→ update contracts, state, decisions, lessons, memory, gates
→ refresh and verify the map
→ report what changed and what was proven
```

A material code change with no map update must fail the suite. A map update
with no matching code evidence must fail review (Part 21.5).

---

## 10. RELEASE PROTOCOL

```text
BUILD_RELEASE      build the one-folder app from pinned local inputs only
                   PROJECT_TOOL architecture verify --release release/current
VERIFY_OFFLINE     block the network, start, health-check, process a fixture, restart
clean-PC gate      Part 30.4 on a real offline Windows PC, standard non-admin account
rollback           keep the previous approved version until migration and health checks pass
```

No release while any `severity: block` gate is unproven (Part 38.2 rule 4).
Generate the Part 34.4 completion declaration **from the ledger**, never from
memory.

---

## 11. MEMORY + IMPROVEMENT

Store only what changes a future decision or prevents repeated work.

```text
.ai/MEMORY.jsonl        sourced, dated, owned records with stable IDs
.ai/LESSONS.md          concise accepted lessons by topic
.ai/OPPORTUNITIES.md    improvement register with disposition
docs/decisions/         architecture and business decision records
```

Never store secrets, raw sensitive rows, chat history, temporary guesses, or
facts already obvious from code. Conflicts are marked and superseded
explicitly, never overwritten (Part 21.6).

End every meaningful task with:

```text
PROJECT_TOOL memory suggest --task "<completed task>" --max 3
```

Maximum three suggestions; zero is valid. Finish the requested work first, and
never implement an optional suggestion without approval (Part 21.7).

---

## 12. COMMAND INDEX

Safe, exact, non-destructive:

```text
PROJECT_TOOL doctor
PROJECT_TOOL map verify | refresh --review | context --task "..." --budget 4000
PROJECT_TOOL map explain --path app/data/history.py | changed --base <ref>
PROJECT_TOOL memory validate | suggest --task "..." --max 3
PROJECT_TOOL architecture verify --baseline | --source-scan | --release <folder>
PROJECT_TOOL constitution audit | cross-references | architecture-terms | commands
PROJECT_TOOL gates status | set --id <GATE> --status <s> --evidence <path>
PROJECT_TOOL report new --id <id> | validate --id <id> --mode production
```

Destructive commands are deliberately absent from this index (Part 24.2).
Database rebuild and archive restore live in `docs/OPERATIONS.md` behind an
explicit operator procedure.

---

## 13. POINTERS

| Need | Go to |
|---|---|
| The law | `constitution/EXCEL_AUTOMATION_CONSTITUTION.md` |
| What changed in the law and why | `docs/CONSTITUTION_IMPROVEMENTS.md`, `docs/CONSTITUTION_CHANGELOG.md` |
| Exhaustive file catalog | `.ai/PROJECT_MAP.md` |
| Proven status | `acceptance/gates.yaml` |
| Public contracts | `.ai/CONTRACTS.md`, `contracts/` |
| Decisions | `docs/decisions/` |
| Lessons | `.ai/LESSONS.md` |
| Acceptance evidence | `docs/ACCEPTANCE.md`, `acceptance/evidence/` |
| Operations and recovery | `docs/OPERATIONS.md` |
| Security posture | `docs/SECURITY.md` |
