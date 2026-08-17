# AGENTS.md — read this before touching anything

Universal entry pointer (Constitution Part 20.2). Every agent entry file —
`AGENTS.md`, `CLAUDE.md`, `.clinerules`, `.github/copilot-instructions.md` —
points at the same source of truth. **None of them forks the rules.**

## Do not scan this repository

Broad exploratory reading is forbidden while the map is fresh (Part 0.1). It
burns context and it is not how you find the right file here.

## Start in this exact order

```text
1. Read PROJECT_SKILL.md                       (the project contract + router)
2. Read .ai/READ_FIRST.md                      (commands and stop conditions)
3. Run  PROJECT_TOOL doctor                    (one command, all verifiers)
4. Run  PROJECT_TOOL map context --task "<your task>" --budget 4000
5. Read .ai/CURRENT_STATE.md and .ai/CONTEXT_PACK.md
6. Open only the files the router named, plus their direct dependencies
```

On Windows use `PROJECT_TOOL.bat`; on Linux/macOS use `./project_tool.sh`.
They are the same tool (Part 37.2).

If `doctor` fails, **stop feature work** and repair what it reports (Part 0.1
step 7). If it reports BLOCKED, something was *not verified* — never report
that as a pass (Part 37.4).

## The five rules that get broken most

1. **Offline means bundle the dependencies — never delete them.** "I made it
   simpler by using only Windows and Excel" is a release-blocking violation
   (Part 0.6).
2. **"No external server" does not mean "no local server."** The bundled
   FastAPI/Uvicorn API on `127.0.0.1` stays (Part 0.9).
3. **Never invent business meaning.** Grain, business key, formulas,
   thresholds and deletion rules belong to a named human. Write
   `PENDING_APPROVAL` and ask (Parts 3.1, 41).
4. **Excel is the authorized door to the data — not the calculation engine.**
   Trusted arithmetic lives in versioned SQL (Part 1.3, rule 6).
5. **Code, tests, contracts, state and map move together in one change set.**
   A material change with no map update fails the suite (Part 21.5).

## Before you say "done"

```text
PROJECT_TOOL map verify
PROJECT_TOOL architecture verify --source-scan
PROJECT_TOOL constitution audit
PROJECT_TOOL memory validate
PROJECT_TOOL gates status
```

Then update `.ai/CURRENT_STATE.md`, refresh the map, and record gate evidence
with `PROJECT_TOOL gates set`. A gate cannot pass on a sentence — it needs an
evidence file that exists (Part 38.2).

## Full law

`constitution/EXCEL_AUTOMATION_CONSTITUTION.md` — read once, in full, if you
are the first builder. Afterwards, route to it by Part number instead of
rereading it (Part 0.3).
