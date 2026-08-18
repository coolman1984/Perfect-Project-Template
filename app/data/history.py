"""The history engine: connected history without duplicates (Part 8).

Layer 6, and the layer where a mistake is most expensive — this is the single
truth every dashboard number comes from.

Four load modes, each report declaring exactly one:

    append          every file contains only new permanent transactions
    upsert          old records may be corrected
    snapshot        each file is the full state at a point in time
    replace_period  one file fully replaces one approved period

The whole update runs inside one transaction. On any failure it rolls back and
trusted history is exactly as it was (Part 8.5, rule 9).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from app.data.database import Database

APPEND, UPSERT, SNAPSHOT, REPLACE_PERIOD = "append", "upsert", "snapshot", "replace_period"
LOAD_MODES = (APPEND, UPSERT, SNAPSHOT, REPLACE_PERIOD)

# Deletion rules (Part 8.4). What a disappearing row MEANS is a human decision;
# the engine only executes the approved rule and never infers one.
IGNORE, MARK_INACTIVE, SOFT_DELETE, CLOSE_VERSION, PHYSICAL = (
    "ignore", "mark_inactive", "soft_delete", "close_version", "physical")


class HistoryError(RuntimeError):
    """The requested load cannot be performed safely."""


@dataclass
class HistoryResult:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    deactivated: int = 0

    @property
    def total_touched(self) -> int:
        return self.inserted + self.updated + self.unchanged


class HistoryEngine:
    """Applies a validated clean batch to trusted history.

    Report-agnostic: the table and column names come from configuration, so a
    new report needs no new engine code. That is the Factory Core boundary.
    """

    def __init__(
        self,
        database: Database,
        *,
        history_table: str,
        clean_table: str,
        business_columns: list[str],
        key_columns: list[str],
        event_date_column: str,
    ) -> None:
        self.database = database
        self.history_table = history_table
        self.clean_table = clean_table
        self.business_columns = business_columns
        self.key_columns = key_columns
        self.event_date_column = event_date_column

    # -- entry point -------------------------------------------------------

    def apply(
        self,
        run_id: str,
        *,
        load_mode: str,
        lookback_days: int = 0,
        deletion_rule: str = IGNORE,
        requested_period: str | None = None,
    ) -> HistoryResult:
        if load_mode not in LOAD_MODES:
            raise HistoryError(
                f"unknown load mode {load_mode!r}. A human approves this "
                f"(Part 3.1); the engine never guesses.")

        with self.database.transaction():
            if load_mode == REPLACE_PERIOD:
                result = self._replace_period(run_id, requested_period)
            elif load_mode == APPEND:
                result = self._append(run_id)
            else:
                # snapshot and upsert share the same compare-and-merge core;
                # they differ only in how disappearance is treated.
                result = self._upsert(run_id)
                if load_mode == SNAPSHOT or deletion_rule != IGNORE:
                    result.deactivated = self._apply_deletion_rule(
                        run_id, deletion_rule, lookback_days, load_mode)
            return result

    # -- modes -------------------------------------------------------------

    def _append(self, run_id: str) -> HistoryResult:
        """Insert every clean row. Existing keys are still protected: an
        append report that receives the same key twice is a contradiction the
        quality gate has already rejected."""
        columns = ", ".join(self.business_columns)
        inserted = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            WHERE c._run_id = ?
              AND NOT EXISTS (SELECT 1 FROM {self.history_table} h
                              WHERE h.business_key_hash = c.business_key_hash)
        """, [run_id]) or 0

        self.database.execute(f"""
            INSERT INTO {self.history_table}
                ({columns}, business_key_hash, row_content_hash, is_active,
                 first_seen_run_id, last_seen_run_id, _source_file, _source_row_number)
            SELECT {columns}, c.business_key_hash, c.row_content_hash, TRUE,
                   c._run_id, c._run_id, c._source_file, c._source_row_number
            FROM {self.clean_table} c
            WHERE c._run_id = ?
              AND NOT EXISTS (SELECT 1 FROM {self.history_table} h
                              WHERE h.business_key_hash = c.business_key_hash)
        """, [run_id])
        return HistoryResult(inserted=int(inserted))

    def _upsert(self, run_id: str) -> HistoryResult:
        """Same key + changed values -> update. New key -> insert.

        The two hashes give insert/update/unchanged in one pass (Part 8.2), so
        rerunning identical input changes nothing at all (rule 5).
        """
        changed = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            JOIN {self.history_table} h ON h.business_key_hash = c.business_key_hash
            WHERE c._run_id = ? AND h.row_content_hash <> c.row_content_hash
        """, [run_id]) or 0

        unchanged = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            JOIN {self.history_table} h ON h.business_key_hash = c.business_key_hash
            WHERE c._run_id = ? AND h.row_content_hash = c.row_content_hash
        """, [run_id]) or 0

        assignments = ", ".join(
            f"{column} = c.{column}" for column in self.business_columns)
        self.database.execute(f"""
            UPDATE {self.history_table} AS h
            SET {assignments},
                row_content_hash = c.row_content_hash,
                is_active = TRUE,
                last_seen_run_id = c._run_id,
                _source_file = c._source_file,
                _source_row_number = c._source_row_number
            FROM {self.clean_table} AS c
            WHERE h.business_key_hash = c.business_key_hash
              AND c._run_id = ?
              AND h.row_content_hash <> c.row_content_hash
        """, [run_id])

        # Touch unchanged rows so "last seen" stays truthful without counting
        # them as an update.
        self.database.execute(f"""
            UPDATE {self.history_table} AS h
            SET last_seen_run_id = c._run_id
            FROM {self.clean_table} AS c
            WHERE h.business_key_hash = c.business_key_hash
              AND c._run_id = ?
              AND h.row_content_hash = c.row_content_hash
        """, [run_id])

        inserted = self._append(run_id).inserted
        return HistoryResult(inserted=inserted, updated=int(changed),
                             unchanged=int(unchanged))

    def _replace_period(self, run_id: str, requested_period: str | None) -> HistoryResult:
        """Delete ONE approved period and insert the new one.

        Never all history. The requested period is validated against the
        source's actual date range first, because replacing the wrong period is
        unrecoverable without the archive (Part 27.4).
        """
        if not requested_period:
            raise HistoryError(
                "replace_period requires an explicit approved period — refusing "
                "to guess which period to delete (Part 27.4)")

        bounds = self.database.query(
            f"SELECT min({self.event_date_column}), max({self.event_date_column}) "
            f"FROM {self.clean_table} WHERE _run_id = ?", [run_id])
        low, high = bounds[0] if bounds else (None, None)
        if low is None:
            raise HistoryError("no clean rows to load for replace_period")
        if not (str(low).startswith(requested_period)
                and str(high).startswith(requested_period)):
            raise HistoryError(
                f"source data spans {low}..{high}, which is outside the requested "
                f"period {requested_period}. Refusing to replace the wrong period.")

        self.database.execute(
            f"DELETE FROM {self.history_table} "
            f"WHERE strftime({self.event_date_column}, '%Y-%m-%d') LIKE ?",
            [f"{requested_period}%"])
        return self._append(run_id)

    # -- deletions ---------------------------------------------------------

    def _apply_deletion_rule(
        self, run_id: str, rule: str, lookback_days: int, load_mode: str
    ) -> int:
        """Handle records that exist in history but not in this batch.

        Only within the approved lookback window: anything older is assumed
        final unless a full rebuild is requested (Part 8.3). Inferring deletion
        from absence outside that window is exactly the guess Part 8.4 forbids.
        """
        if rule == IGNORE:
            return 0
        if rule not in (MARK_INACTIVE, SOFT_DELETE, CLOSE_VERSION, PHYSICAL):
            raise HistoryError(f"unknown deletion rule {rule!r} (Part 8.4)")

        window_clause, parameters = "", [run_id]
        if load_mode != SNAPSHOT and lookback_days > 0:
            cutoff = self._batch_max_date(run_id)
            if cutoff is None:
                return 0
            window_clause = f"AND h.{self.event_date_column} >= ?"
            parameters.append(cutoff - timedelta(days=lookback_days))

        # Resolve the affected keys once, then act on that explicit list. This
        # is longer than a correlated UPDATE but it is readable, and the list
        # itself becomes the evidence for what the deletion rule touched.
        rows = self.database.query(f"""
            SELECT h.business_key_hash
            FROM {self.history_table} h
            WHERE h.is_active = TRUE
              AND NOT EXISTS (SELECT 1 FROM {self.clean_table} c
                              WHERE c._run_id = ?
                                AND c.business_key_hash = h.business_key_hash)
              {window_clause}
        """, parameters)
        keys = [row[0] for row in rows]
        if not keys:
            return 0

        placeholders = ", ".join("?" for _ in keys)
        if rule == PHYSICAL:
            self.database.execute(
                f"DELETE FROM {self.history_table} "
                f"WHERE business_key_hash IN ({placeholders})", keys)
        else:
            self.database.execute(
                f"UPDATE {self.history_table} SET is_active = FALSE "
                f"WHERE business_key_hash IN ({placeholders})", keys)
        return len(keys)

    def _batch_max_date(self, run_id: str) -> date | None:
        value = self.database.scalar(
            f"SELECT max({self.event_date_column}) FROM {self.clean_table} "
            f"WHERE _run_id = ?", [run_id])
        return value

    # -- reporting ---------------------------------------------------------

    def active_row_count(self) -> int:
        return int(self.database.scalar(
            f"SELECT count(*) FROM {self.history_table} WHERE is_active = TRUE") or 0)

    def total(self, column: str) -> Any:
        return self.database.scalar(
            f"SELECT COALESCE(SUM({column}), 0) FROM {self.history_table} "
            f"WHERE is_active = TRUE")
