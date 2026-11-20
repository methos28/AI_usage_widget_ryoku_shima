# ai-usage upstream synchronization

Completed 2026-11-10 12:07 IST, following the user's explicit request to synchronize the
branch even though the incoming commits do not affect the widget. This
supersedes the earlier conditional no-merge decision in UPSTREAM_CHECK_2026-11-10.md.

The local and published methos28/ryoku:ai-usage heads are
4df46ffca777856ad13c04bbdf5b9363b9fd1e67. The merge preserves the prior feature
head b650d0c474553931ef551332051e46fe3d651d62 and incorporates official
unstable-dev cd1a06478d5b7c8f952180c89c1f42576fad41da. No history was rewritten.
There are zero upstream unstable-dev commits missing from ai-usage.

The three incoming commits update bug-report fields, remove retired project
workflows and their advisory CI entries, and bump VERSION to 1.10.3. All five
incoming paths match the upstream tree. All 44 feature paths remain unchanged.
The resulting commit tree matches the preflight merge-tree simulation exactly.

All 172 fork regression cases pass on the merged tree, along with Codex shell
fixtures, isolated cache contract, CI-gate shell syntax, delivery, WM isolation,
staged whitespace and normal hooks. GitHub's actual remote branch head was
verified after a normal non-force push. The fork worktree/index are clean.
These are local validation results; no new remote CI result is claimed.

No widget implementation files changed, so the existing live widget remains
valid and needed no redeployment or shell reload. No package upgrade, boot
configuration, standalone implementation, service, credential or upstream
branch changed. Local unstable-dev remains f26ede8ad; the fork's remote
unstable-dev remains cd1a06478.

Backup Git bundle, exact pre-merge manifest and full validation logs:
/tmp/ai-usage-sync-20261110/.

Commit: https://github.com/methos28/ryoku/commit/4df46ffca777856ad13c04bbdf5b9363b9fd1e67
