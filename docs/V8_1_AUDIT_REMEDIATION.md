# V8.1 Deep Audit Remediation Ledger

This ledger exists because a prior implementation pass followed the adaptation idea but failed to reconcile the complete V8.1 deep audit first. The repository must not call itself fully universal while a critical finding remains open.

| Finding | Status | Repository response |
|---|---|---|
| C1 project-centric unit | IN PROGRESS | `projects/<id>/` contract added; legacy `reports/` retained temporarily for executable references |
| C2 multi-source contract | CONTRACT DEFINED | `contracts/source_registry.schema.json`, `factory/project_contract.py`, Supply Chain 3-source reference |
| C3 per-source keys/history | CONTRACT DEFINED | each `[[sources]]` owns key/date/history mode/lookback/deletion |
| C4 presentation configuration | IMPLEMENTED | project/report `dashboard.toml` plus dashboard component registry |
| C5 SQL/Python contradiction | RULE FIXED | V8.1 authority + capability registry: SQL preferred, isolated tested Python only when justified |
| C6 quality FAIL/BLOCK conflict | IMPLEMENTED | quality verdicts canonicalized to PASS/WARNING/BLOCK; run state remains FAILED |
| C7 report-specific history.sql | IMPLEMENTED | legacy `history.sql` wiring/files removed; `app/data/history.py` is the reusable implementation |
| C8 machine core scope | IMPLEMENTED | `TEMPLATE_BASELINE.json` + path-scope tool; project map entries carry scope after refresh |
| C9 no-Git baseline | IMPLEMENTED | `tools/template_baseline.py` seal/verify with SHA-256 hashes |
| C10 local core promotion | CONTRACT DEFINED | employee copies may emit candidates only; central master promotes |
| C11 template lineage/upgrades | CONTRACT DEFINED | project lineage + baseline ownership rules; executable upgrade migration still OPEN |
| C12 overclaimed proof | FIXED | Supply Chain reference explicitly says contract proven / execution not yet proven |
| H1 machine config direction | IN PROGRESS | project/source/relationship/presentation contracts added; old report compatibility remains |
| H2 source roles/relationships | CONTRACT DEFINED | explicit source/relationship files and parser |
| H3 capability registry | IMPLEMENTED | `capabilities/registry.json` + schema |
| H4 analytical reuse contract | IMPLEMENTED | analytics capability defines patterns and extension boundary |
| H5 dashboard component catalog | IMPLEMENTED | `capabilities/dashboard_components.json` |
| H6 adaptation manifest schema | IMPLEMENTED | versioned schema added |
| H7 token measurement | IMPLEMENTED | context pack emits portable proxy metrics; provider tokens optional |
| H8 giant constitution vs token goal | IMPLEMENTED | `PROJECT_SKILL.md` remains compact first read; deep constitution is routed/on-demand |
| H9 unnecessary rebuild per adaptation | RULE FIXED | sealed runtime reused when core/runtime unchanged |
| H10 security ownership | IMPLEMENTED | `policy/security_policy.toml` IT-owned; employee questionnaire no longer asks architecture |
| H11 sample-data safety | IMPLEMENTED | metadata-only default; sample inclusion needs explicit policy permission |
| M1 project/report naming drift | IN PROGRESS | new model uses project; old reference compatibility remains |
| M2 artificially SMALL logic wording | FIXED | `PROJECT_SPECIFIC_BUSINESS_LOGIC` is canonical classification |
| M3 absolute Python hardcode ban | FIXED | ban applies to project-specific values in reusable core, not tests/fixtures/system columns |
| M4 map engine rebuild on employee PC | FIXED | employee mode verifies; missing core tooling is template-integrity failure |
| M5 architecture files create-or-verify | FIXED | employee mode verifies; master-core mode alone creates/seals foundational artifacts |
| M6 generated build brief | IMPLEMENTED | `.ai/BUILD_BRIEF.md` and generator exist; project-centric version added |
| M7 reuse percentage denominator | FIXED | percentage removed from primary proof; reuse report uses core/config/rule/test/context counts |

## Release blockers that remain intentionally open

1. Execute the **three-source** Supply Chain reference end to end through shared staging, quality, per-source history and relationship SQL.
2. Complete project-centric generator/UI migration so a new employee project does not need legacy `reports/<id>` at all.
3. Implement and prove template upgrade/migration/rollback between sealed versions.
4. Seal a real distributable `TEMPLATE_BASELINE.json` only after core work is complete.
5. Bundle and hash the real ECharts asset, wire full browser/offline/accessibility/RTL proof, and finish the offline release payload.
6. Complete real protected Excel COM/DRM proof on the authorized corporate Windows environment.
7. Reconcile the 225k-line legacy constitution mechanically with this V8.1 authority and then remove the temporary addendum status.

**Current approval verdict: NOT READY FOR EMPLOYEE DISTRIBUTION.** That is deliberate and honest until the blockers above are proven.
