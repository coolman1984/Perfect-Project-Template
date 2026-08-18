"""Population and control-total reconciliation.

Quality verdicts are PASS / WARNING / BLOCK. A BLOCK verdict means the run must
not update trusted history. The execution state can then become FAILED; the two
vocabularies are intentionally separate.
"""
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from app.quality.engine import BLOCK, PASS, CheckResult, QualityReport

@dataclass(frozen=True)
class Population:
    source_rows:int; accepted_rows:int; rejected_rows:int; intentionally_filtered_rows:int
    filter_reasons:tuple[tuple[str,int],...]=()
    @property
    def difference(self)->int:
        return self.source_rows-self.accepted_rows-self.rejected_rows-self.intentionally_filtered_rows

@dataclass(frozen=True)
class ControlTotal:
    name:str; source_value:Decimal; database_value:Decimal
    @property
    def difference(self)->Decimal:return self.source_value-self.database_value

def check_population(report:QualityReport,population:Population)->CheckResult:
    status=PASS if population.difference==0 else BLOCK
    reasons=", ".join(f"{name}={count}" for name,count in population.filter_reasons) or "none"
    result=CheckResult("population.equation","dataset","block",status,"source rows reconcile to accepted + rejected + explicitly filtered" if status==PASS else "row population does not reconcile — publishing is blocked",str(population.source_rows),f"accepted={population.accepted_rows}; rejected={population.rejected_rows}; filtered={population.intentionally_filtered_rows}; reasons={reasons}",str(population.difference),"0")
    report.add(result);return result

def check_control_total(report:QualityReport,control:ControlTotal,*,tolerance:Decimal=Decimal(0),severity:str="block")->CheckResult:
    within=abs(control.difference)<=tolerance; status=PASS if within else BLOCK
    result=CheckResult(f"control_total.{control.name}","dataset",severity,status,f"{control.name} reconciles" if within else f"{control.name} differs by {control.difference} — publishing is blocked",str(control.source_value),str(control.database_value),str(control.difference),str(tolerance))
    report.add(result);return result
