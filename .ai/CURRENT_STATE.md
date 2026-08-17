# CURRENT STATE

The latest proven operational truth (Constitution Part 20.2). Always read this.
Update it in the **same change set** as the code it describes (Part 21.5).

> Claims here must be supported by evidence. `map verify` fails when this file
> asserts a feature or test result the evidence does not support (Part 20.5).
> The authoritative gate status is `acceptance/gates.yaml`.

---

## Status

| | |
|---|---|
| **Phase** | −2 — template, not yet instantiated (Part 39) |
| **Application version** | 0.0.0 |
| **Constitution version** | 7.2 |
| **Report configured** | none |
| **Last verified** | on first `PROJECT_TOOL doctor` run |

## What works right now

- The portable tool tier: `doctor`, `map`, `memory`, `architecture`,
  `constitution`, `gates`, `report` all run on Windows, Linux and macOS.
- The constitution audit, architecture source scan, gate ledger and memory
  validation all execute and enforce real rules.
- The template scaffold: contracts, entry pointers, report template, app and web
  skeletons, tests, launchers.

## What does not work yet

Everything that touches real data. This is a scaffold, not a running product:

- No report is configured. No business meaning is approved.
- `app/` modules define their contracts and raise `NotImplementedError`.
- No Excel extraction, no database, no analytics, no dashboard rendering.
- No release has been built; no clean-PC gate has been run.

## Pending decisions

All of Part 18 is open. The blocking subset for the first slice:

```text
[ ] Which report is first, and who is its business owner?
[ ] What does ONE ROW mean (grain)?
[ ] What is the business key?
[ ] Which column is the control total?
[ ] Which load mode, and what lookback window?
[ ] What does a disappearing row mean (deletion behaviour)?
[ ] Where may extracted data be stored (IT approval)?
[ ] SQL Server: now, later, or never?
[ ] Is AI narrative allowed on this data?
[ ] Which decision must the dashboard support, and who makes it?
```

Do **not** ask the user to redesign or reconfirm the architecture — it is
already approved by the constitution (Part 18).

## Known risks

| Risk | Response |
|---|---|
| Protected-file extraction cannot be proven off Windows | Build everything else against fixtures; `GATE_PROTECTED_FILE_PROOF` stays conditional (Part 44.3 rule 3) |
| An agent "simplifies" the architecture to make it run locally | `architecture verify --source-scan` blocks it; Part 44 removes the motive |
| Business meaning gets invented under time pressure | `PENDING_APPROVAL` sentinels fail production validation (Part 41.3) |

## Next safe tasks

1. Run Phase −2 instantiation: choose the project slug, first report id and title.
2. Pin versions in `IMPLEMENTATION_BASELINE.lock.json` (Phase −1).
3. Fill `reports/<id>/report_definition.md` **with the business owner** (Phase 0).
4. Only then write extraction code (Part 4 hard gate).
