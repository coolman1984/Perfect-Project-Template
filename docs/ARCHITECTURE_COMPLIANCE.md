# Architecture compliance

Constitution Parts 0.7, 0.8, 23.8, 23.9.

## Handshake

Reported before production code is written (Part 0.8):

```text
approved external prerequisites: Windows + desktop Excel only
bundled runtime: planned
bundled libraries/assets: planned
local loopback API: retained; 127.0.0.1; standard-user process
administrator/elevation/service/firewall changes: NONE
forbidden runtime downloads: verified (architecture verify --source-scan)
architecture deviations: none
```

Verify at any time:

```bash
./project_tool.sh architecture verify --baseline
./project_tool.sh architecture verify --source-scan
```

## Locked components

`IMPLEMENTATION_BASELINE.lock.json` is the machine-readable contract; Part 23.8
is the prose. Pinning a version is ordinary work. **Removing or replacing a
component is an architecture deviation** requiring explicit user approval.

## Precedence

```text
1. User's latest explicit approval
2. This constitution and its locked baseline
3. Approved architecture decision records
4. Versioned contracts and dependency lock
5. Existing implementation
6. Agent preference, convenience, or "simpler idea"
```

Existing code is not automatically correct just because it exists. An
agent-authored decision record without user approval cannot override the
baseline.

## What an agent may never do alone

- Remove Python, `pywin32`, DuckDB, Parquet, FastAPI/Uvicorn/Pydantic, ECharts,
  packaging, tests or the map engine.
- Replace the local application with static HTML, an Excel-only workbook, a
  PowerShell-only script, a CSV/JSON folder, or browser storage.
- Use Excel as the database or the trusted calculation engine.
- Assume system Python, Node.js, pip, npm, Git, an editor, a terminal or
  internet access.
- Use a CDN, remote font, remote icon, telemetry endpoint or runtime download.
- Remove a feature because its dependency is difficult to package.
- Change the architecture first and tell the user afterwards.
- Describe a downgrade as "more portable", "simpler", "native" or "closer to
  copy-and-run".

## Deviation request template

Copy into `docs/decisions/` and fill completely. **No deviation is implemented
until the user explicitly approves it.** Silence, time pressure, package size,
personal preference and untested assumptions are not approval.

```text
Decision ID:
Date:
Component and contract affected:
Measured incompatibility evidence:      (measurements, not opinions)
Options considered:
Proposed replacement:
Lost capabilities:
Offline / package / security impact:
Migration and rollback:
Equivalence tests:
Explicit user approval required: YES
Approved by:                            (a named human)
Approved at:
```

## Deviation register

| ID | Component | Status | Approved by | Date |
|---|---|---|---|---|
| _(none)_ | | | | |
