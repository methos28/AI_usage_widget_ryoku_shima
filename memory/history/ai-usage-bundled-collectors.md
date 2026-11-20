# AI Usage uses bundled collectors

Current architecture, implemented and verified live on 2026-11-09. This
supersedes using a protected libexec collector and service override for the
widget itself. Earlier global helper/service customizations are still present
for other shell panels and were not removed.

The primary source is ~/Documents/opencode_widget_ryoku_shima/ai-usage. The
user's review port is ~/Projects/ryoku-unstable on ai-usage. Both scripts and
their collect-usage launcher are canonical files in widget/bin. Earlier source
collector paths are relative symlinks; package/source installs dereference
them into regular global executables for other widgets.

UsageModel resolves bin/collect-usage from its own QML URL. The widget writes
and reads ~/.cache/ai-usage, independently of older shared system caches. It
does not require ryoku-rashin or a service drop-in. The standalone installer
now copies only the complete widget and reloads the shell.

The existing monthly spending ledger and historical price snapshots are
preserved. The launcher takes the legacy Codex lock before the private cache
lock to serialize ledger updates, returns a retry status when busy, and the
model retries. Initial collection and complete availability batches preserve a
saved agent while private caches are being created.

All 48 primary and 50 fork tests pass, including actual Qt cold-start/retry,
both native stores, paths with spaces, older command/cache isolation, source
and package delivery, existing collector fixtures and QML/delivery gates. A
negative control detects premature agent fallback when its readiness guard is
removed. Token/quota/pricing collector bodies remain unchanged from HEAD.

The live user-owned widget now matches the primary source and collects both
agents through its own bin directory. Native rpc/Plus and storage+v2 caches,
history and spending were inspected. Both caches are 0600; Codex/Last 7 days
settings and global helper/service hashes are unchanged. No relevant runtime
errors appeared in the inspected log tail.

Changes remain uncommitted; the published fork head is still c2dbdc496. Do not
commit, push, change upstream, or remove the legacy service configuration without
a new user request. Full record: BUNDLED_COLLECTORS_2026-11-09.md in the primary
project. Backup: ~/.local/share/ryoku/ai-usage-backup/bundled-collectors-20261109-034353/.
