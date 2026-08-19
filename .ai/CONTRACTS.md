# CONTRACTS

Public contracts and their versions (Constitution Part 20.2). **Read this only
when your change may affect a contract** — that is the whole point of routing.

Version independently (Part 25.7):

```text
application · report configuration · mapping · database schema
quality rules · metric registry · dashboard JSON · dashboard template
```

Raise a **major** version for incompatible field meaning or removal. Raise a
**report** version when grain, business key, load mode, metric meaning or
population changes. Cosmetic dashboard changes do not change metric versions.

---

## Machine-validated contracts

| Contract | File | Version | Consumers | Breaking change requires |
|---|---|---|---|---|
| Report configuration | `contracts/report_config.schema.json` | 1.0 | orchestrator, extractor, quality, history | report_version bump + migration |
| Dashboard package | `contracts/dashboard.schema.json` | 1.0 | JSON builder, HTML builder, `web/` | schema_version bump + renderer update |
| Run progress event | `contracts/run_event.schema.json` | 1.0 | events store, local API, `web/app.js` | sequence-compatible additive change only |
| Run manifest | `contracts/run_manifest.schema.json` | 1.0 | manifest writer, history UI, acceptance | additive fields preferred |
| Error codes | `contracts/error_codes.json` | 1.0 | every raising site, UI error screens, retry policy | new code = additive; changing a class is breaking |
| Run states | `contracts/run_states.json` | 1.0 | `app/state_machine.py`, events, UI stages | adding a state is a versioned change (Part 42.3) |
| Implementation baseline | `IMPLEMENTATION_BASELINE.lock.json` | 1 | architecture verifier, build, release | user-approved deviation only (Part 0.7) |
| Final operator package | `contracts/operator_package.json` | 1 | release builder, package verifier | explicit product decision + matching verifier/test update |
| AI master-template package | `contracts/master_template_package.json` | 1 | first commissioning, cloud adaptation, master verifier | explicit product decision + verifier/privacy tests |

The operator-package contract exposes exactly `START.bat`, `QUICK_START.html`
and `Application/` at the ZIP root. The sealed runtime remains inside
`Application/`; developer and build machinery are not part of the employee's
operating surface.

The master-template contract exposes the portable adapting source, canonical
agent instructions and `sealed_runtime/`. Its verifier binds immutable source
files to `MASTER_TEMPLATE_MANIFEST.json`, enforces the sealed baseline and
rejects production Excel/data files, developer caches and non-reference project
packs. Its mutable surface is limited to new lower-case project/test packs and
their evidence/context.

## Local API contract

Part 25.5. The typed boundary between renderer and application. Browser
JavaScript may not bypass it to reach Excel COM, DuckDB or the filesystem.

| Method and path | Purpose | Important rule |
|---|---|---|
| `GET /api/health` | runtime and database readiness | no sensitive data |
| `GET /api/reports` | configured reports and requirements | configuration-derived |
| `POST /api/uploads` | copy files into intake | local-only, validated, size-limited |
| `POST /api/runs` | start one run | idempotency key + report lock |
| `GET /api/runs/{id}` | current state | durable database state |
| `GET /api/runs/{id}/events` | progress since sequence | ordered, replayable |
| `POST /api/runs/{id}/answer` | answer a waiting question | validate expected question id |
| `POST /api/runs/{id}/cancel` | request safe cancellation | honour only at a safe boundary |
| `GET /api/dashboard` | latest approved dashboard JSON | never expose failed staging |
| `GET /api/history` | weekly approved history | paginated/limited |
| `GET /api/quality/{id}` | checks, exceptions, reconciliation | restricted if row-level data appears |
| `GET /outputs/{file}` | approved local output | path allow-list; no arbitrary files |

Transport invariants (Part 25.5.1): `asInvoker`; verified bound address
`127.0.0.1`; per-launch secret in memory only; exact Origin and Host validation;
no wildcard CORS; durable state survives a browser refresh; fail closed with a
stable code.

## Extraction port

Part 44.2. `ExtractionPort` is the contract; `com_adapter` is the only
production implementation; `fixture_adapter` is dev/test only and must never
appear in a release.

```text
open(source, config)      -> WorkbookIdentity
chunks()                  -> Iterator[Chunk]   rectangular Value2 blocks
lineage()                 -> the Part 7.7 fields for every staged row
close()                   -> restores every Excel setting, in a finally block
```

## Internal invariants that are not files

- `source_rows = accepted + rejected + intentionally_filtered` (Part 25.3)
- Control-total difference is exactly zero at the defined precision (Part 9.4)
- `business_key_hash` answers "same record?"; `row_content_hash` answers "did it
  change?" — neither replaces the human-readable key columns (Part 25.2)
