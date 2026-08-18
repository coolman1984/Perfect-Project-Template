from __future__ import annotations
import json,subprocess,sys,unittest
from pathlib import Path
from factory.project_questionnaire import PROJECT_QUESTIONS,validate_plain_language_questions
from tools._common import REPO_ROOT
from tools.project_map import build_manifest

class TestV81AgentAndEmployeeBoundary(unittest.TestCase):
    def test_normal_project_questions_do_not_ask_security_or_software_architecture(self):
        self.assertEqual(validate_plain_language_questions(),[])
        prompts=" ".join(q.prompt.lower() for q in PROJECT_QUESTIONS)
        for term in ("storage location","retention","duckdb","fastapi","parquet","firewall"):
            self.assertNotIn(term,prompts)
    def test_map_manifest_carries_machine_scope(self):
        manifest=build_manifest(); self.assertTrue(manifest["files"])
        self.assertTrue(all(entry.get("scope") for entry in manifest["files"].values()))
        self.assertEqual(manifest["files"]["app/pipeline.py"]["scope"],"universal_core")
        self.assertEqual(manifest["files"]["projects/_REFERENCE_SUPPLY_CHAIN/sources.toml"]["scope"],"project_config")
    def test_project_tool_exposes_v81_commands(self):
        for args in (("adaptation",),("template-baseline",)):
            result=subprocess.run([sys.executable,"tools/project_tool.py",*args],cwd=REPO_ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
    def test_context_metrics_are_portable_proxies(self):
        result=subprocess.run([sys.executable,"tools/project_tool.py","map","context","--task","adapt Supply Chain project","--budget","1200"],cwd=REPO_ROOT,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        payload=json.loads((REPO_ROOT/"workspace/context_metrics.json").read_text("utf-8"))
        for key in ("estimated_tokens","files_selected","bytes_selected","expansions","provider_tokens"): self.assertIn(key,payload)
        self.assertIsNone(payload["provider_tokens"])

if __name__=="__main__": unittest.main()
