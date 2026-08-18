# Universal Excel Automation Engine — Adaptation Skill

**The ready template is the product. The employee AI agent adapts it; it does not rebuild it.**

## Mental model

```text
SEALED UNIVERSAL CORE
+ EMPLOYEE PROJECT PACK
= UNIQUE WORKING AUTOMATION
```

The project, not a report, is the adaptation unit. One project may contain orders, inventory, master data, targets, corrections and multiple outputs.

Normal project-owned files live under `projects/<project_id>/`: source roles, mappings, relationships, quality controls, metric bindings, presentation configuration and isolated project-specific business rules.

## Work order

```text
UNDERSTAND → PROFILE → CAPABILITY MAP → CONFIGURE → PROJECT-SPECIFIC LOGIC → TEST → DELIVER
```

Classify every requirement as `REUSE_AS_IS`, `CONFIGURE`, `PROJECT_SPECIFIC_BUSINESS_LOGIC`, or `NEW_REUSABLE_CAPABILITY_CANDIDATE`.

Search `capabilities/registry.json` before reading core source. The registry names supported patterns, configuration entry points, extension points, tests and limitations.

## Multi-source is mandatory

Each source has an independent role, file pattern, sheet/table discovery, grain, business key, date/period, load/update strategy and quality controls. Relationships are explicit and approved. Never concatenate unrelated workbooks merely to claim multi-source support.

`projects/_REFERENCE_SUPPLY_CHAIN/` is the required three-role reference: orders, inventory and item master. Until its golden execution is implemented, it remains contract-proven only and the template is not fully universal.

## Core guard without Git

`TEMPLATE_BASELINE.json` owns path scopes and sealed SHA-256 hashes. Git may add evidence, but copied employee folders must remain verifiable with no Git history.

Employee projects may propose reusable-capability candidates. Promotion happens only in the authoritative master template, which creates a new template version and upgrade path.

## Calculations, history, quality

Prefer deterministic SQL. Use isolated tested Python only where SQL is materially unsafe or unclear; never duplicate a trusted formula. JavaScript is not the trusted calculation layer.

History semantics are Universal Core and selected per source. Normal project packs do not implement `history.sql`.

Quality verdicts are `PASS`, `WARNING`, `BLOCK`. A BLOCK causes run state `FAILED` and leaves trusted history/last-good output untouched.

## Human boundary

The employee supplies business meaning and approvals. IT/Security owns storage, retention and external-AI policy. Source profiling is metadata-only by default; raw/protected values require explicit policy permission.

## Low-token proof

The first context is `PROJECT_SKILL.md` + current state + generated context pack. The map carries machine path scope. Context reporting uses portable proxies: estimated tokens, files selected, bytes selected and expansion count. Actual model tokens are reported only when the tool exposes them.

## Packaging

No core/runtime change means reuse the sealed runtime and package/validate the project pack. Core/runtime change means master-core rebuild, new sealed baseline/version, compatibility migration, verification and rollback.

The important reuse proof is not a flattering percentage. It is few/no core files changed, reused capabilities/tests, limited project-specific code, no new architecture decision, and a small routed context.
