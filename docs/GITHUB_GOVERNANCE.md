# GitHub governance

The canonical integration branch should be `main`.

Recommended GitHub settings:

- Default branch: `main`
- Require pull requests before merging to `main`
- Require review and conversation resolution for material Core changes
- Require Linux and Windows verification checks
- Block force-pushes and deletion of `main`
- Keep CODEOWNERS review for Universal Core

Repository files cannot themselves switch GitHub's default branch or enable branch protection. Do not claim those settings are active until GitHub Settings shows them active.

At the time this document was added, the repository default branch was still `claude/excel-automation-template-ewsbzf` even though `main` held the same commit. Change the GitHub default branch to `main` and apply the protection above.

Linux CI is not proof of Windows batch launchers, Unicode/space paths or packaging. Windows CI is separate evidence. Real protected Excel + desktop COM is stricter still and must run on the authorized corporate Windows PC.
