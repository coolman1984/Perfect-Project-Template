"""COM extraction adapter — the ONLY production implementation (Parts 7, 23.5).

This is the fragile part of the system, done carefully. Everything here runs on
Windows, in an interactive logged-in session, against files the logged-in user
is already authorized to open. **Never bypass DRM** (rule 1): we read only what
the user can already open, through their own Excel.

Implementation checklist — every line is a rule from Part 7 or 23.5:

    [ ] Prefer a dedicated hidden Excel instance owned by this run (7.1)
    [ ] Fall back to attach only on the EXACT full path; never a similar name
    [ ] Never close or save a workbook the user owns
    [ ] Open read-only, disable link updates, set calculation to manual
    [ ] Snapshot every Excel setting changed, restore it in `finally` — even
        after failure
    [ ] Record the PID of every Excel process this app creates; at startup
        terminate ONLY a verified stale process this app owns. Never mass-kill
        EXCEL.EXE — some processes belong to the employee (7.1 watchdog)
    [ ] Find data by table -> named range -> header row -> bounded discovery,
        in that priority order (7.2)
    [ ] Never trust UsedRange: Excel remembers deleted rows (7.2)
    [ ] Never map columns by position; map by approved name (7.2)
    [ ] Read Range.Value2 rectangular blocks, projecting only approved columns
    [ ] Size chunks in cells via port.rows_per_chunk (7.3)
    [ ] Write each chunk straight to staging; never hold the file in memory
    [ ] Detect the workbook's 1900 vs 1904 date system and pass it on (27.1)
    [ ] Release workbook, worksheet, range and application objects in `finally`
    [ ] Use timeouts, checkpoints and a recoverable WAITING_FOR_USER state for
        DRM prompts (22.5) — never click through a prompt blindly

If COM is genuinely blocked, follow Part 7.8 plans B/C/D and the Part 0.7
deviation process. Record which plan is active; never switch silently. Falling
back to the fixture adapter is forbidden (Part 44.3 rule 4).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from app.excel.port import Chunk, ExtractionPort, LineageStamp, WorkbookIdentity


class ComExtractionAdapter(ExtractionPort):
    """Reads protected workbooks through the authorized Excel desktop session."""

    #: The only adapter that can satisfy GATE_PROTECTED_FILE_PROOF (Part 44.3).
    provides_production_evidence = True

    def __init__(self) -> None:
        self._excel: Any = None
        self._workbook: Any = None
        self._owned_pid: int | None = None
        self._saved_settings: dict[str, Any] = {}
        self._identity: WorkbookIdentity | None = None

    def open(self, source_path: str, config: dict[str, Any]) -> WorkbookIdentity:
        raise NotImplementedError(
            "Implement in Phase 1 (protected-file proof) on a Windows machine "
            "with Excel and real DRM-protected files. See the checklist in this "
            "module's docstring and Constitution Parts 7.1, 7.2 and 23.5.")

    def chunks(self) -> Iterator[Chunk]:
        raise NotImplementedError(
            "Implement rectangular Value2 block reads with adaptive chunk "
            "sizing (Part 7.3). A per-cell loop is a release-blocking "
            "violation of rule 2: 20 million border crossings take hours, one "
            "block read takes seconds.")

    def lineage(self) -> LineageStamp:
        raise NotImplementedError(
            "Return the Part 7.7 lineage fields so every dashboard number "
            "traces back to its exact Excel row (rule 8).")

    def close(self) -> None:
        raise NotImplementedError(
            "Restore every changed Excel setting and release every COM object "
            "in a finally block, even after failure. Close only the process "
            "this run created (Part 23.5).")
