# Security posture

Constitution Parts 13.5, 22.10, 27.7, 43.

## The one thing to understand first

⚠️ **Extracted data is not DRM-protected.**

DuckDB files, Parquet archives, dashboard JSON, standalone HTML, exports, logs
and backups all contain the same data as the source Excel files — **without**
the company DRM wrapper. That is a real change in security posture, and it is
the single most likely reason for a working project to be switched off in
month 3.

Get written answers before go-live (Part 13.5):

| Question | Answer | Approved by | Date |
|---|---|---|---|
| Where may the warehouse and archive folders live? | `PENDING_APPROVAL` | | |
| Who may read them? | `PENDING_APPROVAL` | | |
| Does the dashboard output need restriction? | `PENDING_APPROVAL` | | |
| How long may extracted data be retained? | `PENDING_APPROVAL` | | |
| Is any external AI service permitted to see this data? | `PENDING_APPROVAL` | | |

## Local security boundary

The application binds **only** to IPv4 loopback `127.0.0.1`. This is a
single-user desktop boundary, not a shared deployment mode.

| Required | Forbidden |
|---|---|
| `asInvoker`, standard user | UAC elevation, `runas`, `requireAdministrator` |
| Bind `127.0.0.1` | `0.0.0.0`, `::`, hostname, LAN, public interface |
| OS-assigned or bounded high port | ports 80 / 443 |
| Per-launch secret on state-changing requests | reusable token, secret in a URL |
| Exact Host and Origin validation | wildcard CORS, credentials-to-wildcard |
| Per-run folders, allow-listed output paths | arbitrary path access |
| Process stops with the app | Windows Service, IIS, HTTP.sys reservation |

If corporate endpoint policy blocks the loopback socket, that is an
environmental compatibility issue to document with IT. It is **not** permission
to elevate, add a firewall rule, bind to the LAN, or delete the local API.

## Secret handling (Part 43)

| Secret | Storage | Lifetime | Never |
|---|---|---|---|
| Per-launch API secret | process memory only | one launch | disk, log, URL, browser history, manifest, crash dump |
| SQL Server credentials | Windows Integrated Authentication **by default** | per connection | `report.toml`, Git, the release ZIP |
| SQL credentials when integrated auth is impossible | DPAPI per-user store outside the app folder, written by an operator | until rotated | plaintext config, `.bat` environment variable, source |
| Backup destination credentials | OS credential store or pre-authenticated mount | per operation | `BACKUP.bat` |

Rules: a stored credential is a deviation needing IT approval · no secret is
ever a build input · `architecture verify --source-scan` fails on
credential-shaped strings · logs record the identity *class*
(`integrated` / `stored`), never the credential · rotation is a runbook step,
not a code change.

## Data handling

- **Logs** record counts, hashes and safe identifiers. Row values are redacted
  by default (Part 27.7).
- **Exports** escape formula-injection prefixes (`=`, `+`, `-`, `@`) per output
  policy.
- **Uploads** are sanitized: fixed intake root, extension and signature checks,
  no path traversal, no zero-byte or partial files.
- **Shared PCs** use a per-user restricted data folder with explicit cleanup.
- **Backups** inherit the same classification and access controls as the live
  database.
- **External AI** receives verified evidence objects only, and only when the
  data owner has approved the exact provider and disclosure scope (Part 20.11).
  Default is deterministic local insights; no data leaves the device.

## Reporting a concern

Record it in `docs/decisions/` with evidence and impact. A security limitation
discovered late is still worth recording — an undocumented one is not a
limitation, it is a surprise.
