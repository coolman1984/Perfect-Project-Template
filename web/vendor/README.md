# web/vendor — pinned local assets

Constitution Parts 23.6, 23.8.

This folder holds **locally bundled** third-party front-end assets. It is empty
in the template because assets are pinned and hash-recorded at build time.

## What belongs here

| Asset | Purpose | Version | SHA-256 | License |
|---|---|---|---|---|
| `echarts.min.js` | interactive charts | `PIN_AT_BUILD` | `POPULATE_FROM_RELEASE` | Apache-2.0 |

## Rules

1. **No CDN reference, ever.** Not in HTML, CSS, JS, or a generated report.
   `PROJECT_TOOL architecture verify --source-scan` fails on one.
2. **No remote font or icon.** Use the local system font stack and inline SVG.
3. Record every asset's version, SHA-256 and license in
   `IMPLEMENTATION_BASELINE.lock.json`, `sbom.spdx.json` and
   `THIRD_PARTY_NOTICES.md`.
4. Front-end assets are built **before** release. Node.js and package managers
   are never runtime requirements.
5. Never hand-edit a vendored file. Re-pin the upstream version instead, and
   record the upgrade per Part 23.7 — one layer at a time.
