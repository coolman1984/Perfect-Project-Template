# Report definition — <REPORT_TITLE>

> **Hard gate (Constitution Part 4).** No extraction code is written until this
> file is filled in and approved by the named business owner. A guessed business
> rule is the most expensive bug in this system.
>
> **The AI agent fills in the *structure*. A named human fills in the
> *meaning*.** An agent may write `PENDING_APPROVAL` freely; an agent may never
> resolve one (Part 41.3).

---

## Identity

| Field | Value |
|---|---|
| Report name | `<REPORT_TITLE>` |
| Report id | `<REPORT_ID>` |
| Business owner (approves meaning) | `PENDING_APPROVAL` |
| Data/report owner (responsible) | `PENDING_APPROVAL` |
| Frequency | `PENDING_APPROVAL` |
| Data period | `PENDING_APPROVAL` |

## Purpose — the decision this supports

Part 26.1: a chart without a decision question is removed.

| Question | Answer |
|---|---|
| Who is the audience? | `PENDING_APPROVAL` |
| What must they decide? | `PENDING_APPROVAL` |
| When do they decide it? | `PENDING_APPROVAL` |
| What can they change after seeing it? | `PENDING_APPROVAL` |
| Which trusted measures support that action? | `PENDING_APPROVAL` |

## Grain — what ONE ROW means

> Write this as a full sentence. "One row is one production order, for one
> model, on one line, on one production date."

`PENDING_APPROVAL`

## Business key

The columns that make one row unique. This decides what "the same record"
means, so it decides what an update is (Part 8.2).

`PENDING_APPROVAL`

## Sources

| Role | File pattern | Sheet | Required? | Notes |
|---|---|---|---|---|
| `PENDING_APPROVAL` | | | | |

## Measures and fields

| Field | Meaning | Type | Unit | Nullable? |
|---|---|---|---|---|
| `PENDING_APPROVAL` | | | | |

## History behaviour

| Question | Answer |
|---|---|
| Load mode (append / upsert / snapshot / replace_period) | `PENDING_APPROVAL` |
| Lookback window in days (how far back do real corrections happen?) | `PENDING_APPROVAL` |
| What does it mean when a row disappears from the source? | `PENDING_APPROVAL` |

Deletion options (Part 8.4) — the system must know this in advance, never infer
it: `ignore` · `mark_inactive` · `soft_delete` · `close_version` · `physical`

## Units and time

| Field | Value |
|---|---|
| Currency | `PENDING_APPROVAL` |
| Units | `PENDING_APPROVAL` |
| Time zone | `PENDING_APPROVAL` |
| Fiscal calendar | `PENDING_APPROVAL` |

## Quality rules

| Rule | Value |
|---|---|
| Control total column (the strongest check, Part 9.4) | `PENDING_APPROVAL` |
| Maximum duplicate business-key rate | `PENDING_APPROVAL` |
| Maximum required-null rate | `PENDING_APPROVAL` |
| Maximum row-count change vs history | `PENDING_APPROVAL` |
| Which rules are blocking vs warning? | `PENDING_APPROVAL` |

## Security and retention (Part 13.5)

⚠️ Extracted Parquet, DuckDB, JSON, HTML, exports and logs contain the same data
as the protected Excel files, **without** the DRM protection. That is a real
change in security posture. Get written answers:

| Question | Answer | Approved by |
|---|---|---|
| Where may the warehouse and archive folders live? | `PENDING_APPROVAL` | |
| Who may read them? | `PENDING_APPROVAL` | |
| Does the dashboard output need restriction? | `PENDING_APPROVAL` | |
| How long may extracted data be retained? | `PENDING_APPROVAL` | |
| Is any external AI service permitted to see this data? | `PENDING_APPROVAL` | |

> A project switched off in month 3 is worse than one that started a week later.

## Approval record

| Item | Approved by | Date (UTC) | Evidence |
|---|---|---|---|
| Grain | | | |
| Business key | | | |
| Load mode and deletion rule | | | |
| Metric definitions | | | |
| Quality thresholds | | | |
| Storage and retention | | | |

Both halves are required: a filled value with an empty approver counts as
unapproved (Part 41.2).
