# BUILD BRIEF — line_downtime

## Mission

The application already exists. Teach the Universal Excel Automation Engine what this Excel process means. Do not build another application.

Normal order: `PROFILE -> MAP -> CONFIGURE -> SMALL BUSINESS LOGIC -> TEST`.

## Approved business decisions

- business_key: `['event_date', 'line', 'event_id']` — Sara Ahmed <sara.ahmed@example.com>
- deletion_rule: `ignore` — Sara Ahmed <sara.ahmed@example.com>
- load_mode: `upsert` — Sara Ahmed <sara.ahmed@example.com>

## Pending human meaning

- control_total_column: NEEDS_YOUR_APPROVAL — The value changed after approval. Approved 'Total downtime minutes', now 'downtime_minutes'.
- lookback_days: NEEDS_YOUR_APPROVAL — Proposed value is set but nobody has approved it: 7
- storage_allowed: NEEDS_YOUR_APPROVAL — The value changed after approval. Approved ['D:/secure/downtime'], now ['tests/expected/downtime'].

## Reuse first

- Capability-level reuse indicator: **67%** (directional, not exact code math)
- Start with `reports/_REFERENCE/` for full-pipeline patterns. Copy its pattern; configure and extend it. **Do not redesign it.**
- Use `reports/line_downtime/` as proof that a different business shape uses the same core.

## Variation points — files you normally change

| Variation point | What belongs there |
|---|---|
| `reports/<id>/report.toml` | source/history/quality contract |
| `reports/<id>/pipeline.toml` | columns/tables/SQL wiring |
| `reports/<id>/dashboard.toml` | KPIs, filters, charts and insight patterns |
| `reports/<id>/sql/clean.sql` | typing/normalization/reject rules |
| `reports/<id>/sql/checks.sql` | control-total queries |
| `reports/<id>/sql/metrics.sql` | trusted KPI calculations |
| `reports/<id>/sql/insights.sql` | evidence queries |
| `migrations/NNNN_*.sql` | business table shape |

### Universal Core (legacy name: Factory Core) — normally unchanged

| Shared area | Why |
|---|---|
| `app/pipeline.py` | Universal run order |
| `app/excel/` | authorized extraction |
| `app/data/` | staging/history/archive |
| `app/quality/` | quality/reconciliation |
| `app/analytics/configured.py` | configured SQL analytics |
| `app/dashboard/json_builder.py` | configured dashboard package |
| `factory/source_profile.py` | compact profiling |
| `factory/adaptation.py` | reuse/core guard |

Do not redesign it for a normal report. If Core must change, explain why configuration is insufficient and keep both references green.

## Required verification

```text
python3 -m unittest discover -s tests -t .
PROJECT_TOOL report validate --mode production
PROJECT_TOOL map verify
PROJECT_TOOL architecture verify --source-scan
PROJECT_TOOL gates status
```

At minimum preserve `GATE_CONTROL_TOTAL`, `GATE_HISTORY_IDEMPOTENT`, `GATE_INSIGHT_EVIDENCE`, and `GATE_DASHBOARD_CONTRACT`. A real protected Excel/COM proof remains conditional until it runs on the authorized Windows PC.
