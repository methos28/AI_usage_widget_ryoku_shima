# Standalone AI usage collector: update and service ordering

Current widget architecture is documented in ai-usage-bundled-collectors.md.
The widget now invokes its bundled scripts and uses private caches. The
libexec/service-override arrangement below remains historical context and
still serves other shared-cache readers; it is no longer this widget's path.

Verified on 2026-11-09 while fixing stale Codex limits after the desktop changed
to the installed unstable Shima baseline. The exact earlier binary replacement
mechanism is unknown; do not assert that the updater copied it.

The project source is ~/Documents/opencode_widget_ryoku_shima. Its Codex
collector already contains the compatible CLI/RPC behavior. The live standalone
collector now lives at ~/.local/libexec/ai-usage/codex-usage, selected by
~/.config/systemd/user/ryoku-ai-usage.service.d/zz-ai-usage.conf. The existing
OpenCode collector remains ~/.local/bin/opencode-usage-v2.

Avoid ~/.local/bin/codex-usage for the standalone service: source deploys
replace that name with the tracked checkout's collector. On packaged installs,
Ryoku doctor's reconcile_dev_residue removes commands with packaged twins;
it explicitly skips source-checkout machines.
Also inspect every service drop-in. This machine has ryoku-dev-bin.conf, which
sorts after override.conf and resets ExecStart to ~/.local/bin/ryoku-ai-usage.
The later zz-ai-usage.conf selects the protected collector without changing the
dev file. The earlier override.conf and home-bin collector remain preserved;
they are not the effective service configuration now.

The corrected service was reloaded and run. Its effective ExecStart includes
the protected collector with exit status 0, and the timer is active. Real RPC
limits, reset countdowns, history and spending are restored. No QML/shared-bar
edit was needed. Installer, unit, regression and documentation changes remain
uncommitted; do not commit or push without fresh user instruction.

All 44 standalone and 46 fork tests passed, plus shell fixtures, cache contracts,
QML lint/compilation/bindings, delivery and WM isolation. Basic live switching
and the Trend menu worked; longer scripted click sequences closed the panel,
so input races remain inconclusive. The original Codex/Last 7 days selection
was restored through the daemon's settings writer and checked on screen.

Full report: ~/Documents/opencode_widget_ryoku_shima/TEST_REPORT_2026-11-09.md.
Backup: ~/.local/share/ryoku/ai-usage-backup/unstable-fix-20261109-022043/.
The official Ryoku checkout remains read-only; the user's review fork remains
clean on ai-usage. Do not put standalone home paths into packaged Ryoku code.

## Actual unstable delivery audit, 2026-11-09

The machine tracks the official ~/ryoku-arch checkout at 0749ec350, not the
user's review branch. Official unstable-dev lacks the bundled module and has
the collector that matched the faulty pre-fix backup. The user's fork unstable
at f26ede8ad contains the enhanced collector/widget but lacks the last discovery
fix. Only ai-usage at 9e4268ff2 has the complete built-in catalog/settings/loader
integration. The live GitHub API reports PR 757 closed without merging on
2026-11-08. Do not claim that the feature is already delivered by official
unstable updates just because the manual module is visible on this machine.

Added one staged package/source delivery regression on the user's review branch.
All 47 fork tests, 44 standalone tests, prior gates and focused Go channel,
service-manifest and doctor tests pass. The older fork unstable snapshot fails
the fresh-profile discovery negative control. The new test is uncommitted;
no branch or remote was changed. Full audit and 31-file placement inventory are
in the standalone project as DELIVERY_AUDIT_2026-11-09.md and
DELIVERY_INVENTORY_2026-11-09.tsv. Official delivery still needs the complete
feature integrated into the actual update branch and its testing gate passed.

## Regression publication, 2026-11-09 03:07 IST

The user authorised committing and pushing the pending fork test. It is now
published on methos28/ryoku:ai-usage as c2dbdc496bd2b123f50ad01476541acc7ee9f3e3;
the remote head is verified and the fork is clean. Nine shared tests and normal
hooks passed. This supersedes the earlier uncommitted-test status. The official
unstable branch still lacks the feature, and standalone installer changes remain
uncommitted in their own project.
