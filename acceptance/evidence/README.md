# Acceptance evidence

Constitution Part 38.2 rule 1: **a gate cannot pass on a sentence.**

When `PROJECT_TOOL gates set --id <GATE> --status pass` runs, the `--evidence`
path must name a file that exists here (or elsewhere in the repository). The
ledger validation fails otherwise, so this folder is what turns "we tested it"
into "here is the proof".

Good evidence:

```text
doctor-2026-08-17.txt                 verifier output, dated
run-RUN-20260817-001-manifest.json    a real run manifest
control-total-reconciliation.txt      expected vs actual, difference = 0
clean-pc-gate-2026-08-17.md           the Part 30.4 sequence, with results
browser-verification-report.json      zero network requests, zero JS errors
operator-handoff-notes.md             what the operator could NOT do alone
```

Not evidence: a summary written from memory, a screenshot with no run ID, or a
claim that a test "passed earlier".
