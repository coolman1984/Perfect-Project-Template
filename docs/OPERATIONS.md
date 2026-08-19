# Operations and recovery

Constitution Parts 12, 30.6.

## Weekly operation

1. Extract the delivered ZIP once.
2. Double-click `START.bat`; the browser opens automatically.
3. Choose the report.
4. Add the new or corrected files.
5. Confirm the detected period and source roles.
6. Process, and watch real progress.
7. Resolve only explicit user-action requests.
8. Review quality and reconciliation.
9. Open the new dashboard **only after** publication succeeds.
10. Confirm the week appears in history.
11. Back up according to the retention policy.

## The golden operating rule

> **If a run fails, the dashboard keeps showing the last good data — and says so
> clearly on screen.**

Never show broken numbers. Never show a blank page. Show the last truth, with
its date.

## Five-minute troubleshooting (Part 12.5)

| Symptom | Check first | Fix |
|---|---|---|
| Run never started | Was the user logged on? | Reschedule, or stay logged in — COM needs an interactive session |
| Excel hangs | The run evidence for the Excel PID **this app created** | Close only that owned process after a graceful timeout. **Never kill all `EXCEL.EXE`** — some belong to the employee |
| "File in use" | Someone has it open | Read-only open handles most cases; otherwise retry |
| Control total mismatch | Quality report → which source | Compare clean vs raw for that report |
| Row count dropped sharply | Source file modified date, sheet name | Confirm with the file owner **before** loading |
| New column error | `schema_diff.json` | Update `report.toml`, raise the version, rerun |
| Dashboard shows an old date | Last run status | Read `run.log.jsonl` |
| "Part of the application is missing" | The support code | `SETUP_OFFLINE.bat` restores from the sealed repair payload |

## Recovery (Part 8.6)

| Situation | Action | Cost |
|---|---|---|
| Calculation logic changed | Drop clean + analytics, rebuild from raw | Minutes, no Excel needed |
| A period was wrong | Delete that `run_id` batch, re-extract those files, reload | Minutes |
| Database lost | Rebuild from the Parquet archive | Minutes |
| Archive lost | Re-extract from Excel | Slow — hence backups |

## Destructive procedures

Deliberately absent from the `PROJECT_SKILL.md` command index (Part 24.2) so
they cannot be run casually. Each requires an operator decision and a recorded
reason:

- **Rebuild database from archive** — `tools/rebuild_database.py`. Verify the
  archive is complete first; reconcile control totals after.
- **Delete a run batch** — identify the exact `run_id`; confirm no later run
  depends on it; take a backup first.
- **Replace a period** — validate the source's actual min/max dates against the
  requested partition before deleting anything (Part 27.4).

## Escalation

| Level | When | What to provide |
|---|---|---|
| Operator | Any user-action state | Follow the on-screen instruction |
| Support | Any support code | The code, the run ID, the data date |
| IT | `LOCAL_LOOPBACK_BIND_FAILED`, `PACKAGE_COMPONENT_BLOCKED`, `ELEVATION_FORBIDDEN` | The support code plus `LOCAL_TRANSPORT_EVIDENCE.json` |
| Data owner | `DQ_CONTROL_TOTAL_MISMATCH`, `SQL_RECONCILIATION_FAILED` | The quality report and the run manifest |
