"""Adaptive block extraction (Part 7.3).

Task contract (Part 17.1):

    LAYER             layer 2
    INPUTS            session + mapping + chunk policy
    OUTPUTS           a stream of chunks
    VALIDATION        row count equals expected; no cell-by-cell call exists
    FAILURE BEHAVIOR  A failed chunk preserves completed checkpoints and requests a retry;
                      partial data never reaches trusted history.

The rule this module exists to enforce: **one COM call per block, not per
cell.** Twenty million cells read individually is twenty million marshalled
border crossings, which takes hours. The same data read as rectangular
`Range.Value2` blocks takes seconds. `tests/architecture/
test_no_cell_by_cell_extraction.py` fails CI on the first per-cell access added
here.

Like `discovery`, this module holds no COM import (Part 44.2). It drives
extraction through a `read_block(first_row, last_row) -> values` callable
supplied by the adapter, so the chunking, projection and row-count arithmetic —
the parts that are easy to get subtly wrong — are testable on any machine.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any

from app.errors import AppError
from app.excel.port import Chunk, as_row_major, rows_per_chunk

#: Part 7.3 defaults, overridden per report by `[extraction]`.
DEFAULT_TARGET_CELLS = 250_000
DEFAULT_MIN_ROWS = 250
DEFAULT_MAX_ROWS = 10_000

ReadBlock = Callable[[int, int], Any]


@dataclass(frozen=True)
class ChunkPlan:
    """One rectangle to request, computed before any reading starts."""

    chunk_number: int
    first_row: int
    last_row: int

    @property
    def row_count(self) -> int:
        return self.last_row - self.first_row + 1


def chunk_rows(config: dict[str, Any], column_count: int) -> int:
    """Rows per chunk for this report's `[extraction]` policy.

    Sized in *cells* rather than rows, because a 272-column workbook and a
    12-column one need very different row counts to occupy the same memory.
    """
    extraction = dict(config.get("extraction", {}))
    return rows_per_chunk(
        target_cells=int(extraction.get("target_cells_per_chunk", DEFAULT_TARGET_CELLS)),
        column_count=max(1, column_count),
        minimum=int(extraction.get("min_rows_per_chunk", DEFAULT_MIN_ROWS)),
        maximum=int(extraction.get("max_rows_per_chunk", DEFAULT_MAX_ROWS)),
    )


def plan_chunks(first_data_row: int, last_row: int, rows: int) -> tuple[ChunkPlan, ...]:
    """Split `[first_data_row, last_row]` into consecutive blocks.

    An empty region (header present, no data rows) plans zero chunks rather
    than one empty chunk — a distinction the control-total check depends on.
    """
    if rows <= 0:
        raise ValueError(f"rows per chunk must be positive, got {rows}")
    if last_row < first_data_row:
        return ()
    plans = []
    start = first_data_row
    number = 1
    while start <= last_row:
        stop = min(start + rows - 1, last_row)
        plans.append(ChunkPlan(chunk_number=number, first_row=start, last_row=stop))
        start = stop + 1
        number += 1
    return tuple(plans)


def projection(column_names: tuple[str, ...],
               projected_columns: list[str] | None) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Map approved column names to their positions — never the reverse.

    Part 7.2: columns are matched **by approved name**, so inserting a column in
    the source workbook shifts positions without corrupting the extract. Mapping
    by position is how a "quantity" column silently starts reporting a date.

    Returns the projected names and their 0-based indexes into each raw row.
    """
    if not projected_columns:
        return tuple(column_names), tuple(range(len(column_names)))

    lookup: dict[str, int] = {}
    for index, name in enumerate(column_names):
        key = name.strip().casefold()
        # First occurrence wins; a duplicate header is reported below rather
        # than silently shadowing the original.
        lookup.setdefault(key, index)

    names: list[str] = []
    indexes: list[int] = []
    missing: list[str] = []
    for wanted in projected_columns:
        index = lookup.get(str(wanted).strip().casefold())
        if index is None:
            missing.append(str(wanted))
            continue
        names.append(str(wanted))
        indexes.append(index)

    if missing:
        raise AppError(
            "SCHEMA_REQUIRED_COLUMN_MISSING",
            support_detail=(
                f"approved columns not present in the source header: "
                f"{sorted(missing)}; header reads {list(column_names)}"),
            missing_columns=sorted(missing),
        )
    return tuple(names), tuple(indexes)


def project_rows(rows: tuple[tuple[Any, ...], ...],
                 indexes: tuple[int, ...]) -> tuple[tuple[Any, ...], ...]:
    """Keep only the approved columns, padding rows COM returned short.

    A comprehension rather than nested loops: this is the exact shape the
    per-cell guard looks for, and expressing the projection declaratively keeps
    the intent (reshape values already in memory) distinct from reading cells.
    """
    return tuple(
        tuple(row[index] if index < len(row) else None for index in indexes)
        for row in rows
    )


def read_region(read_block: ReadBlock, region: Any,
                config: dict[str, Any]) -> Iterator[Chunk]:
    """Stream a `DataRegion` as projected chunks.

    Yields rather than accumulates: each chunk goes straight to staging so a
    20-million-cell workbook never exists in memory at once (Part 7.3).
    """
    names, indexes = projection(
        tuple(region.column_names),
        list(config.get("extraction", {}).get("projected_columns") or []),
    )
    plans = plan_chunks(
        region.first_data_row, region.last_row,
        chunk_rows(config, len(names)))

    for plan in plans:
        try:
            raw = read_block(plan.first_row, plan.last_row)
        except AppError:
            raise
        except Exception as exc:
            # Retryable by registry class: the checkpoint for every chunk
            # already yielded stands, and the run resumes rather than restarts.
            raise AppError(
                "EXCEL_READ_FAILED",
                support_detail=(
                    f"failed reading rows {plan.first_row}-{plan.last_row} "
                    f"of sheet {region.sheet_name!r}: {exc}"),
                first_row=plan.first_row,
                last_row=plan.last_row,
            ) from exc

        rows = as_row_major(raw)
        if len(rows) != plan.row_count:
            raise AppError(
                "EXCEL_READ_FAILED",
                support_detail=(
                    f"requested rows {plan.first_row}-{plan.last_row} "
                    f"({plan.row_count} rows) but Excel returned {len(rows)}"),
                first_row=plan.first_row,
                last_row=plan.last_row,
            )

        yield Chunk(
            chunk_number=plan.chunk_number,
            first_row=plan.first_row,
            last_row=plan.last_row,
            column_names=names,
            values=project_rows(rows, indexes),
        )


def extract(port: Any, config: dict[str, Any]) -> Iterator[Chunk]:
    """Stream an opened port's chunks, verifying the row count as they pass.

    The guarantee is Part 7.3's "row count equals expected": the totals are
    checked against the chunk bounds as data streams, so a short read surfaces
    here rather than as an unexplained drop in a dashboard number.
    """
    expected = 0
    produced = 0
    for chunk in port.chunks():
        expected += chunk.last_row - chunk.first_row + 1
        produced += chunk.row_count
        yield chunk

    if produced != expected:
        raise AppError(
            "EXCEL_READ_FAILED",
            support_detail=(
                f"chunk bounds describe {expected} rows but {produced} were "
                f"produced; partial data must never reach trusted history"),
            expected_rows=expected,
            produced_rows=produced,
        )
