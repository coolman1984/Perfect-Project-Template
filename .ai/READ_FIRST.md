# READ FIRST — Low-token operating rules

The project already contains the application. A new Excel automation is normally an adaptation, not a new architecture.

## Startup

1. `PROJECT_SKILL.md`
2. `UNIVERSAL_ENGINE_SKILL.md`
3. `PROJECT_TOOL doctor`
4. `PROJECT_TOOL map context --task "..." --budget 4000`
5. `.ai/CURRENT_STATE.md` + generated context pack
6. Only routed files plus direct tests/contracts

Do not inspect the whole repository “to understand it.” Repeatedly feeding the same codebase to agents is expensive theatre.

For a new Excel process use:

`business explanation -> compact source profile -> mapping -> configuration -> small report SQL -> focused tests -> full gates`

Never put a huge workbook into model context. Prefer column/type/null/distinct profiles and minimal approved samples.

Stop only for genuinely human-owned business facts such as row meaning, record identity, correction behavior, trusted totals, KPI meaning or storage approval. Do not ask the employee to choose database/API/framework/runtime design.

If a normal adaptation requires shared engine changes, prove why configuration or an extension point cannot express it. A genuine common capability gets one reusable implementation plus regression tests across both references.
