# LESSONS

Concise reusable learning, grouped by topic (Constitution Part 21.2).
**Search this by topic — do not read it by default.**

Capture only knowledge that will change a future agent's decision or prevent
repeated work. Do **not** capture chat history, temporary guesses, verbose work
logs, raw sensitive values, or facts already obvious from code and contracts.

Format:

```text
### L-NNN — one-line title
Evidence: what proved it (file, test, run, benchmark, approval)
Lesson:   what a future agent should do differently
Date:     YYYY-MM-DD · Owner: name or role
```

---

## Template lessons

These come from building this template and apply to any project instantiated
from it. Project-specific lessons are added below as real evidence appears.

### L-001 — A green check that proves nothing is worse than a missing check

Evidence: Part 37.3 was written after observing that agents treat any zero exit
code as permission to proceed.
Lesson: An unimplemented command must exit non-zero with
`TOOL_COMMAND_NOT_IMPLEMENTED` and name the file to implement. Never stub a
verifier to return success. Exit code 3 (BLOCKED) exists so "could not verify"
is distinguishable from "verified and clean".
Date: 2026-08-17 · Owner: platform

### L-002 — Coupling every layer to Excel COM is what makes agents redesign the architecture

Evidence: Layers 3–10 need no Windows, no Excel and no DRM, yet in v7.1 none of
them could be tested without all three.
Lesson: Depend on `ExtractionPort`, not on COM. The dev adapter unblocks
Phases 2–10 everywhere while `GATE_PROTECTED_FILE_PROOF` stays exactly as strict
as before. An agent that is not blocked is not tempted to "simplify" (Part 44).
Date: 2026-08-17 · Owner: platform

### L-003 — Unenforceable rules get violated politely

Evidence: "AI never invents business meaning" is rule 7, restated in Parts 3,
19.5 and 27.8 — and nothing distinguished an approved business key from a
plausible invented one.
Lesson: Give every human-owned decision a machine-checkable sentinel. An agent
may create `PENDING_APPROVAL` freely and may never resolve it. Approval needs
the value *and* a named approver, timestamp and evidence (Part 41).
Date: 2026-08-17 · Owner: platform

### L-004 — Self-assessed completion disappears when the session ends

Evidence: Parts 31.1 and 33 define ~68 prose checkboxes; nothing recorded which
were proven, so each new agent re-declared completion from scratch.
Lesson: Track gates in `acceptance/gates.yaml` with an evidence path that must
exist on disk. Generate the Part 34.4 completion declaration from the ledger,
never from memory (Part 38).
Date: 2026-08-17 · Owner: platform

### L-005 — A scanner that flags its own definitions teaches agents to ignore it

Evidence: The first run of `architecture verify --source-scan` failed on
`verify_architecture.py` itself, because that file necessarily contains every
forbidden pattern it searches for.
Lesson: Exclude exactly one file — the scanner — and scan everything else,
including the rest of the tool tier. Broad exclusions to silence false positives
are how a verifier quietly stops verifying.
Date: 2026-08-17 · Owner: platform

### L-006 — Context windows must follow document structure, not character counts

Evidence: The downgrade-language check flagged a Part 0.9 table cell whose
governing sense ("It does **not** mean") sat in the table header four rows
above, outside a 600-character window.
Lesson: When judging whether surrounding text forbids a phrase, walk back to the
containing table header rather than widening a blind window — a bigger window
swallows unrelated prose and produces false negatives instead.
Date: 2026-08-17 · Owner: platform

### L-007 — A name-based path exclusion hid an entire source layer

Evidence: `data` was excluded by directory name at any depth, to skip the
top-level DuckDB folder. That also excluded `app/data/` — the whole history
engine — from the map manifest and from every architecture scan. A deliberately
injected `import win32com.client` in `app/data/history.py` was reported as PASS.
Evidence: `tests/unit/test_tooling_boundaries.py`.
Lesson: Anchor exclusions to root-relative prefixes, never to a bare directory
name, whenever the name could plausibly recur inside source. Then test the
boundary in BOTH directions — what must be excluded and what must never be. A
scanner that silently skips a layer is worse than no scanner, because its green
output is believed.
Date: 2026-08-17 · Owner: platform

### L-008 — The same unanchored-path bug existed in a second tool, and only CI found it

Evidence: after fixing L-007 in the scanner, `.gitignore` still carried an
unanchored `data/`, which matches at any depth. `git add -A` silently skipped
`app/data/` — seven files, the entire history engine. Every local check passed
because the files were present on disk; the first fresh checkout (CI) failed
immediately on `map verify`. Evidence:
`acceptance/evidence/ci-run-32099712082-failure.txt`.
Lesson: When a root-cause class is found in one tool, grep for it in EVERY tool
that does path matching — `.gitignore`, Docker ignore files, packaging manifests,
test discovery. Fixing one instance proves the class exists, not that it is gone.
Second lesson: local green does not mean committed. `map verify` now fails when
a mapped file is git-ignored, so the gap between "on disk" and "in the
repository" is checked where the work happens, not one push later.
Date: 2026-08-18 · Owner: platform
