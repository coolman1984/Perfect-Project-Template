# CURRENT STATE

## Product identity

This repository is evolving from an Excel Automation Project Factory into a **Universal Excel Automation Engine + Adaptation Template**.

**The application already exists. New department projects adapt configuration and business logic; they do not rebuild the application.**

## Reusable foundation

- Golden Reference executes extract → stage → quality → clean → history → archive → SQL analytics → evidence insights → dashboard JSON against synthetic fixtures.
- History supports append/upsert/snapshot/replace-period and idempotent reruns.
- Approval provenance, business interview, map/context routing and machine verifiers remain.

## Universal-engine changes in this branch

- Shared analytics/presentation are configuration-driven through `dashboard.toml`; `app/pipeline.py` no longer contains Production Quality KPI/filter/chart vocabulary.
- Negative-value checks are explicitly configured per report rather than assumed for every numeric measure.
- `factory/source_profile.py` creates compact structural profiles and omits raw sample values by default.
- `factory/adaptation.py` records adaptation surface and guards unexplained Universal Core changes.
- `reports/line_downtime/` is a genuine second-domain executable proof with different columns, keys, calculations, charts and fixtures.
- Windows CI and GitHub-governance documentation are added. Real protected Excel/COM proof remains conditional on the authorized corporate PC.

## Still not claimed complete

- Real protected Excel COM proof on the corporate environment.
- Loopback API/server lifecycle and production renderer modules that still explicitly carry `NotImplementedError` contracts.
- Standalone HTML/ECharts verification and final offline executable packaging.
- GitHub server settings such as default-branch switch and branch protection must be enabled in GitHub Settings.

This branch must not be declared complete until its GitHub Actions checks are green. Environment-bound gates stay conditional even when CI is green.
