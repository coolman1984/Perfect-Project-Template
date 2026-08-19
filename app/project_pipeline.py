"""Project-centric, multi-source execution coordinator.

This is the V8.1 proof boundary:

- many independent source roles in one project;
- per-source grain/key/types/quality/history strategy;
- explicit approved relationships;
- one atomic trusted-history transaction across all sources;
- cross-source SQL analytics after history is internally consistent;
- no department-specific formula in Universal Core.

The coordinator accepts already-open ExtractionPort objects. Production uses the
COM adapter; tests use the explicit fixture adapter. It never silently switches.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import re
import tomllib
from typing import Any

from app.analytics.configured import ConfiguredAnalytics, load_dashboard_config
from app.analytics.runner import SqlRunner
from app.dashboard import project_json_builder
from app.data.database import Database
from app.data.history import HistoryEngine, HistoryResult
from app.data.migrations import migrate
from app.data.project_migrations import migrate as migrate_project
from app.data.staging import LINEAGE_COLUMNS, StagingWriter
from app.excel.port import LineageStamp
from app.quality.engine import BLOCK, PASS, WARNING, CheckResult, QualityEngine, QualityReport
from app.quality.quarantine import (
    EXACT_DUPLICATE,
    NEGATIVE_MEASURE,
    UNPARSEABLE_DATE,
    UNPARSEABLE_NUMBER,
    UNPARSEABLE_VALUE,
    QuarantinedRow,
    quarantine_rows,
)
from app.quality.reconciliation import ControlTotal, Population, check_control_total, check_population
from app.rules.runner import ProjectRuleRunner, parse_rule_specs
from factory.project_contract import ProjectContract, RelationshipSpec, SourceSpec

SAFE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
NUMERIC_TYPES = ("DECIMAL", "INTEGER", "BIGINT")


class ProjectPipelineError(RuntimeError):
    pass


@dataclass
class SourceOutcome:
    source_id: str
    rows_extracted: int = 0
    rows_rejected: int = 0
    rows_filtered: int = 0
    quality_status: str = PASS
    history: HistoryResult = field(default_factory=HistoryResult)
    control_totals: list[ControlTotal] = field(default_factory=list)


@dataclass
class ProjectOutcome:
    run_id: str
    status: str = "RUNNING"
    quality_status: str = PASS
    sources: dict[str, SourceOutcome] = field(default_factory=dict)
    control_totals: list[ControlTotal] = field(default_factory=list)
    quality_counts: dict[str, int] = field(
        default_factory=lambda: {PASS: 0, WARNING: 0, BLOCK: 0})
    dashboard: dict[str, Any] | None = None
    error_message: str | None = None
    demo_data: bool = False
    unapproved_definitions: bool = False
    #: Rows written per declared project Python rule (Part 14.3). Empty for the
    #: normal project, which expresses everything in SQL.
    rule_rows: dict[str, int] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.status == "COMPLETE"


class ProjectPipeline:
    def __init__(
        self,
        database: Database,
        contract: ProjectContract,
        *,
        application_version: str = "0.0.0",
    ) -> None:
        self.database = database
        self.contract = contract
        self.application_version = application_version
        self.dashboard_config = load_dashboard_config(
            contract.directory / "dashboard.toml")
        self.sql = SqlRunner(database, contract.directory / "business_rules")
        self.analytics = ConfiguredAnalytics(
            self.sql,
            self.dashboard_config,
            metrics_file="metrics.sql",
            insights_file="insights.sql",
        )
        # Part 14.1 keeps Python last: a project declares rules only when SQL
        # cannot express the calculation, and a project with none pays nothing.
        # Declared in metrics.toml (V10 Part 16), not dashboard.toml: a rule is
        # business logic, not presentation, and most projects have no rules at
        # all and so carry no metrics.toml.
        metrics_path = contract.directory / "metrics.toml"
        metrics_config = (
            tomllib.loads(metrics_path.read_text(encoding="utf-8"))
            if metrics_path.is_file() else {})
        self.python_rules = parse_rule_specs(metrics_config)
        self.rules = ProjectRuleRunner(
            database,
            self.sql,
            rules_root=contract.directory / "business_rules" / "python",
            metrics_file="metrics.sql",
        )

    # ------------------------------------------------------------------ schema
    def prepare(self) -> None:
        # 0001 is the reusable sys/quality/checkpoint migration. Reference-report
        # migrations 0002/0003 are legacy compatibility and are intentionally not
        # required by a project-centric execution.
        migrate(
            self.database,
            application_version=self.application_version,
            max_version=1,
        )
        # Three phases, in this order, so both a genuinely fresh database and
        # an evolving one reach the same validated shape (Part 15):
        #
        # 1. CREATE TABLE IF NOT EXISTS from *current* sources.toml. On a
        #    fresh database this alone produces the full current shape and no
        #    migration does real work. On an existing database it is a no-op.
        # 2. Project migrations. On a fresh database each ALTER ... ADD COLUMN
        #    IF NOT EXISTS is a no-op against the column phase 1 just created.
        #    On an existing database this is where a column actually gets
        #    added — which is why migrations cannot run before phase 1: an
        #    ALTER TABLE against a table phase 1 has not created yet fails
        #    outright rather than doing nothing.
        # 3. Validate: current configuration must now match the database
        #    exactly. A configured column with neither history (phase 1
        #    already fresh) nor a migration (phase 2) is the one case this
        #    still rejects, on purpose — Part 15's "schema drift never
        #    silently changes trusted tables".
        for source in self.contract.sources:
            self._create_source_tables(source)
        migrate_project(
            self.database,
            project_id=self.contract.project_id,
            migrations_dir=self.contract.directory / "migrations",
            application_version=self.application_version,
        )
        for source in self.contract.sources:
            self._validate_source_schema(source)

    def raw_table(self, source: SourceSpec | str) -> str:
        source_id = source if isinstance(source, str) else source.source_id
        return f"raw.{self._prefix(source_id)}"

    def clean_table(self, source: SourceSpec | str) -> str:
        source_id = source if isinstance(source, str) else source.source_id
        return f"clean.{self._prefix(source_id)}"

    def history_table(self, source: SourceSpec | str) -> str:
        source_id = source if isinstance(source, str) else source.source_id
        return f"analytics.history_{self._prefix(source_id)}"

    def _prefix(self, source_id: str) -> str:
        for value in (self.contract.project_id, source_id):
            if not SAFE_ID.fullmatch(value):
                raise ProjectPipelineError(f"unsafe SQL identifier: {value!r}")
        return f"{self.contract.project_id}_{source_id}"

    @staticmethod
    def _column(name: str) -> str:
        if not SAFE_ID.fullmatch(name):
            raise ProjectPipelineError(f"unsafe column identifier: {name!r}")
        return name

    @staticmethod
    def _type(kind: str) -> str:
        allowed = {
            "VARCHAR", "DATE", "INTEGER", "BIGINT", "BOOLEAN",
            "DECIMAL(18,4)", "DECIMAL(18,2)",
        }
        if kind not in allowed:
            raise ProjectPipelineError(f"unsupported configured SQL type: {kind}")
        return kind

    def _create_source_tables(self, source: SourceSpec) -> None:
        business = [self._column(name) for name in source.business_columns]
        raw_columns = ",\n                ".join(
            f"{name} VARCHAR" for name in business)
        lineage = """
                _run_id VARCHAR,
                _report_id VARCHAR,
                _source_id VARCHAR,
                _source_file VARCHAR,
                _source_file_hash VARCHAR,
                _source_sheet VARCHAR,
                _source_row_number BIGINT,
                _extracted_at VARCHAR,
                _schema_version VARCHAR"""
        self.database.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.raw_table(source)} (
                {raw_columns},
                {lineage}
            )
        """)
        typed = ",\n                ".join(
            f"{name} {self._type(source.column_types[name])}"
            for name in business)
        self.database.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.clean_table(source)} (
                {typed},
                business_key_hash VARCHAR,
                row_content_hash VARCHAR,
                _run_id VARCHAR,
                _source_id VARCHAR,
                _source_file VARCHAR,
                _source_row_number BIGINT
            )
        """)
        self.database.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.history_table(source)} (
                {typed},
                business_key_hash VARCHAR PRIMARY KEY,
                row_content_hash VARCHAR NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                first_seen_run_id VARCHAR NOT NULL,
                last_seen_run_id VARCHAR NOT NULL,
                _source_file VARCHAR,
                _source_row_number BIGINT
            )
        """)

    def _validate_source_schema(self, source: SourceSpec) -> None:
        business = [self._column(name) for name in source.business_columns]
        expected_raw = set(business) | set(LINEAGE_COLUMNS)
        actual_raw = set(self.database.columns_of(self.raw_table(source)))
        if expected_raw != actual_raw:
            raise ProjectPipelineError(
                f"{source.source_id}: configured raw schema differs from the "
                "existing project database; use an explicit project schema "
                "migration instead of silently changing trusted tables")

    # --------------------------------------------------------------- execution
    def run(
        self,
        run_id: str,
        ports: dict[str, Any],
        *,
        requested_periods: dict[str, str] | None = None,
    ) -> ProjectOutcome:
        requested_periods = requested_periods or {}
        outcome = ProjectOutcome(run_id=run_id)
        missing = [
            source.source_id for source in self.contract.sources
            if source.required and source.source_id not in ports
        ]
        if missing:
            outcome.status = "FAILED"
            outcome.quality_status = BLOCK
            outcome.error_message = f"missing required source roles: {missing}"
            return outcome
        outcome.demo_data = any(
            not bool(getattr(port, "provides_production_evidence", False))
            for port in ports.values())
        outcome.unapproved_definitions = any(
            rel.approval_state != "CONFIRMED"
            for rel in self.contract.relationships)

        try:
            self._clear_run_evidence(run_id)
            source_reports: dict[str, QualityReport] = {}
            for source in self.contract.sources:
                if source.source_id not in ports:
                    continue
                source_outcome, report = self._prepare_source(
                    run_id, source, ports[source.source_id])
                outcome.sources[source.source_id] = source_outcome
                outcome.control_totals.extend(source_outcome.control_totals)
                source_reports[source.source_id] = report

            relation_report = self._validate_relationships(run_id)
            self._persist_report(relation_report)
            all_reports = [*source_reports.values(), relation_report]
            outcome.quality_status = self._aggregate_quality(all_reports)
            outcome.quality_counts = self._quality_counts(all_reports)
            if outcome.quality_status == BLOCK:
                outcome.status = "FAILED"
                outcome.error_message = "quality or relationship validation blocked the project run"
                self._record_run(outcome)
                return outcome

            # The critical boundary: no source history commits on its own.
            # Analytics runs before COMMIT too, so a broken cross-source metric
            # cannot leave a half-updated trusted project behind.
            with self.database.transaction():
                for source in self.contract.sources:
                    if source.source_id not in outcome.sources:
                        continue
                    event_date = source.event_date or source.business_key[0]
                    result = HistoryEngine(
                        self.database,
                        history_table=self.history_table(source),
                        clean_table=self.clean_table(source),
                        business_columns=list(source.business_columns),
                        key_columns=list(source.business_key),
                        event_date_column=event_date,
                    ).apply_in_transaction(
                        run_id,
                        load_mode=source.load_mode,
                        lookback_days=source.lookback_days,
                        deletion_rule=source.deletion_rule,
                        requested_period=requested_periods.get(source.source_id),
                    )
                    outcome.sources[source.source_id].history = result
                # Rules run after trusted history and before presentation, so a
                # rule reads committed-in-transaction history and its output is
                # available to dashboard SQL. A failing rule aborts the same
                # transaction as any other downstream failure.
                outcome.rule_rows = self.rules.run(self.python_rules)
                analytics = self.analytics.run()
                outcome.dashboard = project_json_builder.build(
                    contract=self.contract,
                    config=self.dashboard_config,
                    analytics=analytics,
                    outcome=outcome,
                )
            outcome.status = "COMPLETE"
            self._record_run(outcome)
            return outcome
        except Exception as error:
            outcome.status = "FAILED"
            outcome.error_message = str(error)
            self._record_run(outcome)
            raise

    def _clear_run_evidence(self, run_id: str) -> None:
        self.database.execute(
            "DELETE FROM quality.check_result WHERE run_id = ?", [run_id])
        self.database.execute(
            "DELETE FROM quality.quarantine WHERE run_id = ?", [run_id])
        self.database.execute(
            "DELETE FROM sys.checkpoint WHERE run_id = ?", [run_id])
        self.database.execute(
            "DELETE FROM sys.run WHERE run_id = ?", [run_id])

    def _stage_port(
        self, run_id: str, source: SourceSpec, port: Any
    ) -> tuple[int, list[str]]:
        writer = StagingWriter(
            self.database, self.raw_table(source), list(source.business_columns))
        writer.clear_run(run_id)
        original = port.lineage()
        lineage = LineageStamp(
            run_id=run_id,
            report_id=self.contract.project_id,
            source_id=source.source_id,
            source_file=original.source_file,
            source_file_hash=original.source_file_hash,
            source_sheet=original.source_sheet or source.sheet,
            extracted_at=original.extracted_at,
            schema_version=original.schema_version,
            extra=dict(original.extra),
        )
        total = 0
        present: list[str] = []
        for chunk in port.chunks():
            current = [str(name) for name in chunk.column_names]
            if not present:
                present = current
            elif current != present:
                raise ProjectPipelineError(
                    f"{source.source_id}: source schema changed between chunks")
            staged = writer.write_chunk(chunk, lineage)
            writer.checkpoint(chunk, lineage, staged)
            total += staged
        return total, present

    def _prepare_source(
        self, run_id: str, source: SourceSpec, port: Any
    ) -> tuple[SourceOutcome, QualityReport]:
        rows, present = self._stage_port(run_id, source, port)
        outcome = SourceOutcome(source_id=source.source_id, rows_extracted=rows)
        report = QualityReport(run_id=run_id)
        engine = QualityEngine(self.database, {"quality": {}})
        raw = self.raw_table(source)
        engine.check_required_columns(
            report, present, list(source.required_columns))
        engine.check_no_blank_business_key(
            report, raw, run_id, list(source.business_key))
        self._check_conflicting_duplicates(report, run_id, source)
        if report.status == BLOCK:
            self._prefix_report(report, source.source_id)
            self._persist_report(report)
            outcome.quality_status = BLOCK
            return outcome, report

        rejected_rows, rejected_payload = self._invalid_rows(
            run_id, source)
        filtered_rows, filtered_payload = self._exact_duplicate_rows(
            run_id, source, excluded=rejected_rows)
        if rejected_payload:
            quarantine_rows(
                self.database, run_id, self.contract.project_id,
                rejected_payload)
        if filtered_payload:
            quarantine_rows(
                self.database, run_id, self.contract.project_id,
                filtered_payload)
        outcome.rows_rejected = len(rejected_rows)
        outcome.rows_filtered = len(filtered_rows)
        if rejected_rows:
            report.add(CheckResult(
                "row.invalid_or_negative_measure", "row", "warning", WARNING,
                f"{len(rejected_rows)} row(s) were quarantined and excluded "
                "from trusted history"))
        if filtered_rows:
            report.add(CheckResult(
                "row.exact_duplicate", "row", "warning", WARNING,
                f"{len(filtered_rows)} exact duplicate row(s) were retained "
                "in quarantine and intentionally filtered"))

        self._build_clean(
            run_id, source,
            excluded=sorted(rejected_rows | filtered_rows))
        accepted = int(self.database.scalar(
            f"SELECT count(*) FROM {self.clean_table(source)} "
            "WHERE _run_id = ?", [run_id]) or 0)
        population = Population(
            source_rows=rows,
            accepted_rows=accepted,
            rejected_rows=len(rejected_rows),
            intentionally_filtered_rows=len(filtered_rows),
            filter_reasons=((EXACT_DUPLICATE, len(filtered_rows)),),
        )
        check_population(report, population)
        for column in source.control_totals:
            control = self._control_total(
                run_id, source, column,
                rejected_rows=rejected_rows,
                filtered_rows=filtered_rows)
            check_control_total(report, control, severity="block")
            outcome.control_totals.append(ControlTotal(
                name=f"{source.source_id}.{control.name}",
                source_value=control.source_value,
                database_value=control.database_value,
            ))
        self._prefix_report(report, source.source_id)
        self._persist_report(report)
        outcome.quality_status = report.status
        return outcome, report

    # --------------------------------------------------------------- quality
    def _check_conflicting_duplicates(
        self, report: QualityReport, run_id: str, source: SourceSpec
    ) -> None:
        key_hash = self._hash_expr("r", source.business_key, source)
        content_hash = self._hash_expr(
            "r", source.business_columns, source)
        count = int(self.database.scalar(f"""
            SELECT count(*) FROM (
                SELECT {key_hash} AS business_key_hash
                FROM {self.raw_table(source)} r
                WHERE r._run_id = ?
                GROUP BY business_key_hash
                HAVING count(DISTINCT {content_hash}) > 1
            ) q
        """, [run_id]) or 0)
        report.add(CheckResult(
            "dataset.duplicate_business_key", "dataset", "block",
            BLOCK if count else PASS,
            (f"{count} business key(s) have conflicting row values"
             if count else "no conflicting duplicate business keys"),
            expected="0", actual=str(count)))

    def _invalid_rows(
        self, run_id: str, source: SourceSpec
    ) -> tuple[set[int], list[QuarantinedRow]]:
        reasons: dict[int, str] = {}
        raw = self.raw_table(source)
        # Every configured type is checked, not only the numeric ones. A value
        # that is present but does not parse used to become NULL silently for
        # DATE and BOOLEAN columns, and the row was accepted into trusted
        # history with no quarantine entry at all. When the column is the
        # source's event date that is especially damaging: the lookback window,
        # replace-period boundary and archive partitioning all depend on it,
        # and every one of them would have been working from a NULL nobody was
        # told about (Part 9.5 — nothing is silently dropped, including a
        # field).
        for column, configured in source.column_types.items():
            kind = self._type(configured)
            if kind == "VARCHAR":
                continue
            reason = (
                UNPARSEABLE_NUMBER if kind.startswith(NUMERIC_TYPES)
                else UNPARSEABLE_DATE if kind == "DATE"
                else UNPARSEABLE_VALUE
            )
            for row_number, in self.database.query(f"""
                SELECT _source_row_number FROM {raw}
                WHERE _run_id = ?
                  AND {column} IS NOT NULL AND trim({column}) <> ''
                  AND TRY_CAST({column} AS {kind}) IS NULL
            """, [run_id]):
                reasons.setdefault(int(row_number), reason)
        for column in source.non_negative_columns:
            kind = self._type(source.column_types[column])
            for row_number, in self.database.query(f"""
                SELECT _source_row_number FROM {raw}
                WHERE _run_id = ?
                  AND TRY_CAST({column} AS {kind}) < 0
            """, [run_id]):
                reasons.setdefault(int(row_number), NEGATIVE_MEASURE)
        payload = [
            self._quarantine_row(run_id, source, row_number, reason)
            for row_number, reason in sorted(reasons.items())
        ]
        return set(reasons), payload

    def _exact_duplicate_rows(
        self,
        run_id: str,
        source: SourceSpec,
        *,
        excluded: set[int],
    ) -> tuple[set[int], list[QuarantinedRow]]:
        key_hash = self._hash_expr("r", source.business_key, source)
        content_hash = self._hash_expr(
            "r", source.business_columns, source)
        rows = self.database.query(f"""
            WITH ranked AS (
                SELECT _source_row_number,
                       row_number() OVER (
                           PARTITION BY {key_hash}, {content_hash}
                           ORDER BY _source_row_number) AS duplicate_rank
                FROM {self.raw_table(source)} r
                WHERE r._run_id = ?
            )
            SELECT _source_row_number
            FROM ranked WHERE duplicate_rank > 1
            ORDER BY _source_row_number
        """, [run_id])
        selected = {
            int(row[0]) for row in rows if int(row[0]) not in excluded
        }
        payload = [
            self._quarantine_row(
                run_id, source, row_number, EXACT_DUPLICATE)
            for row_number in sorted(selected)
        ]
        return selected, payload

    def _quarantine_row(
        self, run_id: str, source: SourceSpec,
        row_number: int, reason: str
    ) -> QuarantinedRow:
        columns = ", ".join(source.business_columns)
        rows = self.database.query(
            f"SELECT {columns}, _source_sheet FROM {self.raw_table(source)} "
            "WHERE _run_id = ? AND _source_row_number = ?",
            [run_id, row_number])
        values = rows[0] if rows else tuple([None] * (len(source.business_columns) + 1))
        raw_values = dict(zip(source.business_columns, values[:-1]))
        return QuarantinedRow(
            source_row=row_number,
            reason_code=reason,
            raw_values=raw_values,
            source_id=source.source_id,
            source_sheet=str(values[-1] or source.sheet),
        )

    def _build_clean(
        self, run_id: str, source: SourceSpec, *, excluded: list[int]
    ) -> None:
        clean = self.clean_table(source)
        self.database.execute(
            f"DELETE FROM {clean} WHERE _run_id = ?", [run_id])
        typed = [
            self._typed_expr("r", column, source.column_types[column])
            for column in source.business_columns
        ]
        key_hash = self._hash_expr("r", source.business_key, source)
        content_hash = self._hash_expr(
            "r", source.business_columns, source)
        conditions = ["r._run_id = ?"]
        parameters: list[Any] = [run_id]
        for key in source.business_key:
            conditions.append(f"r.{key} IS NOT NULL AND trim(r.{key}) <> ''")
        for column, kind in source.column_types.items():
            if kind.startswith(NUMERIC_TYPES):
                conditions.append(
                    f"(r.{column} IS NULL OR trim(r.{column}) = '' "
                    f"OR TRY_CAST(r.{column} AS {self._type(kind)}) IS NOT NULL)")
        if excluded:
            placeholders = ", ".join("?" for _ in excluded)
            conditions.append(
                f"r._source_row_number NOT IN ({placeholders})")
            parameters.extend(excluded)
        business_list = ", ".join(source.business_columns)
        typed_list = ", ".join(typed)
        self.database.execute(f"""
            INSERT INTO {clean}
                ({business_list}, business_key_hash, row_content_hash,
                 _run_id, _source_id, _source_file, _source_row_number)
            SELECT {typed_list}, {key_hash}, {content_hash},
                   r._run_id, r._source_id, r._source_file,
                   r._source_row_number
            FROM {self.raw_table(source)} r
            WHERE {' AND '.join(conditions)}
        """, parameters)

    def _typed_expr(self, alias: str, column: str, kind: str) -> str:
        if kind == "VARCHAR":
            return f"trim({alias}.{column})"
        safe_type = self._type(kind)
        return f"TRY_CAST({alias}.{column} AS {safe_type})"

    def _hash_expr(
        self, alias: str, columns: Any, source: SourceSpec
    ) -> str:
        parts = []
        for column in columns:
            typed = self._typed_expr(
                alias, str(column), source.column_types[str(column)])
            parts.append(
                f"COALESCE(CAST({typed} AS VARCHAR), chr(0))")
        return f"md5(concat_ws(chr(31), {', '.join(parts)}))"

    def _control_total(
        self,
        run_id: str,
        source: SourceSpec,
        column: str,
        *,
        rejected_rows: set[int],
        filtered_rows: set[int],
    ) -> ControlTotal:
        kind = self._type(source.column_types[column])
        source_value = self._decimal(self.database.scalar(f"""
            SELECT COALESCE(SUM(TRY_CAST({column} AS {kind})), 0)
            FROM {self.raw_table(source)} WHERE _run_id = ?
        """, [run_id]))
        accepted = self._decimal(self.database.scalar(f"""
            SELECT COALESCE(SUM({column}), 0)
            FROM {self.clean_table(source)} WHERE _run_id = ?
        """, [run_id]))
        rejected = self._sum_raw_rows(
            run_id, source, column, kind, rejected_rows)
        filtered = self._sum_raw_rows(
            run_id, source, column, kind, filtered_rows)
        return ControlTotal(
            name=column,
            source_value=source_value,
            database_value=accepted + rejected + filtered,
        )

    def _sum_raw_rows(
        self,
        run_id: str,
        source: SourceSpec,
        column: str,
        kind: str,
        rows: set[int],
    ) -> Decimal:
        if not rows:
            return Decimal(0)
        placeholders = ", ".join("?" for _ in rows)
        value = self.database.scalar(f"""
            SELECT COALESCE(SUM(TRY_CAST({column} AS {kind})), 0)
            FROM {self.raw_table(source)}
            WHERE _run_id = ? AND _source_row_number IN ({placeholders})
        """, [run_id, *sorted(rows)])
        return self._decimal(value)

    @staticmethod
    def _decimal(value: Any) -> Decimal:
        return Decimal(str(value if value is not None else 0))

    @staticmethod
    def _prefix_report(report: QualityReport, source_id: str) -> None:
        for result in report.results:
            result.check_id = f"source.{source_id}.{result.check_id}"
            result.scope = f"source:{source_id}:{result.scope}"

    def _persist_report(self, report: QualityReport) -> None:
        report.persist(self.database)

    # ----------------------------------------------------------- relationships
    def _validate_relationships(self, run_id: str) -> QualityReport:
        report = QualityReport(run_id=run_id)
        for relationship in self.contract.relationships:
            self._validate_relationship(report, run_id, relationship)
        return report

    def _validate_relationship(
        self, report: QualityReport, run_id: str,
        relationship: RelationshipSpec
    ) -> None:
        if relationship.approval_state != "CONFIRMED":
            report.add(CheckResult(
                f"relationship.{relationship.relationship_id}.approval",
                "relationship", "block", BLOCK,
                "relationship meaning is not human-confirmed"))
            return
        left = self.contract.source(relationship.left_source)
        right = self.contract.source(relationship.right_source)
        left_table = self.clean_table(left)
        right_table = self.clean_table(right)
        if relationship.cardinality in {"many_to_one", "one_to_one"}:
            group = ", ".join(relationship.right_keys)
            duplicate_right = int(self.database.scalar(f"""
                SELECT count(*) FROM (
                    SELECT {group} FROM {right_table}
                    WHERE _run_id = ?
                    GROUP BY {group} HAVING count(*) > 1
                ) q
            """, [run_id]) or 0)
            report.add(CheckResult(
                f"relationship.{relationship.relationship_id}.right_cardinality",
                "relationship", "block",
                BLOCK if duplicate_right else PASS,
                (f"{duplicate_right} right-side key(s) violate "
                 f"{relationship.cardinality}"
                 if duplicate_right else "right-side cardinality is valid"),
                expected="0", actual=str(duplicate_right)))
        if relationship.cardinality == "one_to_one":
            group = ", ".join(relationship.left_keys)
            duplicate_left = int(self.database.scalar(f"""
                SELECT count(*) FROM (
                    SELECT {group} FROM {left_table}
                    WHERE _run_id = ?
                    GROUP BY {group} HAVING count(*) > 1
                ) q
            """, [run_id]) or 0)
            report.add(CheckResult(
                f"relationship.{relationship.relationship_id}.left_cardinality",
                "relationship", "block",
                BLOCK if duplicate_left else PASS,
                "left-side cardinality check",
                expected="0", actual=str(duplicate_left)))
        join = " AND ".join(
            f"l.{left_key} = r.{right_key}"
            for left_key, right_key in zip(
                relationship.left_keys, relationship.right_keys))
        first_right = relationship.right_keys[0]
        unmatched = int(self.database.scalar(f"""
            SELECT count(*) FROM {left_table} l
            LEFT JOIN {right_table} r
              ON r._run_id = ? AND {join}
            WHERE l._run_id = ? AND r.{first_right} IS NULL
        """, [run_id, run_id]) or 0)
        status = BLOCK if relationship.require_match and unmatched else (
            WARNING if unmatched else PASS)
        report.add(CheckResult(
            f"relationship.{relationship.relationship_id}.match",
            "relationship",
            "block" if relationship.require_match else "warning",
            status,
            (f"{unmatched} left-side row(s) have no matching "
             f"{relationship.right_source} record"
             if unmatched else "all required relationship keys match"),
            expected="0", actual=str(unmatched)))

    @staticmethod
    def _aggregate_quality(reports: list[QualityReport]) -> str:
        if any(report.status == BLOCK for report in reports):
            return BLOCK
        if any(report.status == WARNING for report in reports):
            return WARNING
        return PASS

    @staticmethod
    def _quality_counts(reports: list[QualityReport]) -> dict[str, int]:
        counts = {PASS: 0, WARNING: 0, BLOCK: 0}
        for report in reports:
            for result in report.results:
                counts[result.status] = counts.get(result.status, 0) + 1
        return counts

    def _record_run(self, outcome: ProjectOutcome) -> None:
        now = datetime.now(timezone.utc)
        total_rows = sum(item.rows_extracted for item in outcome.sources.values())
        rejected = sum(item.rows_rejected for item in outcome.sources.values())
        filtered = sum(item.rows_filtered for item in outcome.sources.values())
        inserted = sum(item.history.inserted for item in outcome.sources.values())
        updated = sum(item.history.updated for item in outcome.sources.values())
        unchanged = sum(item.history.unchanged for item in outcome.sources.values())
        self.database.execute("""
            INSERT OR REPLACE INTO sys.run
                (run_id, report_id, report_version, application_version,
                 status, stage, started_at, finished_at, rows_extracted,
                 rows_rejected, rows_inserted, rows_updated, rows_unchanged,
                 rows_filtered, quality_status, demo_data, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            outcome.run_id, self.contract.project_id,
            self.contract.project_version, self.application_version,
            outcome.status, outcome.status, now, now, total_rows, rejected,
            inserted, updated, unchanged, filtered, outcome.quality_status,
            outcome.demo_data, outcome.error_message,
        ])
