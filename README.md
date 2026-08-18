# Perfect Project Template — Offline Excel Intelligence

A reusable, self-verifying project template for building **secure offline
Excel-to-database web applications**: protected Excel files in, a trustworthy
one-page management dashboard out, with no internet, no installation for the
employee, and no invented business rules.

Hand this repository to any AI agent with one prompt from
[`AGENT_KICKOFF_PROMPT.md`](AGENT_KICKOFF_PROMPT.md) and it produces the same
shape of project every time.

---

## Start here

| You are | Read | Then |
|---|---|---|
| **The owner** | this file, then [`docs/CONSTITUTION_IMPROVEMENTS.md`](docs/CONSTITUTION_IMPROVEMENTS.md) | Copy a prompt from `AGENT_KICKOFF_PROMPT.md` and hand it to an agent |
| **An AI agent** | [`AGENTS.md`](AGENTS.md) → [`PROJECT_SKILL.md`](PROJECT_SKILL.md) → [`.ai/READ_FIRST.md`](.ai/READ_FIRST.md) | `PROJECT_TOOL doctor`, then work the task router |
| **A developer** | [`PROJECT_SKILL.md`](PROJECT_SKILL.md) §5–6 | `python3 -m unittest discover -s tests -t .` |

```bash
./project_tool.sh doctor          # Linux / macOS — one command, every verifier
PROJECT_TOOL.bat doctor           # Windows — the same tool
```

---

## What makes this a template and not a folder of documents

Most "AI project templates" are instructions an agent can ignore silently. Here
the rules are **executable**. Every claim an agent might make is checkable, and
the checks ship with the template:

| Command | What it actually enforces |
|---|---|
| `map verify` | Manifest hashes match the tree; no uncatalogued file; every agent entry pointer exists |
| `map context --task "…"` | Ranks files for one task within a token budget, so agents stop reading the whole repo |
| `architecture verify --source-scan` | No CDN, no runtime download, no `0.0.0.0` bind, no elevation, no COM outside the adapter, no dev tooling in production code, no credential literals |
| `architecture verify --baseline` | Every locked component from Part 23.8 is present; no self-authorized deviation |
| `constitution audit` | Part numbering, cross-references, command coverage, changelog agreement, and downgrade language in context |
| `gates status` | What is *actually proven*, with an evidence file that must exist on disk |
| `memory validate` | No source-free, malformed, conflicting or secret-bearing memory record |
| `report validate --mode production` | No unresolved `PENDING_APPROVAL`; no value approved by nobody |

All of it is **standard-library Python**, so it runs in a bare workspace, in CI,
on Windows, Linux or macOS, with nothing installed.

```text
108 tests · 0 failures · runs anywhere with Python 3.11+
```

---

## The product this template builds

```text
DRM-PROTECTED EXCEL  →  Excel desktop (the user's own authorized session)
   → ExtractionPort (COM adapter, Value2 rectangular blocks)
   → RAW STAGING  →  QUALITY GATE  →  CLEAN
   → HISTORY ENGINE ── DuckDB (brain) · Parquet (archive) · SQL Server (optional)
   → ANALYTICS (versioned SQL)  →  INSIGHTS (evidence objects)
   → DASHBOARD JSON  →  one-page local web app + standalone HTML  →  VERIFY
```

The employee only ever sees:

```text
Open app → add data → process → see quality → use dashboard → act / export
```

**Golden sentence:** *Excel is the authorized door to the data — Excel is not
the calculation engine.*

### The five rules that matter most

1. **Offline means bundle the dependencies — never delete them.** "I made it
   simpler by using only Windows and Excel" is a release-blocking violation.
2. **"No external server" does not mean "no local server."** The bundled
   FastAPI/Uvicorn API on `127.0.0.1` stays. A user-mode loopback socket has
   never needed administrator rights.
3. **Never invent business meaning.** Grain, business key, formulas, thresholds
   and deletion rules belong to a named human.
4. **Trusted arithmetic lives in versioned SQL.** JavaScript displays; it never
   calculates.
5. **A failure never corrupts trusted history.** The dashboard keeps showing the
   last good data — and says so.

---

## Layout

```text
constitution/     the law: 45 Parts, v7.2 (v7.1 verbatim + Parts 36-44)
AGENTS.md         universal agent entry pointer (Claude/Cline/Copilot mirror it)
PROJECT_SKILL.md  mandatory first read: product, map, task router, runbook
.ai/              READ_FIRST · PROJECT_MAP · CURRENT_STATE · CONTRACTS
                  LESSONS · OPPORTUNITIES · MEMORY.jsonl · MAP_MANIFEST.json
acceptance/       gates.yaml — what is actually proven, with evidence
contracts/        config · dashboard · event · manifest schemas
                  error_codes.json · run_states.json
app/              the ten layers; pure logic is complete, environment-bound
                  code carries its task contract and fails loudly
web/              one-page shell, design tokens, filter state, i18n (en + ar)
reports/_TEMPLATE report definition, config, mappings, metrics, quality, SQL
tools/            the portable tool tier — stdlib only, runs anywhere
tests/            unit · integration · golden · failure · browser
                  architecture · constitution · performance
docs/             improvements · changelog · operations · security · acceptance
```

## What is complete vs. what an agent builds

Being honest about this is the point — a template that overstates itself teaches
agents to overstate too.

| Complete and working | Left for the agent to build |
|---|---|
| The whole portable toolchain and every verifier | Excel COM extraction (needs Windows + Excel + real files) |
| Constitution v7.2 with machine-checked consistency | DuckDB staging, history engine, archive |
| Contracts: config, dashboard, event, manifest, errors, states | Quality engine and reconciliation |
| Run state machine, error registry, value conversion, chunk sizing | Metric SQL, insights, JSON and HTML builders |
| Fixture extraction adapter + synthetic data | The loopback API implementation |
| Gate ledger seeded with every Part 14/28/31/33 gate | Chart rendering, story mode, motion |
| Web shell structure, design tokens, filter state, i18n | PyInstaller release, wheelhouse, clean-PC gate |
| 108 passing tests | Everything downstream of a real report definition |

Every unbuilt piece raises `NotImplementedError` with its task contract and the
Part that governs it. Nothing pretends to work.

---

## Instantiating a project

```bash
./project_tool.sh doctor                                   # verify the skeleton
./project_tool.sh report new --id daily_production \
                            --title "Daily Production"     # scaffold a report
./project_tool.sh report validate --id daily_production    # lists open approvals
```

Then fill `reports/daily_production/report_definition.md` **with the business
owner**. That is a hard gate: no extraction code is written until the definition
is approved. The agent writes the structure; a named human writes the meaning.

---

## Origin

Built from `ULTIMATE_EXCEL_AUTOMATION_SKILL_AND_MASTER_PLAN1.md` (v7.1), which
is preserved **verbatim** as Parts 0–35 of
[`constitution/EXCEL_AUTOMATION_CONSTITUTION.md`](constitution/EXCEL_AUTOMATION_CONSTITUTION.md).

Parts 36–44 are additive amendments that close nine executability gaps — they
add no prerequisite, remove no locked component and weaken no gate. What changed
and why: [`docs/CONSTITUTION_IMPROVEMENTS.md`](docs/CONSTITUTION_IMPROVEMENTS.md).
