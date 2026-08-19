"""Excel session ownership (Part 7.1).

Task contract (Part 17.1):

    LAYER             layer 1
    INPUTS            source config + open mode
    OUTPUTS           an open read-only workbook
    VALIDATION        source file unchanged; the correct workbook matched by exact full path
    FAILURE BEHAVIOR  Restore every changed Excel setting in `finally`. Close only the
                      process this run created — never all EXCEL.EXE (Part 23.5).

This module and `com_adapter.py` are the only two files permitted to import COM
(`architecture verify --source-scan`, Part 44.2). The imports are deliberately
*inside* the functions that need them: the module must stay importable on Linux
so the rest of the suite runs in CI, where `pywin32` does not exist.

Two open modes, and the difference matters for the employee's data:

`dedicated` starts a hidden Excel process that this run owns. It is the default
because owning the process means we may safely close it. `attach` reaches into
the Excel the employee already has running, matches the **exact** full path via
`identity.verify`, and then treats everything it finds as borrowed — it never
closes the workbook, never quits the application, and never saves.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from app.errors import AppError
from app.excel import identity

#: Excel enum values, inlined as plain integers so this module needs no COM
#: import to name them and `discovery` can share them without one at all.
XL_CALCULATION_MANUAL = -4135
XL_UP = -4162
XL_TO_LEFT = -4159

#: Worksheet limits, used as anchors for bounded discovery (Part 7.2). Walking
#: up from the last row is how we find real data without trusting UsedRange,
#: which keeps remembering rows the user deleted years ago.
SHEET_MAX_ROWS = 1_048_576
SHEET_MAX_COLUMNS = 16_384

#: `dedicated_then_attach` is the config default (report schema, `[excel]`):
#: prefer a process we own, and fall back to the employee's session only when
#: starting our own fails — typically because the file is already open there and
#: Excel will not open it twice.
OPEN_MODES = ("dedicated", "attach", "dedicated_then_attach")

#: Application-level settings we change and must put back (Part 23.5). Each is
#: restored individually so one unwritable property cannot strand the others.
_MANAGED_SETTINGS = (
    "ScreenUpdating",
    "DisplayAlerts",
    "EnableEvents",
    "AskToUpdateLinks",
    "Calculation",
    "Visible",
)


def _com_modules() -> tuple[Any, Any, Any]:
    """Import pywin32 on first use, translating absence into a registry code.

    Off Windows — or on a Windows box without pywin32 — this raises
    `EXCEL_NOT_AVAILABLE` rather than `ImportError`, so the operator sees the
    Part 22.8 error screen instead of a stack trace.
    """
    try:
        import pythoncom
        import win32com.client
        import win32process
    except ImportError as exc:  # pragma: no cover - platform dependent
        raise AppError(
            "EXCEL_NOT_AVAILABLE",
            support_detail=(
                f"COM support is unavailable on this machine: {exc}. Extraction "
                f"requires Windows, an interactive session and a licensed Excel "
                f"(Part 44.1)."),
        ) from exc
    return pythoncom, win32com.client, win32process


def verify_com_binding() -> None:
    """Prove the packaged pywin32 binding imports through the authorized layer."""
    _com_modules()


@dataclass
class ExcelSession:
    """An open, read-only workbook plus everything needed to put Excel back.

    Held rather than returned piecemeal because the restore obligation and the
    workbook have exactly the same lifetime: whoever holds one must run the
    other's cleanup.
    """

    application: Any
    workbook: Any
    open_mode: str
    #: PID of the Excel process this run created. `None` in attach mode, which
    #: is what stops `release()` from quitting the employee's own Excel.
    owned_pid: int | None = None
    #: Whether *we* opened this workbook. Attach-mode workbooks are borrowed.
    owns_workbook: bool = False
    _saved_settings: dict[str, Any] = field(default_factory=dict)

    @property
    def date_system_1904(self) -> bool:
        """The workbook's date epoch (Part 27.1).

        A 1904-system workbook read as 1900 is wrong by 1,462 days, silently.
        """
        try:
            return bool(self.workbook.Date1904)
        except Exception:  # pragma: no cover - COM property availability
            return False

    def release(self) -> None:
        """Restore settings and release COM objects. Safe to call twice.

        Ordering is deliberate: settings first (so a failure to close still
        leaves Excel usable), then the workbook, then the application. Every
        step is individually guarded because this runs in a `finally` block
        during failures, where raising again would mask the original error.
        """
        try:
            self._restore_settings()
        finally:
            workbook, application = self.workbook, self.application
            self.workbook = None
            self.application = None

            if workbook is not None and self.owns_workbook:
                try:
                    # SaveChanges=False is the whole point: the source file is
                    # read-only input and must come back byte-identical
                    # (GATE_SOURCE_IMMUTABILITY).
                    workbook.Close(SaveChanges=False)
                except Exception:
                    pass

            if application is not None and self.owned_pid is not None:
                try:
                    application.Quit()
                except Exception:
                    pass
                self._terminate_owned_process()

    def _restore_settings(self) -> None:
        for name, value in self._saved_settings.items():
            try:
                setattr(self.application, name, value)
            except Exception:
                # One un-restorable property must not prevent the others from
                # being put back.
                continue
        self._saved_settings = {}

    def _terminate_owned_process(self) -> None:
        """Last resort for the process *this run* created (Part 7.1 watchdog).

        Scoped to a single recorded PID. Never enumerates or mass-kills
        EXCEL.EXE — some of those processes hold the employee's unsaved work.
        """
        pid = self.owned_pid
        self.owned_pid = None
        if pid is None:
            return
        try:
            import win32api
            import win32con
        except ImportError:  # pragma: no cover - platform dependent
            return
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
        except Exception:
            # Already gone, which is the expected outcome after a clean Quit().
            return
        try:
            win32api.TerminateProcess(handle, 0)
        finally:
            win32api.CloseHandle(handle)

    def __enter__(self) -> ExcelSession:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.release()


def _snapshot_and_configure(application: Any, *, hide: bool) -> dict[str, Any]:
    """Record current settings, then apply the extraction-safe ones.

    Returns only the settings actually read, so `release()` restores exactly
    what it captured and never invents a value for a property this Excel build
    does not expose.
    """
    saved: dict[str, Any] = {}
    for name in _MANAGED_SETTINGS:
        try:
            saved[name] = getattr(application, name)
        except Exception:
            continue

    desired = {
        "ScreenUpdating": False,
        "DisplayAlerts": False,      # never prompt a headless run
        "EnableEvents": False,       # workbook macros must not fire on open
        "AskToUpdateLinks": False,   # links stay stale; we read stored values
        "Calculation": XL_CALCULATION_MANUAL,
    }
    if hide:
        # Only for a process we own. Hiding the employee's Excel would look
        # like a crash to them.
        desired["Visible"] = False

    for name, value in desired.items():
        if name not in saved:
            continue
        try:
            setattr(application, name, value)
        except Exception:
            saved.pop(name, None)
    return saved


def _process_id(application: Any) -> int | None:
    _, _, win32process = _com_modules()
    try:
        _thread_id, pid = win32process.GetWindowThreadProcessId(application.Hwnd)
        return int(pid) or None
    except Exception:  # pragma: no cover - COM/window availability
        return None


def _open_dedicated(source_path: str) -> ExcelSession:
    pythoncom, client, _ = _com_modules()
    pythoncom.CoInitialize()

    try:
        # DispatchEx forces a *new* process rather than binding to the
        # employee's running Excel, which is what makes this instance ours to
        # close (Part 7.1).
        application = client.DispatchEx("Excel.Application")
    except Exception as exc:
        raise AppError(
            "EXCEL_NOT_AVAILABLE",
            support_detail=f"could not start a dedicated Excel process: {exc}",
        ) from exc

    session = ExcelSession(
        application=application,
        workbook=None,
        open_mode="dedicated",
        owned_pid=_process_id(application),
        owns_workbook=True,
    )
    session._saved_settings = _snapshot_and_configure(application, hide=True)

    try:
        session.workbook = application.Workbooks.Open(
            Filename=source_path,
            UpdateLinks=0,                  # 0 = never update
            ReadOnly=True,
            IgnoreReadOnlyRecommended=True,
            AddToMru=False,                 # keep the employee's MRU list clean
            Notify=False,
        )
    except Exception as exc:
        session.release()
        raise AppError(
            "EXCEL_OPEN_FAILED",
            support_detail=f"could not open {source_path!r} read-only: {exc}",
            source_path=source_path,
        ) from exc
    return session


def _open_attached(source_path: str) -> ExcelSession:
    pythoncom, client, _ = _com_modules()
    pythoncom.CoInitialize()

    try:
        application = client.GetActiveObject("Excel.Application")
    except Exception as exc:
        raise AppError(
            "EXCEL_NOT_AVAILABLE",
            support_detail=(
                f"attach mode needs Excel already running with the workbook "
                f"open: {exc}"),
        ) from exc

    # `identity.verify` raises EXCEL_WORKBOOK_AMBIGUOUS when the open workbooks
    # cannot name a single answer. Refusing beats extracting `Q3 Orders (1).xlsx`
    # and reporting it as `Q3 Orders.xlsx`.
    workbook = identity.verify(source_path, list(application.Workbooks))

    return ExcelSession(
        application=application,
        workbook=workbook,
        open_mode="attach",
        owned_pid=None,        # borrowed process: never quit it
        owns_workbook=False,   # borrowed workbook: never close it
    )


def acquire(source_path: str, open_mode: str = "dedicated") -> ExcelSession:
    """Open dedicated, or attach to the exact full path. Never close a
    workbook the user owns.
    """
    if open_mode not in OPEN_MODES:
        raise ValueError(
            f"open_mode must be one of {OPEN_MODES}, got {open_mode!r}")

    if open_mode == "dedicated" and not os.path.isfile(source_path):
        # Checked before starting Excel so a typo costs no process launch.
        raise AppError(
            "EXCEL_OPEN_FAILED",
            support_detail=f"source file does not exist: {source_path!r}",
            source_path=source_path,
        )

    if open_mode == "attach":
        return _open_attached(source_path)
    if open_mode == "dedicated":
        return _open_dedicated(source_path)

    try:
        return _open_dedicated(source_path)
    except AppError as dedicated_error:
        try:
            return _open_attached(source_path)
        except AppError as attach_error:
            # Report the dedicated failure as the cause: it is the mode we
            # wanted, and its message is the one that explains the real problem.
            raise AppError(
                "EXCEL_OPEN_FAILED",
                support_detail=(
                    f"dedicated open failed ({dedicated_error.code}: "
                    f"{dedicated_error.support_detail}); attach fallback also "
                    f"failed ({attach_error.code}: "
                    f"{attach_error.support_detail})"),
                source_path=source_path,
            ) from dedicated_error
