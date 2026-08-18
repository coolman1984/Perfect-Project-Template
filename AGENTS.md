# AI Agent Entry Point

This repository is a Universal Excel Automation Engine, not a blank software project. Your normal job is to adapt a proven application to new Excel files and business meaning with the smallest possible change surface.

## Mandatory startup

1. Read `PROJECT_SKILL.md`.
2. Read `UNIVERSAL_ENGINE_SKILL.md`.
3. Read `.ai/READ_FIRST.md`.
4. Run `PROJECT_TOOL doctor`.
5. Run `PROJECT_TOOL map context --task "<your exact task>" --budget 4000`.
6. Read `.ai/CURRENT_STATE.md` and generated `.ai/CONTEXT_PACK.md`.
7. Open only routed files, direct contracts and tests.

Do not broad-scan the repository. Do not broad-read Excel data into context.

## Five rules agents most often break

1. Adapt, do not rebuild. Configure and extend the engine before writing shared code.
2. Offline means bundle dependencies, not delete them.
3. No external server does not mean no local server. FastAPI/Uvicorn on `127.0.0.1` remains the boundary and needs no admin rights.
4. Production protected Excel extraction remains authorized desktop Excel COM/Value2. Fixture extraction is test-only and never a fallback.
5. Humans own business meaning. Agents may propose values; they may not invent approvals.

## Normal adaptation surface

Prefer `reports/<id>/`, its additive migration, fixtures/expected values and focused tests. Shared `app/`, `factory/`, `tools/`, contracts and architecture are Universal Core. A Core change requires a real reusable capability, explicit reason and regression evidence across both synthetic references.

## Before reporting done

Run focused tests, then:

```text
PROJECT_TOOL map verify
PROJECT_TOOL architecture verify --source-scan
PROJECT_TOOL constitution audit
PROJECT_TOOL gates status
python3 -m unittest discover -s tests -t .
```

On Windows also use `PROJECT_TOOL.bat`. Real protected Excel/COM proof remains conditional until exercised on the authorized corporate PC.
