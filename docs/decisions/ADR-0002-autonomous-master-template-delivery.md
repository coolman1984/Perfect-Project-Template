# ADR-0002 — Autonomous master-template delivery

- **Date:** 2026-08-19
- **Status:** accepted
- **Approved by:** product owner in the project conversation

## Problem

The source repository and final-user ZIP were defined, but a non-technical
owner still had to explain the commissioning/adaptation workflow to each agent.
Future online adaptation also lacked a verified archive that combined portable
instructions/source with a previously built offline Windows runtime.

## Decision

The first connected Windows commissioning produces two distinct archives:

1. `MASTER_TEMPLATE.zip` for capable AI coding environments. It contains
   provider entry instructions, portable source/tests and a sealed Windows
   runtime with exact offline dependencies.
2. `ProjectName.zip` for the non-technical operator. Its root remains exactly
   `START.bat`, `QUICK_START.html`, `Application/`.

The canonical guide auto-detects first commissioning versus uploaded-master
adaptation. Cloud adaptation may change project-owned files only, then composes
one project into a private copy of the sealed runtime. It cannot silently fall
back to a mockup when file execution/testing/ZIP capabilities are absent.

## Evidence and equivalence tests

- Master verifier checks the Git-independent sealed core and immutable hashes.
- Privacy tests reject production Excel/data and non-reference project packs.
- Delivery tests prove the operator runtime contains only the selected project.
- Existing operator ZIP, offline runtime, architecture and release tests remain
  controlling; no runtime capability is removed.

## Risks and rollback

The master archive is large because the complete runtime and dependency cache
are intentional. Provider upload limits may require a coding workspace with
sufficient file capacity. Rollback removes the master contract/builder and
provider entry files; ADR-0001 and the existing operator package remain valid.
