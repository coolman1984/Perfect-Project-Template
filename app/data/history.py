"""Universal history engine: one implementation, configured per source/entity.

The engine owns append, upsert, snapshot and replace-period semantics. Employee
projects select those modes in source configuration; they do not ship their own
history implementation.

`apply()` owns a transaction for the normal single-source caller.
`apply_in_transaction()` performs the exact same semantics inside an existing
project transaction so a multi-source project can commit all source histories
atomically or roll them all back together.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from app.data.database import Database

APPEND, UPSERT, SNAPSHOT, REPLACE_PERIOD = "append", "upsert", "snapshot", "replace_period"
LOAD_MODES = (APPEND, UPSERT, SNAPSHOT, REPLACE_PERIOD)
IGNORE, MARK_INACTIVE, SOFT_DELETE, CLOSE_VERSION, PHYSICAL = (
    "ignore", "mark_inactive", "soft_delete", "close_version", "physical")


class HistoryError(RuntimeError):
    """The requested history change cannot be performed safely."""


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
    """Apply one validated clean source batch to one trusted history table."""

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

    def apply(
        self,
        run_id: str,
        *,
        load_mode: str,
        lookback_days: int = 0,
        deletion_rule: str = IGNORE,
        requested_period: str | None = None,
    ) -> HistoryResult:
        """Normal single-source entry point with an all-or-nothing transaction."""
        with self.database.transaction():
            return self.apply_in_transaction(
                run_id,
                load_mode=load_mode,
                lookback_days=lookback_days,
                deletion_rule=deletion_rule,
                requested_period=requested_period,
            )

    def apply_in_transaction(
        self,
        run_id: str,
        *,
        load_mode: str,
        lookback_days: int = 0,
        deletion_rule: str = IGNORE,
        requested_period: str | None = None,
    ) -> HistoryResult:
        """Apply history semantics while the caller owns the transaction.

        This is the multi-source project boundary. It deliberately does not
        BEGIN/COMMIT. The caller must already be inside `Database.transaction()`.
        """
        if load_mode not in LOAD_MODES:
            raise HistoryError(
                f"unknown load mode {load_mode!r}. Business meaning must be "
                "approved; the engine never guesses history semantics.")

        if load_mode == REPLACE_PERIOD:
            return self._replace_period(run_id, requested_period)
        if load_mode == APPEND:
            return self._append(run_id)

        result = self._upsert(run_id)
        if load_mode == SNAPSHOT or deletion_rule != IGNORE:
            result.deactivated = self._apply_deletion_rule(
                run_id, deletion_rule, lookback_days, load_mode)
        return result

    def _append(self, run_id: str) -> HistoryResult:
        columns = ", ".join(self.business_columns)
        inserted = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            WHERE c._run_id = ?
              AND NOT EXISTS (
                    SELECT 1 FROM {self.history_table} h
                    WHERE h.business_key_hash = c.business_key_hash)
        """, [run_id]) or 0

        self.database.execute(f"""
            INSERT INTO {self.history_table}
                ({columns}, business_key_hash, row_content_hash, is_active,
                 first_seen_run_id, last_seen_run_id, _source_file,
                 _source_row_number)
            SELECT {columns}, c.business_key_hash, c.row_content_hash, TRUE,
                   c._run_id, c._run_id, c._source_file, c._source_row_number
            FROM {self.clean_table} c
            WHERE c._run_id = ?
              AND NOT EXISTS (
                    SELECT 1 FROM {self.history_table} h
                    WHERE h.business_key_hash = c.business_key_hash)
        """, [run_id])
        return HistoryResult(inserted=int(inserted))

    def _upsert(self, run_id: str) -> HistoryResult:
        changed = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            JOIN {self.history_table} h
              ON h.business_key_hash = c.business_key_hash
            WHERE c._run_id = ? AND h.row_content_hash <> c.row_content_hash
        """, [run_id]) or 0
        unchanged = self.database.scalar(f"""
            SELECT count(*) FROM {self.clean_table} c
            JOIN {self.history_table} h
              ON h.business_key_hash = c.business_key_hash
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
        # `is_active = TRUE` matters here, not only in the changed-row update
        # above. A record that vanished from one export was deactivated by the
        # deletion rule; when it reappears with identical content it takes this
        # branch, and leaving it inactive would drop it from every KPI
        # permanently even though the business source says it is present again.
        # Presence in this run's clean data is what makes a record active —
        # not whether its values happened to change (Part 8.3).
        self.database.execute(f"""
            UPDATE {self.history_table} AS h
            SET last_seen_run_id = c._run_id,
                is_active = TRUE
            FROM {self.clean_table} AS c
            WHERE h.business_key_hash = c.business_key_hash
              AND c._run_id = ?
              AND h.row_content_hash = c.row_content_hash
        """, [run_id])
        inserted = self._append(run_id).inserted
        return HistoryResult(
            inserted=inserted, updated=int(changed), unchanged=int(unchanged))

    def _replace_period(
        self, run_id: str, requested_period: str | None
    ) -> HistoryResult:
        if not requested_period:
            raise HistoryError(
                "replace_period requires an explicit approved period; refusing "
                "to guess which trusted period to replace")
        bounds = self.database.query(
            f"SELECT min({self.event_date_column}), max({self.event_date_column}) "
            f"FROM {self.clean_table} WHERE _run_id = ?", [run_id])
        low, high = bounds[0] if bounds else (None, None)
        if low is None:
            raise HistoryError("no clean rows to load for replace_period")
        if not (str(low).startswith(requested_period)
                and str(high).startswith(requested_period)):
            raise HistoryError(
                f"source data spans {low}..{high}, outside approved period "
                f"{requested_period}; refusing to replace the wrong period")
        self.database.execute(
            f"DELETE FROM {self.history_table} "
            f"WHERE strftime({self.event_date_column}, '%Y-%m-%d') LIKE ?",
            [f"{requested_period}%"])
        return self._append(run_id)

    def _apply_deletion_rule(
        self, run_id: str, rule: str, lookback_days: int, load_mode: str
    ) -> int:
        if rule == IGNORE:
            return 0
        if rule not in (MARK_INACTIVE, SOFT_DELETE, CLOSE_VERSION, PHYSICAL):
            raise HistoryError(f"unknown deletion rule {rule!r}")

        window_clause, parameters = "", [run_id]
        if load_mode != SNAPSHOT and lookback_days > 0:
            cutoff = self._batch_max_date(run_id)
            if cutoff is None:
                return 0
            window_clause = f"AND h.{self.event_date_column} >= ?"
            parameters.append(cutoff - timedelta(days=lookback_days))

        rows = self.database.query(f"""
            SELECT h.business_key_hash
            FROM {self.history_table} h
            WHERE h.is_active = TRUE
              AND NOT EXISTS (
                    SELECT 1 FROM {self.clean_table} c
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
        return self.database.scalar(
            f"SELECT max({self.event_date_column}) FROM {self.clean_table} "
            f"WHERE _run_id = ?", [run_id])

    def active_row_count(self) -> int:
        return int(self.database.scalar(
            f"SELECT count(*) FROM {self.history_table} "
            "WHERE is_active = TRUE") or 0)

    def total(self, column: str) -> Any:
        return self.database.scalar(
            f"SELECT COALESCE(SUM({column}), 0) FROM {self.history_table} "
            "WHERE is_active = TRUE")
