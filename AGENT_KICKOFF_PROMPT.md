# Agent kickoff prompt

This file is retained for human reference. Agents must begin with
`00_START_HERE_AI_AGENT.md`; the user no longer needs to copy a technical
prompt. A request such as **"complete the project"** is sufficient after the
repository or `MASTER_TEMPLATE.zip`, Excel files and business explanation are
available.

---

## 1. Adapt the template in ChatGPT Work (the main path)

> Copy everything between the lines.

---

Read `00_START_HERE_AI_AGENT.md` and execute the complete detected mode. Use
this repository as your project template and its constitution as your law.

The user supplies the template ZIP, Excel files and a plain business
explanation. Deliver a tested `ProjectName.zip` whose final-user journey is:
extract → double-click `START.bat` → browser opens → work. Reuse existing
capabilities first, then configuration, then project SQL, then isolated project
Python only if required. Never rebuild an existing engine feature without
evidence of a reusable gap.

**Do not scan the repository.** Start exactly here:

```text
1. Read 00_START_HERE_AI_AGENT.md
2. Read AGENTS.md
3. Read PROJECT_SKILL.md
4. Read .ai/READ_FIRST.md
5. Run  ./project_tool.sh doctor        (Windows: PROJECT_TOOL.bat doctor)
6. Run  ./project_tool.sh map context --task "<the task I gave you>" --budget 4000
7. Read .ai/CURRENT_STATE.md and .ai/CONTEXT_PACK.md
8. Open only the files the task router names
```

Then read `constitution/EXCEL_AUTOMATION_CONSTITUTION.md` **once, in full** —
you are the first builder, so that is required. Afterwards, route to it by Part
number instead of rereading it.

Your job is to **build the product**, not to produce another plan. Work through
the phases in order (Part 39 → Part 14), passing each gate before continuing.
Do not stop merely because a phase finished.

Ask me only for the three Phase −2 questions (project slug, first report id,
report title) and the Part 3.1 business decisions that would change meaning,
security or acceptance. Write `PENDING_APPROVAL` for anything a human must
decide, and never resolve one yourself.

The architecture is already approved and locked. Do not redesign it, do not ask
me to reconfirm it, and do not describe a downgrade as "simpler", "more
portable" or "native". If a locked component is genuinely incompatible, submit
the Part 0.7 deviation request and wait for my explicit approval.

If real protected Excel files or a Windows machine are unavailable, build the
**complete** product against the labelled fixtures, mark only the affected
environmental gates `conditional` in `acceptance/gates.yaml` with an exact next
action, and keep going. A missing environment limits production approval; it
must never reduce the deliverable to a mockup.

Report progress as real passed gates, not narration. When you finish a slice,
run every verifier, record gate evidence, refresh the map, update
`.ai/CURRENT_STATE.md`, and give me the Part 34.4 completion declaration
generated from the ledger.

For first connected-Windows commissioning, build and verify both archives with:

```text
FINALIZE_MASTER.bat <template-version> <project-id> "<Project Name>"
```

For an uploaded sealed master, follow Mode B in the canonical guide and use
`PROJECT_TOOL delivery build`.

---

## 2. Continue an existing project

---

Use this repository's `PROJECT_SKILL.md` as your entry point. Do not scan the
repository.

```text
./project_tool.sh doctor
./project_tool.sh map context --task "<my task>" --budget 4000
```

Read `.ai/CURRENT_STATE.md` and `.ai/CONTEXT_PACK.md`, then open only the files
the task router names plus their direct dependencies. Make the **smallest**
change that fully preserves every contract.

Before you tell me it is done:

```text
./project_tool.sh map verify
./project_tool.sh architecture verify --source-scan
./project_tool.sh constitution audit
./project_tool.sh memory validate
./project_tool.sh gates status
```

Update code, tests, contracts, state and map together in one change set. Record
gate evidence with `gates set` — a gate cannot pass on a sentence.

---

## 3. Audit only, change nothing

---

Audit this project. **Do not modify anything.**

Verify the map and the architecture baseline, then inspect only the routed files
and existing evidence. Report findings ranked by: correctness → data loss →
security → recovery → operability → performance → usability.

Separate **confirmed findings** from **risks** from **unknowns**. For each, give
the exact affected file, the evidence, the impact, and the recommended next
action. Do not guess, and do not present an assumption as a fact.

---

## 4. Add the next week of data (an operating run, not a code change)

---

Treat this as an operating run, not a code change.

Verify source roles, file stability, period, hashes, schema, quality and
completeness. Use the configured history mode. Do not duplicate prior data and
do not overwrite a complete period with partial data. Publish only after
reconciliation and dashboard verification pass. Preserve the full run evidence.

If a run fails, leave the last approved dashboard in place and tell me what
failed in plain language.

---

## What a good agent does in the first ten minutes

Use this to judge whether the agent understood the assignment:

| ✅ Good sign | ❌ Warning sign |
|---|---|
| Runs `doctor` before touching anything | Starts reading files at random |
| Asks the three Phase −2 questions, then stops asking | Asks you to specify the architecture |
| Writes `PENDING_APPROVAL` for the business key | Invents a plausible business key |
| Says a gate is `conditional` and names the next action | Says "done" with no evidence file |
| Reads the Part it cites | Cites Part numbers it has not opened |
| Bundles a dependency it needs | Removes a dependency to "simplify" |
| Keeps the loopback API | Proposes a "direct Windows connection" |
| Reports `BLOCKED` when it could not verify | Reports a pass it did not earn |
