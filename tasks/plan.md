# Implementation Plan: Master-Core Completion and Main-Branch Canonicalization

## Overview

Finish every remaining item that can be completed from this Windows workspace, build and verify the offline release, exercise real Excel COM where the installed environment permits it, update evidence without overstating conditional proof, and publish the verified result to `main`. Human approvals, a supplied DRM-protected workbook, a clean target PC, and an unaided operator exercise remain external evidence gates and must not be invented.

## Architecture decisions

- Keep the Universal Core and existing project contracts; extend only existing gate, browser, extraction, release, and documentation surfaces.
- Treat `acceptance/gates.yaml` as the release-status authority and retain `CONDITIONAL` for evidence that requires a different machine, protected file, human owner, or operator.
- Use `main` as the canonical branch. The remote `agent/universal-excel-automation-engine` branch is already an ancestor of `main`, so no code merge is required.
- Build and validate release artifacts before sealing the template baseline or marking artifact-dependent gates passed.

## Task list

### Phase 1: Classify and route

- [x] Record every non-pass gate and its exact closure evidence.
- [x] Inspect only the implementation, contracts, and tests routed to code-closeable items.
- [x] Confirm GitHub authentication and repository permissions (CLI present; authentication pending).

### Phase 2: Close in-workspace functionality

- [ ] Complete recoverable DRM `WAITING_FOR_USER` behavior and tests if the runtime contract supports it.
- [ ] Complete chart-click cross-filter/drill-through and reconciliation tests.
- [ ] Complete local-app keyboard and contrast accessibility tests.
- [ ] Reconcile stale current-state and audit documentation.
- [ ] Exercise and prove template upgrade/migration/rollback locally.

### Checkpoint: Functionality

- [ ] Focused extraction, browser, accessibility, and upgrade tests pass.
- [ ] Map, architecture, and constitution checks still pass.

### Phase 3: Release and machine evidence

- [ ] Run `BUILD_RELEASE.bat` and inspect the exact output.
- [ ] Verify release completeness, component hashes, fail-closed behavior, and no developer-tool leakage where the verifier supports real checks.
- [ ] Run real Excel COM against a disposable workbook if desktop Excel is installed.
- [ ] Benchmark bulk block reads on a large disposable workbook without treating it as DRM proof.

### Checkpoint: Release

- [ ] Built release passes all locally executable checks.
- [ ] Conditional gates remain conditional unless their required environment was actually exercised.
- [ ] Rollback instructions and release evidence are current.

### Phase 4: Finalize and publish

- [ ] Run all required project verifiers and the full unit-test discovery command.
- [ ] Review staged diff and scan for secrets.
- [ ] Commit logical increments to `main` and push to `origin/main`.
- [ ] Set GitHub default branch to `main` and verify `origin/HEAD`/repository metadata.

## External evidence that cannot be fabricated

- Named business-owner approval and IT/security approval.
- Real DRM-protected workbook proof unless the user supplies an authorized file.
- Standard-user and clean-offline-PC runs unless this machine satisfies those exact conditions.
- Two production-like runs using real approved data.
- Fresh independent-agent onboarding and non-technical operator handoff.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Release build changes many generated files | Review and rollback become difficult | Verify exact targets, keep generated outputs scoped, and commit logical slices |
| COM automation leaves Excel running | User disruption | Use isolated Excel instance, bulk reads, `SaveChanges=False`, and guaranteed cleanup |
| Gate inflation | False readiness claim | Require direct evidence before changing any status to `pass` |
| GitHub setting mutation fails | `main` remains non-default | Verify `gh` authentication before mutation and re-read repository metadata afterward |
