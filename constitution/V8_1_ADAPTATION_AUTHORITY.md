# V8.1 Adaptation Authority Addendum

**Status:** controlling remediation addendum for the Universal Excel Automation Engine branch.

The older constitution remains the deep technical baseline for extraction, DuckDB/Parquet, loopback API, offline packaging, security, testing and recovery. Where its old report-centric wording conflicts with the audited V8.1 adaptation-first direction, this addendum controls until the full constitution is mechanically reconciled.

## Canonical mental model

```text
SEALED UNIVERSAL CORE
        +
EMPLOYEE PROJECT / ADAPTATION PACK
        =
ONE WORKING EMPLOYEE AUTOMATION
```

The **project** is the adaptation unit. A report/dashboard is an output of the project. A project may contain many independent source roles, entities, relationships, calculations and outputs.

Normal employee work changes project-owned configuration, mappings, presentation and isolated business rules. It does not rebuild extraction, database, quality, history, API, UI framework, runtime, packaging, security, map or test infrastructure.

## Canonical rules correcting legacy contradictions

1. **Project-centric, not report-centric.** New adaptations live under `projects/<project_id>/`. `reports/` remains a compatibility/reference area while the migration is completed.
2. **Multi-source is a core requirement, not a future nice-to-have.** Every source can have its own role, file/sheet discovery, grain, key, date, load strategy and quality controls.
3. **Relationships are explicit contracts.** Joins name source roles, keys, cardinality, join semantics and human approval state. The engine never guesses a relationship from similar column names.
4. **History is Universal Core.** Append/upsert/snapshot/replace-period behavior is selected per source/entity by configuration. Normal adaptations do not carry `sql/history.sql` implementations.
5. **Trusted calculation rule.** Prefer deterministic versioned SQL when practical. Use isolated tested Python only when SQL would be unsafe, unreadable or materially inappropriate. Never implement the same trusted formula twice. Browser JavaScript is never the trusted business-calculation layer.
6. **Quality vocabulary.** `PASS`, `WARNING`, `BLOCK` are quality verdicts. A `BLOCK` verdict causes the execution run state to become `FAILED`. Do not use `FAIL` as a second quality vocabulary.
7. **Core ownership is machine-readable.** `TEMPLATE_BASELINE.json` defines path scope and, when sealed, hashes every core/tooling file. Git is optional evidence, not the baseline authority.
8. **No local forked masters.** An employee project may emit a reusable-capability candidate. Only the authoritative master-template process promotes it into Universal Core and issues a new template version.
9. **Upgrade lineage is mandatory.** Project packs record template ID/version/baseline. Master upgrades replace/migrate core-owned paths while preserving project-owned paths, with compatibility verification and rollback.
10. **Security is policy-owned.** Corporate storage, retention and external-AI rules come from IT/Security policy. A non-technical employee supplies business meaning, not security architecture.
11. **AI profiling is metadata-first.** Raw/protected samples are omitted unless policy explicitly permits them. Provider token counts are optional telemetry; portable context proxies are the required measurement.
12. **Normal packaging reuses the sealed runtime.** If core/runtime did not change, validate and package the project pack with the approved runtime. Rebuild/freeze the entire application only through master-core release work.
13. **Completeness is evidence-tiered.** A requirement is tracked as: `REQUIRED`, `CONTRACT_DEFINED`, `MACHINE_VERIFIABLE`, `REFERENCE_PROVEN`. Mentioning a requirement in prose is not proof.

## Required machine artifacts

```text
TEMPLATE_BASELINE.json
contracts/template_baseline.schema.json
contracts/project.schema.json
contracts/source_registry.schema.json
contracts/relationships.schema.json
contracts/adaptation_manifest.schema.json
contracts/reuse_report.schema.json
contracts/source_profile.schema.json
contracts/capability_registry.schema.json
capabilities/registry.json
capabilities/dashboard_components.json
policy/security_policy.toml
projects/<project_id>/project.toml
projects/<project_id>/sources.toml
projects/<project_id>/relationships.toml
projects/<project_id>/dashboard.toml
```

## Distribution gate

The master template is **not employee-ready** while `TEMPLATE_BASELINE.json` is unsealed, while the multi-source Reference B is contract-only rather than executable, or while the required offline/browser/COM environment gates remain unproven. Green unit tests do not override those facts.
