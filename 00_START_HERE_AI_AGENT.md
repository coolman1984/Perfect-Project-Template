# Start here — autonomous Excel project delivery

This file is the canonical first instruction for every capable coding agent,
including Codex CLI, ChatGPT Work, Claude Code, Gemini CLI and cloud agents
that can inspect files, edit them, execute tests and create ZIP archives.

The user should not need to explain the technical workflow. A request such as
"complete the project" means: detect the mode below, ask only unavoidable
business questions, execute the complete workflow, and return the required
verified ZIP files.

## Product promise

```text
MASTER_TEMPLATE.zip + Excel files + plain business explanation
→ understand and confirm business meaning
→ reuse the sealed engine
→ configure first
→ add project SQL, then isolated project Python only when required
→ test, reconcile and verify
→ ProjectName.zip
→ extract → double-click START.bat → browser opens → work offline
```

The final operator never installs or operates Python, packages, Git, a
terminal, databases, ports, migrations, agents or build tools.

## Detect the mode before doing work

### Mode A — first Windows commissioning

Use this mode when all are true:

- the repository source tree is present;
- `TEMPLATE_BASELINE.json` is unsealed;
- the machine is Windows x64 with desktop Excel and Python 3.12;
- the machine may use the internet during this one build.

Goal: finish and prove the reusable master, adapt the first real project, then
produce **both**:

```text
release/operator/MASTER_TEMPLATE.zip
release/operator/ProjectName.zip
```

The master archive is for future AI adaptation. The project archive is for the
non-technical offline operator.

Workflow:

1. Run `PROJECT_TOOL.bat doctor` and read the routed state.
2. Discover supplied workbooks in `inbox/` or from the conversation
   attachments. Hash and preserve them; never place production workbooks in a
   delivery archive.
3. Ask only missing business questions: project name, source roles, row grain,
   business keys, correction/deletion meaning, source precedence, trusted
   control totals, required KPIs/decisions and named approver.
4. Create/adapt `projects/<project_id>/`. Reuse capabilities before adding
   project SQL; use isolated project Python only when SQL is unsuitable. Do not
   rebuild settled core features.
5. Prove the project with synthetic or approved fixtures, reconciliations,
   failure cases, idempotent rerun and two stable production-like runs when the
   required inputs are available.
6. Resolve code defects. Keep unknown business meaning as `PENDING_APPROVAL`;
   an agent may never approve its own interpretation.
7. Run `FINALIZE_MASTER.bat <template_version> <project_id> "<Project Name>"`.
8. Do not report success until that command produces and verifies both ZIPs.
9. State any environment-bound acceptance still required on the separate clean
   offline employee PC. A conditional gate is never a pass.

### Mode B — cloud or copied-master adaptation

Use this mode when `sealed_runtime/` exists and `TEMPLATE_BASELINE.json` is
sealed. This is the normal mode for an uploaded `MASTER_TEMPLATE.zip` in
ChatGPT Work, Claude, Gemini or another capable cloud coding environment.

Goal: produce only:

```text
dist/ProjectName.zip
```

Workflow:

1. Verify the master archive and sealed core:

   ```text
   PROJECT_TOOL master-template verify-folder --root .
   PROJECT_TOOL template-baseline verify
   ```

2. Discover the attached Excel files without broad-reading confidential cell
   data into model context. Profile structure and ask only the missing business
   questions listed in Mode A.
3. Create/adapt only `projects/<project_id>/`, fixtures, expected results and
   project-owned evidence. Never rebuild or modify the sealed runtime or core.
4. Run project validation, reuse/core guard, focused tests, reconciliations,
   source-immutability checks, identical-input rerun and all portable gates.
5. Build the final operator archive:

   ```text
   PROJECT_TOOL delivery build --project <project_id> --project-name "<Project Name>" --master-root . --output-dir dist
   PROJECT_TOOL package verify --zip "dist/<Project Name>.zip"
   ```

6. Return the verified `ProjectName.zip`, a concise result summary and any
   genuine target-PC acceptance still required. Never return source or the
   master archive to the non-technical operator.

## Capability gate for browser-only AI chats

The workflow requires file extraction, file creation, code execution, tests and
ZIP creation. If the current chat cannot do any of these, do not pretend to
finish. State that the task requires the provider's coding/work environment,
then preserve the supplied files unchanged. Never replace the application with
a mockup or a static dashboard merely because execution tools are unavailable.

## Non-negotiable delivery rules

- Final operator ZIP root: `START.bat`, `QUICK_START.html`, `Application/`.
- The complete private Windows runtime and offline dependencies remain inside
  `Application/`; Git is not shipped to the operator.
- No runtime downloads, admin rights, service, firewall change, LAN bind, CDN,
  telemetry or external server.
- Windows and authorized desktop Excel are the only approved external runtime
  prerequisites.
- Trusted calculations are deterministic and defined once. AI explains
  verified evidence; it never creates or approves trusted KPI values.
- A failed run preserves trusted history and the last approved dashboard.
- Production data and credentials are excluded from both delivery archives.
- No release claim until critical gates pass, warnings are disclosed, and the
  exact archives pass their machine verifiers.

## Required completion statement

Report only:

```text
mode: FIRST_WINDOWS_COMMISSIONING / CLOUD_ADAPTATION
project: <id and name>
master template: <path + PASS / not applicable>
operator package: <path + PASS>
tests and reconciliations: <passed counts/evidence>
core changed: NONE / justified master-core list
business approvals: <confirmed/pending>
target-PC acceptance: PASS / exact remaining action
```
