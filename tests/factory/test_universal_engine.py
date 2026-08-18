from __future__ import annotations
import unittest
from dataclasses import dataclass
from factory.adaptation import CoreChangeRequired,classify_path,core_change_guard
from factory.source_profile import compact_text,profile_chunks
@dataclass
class Chunk:
 column_names:tuple[str,...]; values:tuple[tuple[object,...],...]
class TestCompactSourceProfile(unittest.TestCase):
 def test_profile_uses_structure_without_leaking_values_by_default(self):
  profile=profile_chunks([Chunk(("order_id","amount","date"),(("SECRET-001","1,5","2026-08-01"),("SECRET-002","2,5","2026-08-02")))])
  text=compact_text(profile); self.assertEqual(profile.rows,2); self.assertTrue(profile.column_profiles[0].candidate_unique_key); self.assertNotIn("SECRET-001",text); self.assertIn("Raw sample values are intentionally omitted",text)
 def test_schema_drift_between_chunks_is_not_silently_merged(self):
  with self.assertRaises(ValueError): profile_chunks([Chunk(("a",),((1,),)),Chunk(("b",),((2,),))])
class TestAdaptationBoundary(unittest.TestCase):
 def test_report_sql_is_business_logic_not_core(self):
  self.assertEqual(classify_path("reports/finance/sql/metrics.sql"),"business_logic"); self.assertEqual(classify_path("reports/finance/dashboard.toml"),"presentation_config")
 def test_core_change_requires_an_explicit_reason(self):
  with self.assertRaises(CoreChangeRequired): core_change_guard(["reports/finance/report.toml","app/pipeline.py"])
  self.assertEqual(core_change_guard(["app/pipeline.py"],reason="new reusable capability"),["app/pipeline.py"])
 def test_normal_adaptation_needs_no_core_reason(self):
  self.assertEqual(core_change_guard(["reports/finance/report.toml","reports/finance/dashboard.toml","reports/finance/sql/metrics.sql","migrations/0007_finance.sql"]),[])
