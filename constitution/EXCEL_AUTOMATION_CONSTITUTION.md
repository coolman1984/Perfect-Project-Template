---
name: build-offline-excel-intelligence-webapps
description: Build, audit, repair, and evolve secure offline Excel-to-database web applications with protected-file extraction through authorized Microsoft Excel desktop access, large-file chunking, DuckDB history, optional SQL Server synchronization, deterministic analytics, professional dashboards, evidence-backed insights, quality gates, weekly updates, one-click Windows delivery, and a mandatory token-saving self-updating project map. Use for recurring Excel reporting, local management dashboards, factory or enterprise analytics, and projects that must remain operable by non-technical users and understandable to a new AI coding agent without reading the whole repository.
---

# Ultimate Excel Automation Skill + Master Execution Plan

**Version:** 7.2 · **Date:** 2026-08-17 · **Status:** Architecture-locked executable master prompt and living source of truth  
**Merged from:** `EXCEL_AUTOMATION_MASTER_PLAN_V3_CONCISE(1).md` + `EXCEL_AUTOMATION_MASTER_PLAN_V4_MERGED.md` + the complete offline web-app, reusable-skill, project-map, token-control, and continuous-learning requirements.  
**Research refresh:** 2026-08-17 · official/primary implementation and industry references are listed in Part 35.  
**Purpose:** One dual-use document. A business owner can understand the full logic; any local, editor-based, command-line, or web AI agent can build and maintain the project safely without guessing or rereading the entire repository.

> **Amendment notice (7.1 → 7.2).** Parts 0–35 are the approved 7.1 text and are **unchanged**. Parts 36–44 are additive amendments that close executability gaps found when this document was turned into a reusable project template. They add no new external prerequisite, remove no locked component, and weaken no acceptance gate — they only make existing rules machine-checkable and runnable from an empty repository. Rationale and full change list: `docs/CONSTITUTION_IMPROVEMENTS.md`. Where an amendment refines an earlier Part, the amendment says so explicitly and names the Part.

> **Supreme instruction:** This file is the project constitution. The project-local map is the daily navigation system. The constitution defines what must remain true; the map tells an agent exactly where to work. Neither replaces source-code verification for the small set of files being changed.

---

## PART 0 — How to use this document

| You are | Read | Your job |
|---|---|---|
| **Business owner (human)** | Parts 1, 2, 3, 4, 12, 13, 14 | Decide business meaning. Approve. Test the result. |
| **First builder AI / developer** | Read this whole constitution once because it defines the requested product. | Build exactly what is written. Stop and ask only at its explicit gates. |
| **Later maintenance agent** | Read `PROJECT_SKILL.md`, current state and the task-ranked context; open only routed constitution sections. | Make the smallest compliant change without a repository-wide reread. |

**Two rules for this document:**
1. Every technical word is explained once, in Part 2.
2. Avoid uncontrolled duplication. Critical safety and architecture gates may be repeated in short form; the detailed copy must point to its canonical section.

### 0.1 Mandatory 90-second start for every AI agent

When a project already exists, **do not scan or read the whole repository**. Start in this exact order:

1. Read `PROJECT_SKILL.md`—the mandatory project-specific first read.
2. Follow its pointer to `.ai/READ_FIRST.md` and run `PROJECT_TOOL.bat map verify`.
3. Run `PROJECT_TOOL.bat map context --task "<current task>" --budget 4000`.
4. Read `.ai/CURRENT_STATE.md` and the generated `.ai/CONTEXT_PACK.md` only if verification passes.
5. Use the task router to identify the smallest relevant files, contracts, tests, and decision records.
6. Read only those named files and their direct dependencies.
7. If the map is stale, stop feature work, run `PROJECT_TOOL.bat map refresh --review`, review the diff, and repair the map before continuing.
8. Never claim completion until the project skill, map, manifest, tests, state, and this constitution agree with the implementation.

The map is trusted navigation, not blind authority. An agent must still read every file it edits and every contract or test directly affected by the change. Broad exploratory reading is forbidden unless the map is missing, stale, or demonstrably wrong.

### 0.2 Token budget rule

For ordinary changes, the agent may initially load only:

```text
PROJECT_SKILL.md
.ai/CURRENT_STATE.md
.ai/CONTEXT_PACK.md
the exact task request
```

The agent then opens the smallest task-specific set named by the map. It must not run a full-tree read, import every document, or inspect generated/runtime/vendor folders. If it needs more context, it records why and expands one dependency boundary at a time.

`PROJECT_TOOL.bat` always calls the private packaged project-tool runtime. It never depends on system Python. Commands written with `python` elsewhere in historical examples must be implemented through this wrapper before release; the employee never types development commands.

### 0.3 How this file acts as a skill

- Treat the YAML description above as the trigger rule.
- Treat Parts 0, 3, 4, 6, 14, 17, 19–23, 26, 28, 30, 31, 33, and 34 as the operating, release, and consistency workflow.
- Search this file by heading instead of loading unrelated sections when the agent controls file reading.
- At project completion, execute Part 21 to capture lessons and update both the project map and the project-local copy of this skill.

### 0.4 Master execution mandate — build the product, not another plan

When an AI agent receives this document as its prompt, it must treat it as authorization to **create or evolve the complete local project** described here. It must not merely summarize, restate, audit, or produce another roadmap unless the user explicitly asks for planning only.

The default result is:

```text
working local web application
+ protected-Excel extraction pipeline
+ trusted history and analytics
+ one-page interactive management cockpit
+ evidence-backed insight story
+ complete offline Windows release bundle
+ tests, acceptance evidence, recovery tools
+ mandatory project-local AI skill, map, memory, and improvement scout
```

Execution rules:

1. Inspect the supplied sources and existing project, if any, through the map-first rules.
2. Convert this constitution into a task board with objective gates; do not ask the user to translate it into technical tasks.
3. Ask only for a missing decision listed in Part 3 that would change business meaning, security, or acceptance.
4. Make safe, reversible implementation choices **only inside the architecture locked by this document**. The agent may select minor internal details but may not remove, replace, bypass, or weaken a required component without explicit user approval.
5. Pass each phase gate, then continue directly to the next phase. Do not stop merely because one phase finished.
6. If real protected files or a required enterprise system are unavailable, build the **complete demonstrable product** with synthetic/masked fixtures, mark only the untested environmental gates `CONDITIONAL`, and provide the exact later validation step. Do not leave the application as a wireframe.
7. Never use fake KPIs or pretend synthetic results are production evidence. Label demo data clearly in the UI, manifests, and acceptance record.
8. Finish with the release ZIP, checksum, quick-start instructions, acceptance report, known limitations, and the next three highest-value improvements.

### 0.5 Mandatory agent response contract

At the start, the agent reports only:

```text
understood outcome · current evidence · blocking decisions, if any
first executable slice · expected deliverables · verification approach
```

During work, report real completed gates and current blockers—not internal reasoning or theatrical progress. At completion, report:

```text
what is working · what was proven · where the release is
what remains conditional · how a non-technical user starts it
map/skill/memory freshness · three evidence-based improvement options
```

The final delivery is not complete when code exists; it is complete when the non-technical operating flow, offline package, tests, map-first onboarding, and recovery proof all pass.

### 0.6 Critical interpretation: offline does not mean dependency-free

This rule exists to prevent the most dangerous shortcut in this project.

| Requirement | Correct meaning | Forbidden interpretation |
|---|---|---|
| **No internet at runtime** | All required runtimes, libraries, binaries, chart assets, schemas, and migrations are already inside the delivered package | Remove libraries and redesign the system around whatever happens to exist on Windows |
| **No installation for the employee** | Deliver a self-contained ready-to-run application folder | Ship source files and assume Python, packages, or developer tools exist |
| **Copy folder and run** | Copy the complete verified release folder, including its private runtime and dependencies | Use only Windows, Excel, batch files, or PowerShell because they are already installed |
| **Windows + Excel prerequisites** | These are the only approved external prerequisites | These two products replace DuckDB, the local server, analytics, quality, packaging, or chart libraries |
| **Offline repair/update** | Employee repair restores sealed release files; developer update rebuilds from the separate local wheelhouse | Download missing packages during setup or silently omit them |

The following reasoning is a **release-blocking violation**:

> “To avoid external library downloads, I will depend only on Windows and Excel.”

The correct reasoning is:

> “To avoid downloads, I will bundle every approved dependency inside the release and prove the application works when the network, system Python, Node.js, package managers, and developer tools are unavailable.”

Do not confuse **no downloads** with **no dependencies**. The product requires real extraction, database, quality, analytics, API, dashboard, verification, recovery, and project-intelligence capabilities. Windows and Excel alone do not satisfy those contracts.

### 0.7 Architecture authority and non-deviation rule

This document is an approved implementation contract, not a collection of optional suggestions. The precedence for architecture is:

```text
1. User's latest explicit approval
2. This constitution and its locked baseline
3. Approved architecture decision records
4. Versioned contracts and dependency lock
5. Existing implementation
6. Agent preference, convenience, or “simpler idea”
```

The agent may **not** independently:

- remove Python, `pywin32`, DuckDB, Parquet, FastAPI/Uvicorn/Pydantic, ECharts, packaging, tests, the map engine, or another required baseline component;
- replace the local application with a static HTML mockup, Excel-only workbook, PowerShell-only script, CSV/JSON folder, or browser storage;
- use Excel as the database or trusted calculation engine;
- assume system Python, Node.js, `pip`, `npm`, Git, Visual Studio Code, a terminal, or internet access;
- use a CDN, remote font, remote icon, telemetry endpoint, runtime package download, or DuckDB extension download;
- remove a feature because its dependency is difficult to package;
- change the architecture first and tell the user afterward;
- describe a downgrade as “more portable,” “simpler,” “native,” or “closer to copy-and-run.”

If a required component is genuinely incompatible with the approved target, the agent must stop only that affected change and submit a **deviation request** containing:

```text
component and contract affected
measured incompatibility evidence
options considered
proposed replacement and lost capabilities
offline/package/security impact
migration and rollback
equivalence tests
explicit approval required: YES
```

No deviation is implemented until the user explicitly approves it. Silence, time pressure, package size, personal preference, or an untested assumption is not approval.

### 0.8 Mandatory architecture compliance handshake

Before writing production code, the agent must create or verify:

```text
IMPLEMENTATION_BASELINE.lock.json
docs/ARCHITECTURE_COMPLIANCE.md
tools/verify_architecture.py
tests/architecture/
```

Then report this short handshake:

```text
approved external prerequisites: Windows + desktop Excel only
bundled runtime: present/planned
bundled libraries/assets: present/planned
local loopback API: retained; 127.0.0.1; standard-user process
administrator/elevation/service/firewall changes: NONE
forbidden runtime downloads: verified
architecture deviations: none / awaiting explicit approval
```

If the lock or verification fails, feature work may continue only on an isolated prototype; production packaging and any claim of completion are blocked. The agent may never repair a compliance failure by deleting the missing capability.

### 0.9 Local loopback server is mandatory and does not require administration

This section prevents a second dangerous shortcut: confusing the application's **internal loopback API** with an external, installed, or privileged server.

| Phrase | Exact meaning in this project | It does **not** mean |
|---|---|---|
| **No external server** | No cloud host, shared web server, remote API, or office-network dependency is required for normal local use | Remove the bundled local API |
| **Local server** | The bundled FastAPI/Uvicorn process starts with the app, listens only on `127.0.0.1`, serves this user's session, and stops with the app | Windows Service, IIS, HTTP.sys deployment, LAN listener, or always-on daemon |
| **No administrator rights** | Every normal start and run succeeds as the logged-in standard user with an `asInvoker` manifest and user-writable data folders | Replace HTTP/API contracts with an undefined “direct Windows connection” |
| **Copy folder and run** | The verified launcher starts the private runtime, loopback API, and renderer from the release folder | Open `file://` HTML or ask the browser to read Excel, DuckDB, or arbitrary local files directly |

The loopback API is the required, typed boundary between the renderer and the application. It owns validated uploads, run creation, durable progress/events, quality results, approved history, dashboard data, exports, cancellation, and safe shutdown. Browser JavaScript may not automate Excel COM, open DuckDB, or bypass this boundary.

Required runtime model:

```text
standard user launches START_APP.bat
→ verified packaged executable starts with requestedExecutionLevel=asInvoker
→ single-instance lock and writable per-user data path are verified
→ server binds 127.0.0.1 on an OS-selected or bounded approved high port
→ per-launch secret is created and health checked
→ approved renderer opens the exact loopback URL
→ app shutdown stops the listener and releases the instance lock
```

Normal use must never request UAC elevation, install a Windows Service, configure IIS, reserve an HTTP.sys URL, change the firewall, write to protected system folders, bind ports `80`/`443`, or listen on `0.0.0.0`, `::`, a LAN address, or a public interface. If a port is occupied, try a bounded list of approved loopback ports or an OS-selected free port; never “fix” binding by elevating. If no safe loopback port can be bound, fail closed with `LOCAL_LOOPBACK_BIND_FAILED` and an IT-friendly diagnostic.

The agent may not replace this transport with static `file://` HTML, browser-only storage, named pipes, an embedded browser bridge, or another “Windows-native/direct” mechanism unless it submits the Part 0.7 deviation request and proves full equivalence for API typing, security, durable state, events, testing, renderer independence, packaging, and recovery. **“No external server” is not permission to remove the local server. “No admin” is not evidence that a local loopback listener is impossible.**

---

## PART 1 — The goal, the picture, the rules

### 1.1 What we are building

A complete local system that turns protected company Excel files into one beautiful, trustworthy, decision-focused web application—automatically, without breaking security, duplicating history, or requiring internet or technical tools.

The person using it eventually sees only this:

```
Open app → Choose/add data → Process → See quality result → Use one-page dashboard → Act/export
```

### 1.2 The picture

```
DRM-PROTECTED EXCEL FILE
        ↓  (authorized user session)
MICROSOFT EXCEL DESKTOP
        ↓  COM, large Value2 blocks
EXTRACTOR  →  RAW STAGING  →  QUALITY GATE  →  CLEAN DATA
                                                    ↓
                                            HISTORY ENGINE
                                    ┌───────────────┼───────────────┐
                                 DuckDB          Parquet        SQL Server
                                (brain)         (archive)      (optional, shared)
                                    └───────────────┼───────────────┘
                                                    ↓
                 ANALYTICS → INSIGHTS → JSON → LOCAL ONE-PAGE WEB APP + STANDALONE HTML → VERIFY
```

### 1.3 The factory analogy (for the non-technical reader)

| Factory | Our system |
|---|---|
| Supplier truck | Excel file |
| Unloading dock | COM extractor |
| Incoming inspection | Quality gate |
| Raw material store | Parquet archive |
| Production line | DuckDB |
| Finished goods | Mart / analytics tables |
| Shipping box | JSON |
| Showroom | HTML dashboard |

**Golden sentence:** *Excel is the authorized door to the data — Excel is not the calculation engine.*

### 1.4 The seventeen non-negotiable rules

| # | Rule | Why |
|---|---|---|
| 1 | Never bypass DRM. Read only what the logged-in user can already open. | Legal and career safety |
| 2 | Read rectangular blocks with `Range.Value2`. Never cell-by-cell. | 20 million border crossings = hours. One = seconds. |
| 3 | Excel COM runs only in an interactive logged-in session, never as a Windows Service. | DRM + COM require a real user session |
| 4 | New data enters staging first. Trusted history changes only after quality passes. | Bad data must never enter the truth |
| 5 | Running the same input twice must produce the identical result (idempotent). | Safe reruns, safe recovery |
| 6 | All trusted arithmetic lives in tested SQL. JavaScript only displays. | One place to fix logic |
| 7 | AI never invents business meaning. | A wrong formula that looks confident is worse than no dashboard |
| 8 | Every row is traceable back to its source file, sheet and row number. | "Where did this number come from?" must take 30 seconds |
| 9 | A failure must never corrupt trusted history. | Recovery beats perfection |
| 10 | A new agent starts from the verified project map, never a broad repository read. | Faster work and controlled context use |
| 11 | Every material project change updates code, tests, contracts, map, manifest, and current state in the same task. | Documentation cannot drift behind reality |
| 12 | Real business rules are approved by a named human owner; technical defaults are labelled and reversible. | Prevents confident but incorrect automation |
| 13 | Offline means dependencies are bundled—not deleted, replaced, or downloaded later. | Preserves the complete product while remaining truly offline |
| 14 | The approved architecture may change only after an explicit user-approved deviation request. | Stops agents from silently simplifying away required capabilities |
| 15 | A missing packaged component fails closed with a clear integrity error; the app never silently downgrades to Excel-only, static HTML, or reduced logic. | A visible stop is safer than a false “working” product |
| 16 | The bundled FastAPI/Uvicorn loopback API remains the renderer-to-application bridge and listens only on `127.0.0.1` as the logged-in standard user. | Local API does not mean external or privileged server |
| 17 | Normal startup never elevates, installs a service, changes firewall/URL reservations, or writes to protected system locations. | Locked-office compatibility must be proven without weakening the architecture |

---

## PART 2 — Glossary (plain English)

| Word | Meaning |
|---|---|
| **DRM (NASCA)** | The company lock on files. Decides who may open them. |
| **COM** | An invisible hand that remote-controls Excel from Python. |
| **Value2** | The fastest way to read a block of Excel cells. Returns raw numbers (dates arrive as numbers and must be converted). |
| **Chunk** | One rectangular block of cells read in one request. |
| **Staging** | A waiting room for new data before it is trusted. |
| **Quality gate** | The inspection that decides PASS / WARNING / FAIL. |
| **Quarantine** | A holding table for rejected rows. Nothing is ever silently deleted. |
| **Trusted history** | The permanent, checked data. The single truth. |
| **DuckDB** | A fast database inside one file on your PC. No server needed. |
| **Parquet** | A compressed table file. Used as the recovery archive. |
| **SQL Server (MSSQL)** | The shared company database. Optional. |
| **Business key** | The columns that make one row unique (e.g. date + line + order + model). |
| **Load mode** | How new files join old data: append, upsert, snapshot, or replace period. |
| **Lookback window** | How many past days we re-check for corrections (e.g. last 7 days). |
| **Idempotent** | Running twice changes nothing. |
| **Lineage** | The trail from a dashboard number back to its Excel cell. |
| **Control total** | One number (e.g. total quantity) proven equal in Excel and in the database. |
| **Grain** | What one row represents. |
| **Golden test** | A tiny dataset with known correct answers, used to catch broken formulas. |
| **Run manifest** | The record card of one run: what ran, what happened, what was proven. |
| **Metric registry** | The official list of KPI definitions. One formula per KPI, company-wide. |
| **Self-contained release** | A delivered folder that already includes its private runtime, libraries, assets, and configuration; the employee does not install or download them. |
| **Architecture lock** | The approved list of required components and forbidden substitutions. An agent cannot change it without explicit user approval. |
| **Wheelhouse** | A developer/agent folder containing verified Python packages for offline build/update. Employee repair does not install from it. |
| **Fail closed** | Stop safely and explain the missing component instead of silently running a weaker or incorrect version. |

---

## PART 3 — Who decides what

### 3.1 The human decides (the agent may never assume these)

```
What one row means (grain)      Currency and units
Business key                    Time zone and fiscal calendar
Which files are required        Metric formulas
Load mode                       Quality thresholds
Deletion behaviour              Retention policy
Who may access the outputs      Where extracted data may be stored
Whether AI narrative is allowed
Any removal/replacement of a locked architecture component
Any new external prerequisite, runtime download, or reduced-capability fallback
```

### 3.2 The agent builds

```
Excel session + extraction      History engine
Chunking + conversion           Parquet archive
Staging + lineage               SQL Server sync
Quality checks + quarantine     SQL calculations
JSON builder                    HTML dashboard
Tests, logging, recovery, docs
The exact approved bundled runtime and dependency release
```

### 3.3 The agent must STOP and ask when

```
Business key unknown            Deletion behaviour unclear
Formula meaning unclear         Quality tolerance not approved
Currency or unit unknown        Storage location not approved
A source column changed meaning
A locked component seems incompatible or difficult to package
The agent proposes a “simpler” architecture or new external prerequisite
```

**Stopping is correct behaviour, not failure.** A guessed business rule is the most expensive bug in this system.

---

## PART 4 — Report definition (do this BEFORE any code)

Every recurring report gets one folder:

```
reports/<report_id>/
    report_definition.md     ← business meaning, written by the human
    report.toml              ← machine configuration
    sql/                     ← clean, metrics, checks, marts
```

### 4.1 The definition must answer all of this

```
Report name            Worksheet / table / range
Business owner         What ONE ROW means
Purpose (what decision it supports)
Frequency              Business key
Data period            Measures (numbers)
Required files         Descriptive fields
Optional files         Load mode
Currency               Units
Time zone              Fiscal calendar
Quality rules          Retention
Output audience        Approved storage locations
Deletion behaviour
```

### 4.2 Example

```
Report:         Daily Production
Owner:          Production Control
Purpose:        Daily output vs target, and where losses come from
One row:        one production order + model + line + production date
Business key:   production_date + line + order_number + model_code
Load mode:      upsert
Lookback:       7 days
Currency:       EGP
Time zone:      Africa/Cairo
Deletion:       mark inactive (never physical delete)
Control total:  sum of produced_qty
```

> **Hard gate:** no extraction code is written until `report_definition.md` is filled and approved by the business owner.

---

## PART 5 — `report.toml` (the machine contract)

```toml
report_id      = "daily_production"
report_version = 1
load_mode      = "upsert"          # append | upsert | snapshot | replace_period
timezone       = "Africa/Cairo"
currency       = "EGP"

[excel]
sheet              = "Raw Data"
header_row         = 3
data_start_row     = 4
open_mode          = "dedicated_then_attach"   # dedicated | attach | dedicated_then_attach
calculation_policy = "as_saved"                # never recalculate silently
data_area          = "table:tblProduction"     # table: | range: | header_columns | discover

[extraction]
target_cells_per_chunk = 250000
min_rows_per_chunk     = 250
max_rows_per_chunk     = 10000

[history]
business_key   = ["production_date", "line", "order_number", "model_code"]
event_date     = "production_date"
lookback_days  = 7
deletion_rule  = "mark_inactive"   # ignore | mark_inactive | soft_delete | close_version | physical

[quality]
required_columns_block   = true
max_duplicate_key_rate   = 0.0
max_required_null_rate   = 0.0
max_row_count_change_pct = 40.0
control_total_column     = "produced_qty"

[output]
audience        = "Production management"
storage_allowed = ["D:/secure/excel-automation"]
```

**Config rules:**
- Version it in Git. Validate it before every run against `contracts/report_config.schema.json`.
- Never silently change a business key or a metric meaning — that raises `report_version`.
- No file path, sheet name, column name or threshold ever appears inside a `.py` file.

---

## PART 6 — The ten layers and their contracts

Each layer has one job, one output, and one proof. A vertical feature may require coordinated changes across several layers, but each change must remain inside that layer's responsibility and communicate only through versioned contracts. Never hide cross-layer behaviour in one convenient file.

| # | Layer | Input | Output | Proof it works |
|---|---|---|---|---|
| 1 | **Excel session** | source + excel config | open workbook, read-only | source file unchanged; correct workbook matched |
| 2 | **Extractor** | session + mapping + chunk policy | stream of chunks | rows = expected; no cell-by-cell call |
| 3 | **Staging writer** | chunk | raw rows + checkpoint | restartable after crash |
| 4 | **Quality gate** | run_id + rules | PASS / WARNING / FAIL + evidence | control total difference = 0 |
| 5 | **Clean layer** | raw | typed, named, deduplicated | zero nulls in business key |
| 6 | **History engine** | validated clean + load mode | inserted / updated / unchanged / rejected counts | rerun creates zero duplicates |
| 7 | **Archive** | trusted batch | Parquet partitions | database rebuildable from archive |
| 8 | **Analytics** | trusted data + period | KPI + chart tables | golden tests pass |
| 9 | **JSON builder** | analytics + quality + lineage | dashboard JSON | validates against schema; size within limits |
| 10 | **HTML builder + verifier** | JSON + template | one offline HTML | opens with no network, no JS error |

Optional layer: **SQL Server sync** (between 7 and 8) — see 13.4.

---

## PART 7 — Excel extraction (the fragile part, done carefully)

### 7.1 Open modes

| Mode | How | When |
|---|---|---|
| **Dedicated** (preferred) | Create a private Excel instance → open read-only → read → close without saving → quit | Normal case; never touches the user's own workbooks |
| **Attach** (fallback) | Use the workbook the employee already opened | When DRM requires the user to open it manually first |
| **dedicated_then_attach** | Try dedicated; fall back to attach | Safe default |

Attach rules: match the **exact** workbook (full path), never a similar name, and **never close a workbook the user owns**.

Before reading, put Excel into silent mode: no screen updating, no alerts, no events, calculation manual. Restore all settings in a `finally` block — **even after failure**.

**Watchdog:** record the process ID of every Excel instance created by this application. At startup, terminate only a verified stale process that the application owns; never kill all `EXCEL.EXE` processes or an unverified user process. Leftover invisible Excel is a common cause of “it worked yesterday, it hangs today,” but recovery must not destroy the employee’s work.

### 7.2 Finding the data — in this priority order

```
1. Configured Excel Table  (best — survives inserted rows/columns)
2. Configured named range
3. Configured header row + known column names
4. Bounded first-time discovery (only for initial setup, then written into config)
```

**Never trust `UsedRange` blindly** — Excel remembers deleted rows and reports a bigger area than the real data.

**Never map columns by position.** Map by approved name. A moved column must still work; a renamed critical column must FAIL loudly.

### 7.3 Adaptive chunking (cells, not rows)

```
rows_per_chunk ≈ target_cells_per_chunk ÷ number_of_columns
then clamp between min_rows_per_chunk and max_rows_per_chunk
```

Example: 272 columns, target 250,000 cells → ≈ 919 rows per chunk.

This matters because a 272-column file and a 12-column file need very different row counts for the same memory. Write each chunk straight to staging — never hold the whole file in memory.

### 7.4 Value conversion (must be explicit)

Use `Value2` for speed. It returns raw values, so conversion is our responsibility:

| From Excel | To | Rule |
|---|---|---|
| blank / whitespace-only | NULL | — |
| number in a date column | DATE | convert with the workbook's date system (1900 vs 1904) |
| decimal money | `DECIMAL(18,4)` | never floating point — this is what makes reconciliation land on exactly zero |
| text that parses as number | DECIMAL | strip spaces and separators; `(1,234)` → `-1234`; map Arabic-Indic digits `١٢٣` → `123` |
| text that does not parse | keep VARCHAR | count as `conversion_failures` |
| boolean | BOOLEAN | — |
| `#N/A` `#VALUE!` `#DIV/0!` `#REF!` | NULL | **count them.** Never silently convert to zero. |

### 7.5 The dirty-Excel reality list

This is where most real bugs live. Each must be handled explicitly.

| Problem | Handling |
|---|---|
| Merged cells (value only in top-left) | Fill down/right after extraction, per configured columns |
| Multi-row headers | `header_row` + `data_start_row` in config |
| Trailing spaces in headers | Normalization rule 7.6 |
| Phantom rows from deletions | Use table/range, not UsedRange |
| Hidden or filtered rows | Decide once, record the decision (usually: include) |
| Hidden sheets | Config names the sheet explicitly — never "read all sheets" |
| Volatile formulas recalculating | Calculation set to manual before opening |
| File still being written by another process | Check file size is stable across two reads before opening |

### 7.6 Column name normalization (deterministic — same input, same output, always)

```
1. trim spaces
2. lowercase
3. replace every run of non-letter/non-digit with a single "_"
4. remove leading/trailing "_"
5. if it starts with a digit, prefix "c_"
6. if empty, use "col_<position>"
7. if duplicated, append "_2", "_3", ...
```

Example: `"  Total Cost (USD) "` → `total_cost_usd`

### 7.7 Lineage columns (added to every staged row)

```
_run_id            _source_file_hash
_report_id         _source_sheet
_source_id         _source_row_number
_source_file       _extracted_at
_schema_version
```

Goal: any number on the dashboard can be traced to its exact Excel row.

### 7.8 If COM is blocked — backup plans, in order

These are recovery proposals, not automatic architecture changes. Record evidence, obtain the required business/IT approval, and use the deviation process in 0.7 before replacing the locked primary path.

1. **Plan B:** a VBA macro inside the approved Excel environment exports to CSV in an approved folder; Python picks it up.
2. **Plan C:** request a scheduled export from the upstream system (SAP, MES). Going upstream is always cleaner than fighting downstream.
3. **Plan D:** ask IT for a documented account with export rights.

Record which plan is active. Never switch silently.

---

## PART 8 — History engine (connected history, no duplicates)

### 8.1 Four load modes — every report declares exactly one

| Mode | Use when | Behaviour |
|---|---|---|
| **append** | Every file contains only new permanent transactions | old + new |
| **upsert** | Old records may be corrected | same business key + changed values → update; new key → insert |
| **snapshot** | Each file is the full state at a point in time | store with snapshot date |
| **replace_period** | One file fully replaces one approved period | delete that period, insert new — never all history |

### 8.2 Record identity — two hashes

```
business_key_hash  → "Is this the same business record?"
row_content_hash   → "Did any of its values change?"
```

These two answers give you insert / update / unchanged in one pass, with no guessing.

### 8.3 Late corrections

A configurable lookback window. Example: today 16 Aug, lookback 7 → re-check 10–16 Aug. Anything older is assumed final unless a full rebuild is requested.

### 8.4 Deletions — must be configured, never guessed

```
ignore disappearance | mark inactive | soft delete | close historical version | physical delete
```

If a row vanishes from the source, the system must already know what that means.

### 8.5 Safe commit

```
BEGIN
  validate staged rows
  update changed rows
  insert new rows
  apply approved deletion rule
  reconcile counts and totals
COMMIT          ← on any failure: ROLLBACK, history untouched
```

### 8.6 Rebuild and recovery

| Situation | Action |
|---|---|
| Calculation logic changed | Drop clean + analytics, rebuild from raw — minutes, no Excel |
| A period was wrong | Delete that `run_id` batch, re-extract those files, reload |
| Database lost | Rebuild from Parquet archive |
| Archive lost | Re-extract from Excel (the only slow path — hence backups) |

---

## PART 9 — Quality gate (the trust layer)

Every run ends with exactly one verdict: **PASS** (safe to commit) · **WARNING** (continue only if that rule is non-blocking) · **FAIL** (trusted history is not touched).

### 9.1 Structural checks

```
required sheet exists · header exists · required columns exist
no duplicate headers · critical types match · schema version matches
```

| Change detected | Action |
|---|---|
| Column moved | Map by approved name — OK |
| New optional column | Load it, log it — WARNING |
| Required column missing | **FAIL** |
| Critical column renamed | **FAIL** (never fuzzy-match important fields) |
| Critical type changed | **FAIL** |

### 9.2 Row checks

```
business key not blank · business key unique where required · required fields not blank
date valid and in range · quantity ≥ 0 · category in approved list
no Excel error in a critical field
```

### 9.3 Dataset checks

```
row count vs history (±40% default) · min/max date · latest required period present
null-rate movement · category-count movement · freshness of source file
```

### 9.4 Control-total reconciliation — the strongest check

```
Excel total of produced_qty : 4,812,300
Database total              : 4,812,300
Difference                  : 0        → PASS
```

Not "approximately." **Exactly zero**, at the defined decimal precision. If not zero → FAIL, history untouched, dashboard keeps showing the last good data.

This single rule is what converts "a nice dashboard" into "a number I can present to management."

### 9.5 Quarantine — never silently drop a row

Rejected rows go to `quarantine_<report_id>` with:

```
run_id · source_row_number · reason_code · reason_message · raw_values
```

---

## PART 10 — Analytics, metrics and insights

### 10.1 Data model

```
raw  →  clean  →  analytics
```

For larger reports use facts and dimensions:

```
fact_production · dim_model · dim_line · dim_calendar
```

If master data changes and historical classification matters, dimensions carry `valid_from`, `valid_to`, `is_current`.

Build one shared calendar table: day, week, month, quarter, year, fiscal period, working day, holiday. Fiscal logic lives in exactly one place.

### 10.2 Metric registry — one approved definition per KPI

```
Metric ID:        defect_rate
Meaning:          defective quantity ÷ inspected quantity
Formula:          SQL file reference
Source fields:    defect_qty, inspected_qty
Grain:            day, week, month, model, line
Unit:             percent      Currency: n/a
Null rule:        null if inspected_qty is null
Zero rule:        null if inspected_qty = 0   (never divide by zero)
Rounding:         2 decimals, at presentation only
Owner:            Quality      Version: 1
```

All trusted business metric and reconciliation logic lives in versioned `.sql` files. Python may orchestrate, validate, convert and format; JavaScript may render and filter approved pre-aggregations. Neither may contain a second hidden KPI formula.

Reusable families: sum, count, average, min/max, actual vs target, period comparisons, rolling averages, growth rate, variance, rank, share of total, Pareto, yield, defect rate, productivity, margin, cost variance.

### 10.3 Insights — evidence first, words second

| Good | Bad |
|---|---|
| "Output is 8.2% below last week. Models A and C explain 72% of the decline. Model A accounts for 1,240 lost units." | "Performance looks weak." |

Rules are deterministic SQL + a sentence template. Rank by business impact, absolute change, percentage change, persistence, number of records affected. Show at most 5 — more is noise.

If AI narrative is approved by the business owner, it receives **verified evidence objects only**. AI never produces a KPI value.

---

## PART 11 — JSON contract, local web app, and standalone dashboard

### 11.1 JSON is a dashboard package, not a database export

```json
{
  "schema_version": "1.0",
  "report":    { "id": "daily_production", "title": "Daily Production", "period": "2026-08-15" },
  "freshness": { "data_date": "2026-08-15", "generated_at": "2026-08-16T07:00:12+03:00", "run_id": "RUN-20260816-001" },
  "quality":   { "status": "PASS", "checks_passed": 14, "checks_failed": 0 },
  "filters":   {},
  "kpis":      [],
  "charts":    [],
  "tables":    [],
  "insights":  [],
  "actions":   [],
  "lineage":   { "source_file": "Daily_Production_2026-08-15.xlsx", "rows": 482991 }
}
```

**Size discipline:** KPI values → tens · trend points → hundreds · ranking rows → tens or low hundreds · detail rows → only what is genuinely useful. Numbers arrive already calculated and already rounded. The browser never sums a million rows.

Validate every build against `contracts/dashboard.schema.json`.

### 11.2 The two presentation outputs

The primary experience is the bundled one-page local web application described in Parts 22 and 26. Every approved run also creates one self-contained portable report, e.g. `Daily Production - 2026-08-15.html`, containing HTML + CSS + JavaScript + ECharts + the embedded approved JSON.

Both outputs make **zero** unexpected network requests, use the same JSON/chart definitions, support light/dark/responsive/print behaviour, show freshness and quality, and include only decision-relevant charts. The portable file is for viewing/export; upload, processing, history, recovery, and governed drill-through remain in the local app.

### 11.3 Layout

```
TITLE | PERIOD | FRESHNESS | QUALITY
─────────────────────────────────────
KPI CARDS
─────────────────────────────────────
MANAGEMENT SUMMARY (max 5 insights)
─────────────────────────────────────
MAIN TREND        | ACTUAL VS TARGET
─────────────────────────────────────
PARETO            | BREAKDOWN
─────────────────────────────────────
HEATMAP / ROOT CAUSE
─────────────────────────────────────
DETAIL TABLE (sortable, searchable)
─────────────────────────────────────
RISKS | OPPORTUNITIES | ACTIONS
─────────────────────────────────────
SOURCE | DATA DATE | RUN ID | QUALITY
```

This legacy outline is the minimum portable-report story. The exact 2026 one-page application blueprint, filters, motion, slides, and responsive grid are mandatory in Parts 22 and 26 and take precedence when more specific.

### 11.4 Design rules (what "elegant 2026" means concretely)

| Rule | Instruction |
|---|---|
| One accent colour | Everything else greyscale. Colour carries meaning, not decoration. |
| Colour has one job | Green = good, red = bad, grey = neutral. Never colour for beauty. |
| Never colour alone | Always pair with ▲▼ arrows or text — for printing and for colour-blind readers |
| Whitespace | Generous padding, clear grouping, nothing touching edges |
| Typography | One clean font, two number sizes, **tabular figures** so digits align in columns |
| Chart titles | A plain-language question: "Are we above target?" |
| Forbidden | 3D charts, pie charts with many slices, decorative gradients |
| Motion | 150–250 ms fades only. Nothing bounces. |
| Print | A print stylesheet — managers still hand out paper |

### 11.5 Automated verification (the last layer)

After building, a headless browser check confirms:

```
file opens locally · zero network requests · zero JavaScript errors
KPIs present · charts render · filters work · light/dark works
period and quality match the run manifest
```

If verification fails, the run is FAILED and the previous dashboard is left in place.

---

## PART 12 — Operations

### 12.1 The run cycle (every production run, in this order)

```
 1 create run                    15 clean and type data
 2 resolve source files          16 update history (transaction)
 3 confirm file is stable        17 archive if policy allows
 4 identify report + period      18 sync SQL Server if enabled
 5 hash source file              19 calculate KPIs
 6 acquire report lock           20 build evidence-based insights
 7 check RAM / disk / temp       21 build dashboard JSON
 8 open or attach to Excel       22 build one HTML file
 9 validate workbook identity    23 verify HTML automatically
10 locate configured data area   24 save run manifest
11 read adaptive chunks          25 mark COMPLETE
12 write chunks to staging       26 release lock
13 save checkpoints
14 run quality gate  ← STOP HERE IF FAIL
```

### 12.2 Run states (store every transition)

```
CREATED → CHECKING_SOURCE → WAITING_FOR_FILE → OPENING_EXCEL → EXTRACTING →
STAGING → VALIDATING → CLEANING → UPDATING_HISTORY → ARCHIVING →
SYNCING_SQL_SERVER → CALCULATING → BUILDING_INSIGHTS → BUILDING_JSON →
BUILDING_DASHBOARD → VERIFYING → COMPLETE
                                        (or FAILED / CANCELLED at any point)
```

### 12.3 Error codes and their class

Every error carries a code **and** a class: `RETRYABLE` · `USER_ACTION` · `BLOCKING_DATA` · `BLOCKING_SYSTEM`.

```
SRC_NOT_FOUND · SRC_FILE_NOT_READY
EXCEL_NOT_AVAILABLE · EXCEL_OPEN_FAILED · EXCEL_WORKBOOK_AMBIGUOUS
DRM_USER_ACTION_REQUIRED · EXCEL_READ_FAILED
SCHEMA_REQUIRED_COLUMN_MISSING · SCHEMA_TYPE_CHANGED
DATA_DUPLICATE_BUSINESS_KEY · DQ_CONTROL_TOTAL_MISMATCH
RESOURCE_DISK_LOW · RESOURCE_MEMORY_RISK · REPORT_LOCKED
PACKAGE_COMPONENT_MISSING · PACKAGE_COMPONENT_BLOCKED
ARCHITECTURE_BASELINE_MISMATCH · UNEXPECTED_NETWORK_ATTEMPT
LOCAL_LOOPBACK_BIND_FAILED · LOCAL_ORIGIN_REJECTED
LOCAL_TRANSPORT_INTEGRITY_FAILED · ELEVATION_FORBIDDEN
DUCKDB_WRITE_FAILED · HISTORY_COMMIT_FAILED
SQL_CONNECT_FAILED · SQL_BULKCOPY_FAILED · SQL_RECONCILIATION_FAILED
ANALYTICS_TEST_FAILED · JSON_CONTRACT_FAILED
DASHBOARD_BUILD_FAILED · DASHBOARD_VERIFY_FAILED
```

### 12.4 Retry policy

| Retry automatically (with increasing delay) | Requires a person | Never retry — it is a real problem |
|---|---|---|
| temporary SQL connection failure | DRM prompt appeared | required column missing |
| temporary file lock | unauthorized workbook | control total mismatch |
| temporary verification failure | ambiguous workbook match | duplicate business keys above tolerance |
| | required source missing | failed calculation test |

### 12.5 Human troubleshooting — the 5-minute checklist

| Symptom | Check first | Fix |
|---|---|---|
| Run never started | Was the user logged on? | Re-schedule / stay logged in |
| Excel hangs | Check the run evidence for the exact Excel process ID created by this application | Close only that owned process after graceful timeout; never kill all `EXCEL.EXE` processes or the user's workbook |
| "File in use" | Someone has it open | Read-only open handles most cases; else retry |
| Control total mismatch | Quality report → which source | Compare clean vs raw for that report |
| Row count dropped sharply | Source file modified date, sheet name | Confirm with the file owner before loading |
| New column error | `schema_diff.json` | Update `report.toml`, raise version, rerun |
| Dashboard shows old date | Last run status | Read `run.log.jsonl` |

### 12.6 The golden operating rule

> **If a run fails, the dashboard keeps showing the last good data — and says so clearly on screen.**

Never show broken numbers. Never show a blank page. Show the last truth, with its date.

### 12.7 Every run produces

```
runs/RUN-YYYYMMDD-NNN/
    run_manifest.json      quality_report.json
    dashboard_data.json    dashboard.html
    run.log.jsonl          performance.json
    schema_diff.json       rejected_rows.parquet   (optional, policy-controlled)
```

The employee normally sees only: status · data date · quality · warnings · dashboard · history. Everything technical stays under "Support details."

---

## PART 13 — Storage, database and project layout

### 13.1 Project structure

This is only the logical data/application summary. Part 24 is the authoritative complete file tree and includes the architecture lock, project skill, offline build kit, verifier, memory and release evidence. If the two ever appear to conflict, update this summary and follow Part 24.

```
excel-automation/
├── app/
│   ├── orchestrator.py   state_machine.py   locks.py
│   ├── excel/            data/              quality/
│   ├── analytics/        dashboard/         observability/
├── reports/<report_id>/  report.toml · report_definition.md · sql/
├── contracts/            dashboard.schema.json · report_config.schema.json
├── migrations/           ordered database migrations
├── tests/                unit/ integration/ golden/ performance/ fixtures/
├── docs/                 decisions/ · operations.md
├── runtime/ workspace/ output/ archive/
└── pyproject.toml  README.md
```

Report-specific behaviour lives in **configuration, SQL, metric definitions and quality rules** — never by copying the Python engine per report.

### 13.2 DuckDB schemas

```
sys · raw · clean · quality · analytics
```

System tables: `sys.run` · `sys.source_file` · `sys.checkpoint` · `sys.sync_queue` · `sys.schema_migration` · `quality.check_result`.

One coordinated writer only. Configure and benchmark `memory_limit`, `temp_directory`, `max_temp_directory_size`, `threads`. Fail early if RAM or disk is unsafe.

### 13.3 Parquet archive (only if policy permits)

```
archive/report=daily_production/year=2026/month=08/part-*.parquet
```

Purpose: recovery, rebuild, fast historical analysis, compressed storage. Avoid thousands of tiny files.

### 13.4 SQL Server (optional, enterprise mode)

```
trusted local batch → bulk copy → SQL staging → validate → transactional upsert → reconcile
```

If SQL Server is unavailable, the local run still completes with `sync_status = PENDING` and retries later. **Never re-read Excel because a network sync failed.**

DuckDB is the kitchen; SQL Server is the delivery shelf. Skip it entirely until someone outside your team actually needs the data.

### 13.5 Security approval — settle this before go-live

⚠️ Extracted Parquet, DuckDB, JSON, HTML and logs contain the same data as the protected Excel files, **without** the DRM protection. That is a real change in security posture.

Get written answers to:
```
Where may the warehouse and archive folders live?
Who may read them?
Does the dashboard output need restriction?
How long may extracted data be retained?
Is any external AI service permitted to see this data?
```

A project switched off in month 3 is worse than one that started a week later.

---

## PART 14 — Build roadmap

Build in this order and continue after every passed gate. Production approval requires real protected inputs and the real target environment. When either is temporarily unavailable, complete and prove the full product with safe production-like fixtures, label the affected gate `CONDITIONAL`, and schedule the exact real-environment proof.

| Phase | Build | Done when |
|---|---|---|
| **−1 — Architecture + offline release lock** | Baseline lock · allowed prerequisites · required bundled components · forbidden substitutions/downloads · architecture verifier · release bill of materials | User-approved baseline is machine-verified; no required component is silently absent or replaced |
| **0 — Governance + DRM proof** | Storage approval matrix · real protected-file test · safe COM wrapper · read-only open · attach fallback · Value2 benchmark | A representative protected workbook is read reliably, source unchanged |
| **1 — One end-to-end report** | Excel → chunks → DuckDB raw → clean → basic quality → one load mode → 5–10 KPIs → JSON → local one-page app + standalone HTML | Totals match source · rerun creates no duplicates · app/dashboard open offline |
| **2 — Reliability** | Run IDs · state machine · report lock · checkpoints · file hashes · structured logs · resource checks · retry · safe cancel | A crash cannot corrupt trusted history |
| **3 — History** | All four load modes · key + content hashes · late corrections · full rebuild | Repeated daily/weekly files create correct connected history |
| **4 — Strong quality** | Schema checks · row checks · dataset checks · control totals · freshness · cross-source · quarantine | Bad data cannot silently enter trusted history |
| **5 — Archive + recovery** | Parquet archive · retention · rebuild test | A fresh database rebuilds from archive alone |
| **6 — SQL Server (only when enabled/approved)** | Bulk copy · transactional upsert · reconciliation · pending queue · retry | Local and central history stay consistent; otherwise the phase is explicitly not applicable |
| **7 — Metric library** | Shared calendar · reusable KPI definitions · comparison, trend, Pareto logic | The same KPI has one formula everywhere |
| **8 — Insight engine** | Deterministic evidence rules; optional AI narrative *after* verified evidence | Every insight can show the numbers behind it |
| **9 — Dashboard templates** | Executive · Production · Quality · Inventory · Sales · Cost — all on one JSON contract | A new report gets a dashboard without new JavaScript |
| **10 — Product experience** | One page: choose/add data → process → real progress → quality → filtered decision dashboard/story → actions → history/export/recovery | A non-technical employee runs it alone |

**Phase 1 is worth more than Phases 2–10 on paper.** One working vertical slice beats ten empty frameworks.

**Phase −1 is not a design discussion.** It freezes the already approved architecture so a later agent cannot reinterpret “offline” as permission to remove dependencies or capabilities.

> **Production hard gate:** do not approve extraction for production until Phase 0 has read a real protected file with the source unchanged. This does not block building the remaining product against clearly labelled safe fixtures; it blocks only the claim that the protected-file environment is proven.

### 14.1 Benchmark table — measure, never invent

V2 of this plan guessed performance targets. That was wrong. Fill these in from **your** files, then set targets:

```
Excel open time        rows/sec              best chunk size
peak RAM               peak temp disk        DuckDB settings
quality gate time      history update time   SQL sync time
JSON size              HTML size             dashboard open time
typical correction window (how far back do real corrections happen?)
```

---

## PART 15 — Testing

| Type | What it proves |
|---|---|
| **Unit** | column normalization · date conversion · hashing · chunk sizing · business key creation · history comparison · quality rule evaluation |
| **Integration** | Excel → DuckDB · DuckDB → history · DuckDB → SQL staging · analytics → JSON · JSON → HTML |
| **Golden** | Small known dataset, known answers (`total = 10,000`, `defect rate = 1.20%`, `top model = A`). If a number changes unexpectedly, the build fails. |
| **Performance** | Real files, real numbers (14.1) |
| **Failure** | Excel closes mid-run · missing column · duplicate key · disk low · SQL disconnect · cancel · crash before commit. Trusted history must survive all of them. |
| **Browser** | See 11.5 |

Mandatory reruns: load the same batch twice → identical row count and control total. Load day 1, then day 1+2 → only day 2 rows added. Change an old value → it appears after the next run within the lookback window.

---

## PART 16 — Risks, mistakes, and conflict resolution

### 16.1 Risk register

| Risk | Likelihood | Impact | Response |
|---|---|---|---|
| IT tightens DRM / blocks COM | Medium | High | Plans B/C/D (7.8); written approval in Phase 0 |
| Excel layout changes | High | Medium | Schema checks stop the run and name the column |
| Machine must stay logged in | High | Medium | Dedicated machine, or documented manual daily start |
| Data grows beyond memory | Medium | Medium | Adaptive chunking + Parquet partitions |
| Dashboard becomes a pretty toy nobody uses | Medium | High | Every report names the decision it supports (Part 4) |
| **Project stalls at 80%** | **High** | **High** | Phase gates + ship Phase 1 to a real user before anything else |

### 16.2 Common mistakes to prevent

```
cell-by-cell COM reads                     appending every daily file blindly
loading a whole workbook into memory       mapping columns by position
trusting UsedRange                         calculating KPIs in browser JavaScript
dumping raw history into JSON              assuming extraction success = correct data
running Excel COM as a Windows Service     saving protected data anywhere convenient
letting AI invent business rules           building a framework before one report works
```

### 16.3 Decision order — when two instructions conflict

```
1. User's latest explicit approval
2. This constitution and locked architecture baseline
3. Explicitly user-approved architecture/business decision records
4. Versioned report configuration and public data/API/UI contracts
5. Approved metric definitions and golden tests
6. Existing implementation
7. Agent preference, inference or assumption
```

This is the same authority order as 0.7, expressed for implementation work. Existing code is not automatically correct just because it already exists, and an agent-authored decision record without user approval cannot override the locked baseline.

### 16.4 Change control

Any proposed architecture change records: `Decision ID · Date · Problem · Evidence · Options considered · Proposed option · Lost capabilities · Risks · Equivalence tests · Rollback · User approval` in `docs/decisions/`. It becomes active only after explicit user approval.

Version these separately: report configuration · database schema · metric formulas · quality rules · JSON contract · dashboard template · application.

Never change a production schema by hand. Use ordered migrations.

---

## PART 17 — AI agent working protocol

### 17.1 Task format — every task is understood as

```
GOAL              What result is needed?
INPUTS            Which files, tables, config enter?
PROCESS           What happens?
OUTPUTS           What is produced?
VALIDATION        How do we prove it is correct?
FAILURE BEHAVIOR  What happens if it fails?
DONE WHEN         What objective test proves completion?
```

### 17.2 Work cycle

**Before coding:** read `PROJECT_SKILL.md` → run the map and architecture verifiers → confirm the locked dependency baseline → generate the task context pack → read the routed `report.toml`, `report_definition.md`, exact target files/contracts/tests → identify the exact layer and public contract/schema risk. Never begin with a broad repository inspection and never reopen the approved architecture merely for convenience.

**While coding:** smallest clean change · keep the ten layers separate · add or update tests · add a migration if the schema changes · version the contract if behaviour breaks · preserve security and idempotency.

**Before declaring done:** run focused tests → affected integration/golden/failure/browser/offline tests → verify rerun behaviour → update contracts/state/decisions/skill/memory when justified → refresh and verify map/manifest → run improvement scout → report exactly what changed and what was proven.

### 17.3 Safety checklist — all must be true before "done"

```
[ ] Source protection respected            [ ] Dashboard owns no trusted arithmetic
[ ] No cell-by-cell extraction added       [ ] JSON contract valid
[ ] Memory bounded                         [ ] Dashboard opens offline
[ ] Reruns cannot duplicate history        [ ] No unexpected network calls
[ ] New data cannot bypass quality         [ ] Failure cannot corrupt history
[ ] Formulas deterministic and tested      [ ] Logs and lineage sufficient
[ ] Schema/contract changes versioned      [ ] Documentation updated
[ ] Architecture verifier passes           [ ] All required dependencies bundled
[ ] No system Python/Node assumed           [ ] No silent reduced-capability fallback
[ ] Network-disabled runtime passes         [ ] No unapproved architecture deviation
```

---

## PART 18 — Open decisions (fill these in and the plan is final)

```
[ ] Which report is first?
[ ] Who is its business owner (the person who approves meaning)?
[ ] What does ONE ROW mean?
[ ] What is the business key?
[ ] Which column is the control total?
[ ] Which load mode?
[ ] Lookback window in days?
[ ] Deletion behaviour?
[ ] Where may extracted data be stored (IT approval)?
[ ] SQL Server: now, later, or never?
[ ] Is AI narrative allowed on this data?
[ ] Which decision must the dashboard support, and who makes it?
```

The default architecture and the rule “Windows + desktop Excel are the only external prerequisites” are already approved by this document. Do not ask the user to redesign or reconfirm them. Ask only if a measured incompatibility requires the formal deviation process in 0.7.

---

## The one-line build command

> **Define the business meaning, prove authorized extraction, build one tested vertical slice, then continue gate-by-gate until the complete offline product and release package pass acceptance.**

## Next action

Resolve only the blocking items in Part 18 for **one** report, then begin execution immediately. Build the first vertical slice, prove it, and continue through the remaining applicable phases without waiting for a new instruction after each passed gate.

If a production-only dependency is unavailable, finish the full offline application against safe representative fixtures, record the missing proof as `CONDITIONAL`, and give the user one exact validation action. A missing environment may limit production approval; it must not reduce the deliverable to a plan, mockup, or decorative interface.

---

## PART 19 — Universal skill operating contract

### 19.1 What this skill must accomplish

Use this skill to turn recurring Excel work into a secure, deterministic, auditable, offline web application that a non-technical employee can run without an editor or terminal. The result must cover the full cycle:

```text
upload files
→ validate and extract through authorized Excel access
→ stage and check data
→ update connected history safely
→ calculate trusted metrics
→ produce evidence-backed insights
→ build professional interactive dashboards
→ publish reports
→ retain weekly run history
```

The same skill also governs repairs, audits, performance improvements, new report onboarding, schema changes, dashboard changes, SQL Server integration, offline packaging, and project-map maintenance.

### 19.2 Work modes

Classify the task before changing anything:

| Mode | Use when | Minimum outcome | May modify? |
|---|---|---|---|
| **Discovery** | Sources or business rules are not understood | Evidence profile, assumptions, blockers, recommended first slice | Only safe analysis artifacts |
| **Prototype** | One sample exists and rules are incomplete | Working vertical slice, visible warnings, reconciliation | Yes, isolated and reversible |
| **Production** | Recurring business use or management reporting | Configured pipeline, tests, logs, recovery, two stable runs, handoff | Yes |
| **Repair** | Existing automation fails or drifts | Root cause, regression test, smallest safe fix, revalidation | Yes |
| **Audit** | User requests review/report only | Evidence-backed findings and priorities | No, unless separately authorized |
| **Evolution** | Add a source, metric, chart, report, or platform capability | Backward-compatible change or versioned migration, updated map | Yes |

Default to **Production** for recurring, financial, factory, management, customer-facing, or externally distributed reports.

### 19.3 The eight-question task contract

Every task must be rewritten internally into this contract before work begins:

```text
GOAL              What business outcome is required?
INPUTS            Which files, tables, configuration, and prior history enter?
PROCESS           Which exact pipeline layer changes?
BASELINE          Which locked components, bundled dependencies, and allowed prerequisites must remain unchanged?
OUTPUTS           Which files, screens, tables, events, and evidence are produced?
VALIDATION        What independent proof establishes correctness?
FAILURE BEHAVIOR  What remains safe and what does the user see if it fails?
DONE WHEN         Which objective gates must pass?
```

If any missing answer could change business meaning, security, architecture, or acceptance, stop and ask. Do not interrupt the user for cosmetic or reversible implementation choices.

### 19.4 Who owns each decision

| Decision or activity | Business owner | IT/security | Data/report owner | AI agent/developer | Operator |
|---|---:|---:|---:|---:|---:|
| Purpose and decision supported | **A/R** | C | C | I | I |
| Grain, business key, formula, threshold | **A** | I | **R** | C | I |
| Approved storage and retention | C | **A/R** | C | I | I |
| Excel access method and target machine | I | **A** | C | **R** | C |
| Pipeline, database, contracts, tests | I | C | C | **A/R** | I |
| Remove/replace a locked component or add a prerequisite | **A** | C | C | **R for proposal only** | I |
| Data-quality exception disposition | **A** | I | **R** | C | C |
| Run, review, safe rerun, escalation | I | I | C | C | **A/R** |
| Production acceptance | **A** | C | **R** | C | R |

`A` = accountable · `R` = responsible · `C` = consulted · `I` = informed.

### 19.5 Evidence-first behaviour

The agent must distinguish these clearly:

- **Observed:** directly measured from files, logs, database, UI, or tests.
- **Approved:** explicitly accepted by the named human owner.
- **Inferred:** a reversible technical conclusion supported by evidence.
- **Assumed:** unresolved; must be recorded and never promoted silently.
- **Unknown:** cannot be determined from available evidence.

Never present an assumption as a fact. Never invent a business key, target, tolerance, fiscal rule, currency rule, deletion rule, or savings figure.

### 19.6 Mandatory deliverables for a completed production build

```text
working source code               complete versioned offline release bundle
report definition                versioned configuration
database schema + migrations     metric SQL + quality SQL
dashboard JSON contract          offline HTML dashboard
one-page local web application   one-click setup/start/check/update/rollback scripts
unit/integration/golden tests    browser/offline verification
run logs + manifests             exceptions + reconciliation evidence
project skill + ranked map       manifest + current-state + governed memory
operations and recovery guide    acceptance record
```

All of these may live in the project package, but the user-facing experience remains simple.

---

## PART 20 — Token-saving project intelligence map

### 20.1 Purpose

The project map is a verified navigation layer for humans and AI agents. It prevents every new session from reading the whole repository while still protecting correctness. It must answer:

```text
WHAT exists?
WHY does it exist?
WHERE is it?
WHO owns its meaning?
WHEN should it change?
HOW does it work?
WHAT depends on it?
HOW is it tested?
WHAT must never break?
```

### 20.2 Required project-intelligence files

| File | Purpose | Maximum initial-reading rule |
|---|---|---|
| `PROJECT_SKILL.md` | Mandatory first-read project contract, compact map and router | Always first; keep concise and route detail |
| `.ai/READ_FIRST.md` | Exact commands, stop conditions, agent entry compatibility | Follow from skill; keep under 150 lines |
| `.ai/PROJECT_MAP.md` | Complete architecture, folder/file catalog, dependencies, task routes | Search/open relevant section after verification |
| `.ai/CONTEXT_PACK.md` | Generated task-ranked map slice within token budget | Read after `context`; regenerate per task |
| `.ai/CURRENT_STATE.md` | Working features, current version, pending decisions, known risks, next safe tasks | Always read |
| `.ai/CONTRACTS.md` | Public data, API, event, configuration, and UI contracts | Read only when a contract may be affected |
| `.ai/MAP_MANIFEST.json` | Machine-verifiable file list, hashes, versions, generation time | Verify by script; do not load fully unless debugging |
| `.ai/LESSONS.md` | Short reusable lessons accepted from real project work | Search by topic; do not read by default |
| `tools/project_map.py` | Refreshes and verifies map/manifest deterministically | Run before and after material changes |
| `AGENTS.md` | Universal pointer that enforces map-first behaviour | Short; never duplicate the master plan |
| `CLAUDE.md` | Claude entry pointer to the same rules | Short; never fork rules |
| `.clinerules` | Editor-agent entry pointer | Short; never fork rules |
| `.github/copilot-instructions.md` | Copilot entry pointer | Short; never fork rules |

All entry files point to the same source of truth. They must not contain separate, diverging copies of architecture rules.

### 20.3 Required `PROJECT_MAP.md` record for every important file

| Field | Meaning |
|---|---|
| Path | Exact relative path |
| Type | source, config, SQL, schema, test, UI, script, generated, runtime, vendor |
| Purpose | One-sentence job |
| Reads | Direct inputs and dependencies |
| Writes/returns | Outputs or side effects |
| Owner | Business, platform, data, UI, security, operations |
| Change when | Events that justify editing it |
| Do not change when | Common wrong reasons to edit it |
| Contracts affected | Config, schema, API, JSON, database, UI |
| Tests | Exact validating tests/gates |
| Risk | Low, medium, high, critical |

Generated, runtime, archive, database, cache, log, vendor, and large input files are catalogued as groups, not one row per generated file.

### 20.4 Mandatory task router

The map contains routes like these:

| Task | Read first | Usually edit | Must test | Must update |
|---|---|---|---|---|
| Excel cannot open | Excel adapter, source config, last failure event | Excel adapter/config only | protected-file fixture + cleanup test | map if behaviour changed |
| New/renamed column | report definition, mapping, schema contract | mapping/config/migration | drift + reconciliation + golden | contracts, current state, map |
| New KPI | metric registry, source fields, calendar rule | SQL + registry + JSON builder | unit + golden + dashboard | contract if public shape changes |
| New chart | dashboard JSON contract, chart selection rules | chart spec/template | browser + accessibility + print | map/UI contract |
| History duplicates | load-mode config, key rules, history SQL | history engine/migration | same-input rerun + correction test | decision record + lessons |
| SQL Server outage | sync queue, retry policy | connector only if defect exists | disconnect/retry/reconcile | current state if limitation changes |
| Slow large file | profile, projection, chunk logic | extractor/config | representative benchmark | performance evidence + map |
| Text/UI change | language file, component, accessibility rules | UI assets | keyboard + responsive + browser | map only if structure changes |

### 20.5 Freshness enforcement

`PROJECT_TOOL.bat map verify` must fail when any of these occurs:

- an important file is added but not catalogued;
- a catalogued file is removed or moved;
- a tracked file hash changes without a refreshed manifest;
- a contract/schema version changed but the map still names the old version;
- `CURRENT_STATE.md` claims a feature or test result that evidence does not support;
- an entry instruction points to a missing or renamed file.

The refresh command must:

1. scan only approved project paths;
2. ignore inputs, outputs, archives, databases, logs, caches, runtime binaries, and vendor contents while recording those folders as groups;
3. calculate hashes for source-of-truth files;
4. compare files with the catalog;
5. preserve human descriptions;
6. generate a clear diff for added, removed, moved, and changed files;
7. update the manifest only after the agent reviews the diff;
8. run verification again.

### 20.6 Safe reading boundary

The map must never be used to justify editing an unread file. The mandatory boundary is:

```text
verified map
→ identify target files
→ read target files completely
→ read their direct public contracts and relevant tests
→ make the smallest safe change
```

Only expand further when imports, call sites, schemas, or test failures provide evidence that another dependency is involved.

### 20.7 Map quality gate

The map is accepted only when a new agent, given only the four initial files in 0.2 and one realistic task, can correctly identify:

- the responsible component;
- the files to read and edit;
- the contracts at risk;
- the tests to run;
- the expected failure behaviour;
- the map fields to update.

If the agent must search the whole repository to answer these, the map has failed.

### 20.8 Required project-native repository intelligence engine

`tools/project_map.py` is a stable wrapper around a small project-native engine under `tools/project_intelligence/`. It combines two proven ideas:

- **Aider-style structural ranking:** parse definitions and references, build a dependency graph, and use personalized PageRank to select the most relevant symbols/files within a token budget.
- **repo-map-style durable documentation:** keep a Markdown tree, structural JSON, per-file summaries, maintenance notes, SHA-256 cache, ignore rules, and incremental refresh for changed files.

Do not copy either project blindly. Implement and test the minimum local capability the project needs, keep license notices for any reused code, and preserve the security boundary below.

```text
tools/project_intelligence/
    inventory.py        Git-aware, symlink-safe file inventory and exclusions
    languages.py        supported-language and generated/vendor detection
    symbols.py          Tree-sitter/AST definitions, signatures, imports, references
    graph.py            file/symbol dependency graph
    rank.py             task-seeded personalized PageRank and token budgeting
    summaries.py        deterministic purpose/API/risk/test summaries
    cache.py            SQLite cache by relative path + content hash + schema version
    render.py           stable Markdown/JSON/context-pack output
    verify.py           freshness, entry-pointer, contract and orphan checks
    cli.py              refresh, verify, context, explain, doctor commands
```

Implementation requirements:

1. Use Git tracked files when Git is present; otherwise use a symlink-safe walk.
2. Apply built-in exclusions plus root `.gitignore`; prune excluded directories before reading them.
3. Never inspect or summarize secrets, protected input data, databases, archives, outputs, logs, runtime binaries, dependency folders, caches, or generated build files.
4. Parse supported code with packaged Tree-sitter grammars or a language-native parser; fall back to headings/imports/signatures for plain text and configuration.
5. Cache by repository-relative path, SHA-256, parser version, and summary-contract version. Unchanged files are not reparsed.
6. Preserve approved human descriptions in a sidecar/marked human section. Generation may replace only clearly marked generated sections.
7. Produce stable ordering and atomic writes so a refresh does not create meaningless diffs.
8. Detect add, delete, rename, import/contract/test changes and report them before accepting a refreshed manifest.
9. The first build may inventory the approved repository once. Later refreshes must use Git changes or file metadata to hash and parse only candidates, plus directly affected dependants.
10. The engine is development intelligence only. Production modules under `app/` and `web/` must never import it, and application failure must never depend on it.

### 20.9 Mandatory map commands

The wrapper must expose these stable commands even if internal modules change:

```text
PROJECT_TOOL.bat map doctor
PROJECT_TOOL.bat map verify
PROJECT_TOOL.bat map refresh --review
PROJECT_TOOL.bat map context --task "<plain task>" --budget 4000
PROJECT_TOOL.bat map explain --path app/data/history.py
PROJECT_TOOL.bat map changed --base <approved-git-ref>
```

| Command | Required result |
|---|---|
| `doctor` | Parser/cache/entry-file readiness; no source disclosure |
| `verify` | Exit non-zero on stale map, missing pointer, untracked important file, or contract mismatch |
| `refresh --review` | Preview semantic diff, preserve human notes, then atomically update map + manifest |
| `context` | Create `.ai/CONTEXT_PACK.md` with only the highest-value task context within budget |
| `explain` | Show why a file exists, dependants, contracts, tests, risk, and recent map change |
| `changed` | Route a change set to affected tests, contracts, docs, state, and map records |

`RUN_TESTS.bat`, the local pre-commit gate, and any available CI must run `verify`. A material change cannot be committed or released while it fails.

### 20.10 Task-ranked context pack

The exhaustive human map and the prompt-sized context pack are different artifacts:

```text
.ai/PROJECT_MAP.md    complete compact catalog; searched or opened by section
.ai/CONTEXT_PACK.md   regenerated for the current task; safe to load into the agent
```

Ranking starts from task words, named files, changed files, recent failures, public contracts, and tests. It then boosts direct imports/callers/callees and high-centrality symbols. Generated/vendor/runtime/data paths receive zero rank. The pack contains:

```text
task interpretation · relevant architecture slice · ranked files and reasons
important signatures · direct dependencies · contracts at risk · tests to run
invariants · known decisions/lessons · unresolved questions · token estimate
```

Default budget is 4,000 tokens; allow 1,000–8,000 by task complexity. Exceeding the budget requires a written reason and one-boundary expansion, never a silent whole-project dump.

### 20.11 Privacy-safe adaptation of external map ideas

The referenced `cyanheads/repo-map` can send eligible full source files to an external model. That behaviour is **forbidden by default** here because the project may contain company logic or sensitive structures. Reuse only safe design ideas: exclusions, structural metadata, content-hash cache, incremental updates, and structured summaries.

Default summaries are deterministic and local. Optional AI enrichment is allowed only when IT and the data owner approve the exact provider and disclosure scope; prefer an approved local model, send the smallest approved excerpt, record provenance, and require human review before replacing an accepted summary.

---

## PART 21 — Mandatory learning and self-update cycle

### 21.1 When learning is captured

Run this cycle after every completed feature, defect fix, performance benchmark, production incident, schema change, mapping approval, dashboard redesign, or recovery exercise.

### 21.2 What qualifies as reusable learning

Capture only knowledge that will change a future agent's decision or prevent repeated work:

- a confirmed project-specific business rule;
- a proven source-file behaviour or DRM limitation;
- a real performance result and the environment that produced it;
- a recurring defect and its regression test;
- a rejected approach and why it failed;
- a durable file/contract dependency;
- an operator recovery lesson;
- an accessibility or usability finding from a real user;
- a security restriction approved by IT.

Do not capture chat history, temporary guesses, verbose work logs, raw sensitive values, or facts already clear from code/contracts.

### 21.3 Completion update sequence

Before a task can be marked done, the agent must:

```text
1. prove the implementation with the required tests and evidence;
2. update configuration/schema/contract versions when applicable;
3. update the relevant decision record;
4. update `.ai/CURRENT_STATE.md`;
5. add concise reusable learning to `.ai/LESSONS.md` when justified;
6. update the project-local copy of this skill if the operating method changed;
7. refresh `.ai/PROJECT_MAP.md` and `.ai/MAP_MANIFEST.json`;
8. run `PROJECT_TOOL.bat map verify`;
9. report what changed, what passed, and what remains unapproved.
```

### 21.4 Skill update rule

Update the skill itself only when the learning is reusable across future Excel-intelligence projects or changes a mandatory workflow. Keep client-specific business rules in the report definition, configuration, decisions, and project map—not in the universal skill.

Every skill update must remove obsolete advice, avoid duplicated rules, preserve the quick-start section, and remain compatible with local command-line agents, editor extensions, and web agents.

A learning/skill refresh may clarify or strengthen the locked architecture but may not remove/replace a required component, add a prerequisite, or weaken an acceptance gate. Such a proposal follows 0.7 and remains inactive until explicitly approved.

### 21.5 Anti-drift release gate

A material code change with no map update must fail the project test suite. A map update with no matching code/contract evidence must also fail review. Code, tests, contracts, state, and map move together as one change set.

### 21.6 Project memory with an admission gate

Project memory is durable engineering evidence, not a chat transcript. Store it in:

```text
.ai/MEMORY.jsonl        append-only facts/decisions/lessons with stable IDs
.ai/LESSONS.md          concise accepted lessons, grouped by topic
.ai/OPPORTUNITIES.md    deduplicated improvement register and disposition
.ai/CURRENT_STATE.md    latest proven operational truth
docs/decisions/         detailed architecture/business decision records
```

Every memory record contains:

```json
{
  "id": "MEM-...",
  "type": "decision|lesson|constraint|benchmark|incident|preference",
  "statement": "",
  "status": "candidate|validated|superseded|rejected",
  "source": "file/test/run/user approval",
  "recorded_at": "",
  "owner": "",
  "confidence": "verified|approved|inferred",
  "affected_paths": [],
  "supersedes": null,
  "review_on": null
}
```

Admission rules:

1. Store only knowledge that changes a future decision or prevents repeated work.
2. Require a source and date; business meaning requires a named approval owner.
3. Never store secrets, raw sensitive rows, hidden reasoning, temporary guesses, or duplicated code facts.
4. Mark conflicts instead of overwriting history. New accepted records supersede old IDs explicitly.
5. Age time-sensitive constraints and benchmarks; revalidate them on `review_on` or when the affected component changes.
6. `tools/project_memory.py validate` must fail malformed, source-free, conflicting active, or orphaned path references.

### 21.7 Mandatory improvement scout

Every meaningful task ends with a short improvement scan. The agent must suggest improvements continually **without distracting from the requested work or making unapproved changes**.

Run:

```text
PROJECT_TOOL.bat memory suggest --task "<completed task>" --max 3
```

Each suggestion must be evidence-based and contain:

```text
stable opportunity ID · observed evidence · proposed improvement
business value · effort · risk · dependencies · proof of success
recommended timing: now / next / later
```

Rules:

- Maximum three suggestions after a task; zero is valid when no useful evidence exists.
- Finish and prove the user's requested task before proposing optional scope.
- Deduplicate against `.ai/OPPORTUNITIES.md`.
- Track `suggested`, `accepted`, `deferred`, `rejected`, and `done` states.
- Never repeat a rejected/deferred suggestion unless new evidence materially changes it.
- Prioritize correctness, data trust, operator effort, recovery, performance, and decision value before decorative features.
- Do not implement an optional suggestion without user approval unless it is necessary to meet an existing mandatory gate.

---

## PART 22 — Offline web application product specification

### 22.1 Product promise

The employee must not need an editor, terminal, database tool, configuration editor, or file-system inspection. The local web application is the complete work surface.

```text
رفع الملفات → متابعة التنفيذ → لوحة تفاعلية → تقارير → سجل الأسابيع
Upload files → Follow progress → Interactive dashboard → Reports → Weekly history
```

### 22.2 One-page application shell

The product is one responsive single-page work surface, not a collection of disconnected pages. Normal work happens on `/` without a full-page reload. A compact side rail or top command bar jumps to sections; upload, history, quality, support, and settings open as anchored sections, drawers, or focused dialogs while preserving the current filters.

| One-page region | User question answered | Required capabilities |
|---|---|---|
| **Command header** | What report, period, data state, and quality am I viewing? | report selector, freshness, PASS/WARNING/FAIL, language, theme, help |
| **Sticky filter ribbon** | Which slice and comparison do I want? | period, compare mode, product/model/process/line filters, active chips, reset |
| **Executive first viewport** | What happened and should I act now? | 4–6 KPIs, target/previous comparison, partial-data warning, top verified insight |
| **Performance story** | What changed and what explains it? | trend, variance, Pareto, heatmap/distribution, insight slides with evidence |
| **Action zone** | What should we investigate or do next? | ranked contributors, owner/status where available, evidence links |
| **Data and run zone** | How do I add or replace the next approved source? | file picker/drop, role detection, readiness, start, durable progress, safe retry |
| **History and quality zone** | Can I trust it and what changed between runs? | weeks/runs, hashes, completeness, reconciliation, schema differences, last good output |
| **Support and exports** | How do I recover or take the result with me? | plain-language recovery, standalone HTML, approved exports, manifest, support code |

The first viewport must answer the management question without scrolling. The rest of the same page forms a clear top-to-bottom evidence story. Deep technical details remain collapsed by default. Browser Back/Forward and a copied local URL may restore non-sensitive filter state, but never expose secrets or raw row values.

### 22.3 Upload behaviour

The upload page must:

- accept click, drag/drop, and file picker;
- identify expected source role from configured pattern and workbook structure;
- show file name, size, modified time, role, period, and duplicate/hash state;
- reject unsafe extensions, zero-byte files, partial copies, unexpected files, and path traversal;
- wait until file size and modified time are stable across two checks;
- copy to a run-specific intake folder without modifying the source;
- allow the user to open a protected workbook in Excel manually when required, then retry;
- never upload data to the internet;
- make missing required sources obvious before processing begins.

### 22.4 Progress is an event stream, not animation

The UI receives durable events containing:

```json
{
  "run_id": "RUN-20260816-001",
  "sequence": 18,
  "time": "2026-08-16T10:42:08+03:00",
  "stage": "EXTRACTING",
  "status": "RUNNING",
  "percent": 36,
  "message": "Reading Sheet / rows 12001–13000",
  "rows_done": 13000,
  "rows_total": 38017,
  "warning_count": 0,
  "action_required": false
}
```

Use server-sent events through the required local API after compatibility tests pass; if a verified renderer limitation blocks SSE, poll the same API by `run_id` and last `sequence`. Polling is a delivery fallback, not permission to remove the server. Events must be stored before delivery so browser refresh or temporary closure never loses progress.

### 22.5 User-action states

When a person must act, the run changes to `WAITING_FOR_USER`, preserves its checkpoint, and presents one direct instruction, such as:

```text
Open “ProcessDefect_Result.xlsx” in Microsoft Excel, confirm you can see the data,
leave it open, then press Retry.
```

The application must not disguise a required user action as a technical failure.

### 22.6 Dashboard interaction

Required filters depend on the report but normally include period/week, factory division, product, model/project, process, line, work group, and defect family. Filters must:

- show active state clearly;
- provide searchable single-select or multi-select controls chosen by field cardinality;
- support `Current`, `Previous period`, `Target`, and approved custom comparison modes;
- show the selected comparison beside every affected KPI/chart, never only in a hidden tooltip;
- have a one-click reset;
- update all affected charts and tables consistently;
- allow chart selection to cross-filter the page, with a visible removable filter chip;
- preserve filter state while opening evidence, history, upload, quality, or support surfaces;
- preserve the displayed control total;
- never recalculate trusted business logic in the browser;
- offer drill-through from KPI → contributor → source lineage when data policy allows.

The operator may change **the view**, comparison, filter, and approved scenario—not trusted source records or metric formulas. A data correction uses a corrected source file, an approved mapping/configuration change, or a governed exception workflow with audit history. Never add spreadsheet-like silent editing to trusted data.

The page must distinguish:

```text
global filters      affect every compatible visual
section filters     affect one clearly bounded analysis region
cross-filters       created by selecting a chart mark
comparison state    defines the baseline but does not hide current values
```

All filters are applied through one typed filter-state object. No component keeps a private contradictory copy. The server returns approved pre-aggregations for supported filter grains; the browser may select among them but never invent a new KPI formula.

### 22.7 Reports and history

Every successful run produces immutable run evidence and a separately published “latest approved” dashboard. A failed run never replaces the latest approved output.

Weekly history must show:

```text
week · data date · source files · source hashes · rows · inserted · updated
unchanged · rejected · quality · completeness · dashboard · run duration
```

The user may safely rerun an identical input; the result must show zero unintended duplicates.

### 22.8 Non-technical error design

Every error screen contains only:

1. what went wrong in plain language;
2. whether trusted history and the last dashboard remain safe;
3. the one next action;
4. a support code and expandable technical detail.

Never expose a raw stack trace as the primary message.

### 22.9 Language, accessibility, and visual behaviour

- Arabic and English use the same data contract; text lives in language dictionaries.
- Arabic uses correct right-to-left layout, not only translated words.
- Default body text is at least 16 px; important numbers are materially larger.
- Keyboard navigation, visible focus, semantic labels, text alternatives, and screen-reader summaries are mandatory.
- Text contrast targets WCAG 2.2 AA; meaning never depends on colour alone.
- Touch/click targets are comfortably sized; dense controls remain usable at 125–150% Windows scaling.
- Light, dark, responsive, and print layouts are required.
- Motion is subtle and disabled when the user prefers reduced motion.

### 22.10 Local security boundary

Bind the application **only** to IPv4 loopback `127.0.0.1`, never to the office network. Reject `0.0.0.0`, `::`, machine hostnames, LAN addresses, and forwarded/proxy exposure. This is a single-user desktop boundary, not a shared deployment mode.

The local API must:

- run as the same standard interactive user as Excel and the renderer, with no elevation or installed service;
- generate a cryptographically random per-launch secret and require it on state-changing/API requests using a launch-scoped header or equivalent protected handshake;
- validate `Host` and `Origin`, allow only the exact current loopback origin(s), disable wildcard CORS and credentials-to-wildcard combinations, and reject unexpected browser origins;
- use `SameSite=Strict` and appropriate secure cookie attributes when cookies are used; never place a reusable secret in logs, output files, or browser history;
- apply request, upload, body, file-count, extension/signature, and rate/concurrency limits;
- block arbitrary path access, canonicalize/allow-list approved output paths, use per-run folders, and keep secrets outside the package;
- disable developer documentation/debug endpoints in the employee release unless explicitly required and protected;
- start only after integrity verification and stop cleanly with the application.

Corporate endpoint controls may still block a process or loopback socket. That is an environmental compatibility failure to diagnose and document—not permission to request administrator rights, add firewall exclusions, bind to the LAN, or delete the local API. Shared access or SQL Server credentials require explicit configuration and a separate security approval.

### 22.11 Motion, slides, and presentation mode

The web app must feel polished and alive while remaining fast and serious:

- animate only state change, hierarchy, and cause/effect;
- use 160–240 ms UI transitions and 250–450 ms chart transitions;
- stage the first dashboard reveal once, in reading order, within 700 ms total;
- morph or update existing marks on filter change instead of replaying all entrance effects;
- never bounce, spin, flash, pulse continuously, or animate decorative backgrounds;
- stop all non-essential motion under `prefers-reduced-motion: reduce`;
- keep progress animation tied to durable events—never fake activity;
- maintain 60 fps on the target PC and avoid layout shifts.

Provide an optional **Insight Story** presentation mode inside the same page. It is a manual previous/next slide deck generated from verified insight objects:

```text
1 executive result
2 trend and comparison
3 largest contributors / Pareto
4 concentration or stability view
5 actions, owners, risks, and data-quality caveat
```

Each slide shows one message, the evidence chart, period/filter context, and source/run reference. No autoplay by default; pause when the window loses focus; keyboard and touch controls are required; exporting or printing must preserve the message without animation.

---

## PART 23 — Best-practice technology choices

Versions below are the validated baseline for this plan, not permanent truth. Lock exact versions in the delivered package, record licenses and hashes, and review upgrades deliberately.

### 23.1 Default local stack

| Need | Locked default | Why | Deviation may be proposed only when; explicit user approval still required |
|---|---|---|---|
| Windows release runtime | PyInstaller one-folder build containing a private pinned CPython 3.12 x64 runtime | User needs no system Python installation, package manager, editor, terminal, or internet; faster and easier to diagnose than one-file extraction | Enterprise installer/distribution is approved or target policy rejects bundled executables |
| Employee repair payload | Sealed/hash-verified copy of the exact approved release components | Restores damaged files without installing packages or rebuilding on the employee PC | Enterprise software repair channel replaces it |
| Offline build/update kit | Pinned CPython + hash-locked wheelhouse, kept outside the end-user runtime path | Allows developers/agents to rebuild and verify without internet | Only a signed enterprise build pipeline may create releases |
| Excel control | `pywin32` with a dedicated Excel desktop process; attach fallback | Direct authorized COM access and fast block reads | A documented upstream export replaces Excel extraction |
| Ordinary unprotected `.xlsx` | `openpyxl` read-only for discovery/tests only | Convenient structural inspection | Exact Excel calculation/refresh/fidelity is required |
| Local analytical database | DuckDB 1.4.x, one coordinated writer | Fast analytical SQL, embedded file, Parquet support | Concurrent multi-service writes require a server database |
| Recovery archive | Parquet through DuckDB | Compressed columnar history and rebuild | Policy prohibits extracted archives |
| Central database | SQL Server through Microsoft `mssql-python` | Enterprise sharing, bulk copy, Windows/Azure authentication | SQL Server is not needed or another approved connector is mandated |
| Configuration | TOML + JSON Schema | Human-readable configuration with machine validation | Central configuration service is approved and justified |
| Trusted calculations | Versioned DuckDB/SQL Server SQL | Auditable, deterministic, testable | A calculation cannot be expressed safely in SQL; document exception |
| Local server | FastAPI + Uvicorn + Pydantic + approved multipart upload parser, fully bundled; standard-user process bound only to `127.0.0.1` | Typed contracts, uploads, durable run APIs, streaming progress, validation, and testability justify the packaged cost; it is an internal application component, not an external server | A proven replacement meets every contract with less risk and receives explicit user approval |
| Charts | Apache ECharts 6.x bundled locally | Strong interactive charts, accessibility options, canvas/SVG | A company-approved visualization library is required |
| Front end | Semantic HTML, modern CSS, plain JavaScript modules | Small, durable, offline, easy to audit | Product complexity proves a framework is necessary |
| Browser verification | Playwright with its pinned local browser in the project/QA kit; verify the approved Windows renderer separately | Catches JavaScript, rendering, accessibility, responsive, and network failures without assuming a developer browser | Target policy blocks browser automation |
| Logs | JSON Lines + database system tables | Human-readable and queryable | Central logging is approved |
| Packaging | ZIP containing a PyInstaller one-folder release, source/update kit, hash-locked wheelhouse, local assets, SBOM, notices, launchers, and checksums | One-copy offline use plus reproducible repair/update | Enterprise software distribution replaces it |
| Project intelligence | Local Tree-sitter/AST parsers + SQLite cache + project-native ranker | Aider-style task relevance and repo-map-style incremental documentation without source disclosure | Repository is too small to justify it; keep the same entry contract |

### 23.2 Do not start with unnecessary platform complexity

Do not introduce Spark, Kafka, Kubernetes, Airflow, distributed microservices, a cloud database, a cloud dashboard, or a JavaScript framework merely because it is popular. Add complexity only after measured scale, concurrency, governance, or team needs prove the smaller architecture insufficient.

### 23.3 DuckDB operating rules

- Use one coordinated writer process per database file.
- Multiple read connections inside the same application are acceptable; avoid uncontrolled cross-process writers.
- Load in batches or use bulk import/appender patterns, not one SQL insert per row.
- Push projection, filtering, joining, and aggregation into SQL.
- Configure `memory_limit`, `temp_directory`, `max_temp_directory_size`, and `threads` from measured workloads.
- Run schema changes through ordered migrations inside transactions.
- Keep raw, clean, quality, analytics, and system schemas separate.
- Checkpoint and back up only at safe boundaries.

### 23.4 SQL Server operating rules

```text
trusted local change set
→ bulk copy into SQL staging
→ validate row count, keys, and totals
→ transactional merge/upsert
→ independent reconciliation
→ mark sync complete
```

A network failure creates a durable pending-sync item. It does not fail the already valid local report and never causes Excel to be extracted again.

### 23.5 Excel COM operating rules

- Use an interactive logged-in Windows session with Microsoft Excel installed.
- Prefer a dedicated hidden Excel instance owned by the run.
- Open source read-only, disable link updates, and never save it.
- Snapshot and restore every Excel setting changed by the automation.
- Read `Range.Value2` rectangular blocks and project only required columns.
- Determine real bounds from configured tables/ranges or bounded searches; do not trust `UsedRange` blindly.
- Release workbook, worksheet, range, and application objects in `finally` blocks.
- Close only the Excel process created by the run. **Never kill all `EXCEL.EXE` processes**, because some may belong to the user.
- In attach mode, match the exact full path and never close the user's workbook.
- Use timeouts, checkpoints, and a recoverable `WAITING_FOR_USER` state for DRM prompts.

### 23.6 Offline dependency discipline

The package contains:

```text
ready-to-run one-folder executable and private runtime
source/update kit and locked Windows wheels/packages
local JavaScript/chart library
license notices
software bill of materials (SBOM)
SHA-256 manifest
setup self-test
employee repair script that restores exact release files from the sealed repair payload
```

No run command may download a package, browser, DuckDB extension, font, icon, script, map, telemetry asset, or chart asset. Front-end assets are built before release; Node.js and package managers are not runtime requirements. Block or detect all unexpected network requests during browser verification.

Required safeguards:

```text
pin direct and transitive versions
record SHA-256 for every distributed binary/wheel/asset
developer/agent rebuild installs only from wheelhouse with --no-index --find-links and hash checking
employee repair restores sealed release files and never invokes pip
disable DuckDB extension autoinstall/autoload; package and load only approved extensions
verify licenses and third-party notices
scan the final release, not only source requirements
prove clean-machine start with network disabled
```

The release build is `onedir`, not `onefile`, unless measured evidence proves one-file is better on the target PCs. One-folder avoids temporary self-extraction, starts faster, is easier for antivirus review, and makes missing assets diagnosable. Publish atomically by building to a new version folder, verifying it, then switching the `current` pointer/launcher; never patch a running folder in place.

### 23.7 Upgrade policy

Upgrade one layer at a time. Record the reason, old/new versions, security effect, data-contract effect, migration, rollback, and test evidence. Never combine runtime, database, extraction, and dashboard-library upgrades in one uncontrolled change.

### 23.8 Locked component baseline

The capability and delivery method below are mandatory. Exact supported patch versions are pinned after compatibility and security testing; changing a version is an upgrade, while removing/replacing a component is an architecture deviation requiring explicit user approval.

| Component | Capability contract | Delivery | Forbidden substitute/fallback |
|---|---|---|---|
| Windows 10/11 x64 | approved desktop operating environment | external prerequisite | unsupported legacy Windows or server/service session |
| Microsoft Excel desktop | authorized protected-file opening | external prerequisite | attempting to bypass protection or parsing protected files with ordinary readers |
| CPython private runtime | application execution | bundled in the one-folder app | system Python, `py`, Microsoft Store, or first-run download |
| Native runtime DLLs required by packaged wheels | low-level execution of the exact build | bundled or explicitly proven in the approved Windows image, with offline redistributable when needed | assuming the build PC's Visual C++/DLL state exists everywhere |
| `pywin32` + support binaries | controlled Excel desktop automation | bundled and smoke-tested | PowerShell/VBA-only redesign or cell-by-cell automation |
| DuckDB | trusted local history and analytical SQL | bundled library/binary | CSV/JSON files, browser storage, Excel sheets, or in-memory-only history |
| Parquet capability | approved recovery/rebuild archive | bundled through the verified DuckDB build | unversioned CSV dump or no recovery archive when policy permits archive |
| FastAPI + Uvicorn + Pydantic + multipart parser | typed loopback API, validated uploads, progress and local web service | bundled in the app | static HTML-only product, ad-hoc file server, or batch-script workflow |
| Standard-user loopback transport | renderer-to-application control/data boundary, lifecycle and security | bundled process; `127.0.0.1`; `asInvoker`; OS-selected/bounded high port | LAN/public bind, `file://` application, direct browser access to COM/DB/files, Windows Service, IIS/HTTP.sys deployment, firewall/URL-reservation change, or administrator requirement |
| Apache ECharts | professional interactive charts and accessible summaries | pinned local vendor asset | CDN, online chart service, screenshot-only charts, or reduced chart set |
| HTML/CSS/JavaScript modules | one-page responsive application | bundled local assets | online framework/runtime or Excel-based UI |
| JSON Schema/TOML/config validation | machine-checked contracts | bundled | unchecked configuration or hard-coded report rules |
| PyInstaller specification/hooks | reproducible self-contained Windows release | build kit + verified one-folder output | source-only delivery or requirement for user installation |
| Hash-locked wheelhouse | offline developer/agent rebuild | bundled in project/update kit | employee runtime repair, live `pip`, package index, or unverified copied environment |
| Browser renderer | supported Edge/WebView2 supplied by the approved Windows image; package the official offline standalone/fixed runtime when that image cannot guarantee it | proven as part of the Windows baseline or included offline | online bootstrapper or “the browser is probably installed” |
| SQL Server connector | central synchronization when enabled | bundled with native prerequisites and tests | silently disabling synchronization or using an unapproved driver |
| Project map/memory toolchain | agent onboarding and token control | bundled in project/update kit, isolated from user runtime | deleting the map/skill to reduce package size |

Anything imported, dynamically loaded, rendered, migrated, or executed by the final application must appear in the release bill of materials and checksum manifest. A component listed in a requirements file but absent from the final app is missing.

For a strictly disconnected target, prefer a packaged WebView2 Fixed Version or another user-approved bundled renderer. Corporate-managed Evergreen WebView2 is acceptable only when it is formally part of the approved Windows image; the application itself never bootstraps, downloads, or updates it.

### 23.9 Machine-readable implementation baseline

Create `IMPLEMENTATION_BASELINE.lock.json` and version it with the project. Minimum shape:

```json
{
  "schema_version": 1,
  "baseline_version": 1,
  "approved_external_prerequisites": [
    "Windows 10/11 x64",
    "Microsoft Excel desktop",
    "interactive logged-in user session"
  ],
  "forbidden_runtime_requirements": [
    "internet",
    "administrator_or_elevation",
    "windows_service_or_iis",
    "firewall_or_url_reservation_change",
    "system_python",
    "system_node",
    "pip",
    "npm",
    "vscode",
    "terminal_for_normal_use",
    "cdn"
  ],
  "required_components": [
    {
      "id": "python-runtime",
      "capability": "application execution",
      "delivery": "bundled",
      "required_paths": [],
      "version": "PIN_AT_BUILD",
      "sha256": "POPULATE_FROM_RELEASE",
      "smoke_test": "app --self-test runtime"
    }
  ],
  "optional_components": [],
  "approved_deviations": []
}
```

The real file contains one record for every row in 23.8, exact release paths, versions, hashes, license reference, owning test, and enabled/disabled reason. `approved_deviations` may contain only a decision ID with explicit user approval; an agent cannot self-authorize it.

### 23.10 Architecture verifier

`PROJECT_TOOL.bat architecture verify --release <folder>` must fail the build when any of these is true:

```text
required component/path/import/asset missing
version or hash differs from the baseline/release manifest
SBOM and actual bundle disagree
license/notice missing
HTML/CSS/JS contains an unapproved remote URL, CDN, font, icon, telemetry or API
batch/PowerShell/Python runtime path invokes live pip/npm/curl/download/bootstrapper
system Python, Node.js, Git or developer PATH is required
DuckDB can autoinstall/autoload an unapproved extension
application silently chooses static/Excel-only/reduced mode after a dependency failure
launcher starts source code instead of the verified private runtime
enabled SQL mode lacks its connector/native prerequisites
project skill/map/update kit is missing from the complete project package
loopback API is absent, bypassed, or replaced by direct renderer access to Excel/COM, DuckDB, filesystem, or browser storage
server binds to 0.0.0.0, ::, a hostname/LAN/public interface, or privileged/default web ports 80/443
launcher, manifest, script, or code requests requireAdministrator/highestAvailable, runas, service installation, IIS, HTTP.sys URL reservation, registry/system-folder writes, or firewall changes
release cannot start, bind, health-check, process a fixture, and stop under a representative standard non-admin account
origin/host/launch-secret protections or local transport lifecycle evidence are missing
```

The network scanner examines executable code, launchers, runtime HTML/CSS/JS, configuration and generated reports. Documentation/reference hyperlinks are allowed as text and must not be mistaken for runtime network calls; they are never opened automatically.

Required commands:

```text
PROJECT_TOOL.bat architecture verify --baseline
PROJECT_TOOL.bat architecture verify --source-scan
PROJECT_TOOL.bat architecture verify --release release/current
PROJECT_TOOL.bat architecture verify --simulate-clean-pc
PROJECT_TOOL.bat architecture verify --simulate-missing <component-id>
PROJECT_TOOL.bat architecture verify --standard-user-loopback
```

The verifier writes `release/ARCHITECTURE_EVIDENCE.json` with every component, actual path/version/hash, test result, and any approved deviation, plus `release/LOCAL_TRANSPORT_EVIDENCE.json` with user identity class, manifest level, bound address/port, listener process ownership, rejected non-loopback/origin probes, lifecycle result, and proof that no service/firewall/URL reservation was created. It exits non-zero on failure and is called by `RUN_TESTS.bat`, `BUILD_RELEASE.bat`, `VERIFY_OFFLINE.bat`, the map completion gate, and release acceptance.

### 23.11 Fail-closed component policy

When a required component is missing, corrupt, incompatible, or blocked:

```text
stop startup or the affected operation safely
preserve source files, trusted history, and last approved dashboard
show PACKAGE_COMPONENT_MISSING/BLOCKED with the exact component
offer employee repair only from the sealed verified release-repair payload
record evidence and keep the current approved release unchanged
```

Never respond by removing the capability, changing the database, using Excel for calculations/history, producing static HTML only, or declaring a reduced product “good enough.” A different implementation may be proposed only through 0.7 and must prove full contract equivalence.

### 23.12 Build environment versus employee runtime

These are separate boundaries:

| Boundary | Internet allowed? | Package tools allowed? | Result |
|---|---:|---:|---|
| Approved build machine while preparing the release cache | Only when company policy permits | Yes, controlled and logged | Downloads verified inputs once, pins versions/hashes/licenses |
| Reproducible release build | No after cache preparation | Local tools and wheelhouse only | Produces the one-folder app, manifests and ZIP |
| Employee runtime | No | No `pip`, `npm`, installer, compiler, editor or terminal | Starts and runs the complete product |
| Employee offline repair | No | Packaged repair launcher only | Verifies/restores exact files from the sealed release-repair payload |
| Developer/agent offline update | No | Private build runtime + local wheelhouse | Rebuilds, tests and packages a new version; never mutates the running release in place |

The agent must never solve a runtime packaging problem by moving build work onto the employee's PC.

---

## PART 24 — Canonical project and file map

Use this as the standard starting structure. The generated `.ai/PROJECT_MAP.md` must describe the actual project, including any justified differences.

```text
excel-intelligence/
├── AGENTS.md                         universal map-first instruction
├── CLAUDE.md                         Claude pointer to the same instruction
├── .clinerules                       Cline pointer to the same instruction
├── .github/copilot-instructions.md   Copilot pointer to the same instruction
├── PROJECT_SKILL.md                   mandatory first-read project skill + compact map/router
├── IMPLEMENTATION_BASELINE.lock.json machine-enforced component/prerequisite contract
├── .ai/
│   ├── READ_FIRST.md                 90-second start and task router
│   ├── PROJECT_MAP.md                architecture + exact file catalog
│   ├── CONTEXT_PACK.md               generated task-ranked prompt context
│   ├── CURRENT_STATE.md              proven status + pending decisions
│   ├── CONTRACTS.md                  public contracts and versions
│   ├── LESSONS.md                    concise reusable learning
│   ├── OPPORTUNITIES.md              improvement register + accepted/deferred status
│   ├── MEMORY.jsonl                  sourced, versioned project memory records
│   └── MAP_MANIFEST.json             machine freshness evidence
├── app/
│   ├── server.py                     local HTTP server and API routing
│   ├── local_transport.py            loopback bind, launch secret, origin/host checks, lifecycle
│   ├── orchestrator.py               full run order; no business formulas
│   ├── state_machine.py              legal states and transitions
│   ├── events.py                     durable progress/user-action events
│   ├── locks.py                      one writer + stale-lock recovery
│   ├── settings.py                   environment paths and safe defaults
│   ├── excel/
│   │   ├── session.py                dedicated/attached Excel ownership
│   │   ├── discovery.py              bounded sheets/headers/tables profile
│   │   ├── extractor.py              Value2 adaptive block stream
│   │   ├── conversion.py             explicit dates/decimals/errors/text
│   │   └── identity.py               exact workbook/source matching
│   ├── data/
│   │   ├── database.py               DuckDB connection and transaction policy
│   │   ├── staging.py                raw chunk writer + checkpoints
│   │   ├── history.py                append/upsert/snapshot/replace-period
│   │   ├── archive.py                Parquet partition and rebuild
│   │   ├── migrations.py             ordered schema migrations
│   │   └── sql_server.py             optional staged bulk sync and queue
│   ├── quality/
│   │   ├── engine.py                 executes configured checks
│   │   ├── reconciliation.py         independent population/control totals
│   │   ├── drift.py                  schema/type/distribution differences
│   │   └── quarantine.py             retained rejected rows and reasons
│   ├── analytics/
│   │   ├── registry.py               metric metadata and versions
│   │   ├── runner.py                 executes approved SQL only
│   │   ├── insights.py               evidence ranking + sentence templates
│   │   └── calendar.py               shared fiscal/working-day calendar
│   ├── dashboard/
│   │   ├── json_builder.py           validated small dashboard package
│   │   ├── html_builder.py           standalone HTML assembly
│   │   └── verifier.py               offline/network/JS/render checks
│   └── observability/
│       ├── logger.py                 privacy-safe structured logs
│       ├── manifest.py               run evidence and hashes
│       └── performance.py            timings, rows/sec, RAM/temp metrics
├── web/
│   ├── index.html                    local application shell
│   ├── styles.css                    design tokens, responsive/print/RTL
│   ├── app.js                        navigation, API, events, accessibility
│   ├── dashboard.js                  one-page chart rendering; no trusted maths
│   ├── filters.js                    one typed global/section/cross-filter state
│   ├── story.js                      verified manual insight-slide presentation
│   ├── motion.js                     reduced-motion-safe transitions
│   ├── i18n/en.json                  English UI text
│   ├── i18n/ar.json                  Arabic UI text and RTL labels
│   └── vendor/                       pinned local ECharts and licenses
├── reports/<report_id>/
│   ├── report_definition.md          approved meaning and pending decisions
│   ├── report.toml                   machine contract
│   ├── mappings.toml                 aliases, fields, types, approvals
│   ├── metrics.toml                  KPI registry records
│   ├── quality.toml                  checks, severity, tolerances
│   └── sql/
│       ├── clean.sql                 raw → typed clean data
│       ├── checks.sql                report-specific validation
│       ├── history.sql               report load behaviour
│       ├── metrics.sql               trusted KPI calculations
│       └── insights.sql              verified evidence objects
├── contracts/
│   ├── report_config.schema.json     validates report configuration
│   ├── dashboard.schema.json         browser data contract
│   ├── run_event.schema.json         progress event contract
│   └── run_manifest.schema.json      completion evidence contract
├── migrations/                       ordered, immutable database migrations
├── tests/
│   ├── unit/                         deterministic small logic
│   ├── integration/                  layer-to-layer pipeline tests
│   ├── golden/                       known source → known trusted result
│   ├── failure/                      crash, lock, disk, DRM, SQL, rollback
│   ├── browser/                      offline UI, filters, RTL, theme, print
│   ├── architecture/                 baseline, standard-user loopback, missing-component, no-download, clean-PC gates
│   ├── constitution/                 prompt ordering, references, commands and contradiction gates
│   ├── performance/                  representative real-volume benchmarks
│   ├── fixtures/                     synthetic/masked safe inputs
│   └── expected/                     approved outputs and evidence
├── tools/
│   ├── project_map.py                verify/refresh map and manifest
│   ├── project_intelligence/         inventory, parse, graph, rank, cache, render, verify
│   ├── project_memory.py             validate memory + deduplicate/rank opportunities
│   ├── verify_architecture.py         locked components, paths, hashes, imports, network scan
│   ├── verify_constitution.py         structure, cross-reference, command and rule consistency
│   ├── profile_source.py             privacy-conscious source profiler
│   ├── setup_check.py                runtime, Excel, disk, permissions
│   ├── rebuild_database.py           archive-based recovery
│   └── verify_package.py             clean-machine delivery check
├── docs/
│   ├── decisions/                    architecture decision records
│   ├── ARCHITECTURE_COMPLIANCE.md     approved baseline, evidence, deviations and ownership
│   ├── CONSTITUTION_AUDIT.md          latest machine + semantic consistency evidence
│   ├── OPERATIONS.md                 run, schedule, recover, escalate
│   ├── ACCEPTANCE.md                 gates, evidence, sign-off
│   └── SECURITY.md                   storage, access, retention, exposure
├── runtime/                          bundled portable runtime; generated group
├── offline_packages/                 developer/agent hash-locked build wheelhouse
├── repair_payload/                   sealed exact approved release files for employee repair
├── inbox/                            local sources; ignored, never committed
├── workspace/                        run staging/checkpoints; ignored
├── data/                             DuckDB; restricted and backed up
├── archive/                          optional Parquet; restricted
├── output/                           approved dashboards/reports
├── runs/                             immutable per-run evidence
├── logs/                             structured logs; retention-controlled
├── PROJECT_TOOL.bat                  private project-tool runtime wrapper for agent/build commands
├── SETUP_OFFLINE.bat                 one-click environment check/repair
├── START_APP.bat                     one-click local application start
├── UPDATE_NEXT_WEEK.bat              starts guided weekly update flow
├── RUN_TESTS.bat                     offline verification
├── BACKUP.bat                        approved data/output backup
├── BUILD_RELEASE.bat                 reproducible PyInstaller one-folder release
├── VERIFY_OFFLINE.bat                network-disabled package + browser checks
├── ARCHITECTURE_EVIDENCE.json        generated final component evidence
├── LOCAL_TRANSPORT_EVIDENCE.json     generated non-admin loopback/security/lifecycle proof
├── requirements-lock.txt             exact dependency and hash record
├── THIRD_PARTY_NOTICES.md             licenses and attributions
└── sbom.spdx.json                     machine-readable software inventory
```

### 24.1 Dependency direction

```text
web → local API → orchestrator → components
excel → raw → quality → clean → history → analytics → JSON → HTML
configuration/contracts point inward; business logic never leaks into UI
tests may depend on all layers; production layers never depend on tests
```

Circular dependencies between extraction, history, analytics, and dashboard are forbidden.

### 24.2 Mandatory project-local AI skill

The first builder creates an initial `PROJECT_SKILL.md`, entry pointers and map skeleton during Phase −1, before broad production implementation; it then keeps them current and completes their evidence before the first usable release. Every agent entry file points to the skill as the first read. It is project-specific and must not be a copy of this universal constitution.

Required front matter:

```yaml
---
name: <project-id>-project-operator
description: Build, run, diagnose, verify, and evolve this exact offline Excel intelligence project using its verified task-ranked project map. Use whenever an AI agent enters this repository or changes extraction, data, analytics, dashboard, packaging, tests, or project memory.
---
```

Required sections, in this order:

```text
1. READ THIS FIRST — exact verify/context commands and stop conditions
2. PRODUCT — user, decision, sources, outputs, security boundary
3. CURRENT TRUTH — version, proven features, conditional gates, known limits
4. ARCHITECTURE — compact end-to-end flow and dependency direction
5. COMPACT PROJECT MAP — important folders/files, purpose, owner, risk
6. TASK ROUTER — task → context command → files → contracts → tests
7. BUSINESS INVARIANTS — grain, keys, metrics, quality, history, deletion
8. OPERATING RUNBOOK — start, upload, process, publish, retry, recover, back up
9. CHANGE PROTOCOL — reproduce, test, edit, validate, map/memory refresh
10. RELEASE PROTOCOL — build, hash, clean-PC/offline verify, rollback
11. MEMORY + IMPROVEMENT — admission, opportunity states, completion scan
12. COMMAND INDEX — safe exact commands; destructive commands clearly absent
13. POINTERS — exhaustive map, contracts, decisions, lessons, acceptance evidence
```

“Maximum detail” means maximum useful routing detail, not pasting source code or duplicating the exhaustive map. Keep the first-read skill compact enough to load, and route deep detail to `.ai/PROJECT_MAP.md` sections and generated `.ai/CONTEXT_PACK.md`. A new agent must be able to locate the correct files/tests without a repository-wide read.

Update rules:

1. The generated compact-map section is replaced only by `project_map.py refresh`; human sections are protected by markers.
2. A behaviour, architecture, command, release, or operating-flow change updates the skill in the same change set.
3. Ordinary implementation detail updates the exhaustive map, not necessarily the skill.
4. `verify` fails when entry pointers, named commands, file paths, versions, or task routes in the skill are stale.
5. Every release includes a first-session test: an independent agent receives only `PROJECT_SKILL.md`, `CURRENT_STATE.md`, and a realistic task, then names the correct files, risks, contracts, and tests without broad scanning.

---

## PART 25 — Canonical data, API, and event contracts

### 25.1 System tables

#### `sys.run`

```text
run_id · report_id · report_version · application_version · requested_period
status · stage · progress · started_at · finished_at
rows_extracted · rows_rejected · rows_inserted · rows_updated · rows_unchanged
quality_status · archive_status · sql_sync_status
error_code · error_message · output_json · output_html
```

#### `sys.source_file`

```text
run_id · source_id · source_role · file_name · safe_path_reference
physical_file_hash_before · physical_file_hash_after · logical_content_hash
file_size · modified_time · workbook_identity · sheet_name · rows_extracted
```

#### `sys.checkpoint`

```text
run_id · source_id · sheet_name · chunk_number · first_row · last_completed_row
rows_staged · chunk_hash · completed_at
```

#### `quality.check_result`

```text
run_id · check_id · scope · severity · status
expected · actual · difference · tolerance · message · evidence · checked_at
```

#### `quality.quarantine`

```text
run_id · source_id · source_sheet · source_row · business_key_hash
reason_code · reason_message · raw_values · resolution_status
```

#### `sys.sync_queue`

```text
sync_id · run_id · target · batch_reference · status · attempts
next_attempt_at · last_error · created_at · completed_at
```

#### `sys.schema_migration`

```text
version · name · checksum · applied_at · application_version
```

### 25.2 Row identity and lineage

Every staged row includes:

```text
_run_id · _report_id · _source_id · _source_file · _source_file_hash
_source_sheet · _source_row_number · _extracted_at · _schema_version
_business_key_hash · _row_content_hash
```

The business-key hash answers “same business record?” The row-content hash answers “did its values change?” Neither hash replaces the human-readable business-key columns.

### 25.3 Population equation

Every run must prove:

```text
source_rows = accepted_rows + rejected_rows + intentionally_filtered_rows
```

For additive control measures:

```text
source_total = accepted_total + rejected_total + intentionally_filtered_total
```

Filters and exclusions are named evidence, never balancing figures.

### 25.4 Dashboard JSON contract

```json
{
  "schema_version": "1.0",
  "report": {"id": "", "title": "", "period": "", "version": 1},
  "freshness": {"data_date": "", "generated_at": "", "run_id": "", "is_partial": false},
  "quality": {"status": "PASS", "passed": 0, "warnings": 0, "failed": 0, "control_totals": []},
  "filters": {"definitions": [], "active": {}},
  "kpis": [],
  "charts": [],
  "tables": [],
  "insights": [],
  "actions": [],
  "lineage": {"sources": [], "rows": 0, "mapping_version": "", "metric_version": ""},
  "downloads": []
}
```

Each KPI contains `id`, `label`, `value`, `display`, `unit`, `comparison`, `direction`, `status`, `evidence_ref`, and `updated_at`. Each chart contains a business-question title, type, dimensions, series, units, accessible summary, and evidence reference.

### 25.5 Local API contract

| Method and path | Purpose | Important rule |
|---|---|---|
| `GET /api/health` | runtime and database readiness | no sensitive data |
| `GET /api/reports` | configured reports and requirements | configuration-derived |
| `POST /api/uploads` | copy files into intake | local-only, validated, size-limited |
| `POST /api/runs` | start one run | idempotency key + report lock |
| `GET /api/runs/{id}` | current state | durable database state |
| `GET /api/runs/{id}/events` | progress since sequence | ordered, replayable |
| `POST /api/runs/{id}/answer` | answer a waiting question | validate expected question ID |
| `POST /api/runs/{id}/cancel` | request safe cancellation | honour only at safe boundary |
| `GET /api/dashboard` | latest approved dashboard JSON | never expose failed staging |
| `GET /api/history` | weekly approved history | paginated/limited |
| `GET /api/quality/{id}` | checks, exceptions, reconciliation | restricted if row-level data appears |
| `GET /outputs/{file}` | approved local output | path allow-list; no arbitrary files |

#### 25.5.1 Local transport and startup contract

The table above is not optional merely because the product is offline. The browser/renderer talks to the application through this loopback contract; only the local API talks to orchestration, Excel COM, DuckDB, files, and exports.

```text
START_APP.bat
→ verify package hashes and asInvoker execution level
→ acquire per-user single-instance lock
→ choose OS-assigned port (port 0) or bounded approved high loopback port
→ generate per-launch secret in memory
→ start bundled FastAPI/Uvicorn on 127.0.0.1 only
→ health check exact process/address/port
→ open renderer with a one-time bootstrap handshake
→ persist all run/events/history state in the database, not browser memory
→ on exit: reject new work, finish/rollback safe boundary, stop listener, release lock
```

Mandatory invariants:

1. The executable runs under the invoking standard user's token; its manifest is `asInvoker`. No child process may self-elevate.
2. The launcher never uses `runas`; code never installs a service or invokes `netsh` to add a URL reservation or firewall rule.
3. The socket's actual bound address is verified as `127.0.0.1`. A host string alone is not proof.
4. The API accepts only the exact launch session and expected loopback origin/host. CORS wildcard is forbidden.
5. Port conflict recovery changes only the local port within the approved algorithm and updates the exact URL opened by the launcher.
6. Browser refresh reconnects to durable state by `run_id` and event sequence; the renderer cannot become the source of truth.
7. Startup fails closed with a stable code and diagnostic evidence if integrity, safe binding, standard-user access, origin protection, or health checks fail.
8. A standalone HTML export remains read-only and self-contained; it does not replace the operating local application or its API.

Any proposal called “direct Windows connection,” “native connection,” “no-server mode,” “static local mode,” or similar is treated as an architecture deviation until its exact transport, threat model, contract equivalence, testability, lifecycle, and recovery are documented and explicitly approved.

### 25.6 Run-state legality

Every transition is validated. Examples:

```text
CREATED → CHECKING_SOURCE
CHECKING_SOURCE → WAITING_FOR_FILE | OPENING_EXCEL | FAILED
OPENING_EXCEL → WAITING_FOR_USER | EXTRACTING | FAILED
EXTRACTING → STAGING | CANCELLED | FAILED
VALIDATING → CLEANING | FAILED
UPDATING_HISTORY → ARCHIVING | CALCULATING | FAILED
VERIFYING → COMPLETE | FAILED
```

`COMPLETE`, `FAILED`, and `CANCELLED` are terminal. A retry creates a linked attempt or resumes only from a verified checkpoint; it does not erase the previous event record.

### 25.7 Versioning rules

Version independently:

```text
application · report configuration · mapping · database schema
quality rules · metric registry · dashboard JSON · dashboard template
```

Raise a major contract version for incompatible field meaning/removal. Raise a report version when grain, business key, load mode, metric meaning, or population changes. Cosmetic dashboard changes do not change metric versions.

---

## PART 26 — Professional dashboards, graphs, and useful insights

### 26.1 Start with the decision, not the chart

Every dashboard declares:

```text
Audience: who will use it?
Decision: what must they decide?
Frequency: when do they decide?
Action: what can they change after seeing it?
Evidence: which trusted measures support that action?
```

A chart without a decision question is removed.

### 26.2 Chart selection map

| Business question | Best default | Avoid |
|---|---|---|
| Is performance improving over time? | line chart; small multiples for many lines/models; restrained volume columns only when needed | many overlapping series |
| Is the process stable or only moving randomly? | control chart with approved centre/control-limit method and rule flags | ordinary trend labelled “stable” without statistical rules |
| Are we above/below target? | actual/target bullet or variance bar | speedometer gauge |
| What explains most of the problem? | sorted Pareto bars + cumulative line | multi-slice pie |
| Which category contributes most? | sorted horizontal bars | alphabetical bars |
| Where and when is the issue concentrated? | heatmap with explicit values/tooltips | decorative map |
| Which line/model performs differently? | normalized small multiples or dot plot on a shared scale | unequal axes that exaggerate differences |
| How does a process move between stages? | funnel only for true sequential populations; otherwise flow table | misleading funnel |
| How is a distribution behaving? | histogram/box plot | average alone |
| Are two measures associated? | scatter plot with volume/segment context and non-causality note | claiming root cause from correlation |
| What changed between two periods? | variance/waterfall with reconciled bridge | unrelated before/after cards |
| When did downtime/changeover happen? | event timeline or Gantt only when start/end timestamps exist | categorical bars pretending to show sequence |
| How do losses split across availability/performance/quality? | reconciled loss tree or waterfall; OEE components only with approved inputs | inventing OEE from output/defect data alone |
| Which items need action? | ranked table with severity and owner | chart that hides identifiers |

### 26.3 Standard management page

```text
sticky command header + report/period/freshness/quality
sticky shared filters + comparison + active cross-filter chips + reset
FIRST VIEWPORT: 4–6 KPI cards + main trend/target + top verified insight
STORY: comparison bridge + Pareto contributors + concentration/stability view
ACTION: ranked investigation table with evidence and owner/status where available
TRUST: risks, quality, completeness, lineage, run/metric/mapping versions
OPERATE: add data, progress, weekly history, exports, recovery/support
```

This is one route and one connected filter state. It may scroll vertically; it must not fragment one management story across unrelated pages.

### 26.4 Visual design tokens

| Token | Rule |
|---|---|
| Page width | fluid with readable maximum width; dashboard grids collapse cleanly |
| Spacing | 4/8 px base; generous grouping; no cramped cards |
| Radius | restrained 10–16 px; consistent |
| Font | local system font stack; no online fonts |
| Body | 16–18 px; 1.45–1.6 line height |
| KPI | tabular figures; unit and period always visible |
| Accent | one primary blue; semantic green/amber/red only for meaning |
| Border | subtle but visible in light and dark themes |
| Focus | strong high-contrast outline |
| Motion | 150–250 ms; reduced-motion respected |
| Print | white background, legends/labels retained, interactive-only controls hidden |

### 26.5 KPI rules

- Show the current value, unit, period, comparison base, direction, and freshness.
- Use weighted rates from summed numerator/denominator; never average row percentages unless the metric definition explicitly requires it.
- Round only for presentation, after calculation and reconciliation.
- Use null for undefined rates or zero denominators; never show a false zero.
- Mark partial periods clearly and exclude them from automatic comparisons unless the metric specifically supports partial-period comparison.
- Targets must be approved and versioned, never inferred from history without an explicit label.

### 26.6 Insight evidence object

Before text is generated, build:

```json
{
  "type": "period_change",
  "metric_id": "defect_rate_ppm",
  "current_period": "2026-W21",
  "current": 2216,
  "comparison_period": "2026-W20",
  "comparison": 3050,
  "change_absolute": -834,
  "change_percent": -27.34,
  "drivers": [],
  "confidence": "verified",
  "evidence_refs": ["metric:defect_rate_ppm", "run:RUN-..."]
}
```

Sentence templates transform verified objects into concise management language. Optional AI receives only these objects and may improve wording, not numbers or causal claims.

### 26.7 Insight ranking

Rank candidates by:

```text
business impact × magnitude × persistence × affected population × confidence
```

Show no more than five. Prefer one clear cause/contributor insight over several descriptions of the same movement. Separate observation, likely contributor, risk, opportunity, and recommended action.

### 26.8 Action quality

An action must name:

```text
what to investigate or change · why now · evidence · suggested owner
urgency · expected confirmation metric · status
```

Do not generate generic actions such as “monitor closely” when a specific contributor is known.

### 26.9 Detail-table rules

- Search, sort, filter, and export the currently approved view.
- Keep identifiers as text and preserve leading zeroes.
- Freeze important columns and use sensible pagination/virtualization.
- Never send hundreds of thousands of detail rows to the browser by default.
- Allow lineage drill-through only under approved access rules.
- Clearly distinguish record count from summed defect quantity.

### 26.10 Dashboard verification

Automated checks must prove:

```text
local file/page opens · zero unexpected network requests · zero JavaScript errors
required KPIs exist · chart containers are non-empty · filters change expected data
quality/freshness/run ID match manifest · RTL and English render correctly
light/dark/print layouts work · keyboard navigation and focus work
no trusted calculation is performed only in browser code
```

### 26.11 Exact one-page responsive blueprint

Use a 12-column desktop grid, 8-column tablet grid, and single-column mobile flow. Maximum content width is approximately 1600 px with responsive side margins.

| Region | Desktop span | Minimum height | Behaviour |
|---|---:|---:|---|
| Command header | 12 | 64 px | Sticky; quality/freshness never hidden |
| Filter ribbon | 12 | 56 px | Sticky below header; horizontal scroll only on narrow screens |
| KPI strip | 12 | 132 px | 4–6 equal cards; 2 columns tablet; 1–2 mobile |
| Hero trend | 8 | 360 px | Primary decision chart; clear target/comparison |
| Insight focus | 4 | 360 px | Top evidence statement + contribution + next action |
| Pareto | 7 | 340 px | Sorted contributors and cumulative share |
| Compare/bridge | 5 | 340 px | Reconciled period change or target gap |
| Heatmap/distribution/stability | 12 | 360 px | Select exactly one most useful diagnostic default |
| Action table | 12 | 320 px | Virtualized/paginated, identifiers retained |
| Trust + operation | 12 | content | Quality, lineage, add data, history, downloads, support |

Do not force every possible chart onto the page. Unavailable or decision-irrelevant regions disappear cleanly; the grid reflows without empty cards. The agent chooses visuals from the approved metric/data availability matrix and records why each remained.

### 26.12 Factory decision and KPI availability matrix

Use ISO 22400 concepts as a definition framework, not permission to display every manufacturing KPI. A KPI appears only when its numerator, denominator, grain, time behaviour, target, owner, and data-quality proof are available.

| Decision level | Typical question | Candidate measures only when supported |
|---|---|---|
| Shift/operator | Where must we act now? | output vs plan, defect quantity/rate, top symptom, open repair, line/process concentration |
| Supervisor/day-week | What changed and which contributor explains it? | weighted PPM, first-pass yield, rework, downtime reason, schedule attainment, rolling trend |
| Manager/week-month | Where is the persistent loss and value opportunity? | persistent Pareto, cost of poor quality, throughput, yield, action closure, validated OEE components |
| Plant leadership | Are performance and risk improving sustainably? | approved target attainment, cross-line comparison, quality loss, capacity/availability, data trust |

Specific guardrails:

- Do not calculate OEE unless availability, performance, and quality inputs share an approved equipment/time grain.
- Do not calculate first-pass yield unless first-pass and rework/retest events can be distinguished.
- Do not call a category “root cause” unless a governed investigation confirms causality; dashboard analytics identify contributors and priorities.
- Use defect **quantity** for impact and weighted defect **rate** for performance; show production volume so low-volume extremes are not misread.
- Compare complete periods by default. Partial periods require like-for-like elapsed-time comparison or a prominent exclusion warning.

### 26.13 Visual system and motion specification

Use CSS custom properties so light, dark, print, and future brand themes share one system:

```text
spacing: 4, 8, 12, 16, 24, 32, 48
radius: 12 px controls/cards; 16 px hero panels
font: local system UI stack; 16 px minimum body; tabular numbers
primary: deep enterprise blue/cobalt; one accent only
semantic: success, warning, danger, neutral; each paired with icon/text/pattern
surface: strong hierarchy with subtle borders/shadows; no heavy glass blur
chart: restrained gridlines, direct labels where useful, shared units and scales
```

Starter tokens may use light surfaces around `#F6F8FC/#FFFFFF` with dark text around `#101828`, and dark surfaces around `#080D18/#111827` with near-white text. A cobalt such as `#2563EB` may be the primary accent. These are starting values, not automatic approval: test every text/control/state pair to WCAG 2.2 AA, verify printed greyscale meaning, and adjust the theme rather than shrinking or muting important information.

Motion uses opacity and transform when possible. Animate between old and new chart states so the user can follow change; do not animate axes in a way that disguises scale changes. Story slides use one directional transition and preserve focus. Test normal, reduced-motion, low-power, 125%, and 150% Windows scaling.

### 26.14 Interaction truth and filter reconciliation

Every visual declares the filters and grain it supports. When a filter cannot apply, the UI explains that rather than silently ignoring it. After each filter/comparison change, verify:

```text
all affected components share filter_state_version
KPI numerator/denominator match visible evidence tables
Pareto bars reconcile to the filtered total
drill-through inherits the exact filter/comparison context
reset returns the authored approved default
loading/error/empty states do not retain stale values
```

URL/local persistence may store approved dimension keys and periods only. Clear invalid stored values after a schema/version change. A screenshot/export always includes active filters, comparison, data date, quality, and run ID.

### 26.15 Manufacturing product pattern cross-check

The design deliberately adopts recurring patterns visible across established manufacturing analytics products without copying a vendor screen or inventing unsupported KPIs:

| Observed industry pattern | Adopt here | Guardrail |
|---|---|---|
| Microsoft supplier-quality sample focuses on defects and resulting downtime across suppliers/plants | pair quality rate/quantity with business impact and ranked contributors | show only impact measures present in approved sources |
| Siemens performance tools surface OEE, availability, performance, quality, MTBF/MTTR at plant/machine level | allow level-aware KPI cards, trends, and drill-down when equipment/time data exists | never infer equipment KPIs from defect workbooks alone |
| Rockwell production analytics combines output, downtime, quality, machine/line status, and root-cause views | use a management summary followed by loss/contributor diagnostics and action tracking | call findings contributors until causal investigation confirms root cause |
| Tulip quality guidance uses defect Pareto, first-pass yield, scrap, supplier defects, and cost-of-quality views | include Pareto/action workflow and enable quality metrics through the registry | every numerator, denominator, unit and population must be approved |
| Grafana and Power BI guidance use one sourced dashboard with variables/filters, hierarchy, drill-down, and uncluttered first view | one shared filter state, first-viewport priority, directed evidence drill-down, versioned JSON | remove redundant visuals and never hide active context |

The builder records a short `dashboard_decisions.md`: audience, five decisions, selected visuals, rejected visuals, available/absent data, and usability feedback. “Modern” is proven by clarity, speed, accessibility, and coherent interaction—not by adding more cards or effects.

### 26.16 Interaction performance budgets

Measure on the approved target PC and record p50/p95. Initial acceptance budgets are:

```text
warm application shell visible                    ≤ 2.0 s
filter control acknowledges input                 ≤ 100 ms
pre-aggregated filter → complete visual update    ≤ 500 ms p95
server-backed filtered view                       ≤ 2.0 s p95 or show real progress
story slide change                                ≤ 300 ms motion, no focus loss
scroll/animation                                  no sustained visible jank
```

If representative data cannot meet a budget, reduce browser payload, pre-aggregate, virtualize, cache approved query results, or simplify the visual before raising the limit. Never hide slow work behind fake animation.

---

## PART 27 — Edge cases and required solutions

### 27.1 Excel, DRM, and source files

| Edge case | Required behaviour |
|---|---|
| Protected file opens only manually | Enter `WAITING_FOR_USER`; exact instruction; attach to exact full path; never close user workbook |
| Dedicated Excel open fails | Bounded retry, then attach; record active mode |
| Wrong workbook with similar name is open | Reject; match canonical full path and expected workbook identity |
| DRM prompt appears mid-run | Preserve checkpoint; user action; no blind clicking or bypass |
| Workbook is locked | Read-only open if safe; otherwise retry with increasing delay |
| File is still copying | Require stable size and modified time across two checks |
| Excel process remains after crash | Terminate only the recorded process created by this run; never mass-kill Excel |
| User closes attached workbook | Fail current chunk, preserve completed checkpoints, request reopen |
| Hidden/very-hidden sheets | Read only configured sheet; log state; never “read all” automatically |
| Filters/hidden rows | Explicit include/exclude rule in report definition; default include if the table contains them |
| Merged cells | Configured fill rule only for approved fields; preserve original value/position |
| Multi-row headers | Approved header and data-start rows; deterministic combination rule |
| Duplicate headers | Deterministic suffix plus warning; mapping must choose exact normalized field |
| Phantom `UsedRange` | Prefer table/named range/configured columns; bounded `Find` fallback |
| Formula/error cells | Read saved value; count error codes; block if critical; never coerce to zero |
| 1900/1904 date system | Detect workbook setting and convert explicitly |
| `.xls`, `.xlsb`, `.xlsm` | Use Excel desktop path; preserve macro-enabled extension; never strip VBA silently |
| External links/Power Query/pivots | Approved refresh order and timeout; otherwise use as-saved data and disclose |
| Digital signature on macro file | Treat modification as signature risk; prefer read-only extraction |

### 27.2 Scale and memory

| Edge case | Required behaviour |
|---|---|
| 500k rows × 272 columns | Read only approved columns; adaptive cell-based chunks; write each chunk immediately |
| A chunk exceeds safe memory | Halve chunk rows and retry once; record benchmark; fail safely if minimum is unsafe |
| Slow per-cell loop appears | Block code review/test; require range block access |
| Excel row limit exceeded in output | Keep full detail in database/Parquet; publish aggregated workbook/dashboard |
| Browser JSON becomes large | Aggregate server-side; paginate details; size gate blocks publication |
| Temp disk low | Preflight required space; block before extraction; preserve last good output |
| Database spill fills disk | Configured temp limit and safe failure; clean only run-owned temp files |

### 27.3 Schema and data quality

| Edge case | Required behaviour |
|---|---|
| Column moved | Approved name/alias mapping continues |
| Optional new column | Warning and profile; no silent business use |
| Required column missing/renamed | Fail with exact missing field and approved recovery |
| Two columns map to one field | Fail unless explicit coalescing precedence is approved |
| Type drift | Quarantine isolated invalid values or fail material drift per rule |
| Locale number/date ambiguity | Preserve raw text; explicit locale parser; quarantine ambiguity |
| Leading-zero or >15-digit identifier | Store as text end-to-end |
| Zero/negative value | Apply metric-specific approved rule; test boundary |
| Duplicate business key | Apply approved duplicate scope/tie-breaker; otherwise fail |
| Row triggers multiple rules | Count once in population equation; store all applicable reasons if policy permits |
| Master-data lookup missing | Configured fail/quarantine/unknown member; never silent drop |
| Totals/subtotals inside data | Detect only by approved rule; exclude with counted lineage |
| Empty source | Fail or publish “no activity” only if contract explicitly allows it |
| Sudden row/category/null change | Dataset drift warning/fail using pre-approved threshold |

### 27.4 History and corrections

| Edge case | Required behaviour |
|---|---|
| Same file uploaded twice | Source hash/idempotency detects it; no duplicate history |
| Different filename, identical content | Logical content hash prevents duplication |
| Old row corrected | Upsert within lookback or approved full-period rebuild |
| Row disappears | Apply configured deletion rule; never infer deletion |
| Partial week replaces full week | Completeness gate blocks downgrade unless owner approves |
| Replace-period request has wrong period | Validate source min/max dates against requested partition; fail |
| Load fails during update | Transaction rollback; trusted history unchanged |
| Calculation logic changes | Version metric; rebuild clean/analytics from raw/archive; compare golden output |
| Database lost | Rebuild from approved archive + migrations + configuration; reconcile |

### 27.5 Database and SQL Server

| Edge case | Required behaviour |
|---|---|
| Two local writers | Report/database lock; second run waits or exits clearly |
| Schema migration fails | Rollback; retain prior version; block application start if incompatible |
| SQL Server unavailable | Queue trusted batch as pending; local report may complete |
| SQL bulk copy partly succeeds | Use staging transaction; discard/rollback stage; reconcile before publish |
| SQL credentials expire | User-action/system error; never log secret; preserve pending queue |
| Central data differs | Block sync completion; keep local evidence; investigate independently |

### 27.6 Web application and offline package

| Edge case | Required behaviour |
|---|---|
| Browser refreshed mid-run | Reload state/events from durable store |
| Application started twice | Reuse existing local instance or show clear message |
| Port is busy | Try bounded approved local ports and display selected URL |
| Browser blocks local-file script | Serve through loopback local server; standalone report embeds assets safely |
| Agent removes local server to avoid administrator rights | Reject as an architecture violation; keep the bundled standard-user loopback API and prove `asInvoker` startup |
| UAC or administrator prompt appears | Fail `ELEVATION_FORBIDDEN`; inspect manifest/path/launcher and fix the package—never teach the user to elevate |
| Firewall, URL reservation, IIS, or service installation is proposed | Reject; the approved user-mode `127.0.0.1` listener requires none of these project mutations |
| Loopback binding is blocked by endpoint policy | Fail with `LOCAL_LOOPBACK_BIND_FAILED`, preserve evidence, and request IT compatibility approval; never switch to LAN/public bind or reduced product |
| “Direct Windows connection” is proposed | Treat as an unapproved transport replacement under Part 0.7; do not implement or rename it as an internal detail |
| Malicious browser page probes loopback | Reject wrong Origin/Host/launch secret; use no wildcard CORS and expose no reusable token |
| No internet | Normal operation; no warning unless an optional external service was explicitly enabled |
| Missing/corrupt runtime or package | Fail closed with the component ID; employee repair restores the exact file from the sealed release-repair payload or replaces the full release; wheelhouse rebuilds are developer-only; never download, redesign, or run reduced capability |
| Very long/non-Latin path | Use Unicode-safe APIs, normalized absolute paths, and path-length test |
| Antivirus blocks executable/script | Signed/approved distribution where possible; clear IT handoff; no evasion |
| Windows scaling or small screen | Responsive layout, large text, tested 125–150% scaling |
| Partial dashboard generation | Validate temp output; publish atomically only after browser checks pass |

### 27.7 Security and privacy

| Edge case | Required behaviour |
|---|---|
| Extracted output is no longer DRM protected | Written IT approval, restricted folder ACLs, retention, encryption/backup policy |
| Sensitive values appear in logs | Log counts, hashes, safe identifiers; redact row values by default |
| Formula injection in exported CSV/XLSX | Escape untrusted prefixes (`=`, `+`, `-`, `@`) per output policy |
| Malicious upload name/path | Sanitize name, fixed intake root, extension/signature checks |
| External AI is not approved | Deterministic local insights only; no data leaves device |
| Shared PC | Per-user restricted data folder and explicit cleanup/retention |
| Backup contains extracted data | Apply same classification and access controls as live database |

### 27.8 AI-agent and map failures

| Edge case | Required behaviour |
|---|---|
| Map verification fails | Stop feature work; refresh and review map first |
| Map contradicts code/test | Code and executable evidence win temporarily; repair map in same task |
| Agent wants broad scan | Require evidence that task router is insufficient; expand one boundary at a time |
| Agent invents a business rule | Reject change; mark pending approval; add stop-condition test if possible |
| Agent removes a dependency to make the app “more portable/native/simple” | Reject as architecture violation; restore baseline; require explicit deviation approval and equivalence proof |
| Agent assumes a build-machine tool exists on the employee PC | Clean-PC simulation fails; bundle it or remove the runtime requirement without removing capability |
| Required package is difficult to freeze | Fix hooks/spec/native files and test the final bundle; difficulty is not permission to delete the component |
| Agent changes public contract silently | Fail contract/version tests; require migration and map update |
| Agent finishes without learning update | Completion gate fails when material behaviour changed |
| Skill grows with duplicated notes | Consolidate; keep one rule and point to it |

---

## PART 28 — Implementation playbook: how, when, why, and exit gates

Parts 14 and 15 define the high-level roadmap. This section makes execution unambiguous.

### 28.1 Phase control table

| Phase | Why now | Primary owner | Build | Evidence required before next phase |
|---|---|---|---|---|
| **−1. Architecture + offline dependency lock** | Prevent an agent from simplifying away the approved product | User + platform agent | baseline lock, allowed prerequisites, bundled BOM, verifier, deviation protocol | architecture verifier passes; every required component has delivery path/test; no unapproved deviation |
| **0. Business + security contract** | Prevent building the wrong or unapproved system | Business + IT | report definition, storage/retention approval, source inventory, first decision/dashboard audience | signed/preserved approvals; no material unknown hidden |
| **1. Protected-file proof** | Extraction is the riskiest dependency | Platform agent + operator | dedicated Excel session, exact attach fallback, block read, source hash, timing | real representative protected files read twice; source hashes unchanged; Excel cleaned safely |
| **2. One vertical slice** | Prove value before framework growth | Platform + data owner | raw stage, minimal clean model, basic quality, one history mode, 5–10 KPIs, JSON, HTML | totals reconcile; dashboard offline; same input rerun is stable |
| **3. Operability** | Make failure recoverable | Platform | states, events, locks, checkpoints, cancel, logs, manifests, last-good publish | injected crash/lock leaves history and last dashboard safe |
| **4. Connected history** | Support daily/weekly additions and corrections | Data owner + platform | approved load modes, hashes, lookback, deletion policy, rebuild | day/week sequence, correction, duplicate, and replace-period tests pass |
| **5. Strong quality** | Make management numbers trustworthy | Data/report owner | structural, row, dataset, freshness, control, cross-source, quarantine | bad fixtures cannot enter trusted history; population equation passes |
| **6. Recovery archive** | Remove dependence on slow re-extraction | IT + platform | Parquet partitioning, retention, backup, rebuild | empty database rebuilt and reconciled from archive |
| **7. SQL Server (only when enabled/approved)** | Share only after local truth is stable | IT/database owner | bulk staging, transaction, reconcile, durable sync queue | outage/retry/partial-copy tests; local and central totals agree; otherwise explicitly not applicable |
| **8. Metric + insight library** | Reuse correct definitions | Business/data owner | calendar, metric registry, evidence objects, ranked narratives | golden values pass; every insight links to evidence |
| **9. Reusable dashboards** | Scale reports without duplicating UI | Product/UI owner | common JSON, templates, filters, accessibility, RTL, print | new report rendered with configuration/JSON, not copied JavaScript |
| **10. Non-technical product** | Complete adoption | Product + operator | upload, progress, quality, reports, history, settings, support | operator completes two runs and one recovery without developer help |

### 28.2 Phase rule

Do not mark a phase complete because code exists. Mark it complete only when the evidence column passes on real or production-like inputs. Later phases may be prototyped, but they must not weaken an earlier gate.

### 28.3 Daily engineering cycle

```text
verify map
→ verify architecture baseline
→ classify task and layer
→ confirm business/security decisions
→ reproduce current behaviour or defect
→ write/adjust failing test
→ make smallest clean change
→ run focused tests
→ run affected integration/golden/failure/browser gates
→ refresh contracts/state/map/lessons
→ verify architecture + package or output
→ report proof and remaining decisions
```

### 28.4 First-run discovery sequence

1. Hash and inventory sources without modifying them.
2. Capture workbook/sheet/table/range/formula/macro/query/pivot/link/protection structure.
3. Detect candidate header rows, duplicate headers, likely types, row counts, date ranges, and safe samples.
4. Observe the human's current manual process, corrections, judgment points, and control totals.
5. Fill `report_definition.md`; mark unknowns `pending_approval`.
6. Fill `report.toml`, mappings, quality rules, metric registry, and source-role patterns.
7. Approve the extraction/storage security boundary.
8. Only then write report-specific production logic.

### 28.5 Build order inside one vertical slice

```text
source identity
→ Excel session ownership
→ header-only discovery
→ approved column projection
→ adaptive block extraction
→ raw staging + lineage
→ quality and control total
→ typed clean data
→ one transactional history mode
→ metric SQL + golden test
→ dashboard JSON schema
→ standalone HTML + browser verification
→ run manifest + last-good publication
```

---

## PART 29 — Initial Process Defect project contract

This is the first concrete build target described by the user. Treat observed structure as evidence and business meaning as pending until approved.

### 29.1 Expected source roles

| Role | Example file | Observed structure | Initial use |
|---|---|---|---|
| Weekly result | `ProcessDefect_Result(2).xlsx` | Three week-range sheets (`W1~W8`, `W9~W16`, `W17~W22`); rows repeat as production quantity, defect quantity, defect rate by code/model | Authoritative candidate for weekly volume, defects, and PPM |
| Defect details | `ProcessDefectList_Details(1).xlsx` | One sheet; about 38k detail rows and 90 columns; duplicate headers include `Manuf. Part` and `Log File` | Diagnostic candidate for process, line, product, symptom, location, repair, and root-cause analysis |

Observed structure can guide extraction, but the business owner must confirm source authority and whether both files cover the same population and week calendar.

### 29.2 Weekly-result normalization

The source uses three category rows per code/model. Normalize it to one trusted row per `code + week`:

```text
code · model · week · production_qty · defect_qty
reported_defect_rate_ppm · calculated_defect_rate_ppm
source_sheet · source_row_group · run_id · source_hash
```

Rules:

1. Carry code/model only within the explicit three-row group; never across a malformed boundary.
2. Validate the category sequence and fail/quarantine malformed groups.
3. Discover week columns by strict `YYYY-Wnn` pattern, not column position.
4. Calculate weighted PPM as `defect_qty / production_qty × 1,000,000`.
5. Compare calculated PPM with reported PPM within the approved rounding tolerance.
6. Treat zero production as undefined rate, not zero performance.
7. Upsert by `code + week`; rerun must not duplicate.
8. Detect low-volume latest week as partial; do not compare it with a complete prior week automatically.

### 29.3 Detail normalization

Project only fields required for decisions and lineage. Initial candidate fields:

```text
defect time/date · confirmation time · PO · model · basic model · product/project
division · line · shift · process · inspection process · work group
defect symptom/class/code · cause/input · location · material part(s)
defect quantity · repair quantity · remaining quantity · repair status/time
unit/serial identifier · inspector/registrant · chassis/physical size
source row · source file/hash · run ID
```

Duplicate headers receive deterministic names such as `manuf_part` and `manuf_part_2`. The mapping explicitly chooses the intended one.

Until a stable detail business key is approved, use a **temporary full-row content hash** only to prevent identical duplicates. Label this limitation. Do not pretend it safely handles corrected or deleted detail events.

### 29.4 Initial quality gate

Blocking:

```text
both required source roles identified
expected sheet/category/header structure exists
required columns exist uniquely after approved mapping
source hash before = source hash after
weekly group structure valid
no negative production/defect quantities unless explicitly allowed
reported and calculated row PPM reconcile within approved tolerance
weekly business keys unique after normalization
population equation passes
```

Warnings until the business owner decides:

```text
cross-source weekly defect-total differences
temporary detail identity
latest partial week
new optional detail columns
unmapped low-value fields
missing target PPM
```

### 29.5 Initial trusted KPIs

All require an approved definition and SQL golden tests:

```text
production quantity · defect quantity · weighted defect rate PPM
week-on-week rate change · four-week rolling weighted rate
best/worst complete week · number/share of improving codes
top defect-code contribution · repair completion/share remaining
detail coverage and cross-source difference · unresolved quality exceptions
```

### 29.6 Initial graphs

1. Weekly weighted defect-rate line with production-volume columns.
2. Latest complete week vs previous complete week variance.
3. Pareto of codes/models by defect quantity with cumulative share.
4. Pareto of detail defect symptoms.
5. Line × process or week × process heatmap.
6. Product/project breakdown.
7. Repair status and remaining-quantity action table.
8. Cross-source weekly reconciliation table, clearly labelled until scope is approved.

### 29.7 Initial useful insights

Generate only from verified evidence:

- material week-on-week improvement or deterioration;
- the codes/models explaining most of the change;
- persistent symptoms/processes/lines across several complete weeks;
- high-volume vs high-rate distinction;
- unresolved repair concentration;
- data-quality or coverage risk that could change interpretation;
- latest-week partial-data warning.

Avoid claiming root cause merely because a category is correlated with defects. Phrase it as a contributor or investigation priority unless causal evidence exists.

### 29.8 Initial output experience

```text
Upload the two workbooks
→ see role detection and readiness
→ press Process
→ watch extraction/quality/history/analytics/dashboard stages
→ review PASS/WARNING/FAIL
→ open interactive dashboard
→ download standalone HTML and evidence
→ view W01–Wnn history
→ add the next week's files through the same flow
```

---

## PART 30 — One-click offline delivery package

### 30.1 Package outcome

Deliver one ZIP that is copied to an approved user-writable Windows folder, extracted, and started without internet **and without administrator rights**. Normal startup is `asInvoker`; no UAC prompt, installer, service, firewall rule, URL reservation, IIS, or machine-wide change is allowed. If company policy blocks the signed application or loopback listener, record that environmental gate as `CONDITIONAL` and obtain IT approval; do not alter the architecture or elevate around the policy.

Normal operation may rely externally only on the approved Windows desktop image, Microsoft Excel desktop, and an interactive authorized user session. The complete application runtime, database, server, libraries, assets and configuration are inside the ZIP. The agent may not meet this outcome by deleting dependencies or reducing the product to Windows/Excel features.

### 30.2 Required contents

```text
ready-to-run PyInstaller one-folder application + private Python runtime
application source, build specification, migrations, and local web assets
hash-locked Windows wheelhouse: web server, Excel automation, DuckDB, inspection, tests
optional locked SQL Server connector and dependencies
local ECharts/icons/fonts-if-any and licenses; no CDN references
approved DuckDB extensions prepackaged; autoinstall/autoload disabled
report configuration, mappings, SQL, schemas, migrations
tests and synthetic/masked fixtures
setup/start/update/test/backup batch files
sealed employee repair payload containing exact approved release components
project-local skill, project map engine, context pack, memory and universal agent entry files
sample approved dashboard and evidence (no raw confidential source by default)
dependency hashes, SBOM, license notices, version/rollback manifest
implementation baseline lock, architecture verifier, compliance report and evidence
standard-user application manifest and local transport lifecycle/security evidence
```

### 30.3 One-click scripts

| Script | Behaviour |
|---|---|
| `SETUP_OFFLINE.bat` | verifies the complete self-contained release, creates data folders, and restores damaged files only from the sealed release-repair payload; it never runs `pip`/package installation and writes no secrets |
| `START_APP.bat` | runs as the invoking standard user, verifies integrity/single instance, starts one bundled `127.0.0.1` API on a safe selected port, health-checks it, opens the exact approved renderer URL, and shows a clear fail-closed error if blocked; never elevates or changes the machine |
| `UPDATE_NEXT_WEEK.bat` | opens directly to guided upload/process flow |
| `RUN_TESTS.bat` | runs offline unit/integration/golden/map/package checks |
| `BACKUP.bat` | copies approved database/archive/config/output/evidence to configured protected backup destination |
| `STOP_APP.bat` | requests graceful shutdown; does not kill unrelated processes |
| `BUILD_RELEASE.bat` | builds a clean versioned one-folder release only from pinned local inputs |
| `VERIFY_OFFLINE.bat` | blocks network, starts release, executes browser/health/upload/demo/restart checks, writes evidence |

### 30.4 Clean-machine setup gate

On a representative offline Windows PC:

```text
extract ZIP
→ disable network and mask system Python/Node/pip/npm/Git from PATH
→ sign in with a representative standard non-admin account; confirm no UAC prompt
→ run START_APP.bat; its automatic fast self-check must pass
→ verify the listener belongs to the packaged process and is bound only to 127.0.0.1
→ probe wrong Host/Origin/secret and non-loopback access; every probe must fail
→ process safe representative inputs
→ open dashboard
→ close/restart app
→ rerun same inputs
→ verify no duplicates and history remains
→ simulate one source/Excel failure
→ simulate one missing required component and confirm fail-closed integrity error
→ occupy the preferred port and confirm safe automatic local-port selection without elevation/firewall change
→ verify startup/shutdown created no service, IIS/HTTP.sys reservation, firewall rule, or machine-wide registry/config change
→ run SETUP_OFFLINE.bat only to prove diagnosis/repair, then restore the approved release
→ recover using on-screen guidance
```

No hidden development-machine dependency is allowed. Repeat the gate on a PC that has no system Python, Node.js, package manager, editor or compiler. Passing on the build machine is not evidence.

### 30.5 Data-security notice

Do not include confidential production source workbooks in the reusable package. When the user explicitly requests a real-data result, deliver it separately or inside an access-controlled user-specific package, clearly stating that DuckDB, Parquet, JSON, HTML, exports, logs, and backups may contain the same sensitive data without the original DRM wrapper.

### 30.6 Weekly operation

1. Start the app.
2. Choose the report.
3. Add the new/corrected files.
4. Confirm detected period and source roles.
5. Process and watch progress.
6. Resolve only explicit user-action requests.
7. Review quality and reconciliation.
8. Open the new dashboard only after publication succeeds.
9. Confirm the week appears in history.
10. Back up according to retention policy.

### 30.7 Release layout and reproducibility contract

The final ZIP has this user-visible shape:

```text
Excel-Intelligence-vX.Y.Z/
    START_APP.bat
    STOP_APP.bat
    SETUP_OFFLINE.bat
    UPDATE_NEXT_WEEK.bat
    BACKUP.bat
    QUICK_START.pdf-or-html
    app/                    ready-to-run one-folder executable/runtime/assets
    repair/                 sealed exact release-component repair payload
    config/                 approved editable operator settings only
    project/                source, tests, skill, maps, update/build tools
    offline_packages/       hash-locked wheels and approved optional binaries
    licenses/               notices and license texts
    IMPLEMENTATION_BASELINE.lock.json
    ARCHITECTURE_EVIDENCE.json
    LOCAL_TRANSPORT_EVIDENCE.json
    checksums.sha256
    sbom.spdx.json
    VERSION.json
```

`VERSION.json` records application/report/schema/dashboard/map versions, build commit, UTC build time, builder environment, supported Windows/Office architecture, and rollback compatibility. The ZIP itself receives a SHA-256 checksum delivered beside it.

Reproducibility rules:

1. Build from a clean checkout and locked dependencies with network disabled after the local cache is prepared.
2. Never package the developer's live virtual environment or absolute workstation paths.
3. Keep user data/config outside the versioned application folder so upgrades do not overwrite them.
4. Test paths with spaces, Arabic/non-Latin characters, long names, standard-user permissions, and 125–150% scaling.
5. Inspect the executable manifest and launchers; reject `highestAvailable`, `requireAdministrator`, `runas`, service/IIS/HTTP.sys/firewall setup, and writes outside approved user-writable locations.
6. Verify start, update, same-input rerun, restart, backup, restore, failure recovery, loopback lifecycle, and rollback on a representative clean offline PC.
7. Keep the previous approved version until the new one completes migration and health checks; rollback must not downgrade data destructively.

### 30.8 Minimum offline package bill of materials

Exact versions are selected and pinned at build time after compatibility/security review. The package must contain everything actually imported or loaded at runtime, including transitive binaries and metadata. At minimum assess and either include or explicitly prove unnecessary:

```text
private CPython runtime + standard library
FastAPI, Uvicorn, Pydantic, multipart/upload support
pywin32 and required COM support files
DuckDB and approved extensions
native DLL/Visual C++ runtime prerequisites required by the exact bundled wheels
Parquet support used by the chosen DuckDB build
workbook inspection library used by discovery/tests
SQL Server driver and native prerequisites when enterprise sync is enabled
JSON Schema/TOML/config validation dependencies
ECharts and every local UI/icon asset
approved Windows renderer proof plus official offline WebView2 standalone/fixed payload when required
PyInstaller bootloader, hooks, metadata, and application data files
test/browser verification dependencies in the QA/update kit
Tree-sitter/AST grammar wheels and map-tool dependencies in the project kit
licenses, SBOM, checksums, migrations, schemas, SQL, templates, translations
```

The builder must execute a runtime import/resource audit from the final `app/` folder and a network-call audit while processing the representative files. “Present in requirements” is not proof that the release contains it; “works on the developer PC” is not offline acceptance.

---

## PART 31 — Complete verification and acceptance matrix

### 31.1 Mandatory gates

| Gate | Required proof | Release effect |
|---|---|---|
| Source identity/immutability | expected role/period/hash; before = after | Block |
| Extraction completeness | sheet/range/chunks/rows/control total | Block |
| Schema/mapping | required fields/types; approved aliases; no collision | Block |
| Population | accepted + rejected + filtered = source | Block |
| Business rules | unit and golden tests; approved version | Block |
| History | duplicate, correction, lookback, deletion, replace-period tests | Block |
| Reconciliation | source→stage→clean→history→metric→dashboard | Block |
| Exceptions | retained, counted, classified, visible | Block |
| Database safety | transaction rollback, migration, lock, recovery | Block |
| Dashboard contract | schema valid; values match SQL/manifest | Block |
| One-page decision design | first viewport answers status/action; evidence story, action and trust regions present | Major/block for acceptance |
| Filters/comparison | one shared state; cross-filter/drill-through/reset reconcile to evidence | Block |
| Browser/offline | no network/JS error; charts/filters/theme/RTL/print/story mode | Block |
| Standard-user startup | `asInvoker`; no UAC/admin token; app starts/processes/stops from approved user-writable folder | Block |
| Loopback transport | packaged FastAPI/Uvicorn retained; bound only to `127.0.0.1`; port conflict and lifecycle tests pass | Block |
| Loopback request security | wrong Origin/Host/launch secret and non-loopback probes rejected; no wildcard CORS | Block |
| No machine mutation | no service, IIS, HTTP.sys URL reservation, firewall change, privileged ports, or machine-wide install/write | Block |
| Motion | purposeful transitions; reduced-motion and focus preserved; no fake progress | Major |
| Accessibility | keyboard, focus, labels, contrast, reduced motion | Major/block for production |
| Performance | representative volume within measured approved limits | Major |
| Repeatability | identical rerun + two stable production-like runs | Block |
| Security | no secrets/unapproved data/logging/network | Block |
| Map freshness | verify passes; task routes/tests/contracts current | Block |
| Project skill onboarding | independent agent routes a realistic task without broad scan | Block |
| Memory/opportunities | admission validation passes; suggestions deduplicated and sourced | Major |
| Architecture lock | actual source/release matches baseline; every deviation has explicit user-approved decision ID | Block |
| Constitution consistency | machine and semantic audit pass; ordering, commands, tree, prompts and acceptance rules agree | Block |
| Bundled component proof | runtime/import/path/hash/license/smoke test evidence exists for every required component | Block |
| No silent downgrade | remove/block each critical component in test; app fails closed and preserves last good truth | Block |
| No build-machine leakage | clean simulation masks system Python/Node/pip/npm/Git/editor/compiler and still passes | Block |
| Release completeness | final one-folder app, source/update kit, wheelhouse, assets, SBOM, licenses and hashes present | Block |
| Clean offline machine | no preinstalled Python/Node/package downloads; extract/start/process/restart/repair/rollback pass | Block |
| Operator handoff | non-technical operator runs and recovers | Major |

### 31.2 Stable-run definition

Two stable runs require two consecutive production-like executions with no code, configuration, source repair, or manual database correction between them. All critical checks pass; outputs open and reconcile; rerunning an identical input has no destructive side effect.

### 31.3 Performance evidence

Record, do not guess:

```text
file size · rows/columns/projected cells · Excel open time · block size
rows/sec · extraction/conversion/staging/quality/history/analytics time
peak RAM · peak temp disk · database size · JSON/HTML size
dashboard first-open/filter time · SQL sync throughput
```

Performance targets are approved only after representative benchmarks.

### 31.4 Final release decision

Release only when every critical gate passes, major limitations are fixed or formally accepted with owner/date, warnings state impact and next action, rollback/recovery is proven, and the operator witnesses or performs an end-to-end run.

Use `CONDITIONAL` when an environmental gate—such as real protected Excel, production SQL identity, scheduler, or locked-down browser—could not be exercised. Name the exact missing evidence.

---

## PART 32 — Universal AI-agent prompts

### 32.1 Start or continue the project

```text
Use this file as the constitution. Do not scan the repository.
Read `PROJECT_SKILL.md`, follow `.ai/READ_FIRST.md`, verify the map and locked
implementation baseline, generate the
task-ranked `.ai/CONTEXT_PACK.md`, then read it with `.ai/CURRENT_STATE.md`.
Identify the smallest vertical slice or exact task,
the affected layer/contracts/tests, pending business decisions, and security gates.
Implement only after blockers are resolved. Prove the result, then update state,
lessons, project-local skill, map, and manifest in the same task.
```

### 32.2 Add the next week

```text
Treat this as an operating run, not a code change. Verify source roles, stability,
period, hashes, schema, quality, and completeness. Use the configured history mode.
Do not duplicate prior data or overwrite a complete period with partial data.
Publish only after reconciliation and dashboard verification. Preserve full run evidence.
```

### 32.3 Add or change a metric

```text
Read the report definition, metric registry, source fields, calendar rule,
metric SQL, golden tests, dashboard contract, and task route. Confirm human approval
of meaning, grain, filters, units, zero/null/rounding rules, target, and comparison.
Implement in SQL, add golden and edge tests, update versions/contracts/map,
and prove dashboard values equal the SQL evidence.
```

### 32.4 Repair a defect

```text
Reproduce the failure from evidence. Identify root cause and affected invariant.
Write a regression test that fails before the fix. Make the smallest safe change.
Run focused plus affected integration/failure/golden/browser gates. Verify last-good
history/output protection. Capture reusable learning and refresh the map.
```

### 32.5 Audit only

```text
Do not modify. Verify the project map and architecture baseline, inspect only the routed files and evidence,
then report findings ranked by correctness, data loss, security, recovery,
operability, performance, and usability. Separate confirmed findings from risks
and unknowns. Give exact affected files, evidence, impact, and recommended next action.
```

### 32.6 Build the complete project from this document

```text
Treat this document as the executable master prompt and project constitution.
Build the complete production-shaped local application; do not return only a plan,
mockup, dashboard image, or partial UI. Start by resolving only business/security
blockers. If production systems are unavailable, use clearly labelled safe fixtures
and leave only those environmental proofs CONDITIONAL.

The architecture in this document is locked. Offline means bundle the dependencies;
it never means remove them or rely on Windows/Excel as substitutes. Do not replace the
pipeline with static HTML, Excel-only, PowerShell-only, CSV/JSON storage, browser storage,
or another reduced design. Do not assume system Python, Node, pip, npm, Git, an editor,
terminal or internet. If a locked component is incompatible, submit the formal deviation
request and wait for explicit user approval before changing it.

Keep the bundled FastAPI/Uvicorn local API. “No external server” means that this API runs
inside the application session on 127.0.0.1; it does not mean “no local server.” Run the
packaged executable asInvoker under the logged-in standard user, use an OS-selected or
bounded approved high port, and stop the listener with the app. Never request elevation,
install a Windows Service, use IIS/HTTP.sys deployment, change firewall/URL reservations,
bind to 0.0.0.0/::/LAN, or open ports 80/443. The renderer must not access Excel COM,
DuckDB, arbitrary files, or trusted state directly. Treat any “direct Windows connection”
or “serverless local mode” as a formal architecture deviation, not as a harmless packaging choice.

Create the end-to-end protected-Excel → staging → quality → trusted history → SQL
analytics → evidence insights → one-page interactive web cockpit pipeline. The page
must include shared filters/comparisons, KPI first viewport, trend, Pareto, the most
useful diagnostic view, ranked actions, quality/lineage, data picker, durable progress,
weekly history, exports, subtle reduced-motion-safe transitions, and a manual insight
story mode. Never calculate trusted KPIs only in the browser or allow silent source edits.

Package every required runtime, dependency, local asset, approved extension, migration,
schema, test and launcher into a versioned Windows offline ZIP. No system-installed Python or Node, package
download, CDN, internet, terminal, or editor may be required for normal use. Prove the
final built folder on a clean offline PC profile and deliver checksums, SBOM, licenses,
quick start, architecture evidence, recovery, backup and rollback evidence. Test once
with system developer tools hidden and once with a required component removed to prove
that the complete bundle works and missing components fail closed without a downgrade.

Inside the project create PROJECT_SKILL.md, the Aider/repo-map-inspired local structural
map engine, a task-ranked context pack, freshness gates, sourced project memory, and a
deduplicated improvement scout. Make every agent entry file point to the skill first.
After every material change update tests, contracts, state, memory when justified,
project skill, map and manifest together. Finish by giving the user the release ZIP,
proof, conditional items, simple start instruction, and at most three evidence-based
improvement choices.
```

---

## PART 33 — Final definition of done

The work is not done until all applicable statements are true:

```text
[ ] business purpose, grain, key, formulas, quality, deletion, and storage are approved
[ ] source files remain unchanged and protected access is respected
[ ] extraction is block-based, projected, bounded, restartable, and measured
[ ] raw, quality, clean, history, analytics, JSON, and UI layers are separated
[ ] no rejected/filtered row disappears silently
[ ] history is transactional, idempotent, correction-aware, and rebuildable
[ ] trusted arithmetic is deterministic, versioned, reconciled, and golden-tested
[ ] insights are evidence-backed and do not invent causes
[ ] dashboard is useful, readable, responsive, bilingual where required, accessible, and offline
[ ] one page presents executive status, evidence story, diagnostics, actions, trust, data update, and history coherently
[ ] shared filters, comparisons, cross-filtering, drill-through, reset, and exports preserve exact context and reconcile
[ ] animations and insight slides explain change, respect reduced motion, preserve focus, and never fake progress
[ ] upload, progress, reports, quality, and weekly history work for a non-technical user
[ ] failed runs preserve the last approved dashboard and trusted database
[ ] SQL Server outage does not cause Excel re-extraction
[ ] package runs on a clean approved offline Windows machine
[ ] implementation baseline lock matches source, final release, SBOM, hashes, licenses and architecture evidence
[ ] every required runtime/library/asset is bundled or explicitly proven inside the approved Windows/Excel baseline
[ ] normal runtime requires no system-installed Python/Node, package manager, CDN, internet, editor, or terminal; its private runtime remains bundled
[ ] bundled FastAPI/Uvicorn API is retained, starts/stops with the app, and is the only renderer-to-orchestrator boundary
[ ] final executable runs `asInvoker` under a standard non-admin user with no UAC prompt
[ ] listener binds only to `127.0.0.1` on an approved selected port; LAN/public binds and ports 80/443 are rejected
[ ] wrong Host, Origin, launch secret, and non-loopback requests are rejected; wildcard CORS is absent
[ ] normal operation creates no Windows Service, IIS/HTTP.sys reservation, firewall rule, installer, or machine-wide write
[ ] renderer never accesses Excel COM, DuckDB, arbitrary local files, or trusted calculations directly
[ ] blocking/removing a required component produces a clear fail-closed integrity error and no reduced fallback
[ ] no architecture component was removed/replaced and no new prerequisite was added without explicit user-approved deviation
[ ] release contains one-folder app, source/update kit, hash-locked dependencies, assets, SBOM, notices, checksums and rollback metadata
[ ] logs/manifests/exceptions/reconciliation/recovery evidence exist
[ ] two stable runs and identical-input rerun pass
[ ] project map, manifest, current state, decisions, lessons, and project-local skill are current
[ ] task-ranked context generation and map verification work incrementally without external source disclosure
[ ] project memory has sources/status and improvement suggestions are evidence-based, deduplicated, and user-controlled
[ ] another AI agent can locate the next change without reading the whole repository
```

### 33.1 The final operating principle

> Define meaning before code. Prove authorized extraction before scale. Protect trusted history before presentation. Calculate once in tested SQL. Explain only verified evidence. Publish only after quality and offline verification. Leave a verified map so the next human or AI agent starts in minutes, not hours.

---

## PART 34 — AI instruction consistency and constitution audit

### 34.1 One canonical order for every agent

This sequence resolves ordering ambiguity. The first builder continues through all applicable steps; a maintenance agent applies the same sequence to the smallest routed change.

```text
1 read constitution once (first builder) OR PROJECT_SKILL + task context (maintenance)
2 verify project map + implementation baseline
3 classify work mode and rewrite the eight-question task contract
4 resolve only true business/security/deviation blockers
5 reproduce/profile current evidence
6 implement the smallest complete vertical change without weakening other layers
7 run focused → integration/golden/failure/browser/architecture tests
8 build the complete release candidate from locked local inputs
9 verify clean offline machine, missing-component failure, backup and rollback
10 update contracts, decisions, state, skill, memory, opportunities, map and manifests
11 rerun map + architecture + constitution + package verification
12 deliver working artifact, proof, conditional evidence and optional improvements
```

Testing or documentation may occur earlier, but no step may be skipped merely because the UI appears to work.

### 34.2 Conflict-resolution matrix

| Apparent conflict | Correct interpretation |
|---|---|
| Build the full product vs make the smallest change | First build delivers the whole gated product; later maintenance makes the smallest change that fully preserves contracts |
| Offline vs required libraries | Bundle the libraries; never remove capabilities or download at runtime |
| No external server vs local API | No external/cloud/LAN server is required; the bundled standard-user `127.0.0.1` FastAPI/Uvicorn API remains mandatory |
| No administrator rights vs local HTTP listener | A user-mode loopback socket and `asInvoker` executable are the approved design; never remove the API, elevate, install a service, or change firewall/URL reservations |
| “Direct Windows connection” vs typed local API | The phrase has no authority or defined contract; any replacement is a Part 0.7 deviation requiring evidence and explicit approval |
| No employee installation vs `SETUP_OFFLINE.bat` | `START_APP.bat` runs directly; setup is optional integrity diagnosis/repair from a sealed payload, never package installation |
| Windows + Excel prerequisites vs browser rendering | Renderer is formally part of the approved Windows image or included as official offline/fixed runtime |
| No system Python vs Python-based project tools | `PROJECT_TOOL.bat` uses the bundled private project-tool runtime; the employee never supplies Python |
| Project map saves tokens vs code is the truth | Map routes the agent; the agent still reads every edited file, direct contract and affected test |
| Agent autonomy vs architecture lock | Agent chooses reversible internals inside the baseline; user alone approves component removal/replacement/new prerequisites |
| Complete local app vs standalone HTML | Local one-page app is the operating product; standalone HTML is an approved portable report export |
| Synthetic fixtures vs real protected-file proof | Fixtures allow a complete demonstrable build; production approval remains conditional until real-environment evidence passes |
| SQL Server in architecture vs optional local mode | Connector is fully bundled/tested only when enabled; otherwise the phase is explicitly not applicable, never silently removed |
| Wheelhouse included vs no package tools for employee | Wheelhouse is for offline developer/agent rebuild; employee repair restores exact release files from the sealed payload |
| Layer separation vs vertical feature work | A feature may touch several layers through contracts; no layer absorbs another layer's responsibility |
| Improvement suggestions vs scope control | Finish the requested work first; suggest at most three evidence-based options and do not implement them without authority |

### 34.3 Machine and semantic constitution audit

Create `tools/verify_constitution.py`, `tests/constitution/`, and `docs/CONSTITUTION_AUDIT.md`. Expose:

```text
PROJECT_TOOL.bat constitution audit
PROJECT_TOOL.bat constitution cross-references
PROJECT_TOOL.bat constitution architecture-terms
PROJECT_TOOL.bat constitution commands
```

Machine checks must detect:

```text
unbalanced Markdown fences/front matter
duplicate or missing Part/section numbers
broken internal Part/section references
stale filenames/commands not present in the canonical tree
development commands that bypass PROJECT_TOOL.bat
runtime download/install/CDN language outside explicit forbidden/reference sections
required baseline component omitted from BOM, tree, tests or acceptance matrix
an optional component described elsewhere as universally required
Windows/Excel-only or reduced-capability fallback language
phrases that remove/bypass the local server, call the product serverless, or claim a “direct Windows/native connection” without an approved deviation ID
local-server language that implies administrator rights, Windows Service/IIS/HTTP.sys deployment, firewall/URL-reservation changes, or LAN/public binding
manifest/launcher instructions containing requireAdministrator, highestAvailable, runas, ports 80/443, 0.0.0.0, or :: outside explicit forbidden tests/documentation
renderer code or instructions that directly access Excel COM, DuckDB, trusted files/state, or trusted KPI logic
conflicting statements about employee repair versus developer rebuild
version/date/reference-index drift
```

Automation cannot fully understand meaning. After every material constitution change, the agent also performs a semantic review against 34.2 and records:

```text
confirmed contradictions found and fixed
remaining ambiguity and owner
new rule and every section it affects
whether architecture/acceptance/tree/prompts stayed aligned
```

The audit fails closed on unresolved critical contradictions. It may not “fix” them by deleting a required rule; it must identify the canonical rule and update every conflicting pointer.

### 34.4 Agent completion declaration

Every build/evolution task ends with this concise declaration:

```text
architecture baseline: PASS / BLOCKED
removed or replaced locked components: NONE / approved decision IDs
new external prerequisites: NONE / approved decision IDs
runtime downloads/CDNs: NONE
local loopback API: RETAINED / BLOCKED
runtime privilege: STANDARD USER + asInvoker / BLOCKED
service/firewall/URL reservation/machine-wide changes: NONE
clean offline proof: PASS / exact conditional evidence
map + constitution consistency: PASS
```

A statement such as “I made it simpler by using Windows and Excel only,” “I removed the local server to avoid administrator rights,” or “I replaced it with a direct Windows connection” is itself evidence of non-compliance and requires architecture review before accepting any output.

---

## PART 35 — Official technical references

These links support the technology and quality choices; the project remains operable offline after delivery.

- Microsoft Excel performance and range guidance: [Excel performance tips](https://learn.microsoft.com/en-us/office/vba/excel/concepts/excel-performance/excel-tips-for-optimizing-performance-obstructions)
- DuckDB concurrency model: [Concurrency](https://duckdb.org/docs/current/connect/concurrency.html)
- DuckDB bulk/data loading guidance: [Importing Data](https://duckdb.org/docs/current/data/overview.html)
- DuckDB Parquet support and projection/filter pushdown: [Reading and Writing Parquet](https://duckdb.org/docs/stable/data/parquet/overview.html)
- DuckDB configuration: [Configuration Overview](https://duckdb.org/docs/current/configuration/overview.html)
- Apache ECharts local setup: [ECharts Get Started](https://echarts.apache.org/handbook/en/get-started/)
- Apache ECharts accessibility and decal guidance: [ARIA best practices](https://echarts.apache.org/handbook/en/best-practices/aria/)
- Aider task-ranked structural repository maps: [Repository map](https://aider.chat/docs/repomap.html) and [Tree-sitter/PageRank design](https://aider.chat/2023/10/22/repomap.html)
- `cyanheads/repo-map` structural summaries, SHA-256/SQLite cache, exclusions, and disclosure warning: [GitHub repository](https://github.com/cyanheads/repo-map)
- Grafana dashboard consistency, hierarchy, variables, drill-down, and version control: [Dashboard best practices](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)
- Grafana one-source interactive filter variables: [Dashboard variables](https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/)
- Microsoft one-screen hierarchy and decision-first dashboard guidance: [Power BI dashboard design tips](https://learn.microsoft.com/en-us/power-bi/create-reports/service-dashboards-design-tips)
- Microsoft simple, consistent, low-clutter, accessible report guidance: [Design Power BI reports for accessibility](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports)
- Microsoft supplier-quality sample using defect and downtime decisions: [Supplier Quality Analysis sample](https://learn.microsoft.com/en-us/power-bi/create-reports/sample-supplier-quality)
- ISO manufacturing KPI definition framework: [ISO 22400-1 overview](https://www.iso.org/standard/56847.html) and [ISO 22400-2 definitions](https://www.iso.org/standard/54497.html)
- Siemens plant/machine performance KPI patterns: [Performance Insight](https://www.siemens.com/en-us/products/simatic-apps/performance-insight/)
- Rockwell output/downtime/quality production monitoring patterns: [Plex Production Monitoring](https://plex.rockwellautomation.com/en-us/products/production-monitoring.html)
- Tulip manufacturing-quality Pareto pattern: [Pareto chart for manufacturing defects](https://tulip.co/blog/what-is-a-pareto-chart-definition-examples/)
- PyInstaller one-folder build and packaged data: [Using PyInstaller](https://pyinstaller.org/en/stable/usage.html) and [Spec files](https://pyinstaller.org/en/stable/spec-files.html)
- PyInstaller self-contained dependency model: [What PyInstaller does](https://pyinstaller.org/en/stable/operating-mode.html)
- Python private Windows embedding constraints: [Using Python on Windows](https://docs.python.org/3/using/windows.html)
- Repeatable offline Python package cache and hashes: [pip download](https://pip.pypa.io/en/stable/cli/pip_download/) and [pip wheel offline example](https://pip.pypa.io/en/stable/cli/pip_wheel/)
- Microsoft offline/fixed browser-runtime distribution choices: [Distribute WebView2](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution) and [Evergreen vs fixed version](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/evergreen-vs-fixed-version)
- Uvicorn loopback binding and OS-selected port (`127.0.0.1` default; port `0` selects an available port): [Uvicorn settings](https://uvicorn.dev/settings/)
- Microsoft UAC execution levels (`asInvoker` retains the launching process permission level; elevated levels can prompt): [MANIFESTUAC](https://learn.microsoft.com/en-us/cpp/build/reference/manifestuac-embeds-uac-information-in-manifest?view=msvc-170) and [Application manifests](https://learn.microsoft.com/en-us/windows/win32/sbscs/application-manifests)
- Microsoft modern Windows dynamic port range background: [Default dynamic TCP/IP port range](https://learn.microsoft.com/en-us/troubleshoot/windows-server/networking/default-dynamic-port-range-tcpip-chang)
- FastAPI origin model and explicit CORS configuration: [CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- DuckDB extension network controls: [Securing extensions](https://duckdb.org/docs/lts/operations_manual/securing_duckdb/securing_extensions.html)
- W3C accessibility quick reference: [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/)
- W3C contrast guidance: [Understanding Contrast Minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- W3C focus guidance: [Understanding Focus Appearance](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)
- W3C target-size guidance: [Understanding Target Size Minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

Review current official release notes and security advisories before changing pinned versions. Do not make runtime upgrades part of a normal report change.

---

## PART 36 — Amendment index and constitution change control

### 36.1 Why Parts 36–44 exist

Version 7.1 is complete as *law*. It was incomplete as an *executable artifact*: an agent handed an empty repository could not literally perform step 2 of the mandatory 90-second start (Part 0.1), because every command it names lives behind a `PROJECT_TOOL.bat` that does not exist yet and that only runs on Windows. Nine gaps of that kind are closed here.

| # | Gap in 7.1 | Amendment | Refines |
|---|---|---|---|
| 1 | Every named command is a Windows `.bat` requiring a bundled runtime that does not exist in a new or cloud/Linux workspace | Part 37 — portable tool contract | 0.2, 20.9, 34.2 |
| 2 | Acceptance gates (Part 31) are prose tables; nothing tracks which gate actually passed | Part 38 — machine-readable gate ledger | 31, 33 |
| 3 | Roadmap starts at Phase −1 and assumes a project exists | Part 39 — Phase −2 instantiation | 14, 28.1 |
| 4 | Two different canonical trees and project names (13.1 vs 24) | Part 40 — naming and tree precedence | 13.1, 24 |
| 5 | "AI never invents business meaning" is unenforceable prose | Part 41 — `PENDING_APPROVAL` sentinel | 3, 19.5, 27.8 |
| 6 | Error codes and run states exist only as prose lists | Part 42 — codes and states as data contracts | 12.2, 12.3, 25.6 |
| 7 | Secrets (SQL credentials, launch secret) have rules scattered and no storage contract | Part 43 — secret handling contract | 13.5, 22.10, 27.7 |
| 8 | Excel COM makes the whole pipeline untestable off Windows, so agents stall or fake it | Part 44 — extraction port and dev/test adapters | 6, 7, 15, 23.10 |
| 9 | The constitution has no changelog discipline for itself | This Part | 21.4, 34.3 |

### 36.2 Constitution change control

The constitution is versioned `MAJOR.MINOR`.

```text
MINOR  additive amendment: new Part, new machine check, clarified rule
MAJOR  any change to Parts 0–35 text, any locked component change,
       any acceptance gate removed or weakened
```

Every version change appends a row to `docs/CONSTITUTION_CHANGELOG.md` recording version, date, author class (human owner / agent proposal), affected Parts, and — for a MAJOR — the approving human. An agent may author a MINOR amendment that strengthens or clarifies. An agent may **not** author a MAJOR change; that is a Part 0.7 deviation requiring explicit user approval. `PROJECT_TOOL constitution audit` fails when the version block, the changelog, and the amendment index disagree.

---

## PART 37 — Portable tool contract (refines 0.2, 20.9, 34.2)

### 37.1 The bootstrap problem

Part 0.1 orders every agent to run `PROJECT_TOOL.bat map verify` before doing anything. In a fresh repository, on a Linux CI runner, or in a cloud agent workspace, that command cannot exist yet. An agent that obeys literally is blocked; an agent that improvises invents its own workflow and drifts. Both outcomes are worse than the rule was meant to prevent.

### 37.2 Two tiers, one behaviour

Development tooling and employee runtime are separate boundaries (Part 23.12) and get separate rules.

| Tier | Artifact | Runs on | Requires | Used by |
|---|---|---|---|---|
| **Canonical** | `tools/project_tool.py` | any OS with Python 3.11+ **standard library only** | nothing else | agents, developers, CI |
| **Wrapper (Windows)** | `PROJECT_TOOL.bat` | Windows | bundled private runtime when present, else any discoverable Python 3.11+ | developers, agents on Windows |
| **Wrapper (POSIX)** | `project_tool.sh` | Linux/macOS | Python 3.11+ | agents, CI |

Mandatory properties:

1. `tools/project_tool.py` imports **only the Python standard library**. No third-party import, at any code path, ever. This is what makes it runnable in a bare workspace and is enforced by `PROJECT_TOOL architecture verify --source-scan`.
2. The wrappers add nothing but interpreter discovery and argument pass-through. Identical arguments produce identical behaviour and identical exit codes on every platform.
3. Every command named anywhere in this constitution is reachable as `PROJECT_TOOL <group> <command>`. Writing `PROJECT_TOOL.bat map verify` (Parts 0.1, 20.5, 20.9) and `./project_tool.sh map verify` are the same instruction; agents use whichever their platform provides.
4. The project-intelligence engine (Part 20.8) may use packaged parsers **only as an optional accelerator**. When Tree-sitter or any optional parser is absent, the engine degrades to a stdlib AST/heading parser and still returns a correct — if less richly ranked — result. Absence of an optional accelerator is never a reason for `verify` to fail or for an agent to stop.
5. This portable tier is development intelligence only. Part 20.8 rule 10 still applies unchanged: nothing under `app/` or `web/` may import it, and the employee runtime still ships the bundled private runtime described in Part 23.1.

### 37.3 Required command groups

```text
PROJECT_TOOL map          doctor | verify | refresh --review | context --task ... --budget N
                          explain --path P | changed --base REF
PROJECT_TOOL memory       validate | suggest --task ... --max N | add | supersede
PROJECT_TOOL architecture verify --baseline | --source-scan | --release F
                          | --simulate-clean-pc | --simulate-missing ID | --standard-user-loopback
PROJECT_TOOL constitution audit | cross-references | architecture-terms | commands
PROJECT_TOOL gates        status | set --id G --status S --evidence E   (Part 38)
PROJECT_TOOL report       new --id R | validate --id R                  (Part 41)
PROJECT_TOOL doctor                                                     (aggregate readiness)
```

A command that is not yet implemented must exit non-zero with `TOOL_COMMAND_NOT_IMPLEMENTED` and name the file to implement. It must never exit zero, print a fabricated result, or silently do nothing — a green check that proves nothing is the single most damaging failure mode for an agent-operated project.

### 37.4 Exit-code contract

```text
0   pass
1   fail: a real violation the agent must fix
2   usage error: bad arguments
3   blocked: prerequisite missing, nothing was verified   ← never report as pass
```

Exit code 3 exists so an agent can distinguish "verified and clean" from "could not verify". Reporting a 3 as a pass is a compliance violation under Part 34.4.

---

## PART 38 — Machine-readable gate ledger (refines 31, 33)

### 38.1 Why

Part 31.1 defines ~35 gates and Part 33 defines ~33 done-statements, all as prose checkboxes. Nothing in 7.1 stores which gate passed, when, with what evidence, or which are `CONDITIONAL`. Agents therefore self-assess in chat, and the assessment disappears at the end of the session. The next agent starts blind and tends to re-declare completion.

### 38.2 `acceptance/gates.yaml`

Every gate from Parts 31.1 and 33, plus every phase gate from Parts 14 and 28.1, is one record:

```yaml
- id: GATE_CONTROL_TOTAL
  part: "31.1 / 9.4"
  title: Control-total reconciliation is exactly zero
  severity: block            # block | major | minor
  status: not_started        # not_started | in_progress | pass | fail | conditional | not_applicable
  evidence: ""               # path to run manifest, test output, or evidence file
  verified_at: ""            # ISO-8601 UTC
  verified_by: ""            # agent id / human name
  conditional_reason: ""     # required when status = conditional
  next_action: ""            # required when status != pass
```

Rules:

1. `status: pass` requires a non-empty `evidence` path that exists on disk. `PROJECT_TOOL gates status` fails otherwise. Evidence is a file, never a sentence.
2. `status: conditional` requires `conditional_reason` **and** `next_action` naming the exact later validation step (Part 0.4 rule 6, Part 31.4).
3. `status: not_applicable` requires a reason and is legal only for genuinely optional phases, such as SQL Server when it is not enabled (Part 14 Phase 6).
4. No release while any `severity: block` gate is not `pass` or `not_applicable`.
5. The agent completion declaration (Part 34.4) is generated **from this file**, not written by hand from memory.
6. A gate may be moved to `pass` only in the same change set as the evidence it cites, and never by editing the file alone.

### 38.3 Effect on reporting

Part 0.5's completion report and Part 34.4's declaration both read the ledger. "What remains conditional" stops being a recollection and becomes a query. This is the amendment that most directly stops the Part 16.1 "project stalls at 80% and everyone believes it is at 95%" failure.

---

## PART 39 — Phase −2: instantiation from the template (refines 14, 28.1)

### 39.1 Why

Phase −1 (architecture lock) presumes files exist to lock. An agent starting from an empty directory has no `IMPLEMENTATION_BASELINE.lock.json` to verify, no map to refresh, and no skill to read — so Part 0.1 fails at step 1 and the agent improvises the whole structure. Phase −2 makes the first hour deterministic.

### 39.2 Phase −2 definition

| Field | Value |
|---|---|
| **Why now** | Give the agent a verified skeleton so every later rule has something to bind to |
| **Owner** | Platform agent, unattended |
| **Build** | Instantiate the template: project slug, first `report_id`, entry pointers, `.ai/` skeleton, baseline lock draft, gate ledger seeded to `not_started`, contracts, tool tier |
| **Exit gate** | `PROJECT_TOOL doctor` exits 0; `map verify`, `constitution audit`, `memory validate`, `gates status` all run and pass on the skeleton; no business meaning has been invented |

### 39.3 The three questions of Phase −2

Instantiation asks the user for exactly three things, because these three name files and cannot be derived:

```text
1. project slug        e.g. process-defect-intelligence   (folder + package + skill name)
2. first report id     e.g. process_defect                (reports/<id>/ + all contracts)
3. report title        e.g. Process Defect Weekly          (human-facing label)
```

Everything else in Part 4 and Part 18 stays `PENDING_APPROVAL` (Part 41) and is resolved in Phase 0 with the business owner. An agent must not expand these three into guessed business rules — collecting a slug is not collecting a grain.

### 39.4 Ordering

```text
Phase −2 instantiate  → Phase −1 architecture lock → Phase 0 business/security
→ Phase 1 protected-file proof → Phase 2 vertical slice → Phases 3–10
```

Phase −2 is the only phase an agent may complete with no human input.

---

## PART 40 — Naming and tree precedence (refines 13.1, 24)

Part 13.1 shows a tree rooted at `excel-automation/`; Part 24 shows a fuller tree rooted at `excel-intelligence/`. Neither name is normative and the difference is an artifact of the merge.

Resolution:

1. **Part 24 is the canonical tree.** Part 13.1 is a reading aid for the data/application subset and never overrides Part 24.
2. The repository root folder is `<project_slug>` chosen in Phase −2. No rule anywhere depends on the literal strings `excel-automation` or `excel-intelligence`.
3. The Python package under `app/` is `<project_slug>` with hyphens replaced by underscores.
4. `PROJECT_TOOL constitution audit` verifies that the on-disk tree matches Part 24 for every path that is not marked generated/runtime/ignored, and reports additions the map has not catalogued (Part 20.5).
5. Deviating from the Part 24 tree is a documented decision under Part 16.4, not a matter of preference. Adding a folder is ordinary work; removing a required one is an architecture deviation under Part 0.7.

---

## PART 41 — The `PENDING_APPROVAL` sentinel (refines 3, 19.5, 27.8)

### 41.1 Why

Rule 7 ("AI never invents business meaning"), Part 3.1's decision list, and Part 19.5's evidence classes are all correct and all unenforceable — nothing distinguishes an approved business key from one an agent invented at 2 a.m. because it looked reasonable. A confident wrong formula is, by this document's own words, the most expensive bug in the system. It deserves a machine check, not a paragraph.

### 41.2 The sentinel

Any configuration value that Part 3.1 reserves to a human is written as the literal token `PENDING_APPROVAL` until a named human approves it:

```toml
business_key   = "PENDING_APPROVAL"
control_total_column = "PENDING_APPROVAL"

[approvals]
business_key = { approved_by = "", approved_at = "", evidence = "" }
```

Approval replaces the token **and** fills the matching `[approvals]` record with a named person, a UTC timestamp, and an evidence reference (email, meeting note, signed definition). Both halves are required: a filled value with an empty approver is treated as unapproved.

### 41.3 Enforcement

| Mode (Part 19.2) | Sentinel present | Result |
|---|---|---|
| Discovery, Prototype | allowed | Warning; every affected output is watermarked `UNAPPROVED DEFINITION` in the UI, the JSON, and the run manifest |
| Production | forbidden | `PROJECT_TOOL report validate` fails; the run refuses to start with `CONFIG_PENDING_APPROVAL`; nothing enters trusted history |

An agent may **create** sentinels freely — that is the correct way to record "a human must decide this". An agent may never **resolve** one. `PROJECT_TOOL report validate --id <r>` lists every unresolved sentinel, which turns Part 18's open-decisions list into a live query against the actual project.

### 41.4 Interaction with fixtures

Part 0.4 rule 6 lets an agent build the complete product against synthetic fixtures. Fixture-backed reports carry approvals of the form `approved_by = "FIXTURE"`, which are valid in Discovery/Prototype and are rejected in Production. This is what keeps "we built it with demo data" from silently becoming "we shipped it with demo definitions".

---

## PART 42 — Error codes and run states as data (refines 12.2, 12.3, 25.6)

### 42.1 Why

Part 12.3 lists ~35 error codes and Part 25.6 lists the legal state transitions, both as prose. Code, tests, the UI's plain-language error screens (Part 22.8), the retry policy (Part 12.4), and the troubleshooting table (Part 12.5) each re-encode that list by hand and drift apart.

### 42.2 `contracts/error_codes.json`

One record per code, and it is the single source of truth:

```json
{
  "code": "DQ_CONTROL_TOTAL_MISMATCH",
  "class": "BLOCKING_DATA",
  "retryable": false,
  "part": "9.4",
  "operator_message_en": "The totals in the source file and the database do not match. Your previous dashboard is unchanged and still correct.",
  "operator_message_ar": "الإجماليات في الملف المصدر وقاعدة البيانات غير متطابقة. لوحتك السابقة لم تتغير وما زالت صحيحة.",
  "next_action": "Open the quality report to see which source and column differ.",
  "preserves_history": true
}
```

`class` is one of `RETRYABLE`, `USER_ACTION`, `BLOCKING_DATA`, `BLOCKING_SYSTEM` (Part 12.3). Application code raises codes from this registry only; a literal error string in `app/` that is not in the registry fails the architecture verifier. Part 22.8's four-part error screen is assembled from these fields, which is what makes non-technical error design a build-time guarantee rather than a design aspiration.

### 42.3 `contracts/run_states.json`

The Part 12.2 states and Part 25.6 transitions as an explicit adjacency list with terminal flags. `app/state_machine.py` loads it rather than hard-coding transitions, and `tests/unit/test_state_machine.py` proves every state is reachable, terminal states have no outgoing edges, and no transition exists that Part 25.6 does not permit. Adding a state is then a contract change with a version bump, exactly as Part 25.7 requires.

---

## PART 43 — Secret handling contract (refines 13.5, 22.10, 27.7)

7.1 mentions the per-launch secret (22.10), forbids logging secrets (27.7), and requires SQL credentials to have separate approval (22.10) — but never says where a secret may live. Explicitly:

| Secret | Storage | Lifetime | Never |
|---|---|---|---|
| Per-launch API secret | process memory only | one launch | disk, log, URL, browser history, run manifest, crash dump |
| SQL Server credentials | Windows Integrated Authentication by default | per connection | `report.toml`, any file in Git, any file in the release ZIP |
| SQL Server credentials when integrated auth is impossible | Windows DPAPI-protected per-user store outside the application folder, written by an operator action, never by an agent | until rotated | plaintext config, environment variable in a `.bat`, source code |
| Backup destination credentials | operating-system credential store or a pre-authenticated mount | per operation | `BACKUP.bat` |

Additional rules:

1. Integrated Authentication is the default and the documented recommendation. A stored credential is a deviation that needs the IT approval already required by Part 13.5.
2. No secret is ever a build input. `BUILD_RELEASE` fails if a candidate secret pattern appears in the release tree.
3. `PROJECT_TOOL architecture verify --source-scan` scans source, config, launchers, and generated output for credential-shaped strings and fails on a hit.
4. Logs record the *identity class* used (`integrated` / `stored`), never the credential.
5. Rotation is an operator runbook step in `docs/OPERATIONS.md`, not a code change.

---

## PART 44 — Extraction port and dev/test adapters (refines 6, 7, 15, 23.10)

### 44.1 Why

Excel COM requires Windows, an interactive session, a licensed Excel, and DRM-authorized files (Parts 1.4 rule 3, 7.1). Everything downstream — staging, quality, history, analytics, JSON, dashboard — requires none of that. In 7.1 they are nonetheless coupled, so a Linux CI runner, a cloud agent, or a developer without the protected files can test *nothing*. The observed consequences are exactly the two failure modes this document spends the most words forbidding: the agent stalls, or the agent "simplifies" the architecture until it runs where it happens to be sitting.

### 44.2 The port

Layer 2 (Part 6) is defined by an interface, not by COM:

```text
app/excel/port.py          ExtractionPort: the typed contract of layers 1–2
app/excel/com_adapter.py   the ONLY production implementation (pywin32, Parts 7 and 23.5)
app/excel/fixture_adapter.py  DEV/TEST ONLY: replays recorded or synthetic chunks
```

`ExtractionPort` yields exactly what Part 7 specifies — a stream of rectangular chunks plus workbook identity, sheet name, source row numbers, and the Part 7.7 lineage fields. Layers 3–10 depend on the port and never import COM, `pywin32`, or `win32com`. The architecture verifier enforces that import direction.

### 44.3 Adapter selection and the release rule

```text
adapter = com          default; the only adapter permitted in a release build
adapter = fixture      dev/test only; requires ADAPTER_FIXTURE_ACK=1 in the environment
```

Non-negotiable rules, all machine-checked:

1. A release build containing `fixture_adapter.py`, or capable of selecting the fixture adapter, **fails** `architecture verify --release`. The dev adapter never ships.
2. Any output produced through the fixture adapter is watermarked `DEMO DATA` in the UI, the dashboard JSON, the standalone HTML, and the run manifest (Part 0.4 rule 7).
3. `GATE_PROTECTED_FILE_PROOF` (Part 14 Phase 0, Part 28.1 Phase 1) can only ever be satisfied by the COM adapter against a real protected workbook. No amount of fixture testing advances it; it stays `conditional` with a named `next_action` until a Windows machine with the real files runs it.
4. The fixture adapter is not a fallback. It is never selected automatically, never selected on COM failure, and never selected to "keep the run green". COM failure follows Part 7.8 and Part 23.11 — fail closed. Automatic selection is the Part 27.8 "agent removes a dependency to make it portable" violation with a friendlier name.

### 44.4 What this buys

Phases 2–10 become fully testable on any machine, in CI, by any agent — while Phase 0/1 protected-file proof stays exactly as strict as 7.1 wrote it. The untestable part shrinks to the one layer that is genuinely environment-bound, instead of contaminating all ten. An agent is never blocked, and is never tempted to redesign the architecture to unblock itself.
