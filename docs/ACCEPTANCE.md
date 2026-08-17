# Acceptance

Constitution Part 31, made queryable by Part 38.

## The ledger is the record

```bash
./project_tool.sh gates status                    # everything
./project_tool.sh gates status --severity block   # release blockers only
./project_tool.sh gates status --only conditional # what is waiting on an environment
```

`acceptance/gates.yaml` is authoritative. This document explains how to use it;
it does not duplicate its contents, because two copies of the truth drift.

## Recording a result

```bash
./project_tool.sh gates set \
  --id GATE_CONTROL_TOTAL \
  --status pass \
  --evidence acceptance/evidence/control-total-reconciliation.txt \
  --by "name or agent id"
```

The evidence path must exist on disk. A gate cannot pass on a sentence
(Part 38.2 rule 1).

## Status meanings

| Status | Means | Requires |
|---|---|---|
| `not_started` | No work yet | a `next_action` |
| `in_progress` | Being worked | a `next_action` |
| `pass` | Proven | an evidence file that exists, and a timestamp |
| `fail` | Tried and failed | a `next_action` |
| `conditional` | Could not be exercised in this environment | a reason **and** the exact later validation step |
| `not_applicable` | Genuinely out of scope | a reason (e.g. SQL Server disabled) |

`conditional` is the honest answer when a Windows- or Excel-bound gate cannot
run. It is not a soft pass, and it never becomes one by ageing (Part 31.4).

## Stable-run definition (Part 31.2)

Two consecutive production-like runs with **no** code, configuration, source
repair or manual database correction between them. All critical checks pass,
outputs open and reconcile, and rerunning identical input has no destructive
side effect.

## Release decision (Part 31.4)

Release only when:

- every `block` gate is `pass` or `not_applicable`;
- major limitations are fixed, or formally accepted with an owner and a date;
- warnings state their impact and next action;
- rollback and recovery are proven;
- the operator has witnessed or performed an end-to-end run.

## Completion declaration (Part 34.4)

Generate this **from the ledger**, never from memory:

```text
architecture baseline: PASS / BLOCKED
removed or replaced locked components: NONE / approved decision IDs
new external prerequisites: NONE / approved decision IDs
runtime downloads/CDNs: NONE
local loopback API: RETAINED / BLOCKED
runtime privilege: STANDARD USER + asInvoker / BLOCKED
service/firewall/URL reservation/machine-wide changes: NONE
clean offline proof: PASS / exact conditional evidence
map + constitution consistency: PASS
```

A statement such as "I made it simpler by using Windows and Excel only", "I
removed the local server to avoid administrator rights", or "I replaced it with
a direct Windows connection" is **itself evidence of non-compliance** and
requires architecture review before any output is accepted.
