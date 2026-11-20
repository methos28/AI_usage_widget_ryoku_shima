# AI usage upstream synchronization, 2026-11-10

The explicit follow-up request to synchronize ai-usage superseded the earlier
conditional no-merge decision. Local and published methos28/ryoku:ai-usage now
point to 4df46ffca777856ad13c04bbdf5b9363b9fd1e67. This normal merge preserves
widget head b650d0c47 and includes official unstable-dev cd1a06478 (1.10.3).
Zero upstream commits are missing. All 44 feature paths are unchanged.
All 172 fork regressions, shell/cache checks and normal repository gates pass.
The branch is clean and its actual GitHub head is verified. No force push.

Local unstable-dev remains preserved at f26ede8ad; origin/unstable-dev is
cd1a06478 after its previously observed remote reset. No live widget, services,
credentials, package or boot configuration changes were needed.

Backup and validation logs: /tmp/ai-usage-sync-20261110/.
Detailed report: ~/Documents/opencode_widget_ryoku_shima/UPSTREAM_SYNC_2026-11-10.md.

## Superseded by clean rebuild request

The user plans to delete the old fork and clones. Do not reuse or restore this
branch automatically. Read ai-usage-rebuild-handoff.md and the independent
backup REBUILD.md; wait for the fresh checkout before branch recreation.
