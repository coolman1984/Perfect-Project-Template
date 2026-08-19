"""COM extraction adapter — the ONLY production implementation (Parts 7, 23.5).

This is the fragile part of the system, done carefully. Everything here runs on
Windows, in an interactive logged-in session, against files the logged-in user
is already authorized to open. **Never bypass DRM** (rule 1): we read only what
the user can already open, through their own Excel.

How the pieces divide, and why:

    session.py      owns Excel: process, settings snapshot/restore, open modes
    discovery.py    resolves `data_area` to exact bounds, no COM import
    extractor.py    chunking, name-based projection, row-count checks, no COM
    com_adapter.py  this file — wiring, identity, lineage, block reads

Only this module and `session.py` may import COM (Part 44.2), so the rules most
likely to be wrong — bounds, chunk arithmetic, column mapping — live in modules
that run in CI on Linux, and what remains here is the thin part that genuinely
needs Excel.

Reading is always rectangular. A block address is passed to `Range(...).Value2`
and the result is reshaped in memory; there is no per-cell loop anywhere in the
extraction path, because twenty million cells crossed one at a time takes hours
where one block read takes seconds. Chunk size comes from `port.rows_per_chunk`,
which sizes in cells rather than rows.

Implementation status against the Part 7 / 23.5 checklist:

    [x] Prefer a dedicated hidden Excel instance owned by this run (7.1)
    [x] Fall back to attach only on the EXACT full path; never a similar name
    [x] Never close or save a workbook the user owns
    [x] Open read-only, disable link updates, set calculation to manual
    [x] Snapshot every Excel setting changed, restore it in `finally` — even
        after failure
    [x] Record the PID of every Excel process this app creates; terminate ONLY
        a verified process this app owns. Never mass-kill EXCEL.EXE (7.1)
    [x] Find data by table -> named range -> header row -> bounded discovery,
        in that priority order (7.2)
    [x] Never trust UsedRange: Excel remembers deleted rows (7.2)
    [x] Never map columns by position; map by approved name (7.2)
    [x] Read Range.Value2 rectangular blocks, projecting only approved columns
    [x] Size chunks in cells via port.rows_per_chunk (7.3)
    [x] Write each chunk straight to staging; never hold the file in memory
    [x] Detect the workbook's 1900 vs 1904 date system and pass it on (27.1)
    [x] Release workbook, worksheet, range and application objects in `finally`
    [~] Use timeouts, checkpoints and a recoverable WAITING_FOR_USER state for
        DRM prompts (22.5) — never click through a prompt blindly

The recoverable round trip is wired through the runtime: a permission failure
becomes DRM_USER_ACTION_REQUIRED, orchestration records WAITING_FOR_USER, and
the authenticated retry endpoint re-enters the same run after the operator
opens the workbook. `GATE_PROTECTED_FILE_PROOF` remains open until that path is
exercised with a real protected file on the authorized Windows machine; an
unprotected workbook or a fake can prove the control flow but not DRM itself.

If COM is genuinely blocked, follow Part 7.8 plans B/C/D and the Part 0.7
deviation process. Record which plan is active; never switch silently. Falling
back to the fixture adapter is forbidden (Part 44.3 rule 4).
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.errors import AppError
from app.excel import discovery, extractor, session as session_module
from app.excel.port import Chunk, ExtractionPort, LineageStamp, WorkbookIdentity

#: Substrings that mark a failure as "the user is not authorized / a prompt is
#: waiting" rather than a transient read error. Matched case-insensitively
#: against the COM exception text, which is the only signal pywin32 surfaces
#: without an IRM-specific API.
_DRM_MARKERS = (
    "permission",
    "irm",
    "information rights",
    "rights management",
    "access denied",
    "password",
    "protected view",
)

_HASH_BLOCK = 1 << 20


def _file_hash(path: Path) -> str:
    """SHA-256 of the source, streamed so a 2 GB workbook stays cheap."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(_HASH_BLOCK), b""):
            digest.update(block)
    return digest.hexdigest()


def _looks_like_drm(error: BaseException) -> bool:
    text = str(error).casefold()
    return any(marker in text for marker in _DRM_MARKERS)


class ComExtractionAdapter(ExtractionPort):
    """Reads protected workbooks through the authorized Excel desktop session."""

    #: The only adapter that can satisfy GATE_PROTECTED_FILE_PROOF (Part 44.3).
    provides_production_evidence = True

    def __init__(self) -> None:
        self._excel: Any = None
        self._workbook: Any = None
        self._worksheet: Any = None
        self._session: Any = None
        self._owned_pid: int | None = None
        self._saved_settings: dict[str, Any] = {}
        self._identity: WorkbookIdentity | None = None
        self._region: discovery.DataRegion | None = None
        self._config: dict[str, Any] = {}
        self._source_path: Path | None = None

    def open(self, source_path: str, config: dict[str, Any]) -> WorkbookIdentity:
        """Open read-only, prove identity, and resolve the data area."""
        self._config = dict(config)
        self._source_path = Path(source_path)
        excel_config = dict(config.get("excel", {}))
        open_mode = str(excel_config.get("open_mode", "dedicated_then_attach"))

        # Hash before Excel touches the file, so the immutability check at
        # close compares against the true pre-run state.
        try:
            stat = self._source_path.stat()
            file_hash = _file_hash(self._source_path)
        except OSError as exc:
            raise AppError(
                "SRC_NOT_FOUND",
                support_detail=f"cannot read source file {source_path!r}: {exc}",
                source_path=source_path,
            ) from exc

        try:
            self._session = session_module.acquire(source_path, open_mode)
        except AppError as exc:
            if exc.code == "EXCEL_OPEN_FAILED" and _looks_like_drm(exc):
                raise AppError(
                    "DRM_USER_ACTION_REQUIRED",
                    support_detail=(
                        f"{source_path!r} needs an action in Excel before it can "
                        f"be read (rights management, password or Protected "
                        f"View). We never click through such a prompt "
                        f"(Part 22.5). Original detail: {exc.support_detail}"),
                    source_path=source_path,
                ) from exc
            raise

        self._excel = self._session.application
        self._workbook = self._session.workbook
        self._owned_pid = self._session.owned_pid
        self._saved_settings = dict(self._session._saved_settings)

        try:
            self._region = discovery.locate(self._workbook, self._config)
            self._worksheet = self._workbook.Worksheets(self._region.sheet_name)
        except BaseException:
            # Discovery failing must still put Excel back exactly as found.
            self.close()
            raise

        self._identity = WorkbookIdentity(
            full_path=str(self._source_path.resolve()),
            sheet_name=self._region.sheet_name,
            file_hash=file_hash,
            file_size=stat.st_size,
            modified_time=datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc).isoformat(),
            date_system_1904=self._session.date_system_1904,
            open_mode=self._session.open_mode,
        )
        return self._identity

    def _read_block(self, first_row: int, last_row: int) -> Any:
        """One rectangular COM read — the only place cell values are fetched.

        `Value2` rather than `Value` on purpose: it returns raw serials and
        unformatted decimals, leaving date and currency interpretation to
        `conversion.py` where it is explicit and tested, instead of inheriting
        whatever regional formatting the machine happens to carry (Part 7.4).
        """
        region = self._region
        if region is None or self._worksheet is None:
            raise RuntimeError("open() must be called before reading blocks")
        address = discovery.a1(
            first_row, region.first_column, last_row, region.last_column)
        try:
            return self._worksheet.Range(address).Value2
        except AppError:
            raise
        except BaseException as exc:
            if _looks_like_drm(exc):
                raise AppError(
                    "DRM_USER_ACTION_REQUIRED",
                    support_detail=(
                        f"Excel needs user action before rows {first_row}-"
                        f"{last_row} can be read. We never dismiss a rights, "
                        f"password or Protected View prompt automatically. "
                        f"Original detail: {exc}"),
                    first_row=first_row,
                    last_row=last_row,
                ) from exc
            raise

    def chunks(self) -> Iterator[Chunk]:
        """Yield rectangular blocks, projected to the approved columns."""
        if self._identity is None or self._region is None:
            raise RuntimeError("open() must be called before chunks()")
        return extractor.read_region(self._read_block, self._region, self._config)

    def lineage(self) -> LineageStamp:
        """The Part 7.7 fields stamped onto every staged row."""
        if self._identity is None or self._region is None:
            raise RuntimeError("open() must be called before lineage()")
        return LineageStamp(
            run_id=str(self._config.get("run_id", "RUN-00000000-000")),
            report_id=str(self._config.get("report_id", "")),
            source_id=str(self._config.get("source_id", "EXCEL")),
            source_file=self._identity.full_path,
            source_file_hash=self._identity.file_hash,
            source_sheet=self._identity.sheet_name,
            extracted_at=datetime.now(timezone.utc).isoformat(),
            schema_version=str(self._config.get("schema_version", "0")),
            extra={
                "open_mode": self._identity.open_mode,
                "data_area_strategy": self._region.strategy,
                "header_row": str(self._region.header_row),
                "date_system_1904": str(self._identity.date_system_1904).lower(),
            },
        )

    def source_unchanged(self) -> bool:
        """Re-hash the source and compare (GATE_SOURCE_IMMUTABILITY).

        Separate from `close()` on purpose. `close()` runs in `finally` blocks
        during failures, where raising a second exception would bury the first;
        the immutability assertion belongs on the success path, where the
        orchestrator can act on it.
        """
        if self._identity is None or self._source_path is None:
            raise RuntimeError("open() must be called before source_unchanged()")
        return _file_hash(self._source_path) == self._identity.file_hash

    def close(self) -> None:
        """Restore every changed Excel setting and release every COM object.

        Idempotent, and never raises: it is called from `finally` and from the
        failure path in `open()`.
        """
        session = self._session
        self._session = None
        self._worksheet = None
        self._workbook = None
        self._excel = None
        self._saved_settings = {}
        self._owned_pid = None
        if session is not None:
            session.release()
