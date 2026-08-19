"""The extraction port (Constitution Part 44.2).

Layer 2 is defined by this interface, not by COM. Layers 3-10 depend on
`ExtractionPort` and must never import `win32com`, `pywin32` or `pythoncom` —
`architecture verify --source-scan` enforces that import direction.

Why this exists: extraction needs Windows, an interactive session, a licensed
Excel and DRM-authorized files. Everything downstream needs none of that.
Coupling them made the whole pipeline untestable off Windows, which produced
exactly the two failure modes the constitution most wants to prevent — the agent
stalls, or the agent "simplifies" the architecture until it runs where it
happens to be sitting (Part 44.1).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkbookIdentity:
    """Proof that we opened the exact workbook we were configured to open.

    Attach mode matches the **exact** full path, never a similar name, and never
    closes a workbook the user owns (Part 7.1).
    """

    full_path: str
    sheet_name: str
    file_hash: str
    file_size: int
    modified_time: str
    date_system_1904: bool = False
    open_mode: str = "dedicated"


@dataclass(frozen=True)
class Chunk:
    """One rectangular block read in a single COM request (Part 7.3).

    `values` is row-major and raw: `Value2` returns unconverted values, so date
    and decimal conversion is our explicit responsibility (Part 7.4).
    """

    chunk_number: int
    first_row: int
    last_row: int
    column_names: tuple[str, ...]
    values: tuple[tuple[Any, ...], ...]

    @property
    def row_count(self) -> int:
        return len(self.values)

    @property
    def cell_count(self) -> int:
        return self.row_count * len(self.column_names)


@dataclass(frozen=True)
class LineageStamp:
    """Added to every staged row so any dashboard number traces to its cell.

    "Where did this number come from?" must take 30 seconds (Part 7.7, rule 8).
    """

    run_id: str
    report_id: str
    source_id: str
    source_file: str
    source_file_hash: str
    source_sheet: str
    extracted_at: str
    schema_version: str
    extra: dict[str, str] = field(default_factory=dict)


class ExtractionPort(ABC):
    """The contract every extraction adapter satisfies.

    Implementations:
      - `com_adapter.ComExtractionAdapter`      production, the only one shipped
      - `fixture_adapter.FixtureExtractionAdapter`  dev/test only, never shipped

    An adapter must restore every Excel setting it changed in a `finally` block,
    even after failure, and must close only the process it created — never all
    `EXCEL.EXE` processes, some of which belong to the user (Part 23.5).
    """

    #: Set False on any adapter that cannot satisfy GATE_PROTECTED_FILE_PROOF.
    #: Only a real COM read of a real protected workbook advances that gate
    #: (Part 44.3 rule 3).
    provides_production_evidence: bool = False

    @abstractmethod
    def open(self, source_path: str, config: dict[str, Any]) -> WorkbookIdentity:
        """Open read-only and prove workbook identity. Never save the source."""

    @abstractmethod
    def chunks(self) -> Iterator[Chunk]:
        """Yield rectangular blocks. Never read cell by cell (rule 2)."""

    @abstractmethod
    def lineage(self) -> LineageStamp:
        """The Part 7.7 fields stamped onto every staged row."""

    @abstractmethod
    def close(self) -> None:
        """Release COM objects and restore settings, in a finally block."""

    def __enter__(self) -> ExtractionPort:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


def rows_per_chunk(
    target_cells: int,
    column_count: int,
    minimum: int,
    maximum: int,
) -> int:
    """Adaptive chunk sizing in cells, not rows (Part 7.3).

    A 272-column file and a 12-column file need very different row counts for
    the same memory footprint::

        rows = target_cells // columns, clamped to [minimum, maximum]

    Example: 272 columns at a 250,000-cell target gives 919 rows per chunk.
    """
    if column_count <= 0:
        raise ValueError("column_count must be positive")
    if minimum > maximum:
        raise ValueError("minimum must not exceed maximum")
    return max(minimum, min(maximum, max(1, target_cells // column_count)))


def as_row_major(values: Any) -> tuple[tuple[Any, ...], ...]:
    """Normalise whatever `Range.Value2` returned into rows of cells.

    COM does not hand back a consistent shape, and every caller would otherwise
    re-derive the same three cases: a multi-cell range gives a tuple of row
    tuples, a **single cell** gives a bare scalar, and a range whose values are
    all empty can give `None`. Reading a one-row sheet must not take a different
    code path from reading a million-row one.

    Lives here beside `rows_per_chunk` because both are shape rules the port
    defines and every adapter shares — and, unlike the COM calls themselves,
    both are testable on any machine.
    """
    if values is None:
        return ()
    if not isinstance(values, (tuple, list)):
        return ((values,),)
    if not values:
        return ()
    if not isinstance(values[0], (tuple, list)):
        # A single row (or single column) came back flat.
        return (tuple(values),)
    return tuple(tuple(row) for row in values)
