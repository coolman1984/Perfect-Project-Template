# ADR-0001 — Simple final-user product surface

- Status: Accepted
- Date: 2026-08-19
- Decision owner: Product owner

## Context

The complete template correctly contains technical build and governance
machinery, but exposing that machinery in the delivered operator package makes
the non-technical employee responsible for architecture they should never see.

## Decision

Keep the complete template/build package for ChatGPT Work. Deliver a separate
operator ZIP whose visible root contains only `START.bat`, `QUICK_START.html`
and `Application/`.

The package builder consumes the already sealed and verified `release/current`
folder. It does not bypass the existing frozen-runtime, checksum, license,
repair, offline or architecture checks.

## Consequences

- The final employee journey is extract, double-click and work.
- All technical machinery remains private inside `Application/` or the build
  template.
- `PROJECT_TOOL package verify` rejects extra root entries, missing executable
  files and unsafe ZIP paths.
- This decision changes presentation and packaging only. It does not downgrade
  the runtime architecture or mark environment-bound gates as passed.

## Approval

Explicitly approved by the product owner in the project conversation on
2026-08-19.
