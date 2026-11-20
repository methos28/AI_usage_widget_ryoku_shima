# AI Usage transition preview, user approval pending

Updated 2026-11-17 15:34 IST. The user requested live animation preview with a full backup, explicitly before any new local commit. This revokes earlier publication authorization for this preview. No commit or push has occurred. Primary HEAD is 72a6730; fork ai-usage-dashboard HEAD is 98058bcd8. Both indexes are empty.

The live user-owned widget now has AiUsageAnimatedValue.qml and five updated presentation components: eased quota fills (280 ms), token/API Value numbers (300 ms), and state fades (150 ms), scaled by existing Shima motion policy. First/context changes snap, hidden/reduced motion stops, temporary parse resets coalesce, quota row instances persist during updates, token text rounds to whole counts, and currency keeps two decimals. Backend/collector code is unchanged.

Both primary and actual fork-targeted runs pass all 227 cases with no skips, plus QML, binding, delivery/isolation and whitespace checks. The actual page is healthy and left open for the user to inspect real collector changes. The live 32-file widget matches primary. No fake live cache edits were used. Primary and fork mirror changes remain uncommitted; user visual approval is still required before committing.

Backup: /home/methos/.local/share/ryoku/ai-usage-backup/transitions-preview-20261117-151845. It contains the complete before-state widgets/tests, records, guide/changelog, shell settings and private cache reference snapshots, plus rollback notes and new test logs/screenshot. Restore widget code atomically if asked; do not rewind newer usage caches, ledgers or user settings. Check the primary latest PROJECT_LOG.md and PLAN.md for the user's verdict before taking a later action.

## Agent-switch flash repair, 2026-11-17 16:32 IST

The user then reported stale stats flashing under a newly selected agent. Confirmed the 100-percent bar came from OpenCode's hidden local-budget snapshot while Claude had no current quota. Repaired both presentation and read handoff: clear retained quota rows and transition validity on switching; mask all Island stats and the tile until loadedTool matches the selection; preserve layout with Loading usage; capture immutable stat text/tool/epoch snapshots; discard old generations and superseded versions. Normal data-update animations remain. Native frame tests cover all six directions, rapid round trips, missing caches and newer queued snapshots. Both suites now pass 233 cases with no skips, plus QML/integration checks. Live 32-file bundle matches primary and loads without module errors.

Second backup before this repair: /home/methos/.local/share/ryoku/ai-usage-backup/agent-switch-preview-20261117-161425. The original transitions-preview-20261117-151845 remains intact. Heads are still primary 72a6730/fork 98058bcd8, indexes empty, no commits/pushes. User is still testing the preview; do not publish without their approval.

## Slightly longer gentle motion, 2026-11-18 14:08 IST

The latest live preview defaults are 360-ms bars, 380-ms numbers and 180-ms fades, with gentle easing. Both 233-case runs and QML/integration pass. Hardware performance testing shows unchanged frame pacing and a small incremental animation cost; full report is primary PERFORMANCE_2026-11-18.md. New before-state backup: /home/methos/.local/share/ryoku/ai-usage-backup/motion-tuning-20261118-134810. This remains uncommitted/unpushed with the same heads and explicit user-review hold.

## User-approved publication, 2026-11-18 14:16 IST

The user explicitly approved committing to remote. The previous preview hold is released for this delivery. Primary 24b6db3fcecb5b17e1fc52424efba0d7bce6b428 saves the approved source/tests locally; feature 81c0f0e58 and normal sync merge f039733d746563dd4a291484fce603ba62cfa854 are pushed to the existing ai-usage-dashboard branch. Official latest unstable-dev is 3f4f6ee and already contains merged PR #881. GitHub verifies two ahead, zero behind and only eleven motion/switch preview files. The fork is clean and matches origin. The exact tested runtime survives the merge; 233-case results apply, and merged-source five switch/four motion cases plus QML/hooks pass. No new PR, review reply, other-branch push, primary-main remote push, package/channel/auth/data change or history rewrite. Live approved code and backups remain intact. Read latest PROJECT_LOG.md and PR_TRACKER.md; old pending-preview messages are superseded.
