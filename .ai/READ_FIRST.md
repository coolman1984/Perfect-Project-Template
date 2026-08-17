# READ FIRST — the 90-second start

Constitution Part 0.1. Keep this file under 150 lines (Part 20.2).

## The sequence

```text
1. PROJECT_SKILL.md          already read? good. if not, read it now.
2. PROJECT_TOOL doctor       one command, every verifier
3. PROJECT_TOOL map context --task "<your task>" --budget 4000
4. .ai/CURRENT_STATE.md  and  .ai/CONTEXT_PACK.md
5. open ONLY the files the router named, plus direct dependencies
```

Windows `PROJECT_TOOL.bat` · Linux/macOS `./project_tool.sh` — same tool (Part 37.2).

## Token budget

For an ordinary change, load only:

```text
PROJECT_SKILL.md
.ai/CURRENT_STATE.md
.ai/CONTEXT_PACK.md
the exact task request
```

Then open the smallest task-specific set the map names. Do not run a full-tree
read, import every document, or inspect generated/runtime/vendor folders. Need
more? Record why, and expand **one dependency boundary at a time** (Part 0.2).

## Stop conditions

Stop immediately, and say why, when:

| Condition | Action |
|---|---|
| `doctor` FAILS | Repair what it reports before any feature work (Part 0.1 step 7) |
| `doctor` says BLOCKED | Something was not verified. Never report it as a pass (Part 37.4) |
| A business rule is unknown | Write `PENDING_APPROVAL`, ask the named owner (Parts 3.1, 41) |
| A locked component seems incompatible | Part 0.7 deviation request; wait for explicit approval |
| You are about to call something "simpler", "more portable" or "native" | That phrasing is itself a compliance signal (Part 34.4) |
| The map contradicts the code | Code wins temporarily; repair the map in the same task (Part 27.8) |

## Exit codes

```text
0  pass
1  fail      a real violation you must fix
2  usage     bad arguments
3  blocked   a prerequisite is missing and NOTHING was verified
```

Exit 3 is not a pass. It exists precisely so you can tell "verified and clean"
apart from "could not verify" (Part 37.4).

## What this project will not let you do

- Remove Python, `pywin32`, DuckDB, Parquet, FastAPI/Uvicorn/Pydantic, ECharts,
  packaging, tests or the map engine (Part 0.7).
- Replace the app with static HTML, an Excel-only workbook, a PowerShell script,
  a CSV/JSON folder, or browser storage (Part 0.7).
- Use Excel as the database or the calculation engine (Part 1.3).
- Assume system Python, Node.js, pip, npm, Git, an editor, a terminal or the
  internet at runtime (Part 0.6).
- Use a CDN, remote font, remote icon, telemetry endpoint or runtime download
  (Part 23.6).
- Invent a business key, threshold, formula, target or deletion rule (Part 41).

Each of these is machine-checked. `architecture verify --source-scan` will find
them, so there is no benefit to trying.

## Before you report done

```text
PROJECT_TOOL map verify
PROJECT_TOOL architecture verify --source-scan
PROJECT_TOOL constitution audit
PROJECT_TOOL memory validate
PROJECT_TOOL gates status
PROJECT_TOOL memory suggest --task "<what you did>" --max 3
```

Then update `.ai/CURRENT_STATE.md`, refresh the map, and record evidence with
`PROJECT_TOOL gates set --id <GATE> --status pass --evidence <path>`.

A gate cannot pass on a sentence. The evidence path must exist on disk
(Part 38.2 rule 1).
