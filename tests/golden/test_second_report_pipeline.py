"""Second-domain proof: Maintenance downtime, same Universal Core."""
from __future__ import annotations
import os,tempfile,unittest
from decimal import Decimal
from pathlib import Path
from tools._common import REPO_ROOT
try:
 import duckdb  # noqa: F401
 HAS_DUCKDB=True
except ImportError: HAS_DUCKDB=False
FIXTURES=REPO_ROOT/"tests"/"fixtures"/"downtime"

@unittest.skipUnless(HAS_DUCKDB,"duckdb is an application-tier dependency")
class TestSecondDomainReuse(unittest.TestCase):
 def setUp(self):
  from app.data.database import Database
  from app.pipeline import Pipeline,ReportContract
  os.environ["ADAPTER_FIXTURE_ACK"]="1"; self._temp=tempfile.TemporaryDirectory(); self.contract=ReportContract(REPO_ROOT/"reports"/"line_downtime"); self.database=Database(Path(self._temp.name)/"downtime.duckdb"); self.pipeline=Pipeline(self.database,self.contract); self.pipeline.prepare()
 def tearDown(self):
  self.database.close(); self._temp.cleanup(); os.environ.pop("ADAPTER_FIXTURE_ACK",None)
 def run_fixture(self,name,run_id):
  from app.excel.fixture_adapter import FixtureExtractionAdapter
  path=FIXTURES/name; adapter=FixtureExtractionAdapter(path); adapter.open(str(path),{"report_id":self.contract.report_id,"run_id":run_id,"sheet":"Downtime","extraction":self.contract.report["extraction"]}); return self.pipeline.run(run_id,adapter)
 def test_different_department_runs_through_same_engine(self):
  first=self.run_fixture("period_1.csv","RUN-DOWN-001"); second=self.run_fixture("period_2.csv","RUN-DOWN-002")
  self.assertEqual(first.status,"COMPLETE"); self.assertEqual(second.status,"COMPLETE"); self.assertEqual(second.quality_status,"WARNING"); self.assertEqual(second.history.updated,1); self.assertEqual(second.history.inserted,3); self.assertEqual(second.rows_rejected,1); self.assertEqual(second.rows_filtered,1)
  total=self.database.scalar("SELECT SUM(downtime_minutes) FROM analytics.history_downtime WHERE is_active=TRUE"); rows=self.database.scalar("SELECT count(*) FROM analytics.history_downtime WHERE is_active=TRUE")
  self.assertEqual(Decimal(str(total)),Decimal("305.0000")); self.assertEqual(int(rows),7)
  dashboard=second.dashboard; self.assertEqual([x["label"] for x in dashboard["kpis"]],["Downtime","Downtime events","Average event"]); self.assertEqual([x["id"] for x in dashboard["charts"]],["downtime_trend","line_pareto"]); self.assertEqual(dashboard["report"]["period"],"2026-08-03"); self.assertTrue(any("L1" in x["text"] for x in dashboard["insights"]))
 def test_second_period_rerun_is_idempotent(self):
  self.run_fixture("period_1.csv","RUN-DOWN-001"); self.run_fixture("period_2.csv","RUN-DOWN-002"); rerun=self.run_fixture("period_2.csv","RUN-DOWN-003"); self.assertEqual(rerun.history.inserted,0); self.assertEqual(rerun.history.updated,0); self.assertEqual(rerun.history.unchanged,4); self.assertEqual(int(self.database.scalar("SELECT count(*) FROM analytics.history_downtime WHERE is_active=TRUE")),7)
 def test_unexpected_reason_warns_but_loads(self):
  self.run_fixture("period_1.csv","RUN-DOWN-001"); outcome=self.run_fixture("period_2.csv","RUN-DOWN-002"); self.assertTrue(any("reason" in r.check_id for r in outcome.quality_report.results if r.status=="WARNING")); self.assertEqual(int(self.database.scalar("SELECT count(*) FROM analytics.history_downtime WHERE reason='Utility' AND is_active=TRUE")),1)
 def test_control_total_balances_with_reject_and_duplicate(self):
  self.run_fixture("period_1.csv","RUN-DOWN-001"); outcome=self.run_fixture("period_2.csv","RUN-DOWN-002"); self.assertEqual(outcome.control_totals[0].difference,Decimal(0))

class TestUniversalCoreVocabulary(unittest.TestCase):
 def test_shared_pipeline_has_no_reference_department_kpis(self):
  text=(REPO_ROOT/"app"/"pipeline.py").read_text("utf-8").lower()
  for term in ("produced_total","defect_total","defect_rate_ppm","pareto_by_model","model_code","production quality"):
   self.assertNotIn(term,text,f"Universal Core leaked report vocabulary: {term}")
