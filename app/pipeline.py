"""UNIVERSAL CORE — report-agnostic Excel automation pipeline.

The shared application already exists. A department project supplies source
mapping, table shape, business SQL and dashboard configuration. This module
executes those contracts; it must not contain department vocabulary or KPI
formulas.
"""
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from app.analytics.configured import ConfiguredAnalytics, load_dashboard_config
from app.analytics.runner import SqlRunner, as_decimal
from app.dashboard import json_builder
from app.data.archive import archive_history
from app.data.database import Database
from app.data.history import HistoryEngine, HistoryResult
from app.data.migrations import migrate
from app.data.staging import LINEAGE_COLUMNS, StagingWriter
from app.errors import AppError
from app.quality.engine import FAIL, QualityEngine, QualityReport
from app.quality.quarantine import EXACT_DUPLICATE, NEGATIVE_MEASURE, QuarantinedRow, quarantine_rows, summary_by_reason
from app.quality.reconciliation import ControlTotal, Population, check_control_total, check_population
from app.state_machine import RunStateMachine

class ReportContract:
    def __init__(self, directory: Path) -> None:
        self.directory=Path(directory)
        self.report=tomllib.loads((self.directory/"report.toml").read_text("utf-8"))
        self.pipeline=tomllib.loads((self.directory/"pipeline.toml").read_text("utf-8"))
        name=str(self.pipeline.get("dashboard",{}).get("config","dashboard.toml"))
        self.dashboard=load_dashboard_config(self.directory/name)
    @property
    def report_id(self)->str: return self.report["report_id"]
    @property
    def sql_directory(self)->Path: return self.directory/"sql"
    @property
    def uses_fixture_adapter(self)->bool: return self.report.get("excel",{}).get("adapter")=="fixture"
    @property
    def business_columns(self)->list[str]: return list(self.pipeline["columns"]["business"])
    @property
    def key_columns(self)->list[str]: return list(self.report["history"]["business_key"])
    def table(self,name:str)->str: return self.pipeline["tables"][name]
    def sql_file(self,name:str)->str: return self.pipeline["sql"][name]

@dataclass
class RunOutcome:
    run_id:str; status:str; quality_status:str
    history:HistoryResult=field(default_factory=HistoryResult)
    rows_extracted:int=0; rows_rejected:int=0; rows_filtered:int=0
    control_totals:list[ControlTotal]=field(default_factory=list)
    quality_report:QualityReport|None=None; dashboard:dict[str,Any]|None=None
    error_code:str|None=None; error_message:str|None=None; demo_data:bool=False
    quarantine:dict[str,int]=field(default_factory=dict)
    @property
    def succeeded(self)->bool: return self.status=="COMPLETE"

class Pipeline:
    def __init__(self,database:Database,contract:ReportContract,*,application_version:str="0.0.0")->None:
        self.database=database; self.contract=contract; self.application_version=application_version
        self.sql=SqlRunner(database,contract.sql_directory)
        self.analytics=ConfiguredAnalytics(self.sql,contract.dashboard,metrics_file=contract.sql_file("metrics"),insights_file=contract.sql_file("insights"))
    def prepare(self)->None: migrate(self.database,application_version=self.application_version)
    def run(self,run_id:str,port:Any,*,requested_period:str|None=None)->RunOutcome:
        machine=RunStateMachine(); outcome=RunOutcome(run_id,"RUNNING","",demo_data=self.contract.uses_fixture_adapter); started=datetime.now(timezone.utc)
        try:
            for state in ("CHECKING_SOURCE","OPENING_EXCEL","EXTRACTING"): machine.to(state)
            outcome.rows_extracted=self._stage(run_id,port)
            machine.to("STAGING"); machine.to("VALIDATING")
            quality,_population,controls=self._validate(run_id,outcome); outcome.quality_report=quality; outcome.quality_status=quality.status; outcome.control_totals=controls; quality.persist(self.database)
            if quality.status==FAIL:
                machine.to("FAILED"); first=quality.blocking_failures()[0]; outcome.status="FAILED"; outcome.error_code=self._error_code_for(first.check_id); outcome.error_message=first.message; self._record_run(outcome,started); return outcome
            machine.to("CLEANING"); machine.to("UPDATING_HISTORY"); outcome.history=self._update_history(run_id,requested_period)
            machine.to("ARCHIVING"); self._archive(); machine.to("CALCULATING"); package=self.analytics.run(); machine.to("BUILDING_INSIGHTS"); machine.to("BUILDING_JSON")
            outcome.dashboard=json_builder.build(contract=self.contract,analytics=package,outcome=outcome)
            for state in ("BUILDING_DASHBOARD","VERIFYING","COMPLETE"): machine.to(state)
            outcome.status="COMPLETE"
        except AppError as error:
            outcome.status="FAILED"; outcome.error_code=error.code; outcome.error_message=str(error); raise
        finally:
            if outcome.status in ("COMPLETE","FAILED"): self._record_run(outcome,started)
        return outcome
    def _stage(self,run_id:str,port:Any)->int:
        result=StagingWriter(self.database,self.contract.table("raw"),self.contract.business_columns).stage(port,port.lineage()); return result.rows_staged
    def _validate(self,run_id:str,outcome:RunOutcome)->tuple[QualityReport,Population,list[ControlTotal]]:
        quality=QualityReport(run_id=run_id); engine=QualityEngine(self.database,self.contract.report); raw=self.contract.table("raw"); checks=self.contract.sql_file("checks"); clean_sql=self.contract.sql_file("clean")
        present=[c for c in self.database.columns_of(raw) if c not in LINEAGE_COLUMNS]
        staged=[c for c in present if (self.database.scalar(f"SELECT count(*) FROM {raw} WHERE _run_id = ? AND {c} IS NOT NULL",[run_id]) or 0)>0]
        control_column=self.contract.report["quality"]["control_total_column"]
        engine.check_required_columns(quality,staged,self.contract.key_columns+[control_column])
        if quality.status==FAIL:
            source=int(self.sql.scalar(checks,"source_row_count",[run_id]) or 0); return quality,Population(source,0,0,0),[]
        engine.check_no_blank_business_key(quality,raw,run_id,self.contract.key_columns)
        rejected=self._quarantine_rejects(run_id,clean_sql); filtered=self._quarantine_duplicates(run_id,clean_sql); outcome.rows_rejected=rejected; outcome.rows_filtered=filtered
        self.sql.run_script(clean_sql,"build_clean",[run_id])
        engine.check_duplicate_business_keys(quality,self.contract.table("clean"),run_id,self.contract.key_columns)
        non_negative=list(self.contract.report.get("quality",{}).get("non_negative_columns",[]))
        if non_negative: engine.check_non_negative(quality,raw,run_id,non_negative)
        category=self.contract.pipeline.get("columns",{}).get("category"); allowed=self.contract.report.get("quality",{}).get("approved_categories",[])
        if category and allowed: engine.check_category_allowed(quality,self.contract.table("clean"),run_id,str(category),list(allowed))
        source=int(self.sql.scalar(checks,"source_row_count",[run_id]) or 0); accepted=int(self.sql.scalar(clean_sql,"clean_row_count",[run_id]) or 0)
        population=Population(source,accepted,rejected,filtered,(("exact_duplicate",filtered),)); check_population(quality,population)
        source_value=as_decimal(self.sql.scalar(checks,"source_control_total",[run_id])); accepted_value=as_decimal(self.sql.scalar(checks,"accepted_control_total",[run_id])); rejected_value=as_decimal(self.sql.scalar(checks,"rejected_control_total",[run_id])); filtered_value=as_decimal(self.sql.scalar(checks,"filtered_control_total",[run_id]))
        control=ControlTotal(control_column,source_value,accepted_value+rejected_value+filtered_value); check_control_total(quality,control); outcome.quarantine=summary_by_reason(self.database,run_id); return quality,population,[control]
    def _quarantine_rejects(self,run_id:str,clean_sql:str)->int:
        if "negative_measure_rows" not in self.sql.statements(clean_sql): return 0
        rows=self.sql.run_named(clean_sql,"negative_measure_rows",[run_id]); payload=[QuarantinedRow(source_row=r[0],reason_code=NEGATIVE_MEASURE,raw_values=dict(zip(self.contract.business_columns,r[1:]))) for r in rows]
        return quarantine_rows(self.database,run_id,self.contract.report_id,payload)
    def _quarantine_duplicates(self,run_id:str,clean_sql:str)->int:
        if "exact_duplicate_rows" not in self.sql.statements(clean_sql): return 0
        rows=self.sql.run_named(clean_sql,"exact_duplicate_rows",[run_id]); payload=[QuarantinedRow(source_row=r[0],reason_code=EXACT_DUPLICATE,raw_values=dict(zip(self.contract.business_columns,r[1:]))) for r in rows]
        return quarantine_rows(self.database,run_id,self.contract.report_id,payload)
    def _update_history(self,run_id:str,requested_period:str|None)->HistoryResult:
        h=self.contract.report["history"]
        return HistoryEngine(self.database,history_table=self.contract.table("history"),clean_table=self.contract.table("clean"),business_columns=self.contract.business_columns,key_columns=self.contract.key_columns,event_date_column=h["event_date"]).apply(run_id,load_mode=self.contract.report["load_mode"],lookback_days=int(h.get("lookback_days") or 0),deletion_rule=h.get("deletion_rule","ignore"),requested_period=requested_period)
    def _archive(self)->None:
        archive_history(self.database,history_table=self.contract.table("history"),report_id=self.contract.report_id,archive_root=Path("workspace")/"archive"/self.contract.report_id,event_date_column=self.contract.report["history"]["event_date"])
    def _error_code_for(self,check_id:str)->str:
        if check_id.startswith("structural.required_columns"): return "SCHEMA_REQUIRED_COLUMN_MISSING"
        if check_id.startswith("control_total"): return "DQ_CONTROL_TOTAL_MISMATCH"
        if check_id.startswith("dataset.duplicate"): return "DATA_DUPLICATE_BUSINESS_KEY"
        return "ANALYTICS_TEST_FAILED"
    def _record_run(self,outcome:RunOutcome,started:datetime)->None:
        self.database.execute("INSERT OR REPLACE INTO sys.run (run_id, report_id, report_version, application_version, status, stage, started_at, finished_at, rows_extracted, rows_rejected, rows_inserted, rows_updated, rows_unchanged, rows_filtered, quality_status, demo_data, error_code, error_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",[outcome.run_id,self.contract.report_id,self.contract.report["report_version"],self.application_version,outcome.status,outcome.status,started,datetime.now(timezone.utc),outcome.rows_extracted,outcome.rows_rejected,outcome.history.inserted,outcome.history.updated,outcome.history.unchanged,outcome.rows_filtered,outcome.quality_status,outcome.demo_data,outcome.error_code,outcome.error_message])
