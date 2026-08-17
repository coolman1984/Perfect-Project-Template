# Third-party notices

Constitution Parts 23.6, 30.2.

Every distributed binary, wheel and front-end asset appears here with its
version, license and SHA-256. Licenses are verified before release, and the
scan runs against the **final release**, not only the source requirements
(Part 23.6).

| Component | Version | License | SHA-256 | Notice file |
|---|---|---|---|---|
| CPython | `PIN_AT_BUILD` | PSF-2.0 | `POPULATE_FROM_RELEASE` | `licenses/python.txt` |
| FastAPI | `PIN_AT_BUILD` | MIT | `POPULATE_FROM_RELEASE` | `licenses/fastapi.txt` |
| Uvicorn | `PIN_AT_BUILD` | BSD-3-Clause | `POPULATE_FROM_RELEASE` | `licenses/uvicorn.txt` |
| Pydantic | `PIN_AT_BUILD` | MIT | `POPULATE_FROM_RELEASE` | `licenses/pydantic.txt` |
| DuckDB | `PIN_AT_BUILD` | MIT | `POPULATE_FROM_RELEASE` | `licenses/duckdb.txt` |
| pywin32 | `PIN_AT_BUILD` | PSF-style | `POPULATE_FROM_RELEASE` | `licenses/pywin32.txt` |
| Apache ECharts | `PIN_AT_BUILD` | Apache-2.0 | `POPULATE_FROM_RELEASE` | `licenses/echarts.txt` |
| PyInstaller | `PIN_AT_BUILD` | GPL-2.0-with-exception | `POPULATE_FROM_RELEASE` | `licenses/pyinstaller.txt` |

Add a row for every transitive dependency and every bundled asset. A component
that is loaded at runtime but missing from this table is a release-blocking
omission.
