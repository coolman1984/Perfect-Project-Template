# Constitution improvements: 7.1 → 7.2

What I changed in the supplied master plan, why, and what I deliberately did
**not** change.

---

## Summary

The supplied document (v7.1, 3,486 lines) is unusually good. It is internally
consistent, it anticipates the failure modes that actually kill this kind of
project, and it is explicit about the things agents get wrong. I did not
rewrite it.

**Parts 0–35 are unchanged, verbatim.** Every improvement is an additive
amendment in Parts 36–44, each naming the earlier Part it refines.

The gap I found was not in the *law* — it was in **executability**. v7.1 is
complete as a set of rules and incomplete as a thing an agent can actually
perform. The clearest symptom: Part 0.1 orders every agent to run
`PROJECT_TOOL.bat map verify` as step 2 of a mandatory 90-second start, but

- that file does not exist in a new repository,
- it is Windows-only, so a Linux CI runner or cloud agent cannot run it at all,
- and it depends on a bundled runtime that only exists after a release is built.

An agent that obeys literally is blocked at step 2. An agent that improvises
invents its own workflow and drifts — which is exactly what the document spends
3,486 lines trying to prevent. Eight more gaps of that shape are closed below.

---

## The nine improvements

### 1. Portable tool contract (Part 37) — refines 0.2, 20.9, 34.2

**Problem.** Every command the constitution names is a Windows `.bat` behind a
runtime that does not exist yet.

**Fix.** Two tiers, one behaviour. `tools/project_tool.py` is canonical,
**standard-library only**, and runs anywhere with Python 3.11+.
`PROJECT_TOOL.bat` and `project_tool.sh` are thin wrappers that add nothing but
interpreter discovery. `PROJECT_TOOL.bat map verify` and
`./project_tool.sh map verify` are the same instruction.

Also added a four-value exit-code contract, because the old implicit
pass/fail could not express "I could not verify this":

```text
0 pass · 1 fail · 2 usage error · 3 BLOCKED — nothing was verified
```

Exit 3 exists so an agent can tell "verified and clean" apart from "could not
check". Reporting a 3 as a pass is now itself a compliance violation. And an
unimplemented command must exit non-zero naming the file to implement — never
return a green check that proves nothing.

**Employee runtime is untouched.** Part 23.12's boundary between build tooling
and employee runtime still holds; this only fixes the *developer/agent* tier.

### 2. Machine-readable gate ledger (Part 38) — refines 31, 33

**Problem.** Parts 31.1 and 33 define ~68 acceptance checkboxes as prose.
Nothing recorded which ones actually passed, when, or with what evidence. Agents
self-assessed in chat, and the assessment vanished when the session ended.

**Fix.** `acceptance/gates.yaml` — every gate as a record with status, severity,
evidence path, timestamp and next action. Enforced by `PROJECT_TOOL gates`:

- `status: pass` requires an evidence **file that exists on disk**. A gate
  cannot pass on a sentence.
- `conditional` requires a reason *and* the exact later validation step.
- No release while any `block` gate is unproven.
- The Part 34.4 completion declaration is **generated from the ledger**, not
  written from memory.

This is the amendment that most directly attacks the Part 16.1 risk the
document itself rates highest: "project stalls at 80%".

### 3. Phase −2 instantiation (Part 39) — refines 14, 28.1

**Problem.** Phase −1 assumes files exist to lock. An agent starting from an
empty directory fails Part 0.1 at step 1 and improvises the whole structure.

**Fix.** A phase before the first phase, with a defined exit gate
(`PROJECT_TOOL doctor` green) and exactly **three** questions — project slug,
first report id, report title. These name files and cannot be derived.
Everything else stays `PENDING_APPROVAL` for Phase 0. Phase −2 is the only
phase an agent may complete with no human input.

### 4. Naming and tree precedence (Part 40) — refines 13.1, 24

**Problem.** Part 13.1 shows a tree rooted at `excel-automation/`; Part 24 shows
a different one rooted at `excel-intelligence/`. The document notes the conflict
but never resolves it.

**Fix.** Part 24 is canonical; 13.1 is a reading aid. The root is
`<project_slug>`, chosen at instantiation, and no rule anywhere depends on
either literal string.

### 5. The `PENDING_APPROVAL` sentinel (Part 41) — refines 3, 19.5, 27.8

**Problem.** "AI never invents business meaning" is rule 7, restated in Parts 3,
19.5 and 27.8 — and completely unenforceable. Nothing distinguished an approved
business key from a plausible one an agent invented because it looked
reasonable. By the document's own words that is the most expensive bug in the
system, so it deserves a check rather than a paragraph.

**Fix.** Every human-owned decision is written as the literal token
`PENDING_APPROVAL` until a named human approves it. Approval replaces the token
**and** fills a matching `[approvals]` record with approver, UTC timestamp and
evidence — a filled value with an empty approver still counts as unapproved.

- Discovery/Prototype: sentinels allowed, outputs watermarked
  `UNAPPROVED DEFINITION`.
- Production: `PROJECT_TOOL report validate --mode production` fails, and the
  run refuses to start with `CONFIG_PENDING_APPROVAL`.

An agent may **create** sentinels freely — that is the correct way to record "a
human must decide this". An agent may never **resolve** one. This also turns
Part 18's open-decisions checklist into a live query against the real project.

### 6. Error codes and run states as data (Part 42) — refines 12.2, 12.3, 25.6

**Problem.** ~35 error codes and the whole state machine existed only as prose.
Code, tests, the UI's error screens, the retry policy and the troubleshooting
table each re-encoded the list by hand and drifted apart.

**Fix.** `contracts/error_codes.json` and `contracts/run_states.json` as single
sources of truth. `app/state_machine.py` loads transitions rather than hard-coding
them, so adding a state becomes a versioned contract change. Part 22.8's
four-part operator error screen is now *assembled from the registry*, which makes
non-technical error design a build-time guarantee instead of an aspiration —
including the Arabic message, which no longer depends on someone remembering.

### 7. Secret handling contract (Part 43) — refines 13.5, 22.10, 27.7

**Problem.** v7.1 mentions the per-launch secret, forbids logging secrets, and
requires separate approval for SQL credentials — but never says where a secret
may *live*.

**Fix.** An explicit storage table. Integrated Authentication is the default;
the per-launch secret is memory-only; a stored credential requires DPAPI outside
the application folder and is a deviation needing the IT approval Part 13.5
already demands. Credential-shaped literals now fail the source scan.

### 8. Extraction port and dev/test adapters (Part 44) — refines 6, 7, 15, 23.10

**This is the most consequential change.**

**Problem.** Excel COM needs Windows, an interactive session, licensed Excel and
DRM-authorized files. Layers 3–10 — staging, quality, history, analytics, JSON,
dashboard — need none of that. In v7.1 they were coupled anyway, so a Linux CI
runner, a cloud agent, or a developer without the protected files could test
**nothing**.

The observed consequence is precisely the two behaviours the constitution works
hardest to forbid: the agent stalls, or the agent "simplifies" the architecture
until it runs where it happens to be sitting.

**Fix.** Layer 2 is defined by `ExtractionPort`, not by COM. `com_adapter` is the
only production implementation. `fixture_adapter` is dev/test only, with four
machine-checked rules:

1. A release containing it, or able to select it, **fails** release verification.
2. Its output is watermarked `DEMO DATA` in the UI, JSON, HTML and manifest.
3. It can **never** advance `GATE_PROTECTED_FILE_PROOF` — only a real COM read
   of a real protected workbook does, no matter how much fixture testing passes.
4. It is never selected automatically — not on COM failure, not to keep a run
   green. Automatic selection is the Part 27.8 violation with a friendlier name.

Selection needs both `adapter = "fixture"` **and** `ADAPTER_FIXTURE_ACK=1`, so
it cannot be reached by accident.

The result: Phases 2–10 become fully testable everywhere, while Phase 0/1 stays
exactly as strict as v7.1 wrote it. The untestable surface shrinks from ten
layers to the one that is genuinely environment-bound — and an agent that is
never blocked is never tempted to redesign the architecture to unblock itself.

### 9. Constitution change control (Part 36.2)

**Problem.** The document governs everything except itself. No version
discipline, no changelog, no rule about what an agent may amend.

**Fix.** MAJOR/MINOR versioning with `docs/CONSTITUTION_CHANGELOG.md`. An agent
may author a MINOR amendment that strengthens or clarifies; a MAJOR change —
anything touching Parts 0–35, any locked component, any weakened gate — is a
Part 0.7 deviation requiring explicit user approval. The audit fails when the
version block, the changelog and the amendment index disagree.

---

## What I deliberately did not change

Restraint matters more than additions here. I left alone:

| Thing | Why |
|---|---|
| The seventeen non-negotiable rules (1.4) | They are correct, and each one is load-bearing. A test now asserts they survive future edits. |
| The locked component baseline (23.8) | Removing any of it needs *user* approval, not an agent's judgement. I added nothing to it either. |
| The loopback-server insistence (0.9, 22.10) | The single most-attacked rule, and the document is right. I made it machine-checked instead of softening it. |
| The "offline means bundle, not delete" rule (0.6) | The most important sentence in the document. |
| Every acceptance gate | Amendments may only strengthen. Not one gate was removed or weakened. |
| The prose style and the factory analogy (1.3) | It makes the document readable by the business owner, which is half its purpose. |
| Part 29's Process Defect contract | That is a specific project's business content, not template material. It stays as the worked example it is. |

## Honest limitations

- **Nothing here proves the Windows path works.** Every gate that needs real
  Windows, real Excel or real protected files is `not_started` or `conditional`
  in the ledger, with a named next action. That is the honest state, and the
  tooling refuses to let it look better than it is.
- **The amendments are an agent proposal.** `docs/CONSTITUTION_CHANGELOG.md`
  records them as `pending owner review`. They are additive and weaken nothing,
  but the owner should still read Parts 36–44 and confirm.
- **Part 20.8's Tree-sitter engine is implemented at reduced fidelity.** The
  ranker uses stdlib `ast` plus path references rather than full symbol-level
  parsing. Part 37.2 rule 4 makes that an explicitly acceptable degradation, not
  a silent shortfall — and Tree-sitter remains listed as an optional accelerator.
