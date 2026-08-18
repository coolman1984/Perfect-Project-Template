# READ FIRST — Universal Excel Automation Engine

This repository is already the application. Normal work adapts a **project pack**, not a blank report scaffold.

Start:

```text
PROJECT_TOOL doctor
PROJECT_TOOL map verify
PROJECT_TOOL map context --task "<exact task>" --budget 4000
```

Then read `.ai/CURRENT_STATE.md`, `.ai/CONTEXT_PACK.md`, and only the routed project/core files.

For an employee copy, `PROJECT_TOOL template-baseline verify` must pass against a **sealed** `TEMPLATE_BASELINE.json`. In master-core development an unsealed baseline is expected until release, but employee distribution is blocked.

Use `projects/<project_id>/` as the adaptation unit. Check `capabilities/registry.json` before opening Universal Core. Multi-source roles and relationships are first-class. Security policy is IT-owned. Profiling is metadata-only by default.

Do not claim full universality until `projects/_REFERENCE_SUPPLY_CHAIN/` executes end to end as a three-source golden reference. Current detailed status is in `docs/V8_1_AUDIT_REMEDIATION.md`.
