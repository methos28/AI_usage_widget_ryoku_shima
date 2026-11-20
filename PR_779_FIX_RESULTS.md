Latest publication: 2026-11-10 17:04 IST. Fix commit 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1
is pushed to ai-usage-dashboard and verified as PR #779's current head. Normal
hooks pass; fork tree is clean and synchronized. Earlier local-only status below
records the pre-publication verification snapshot.

# PR #779 local fix results

Completed 2026-11-10 16:59 IST. All changes remain uncommitted and unpushed.

Primary: /home/methos/Documents/opencode_widget_ryoku_shima
Fork: /home/methos/ryoku-arch, branch ai-usage-dashboard
Published PR head remains 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667.

## Implemented

1. Claude usage and lifecycle consume the same transcript pass. Standalone
   session detection still works independently. Counts, native PID checks,
   titles, copied records and lifecycle ordering are preserved.
2. OpenCode lifetime residuals are reconciled only when session creation is
   known to fall within the loaded history horizon. Old and undated sessions
   do not add their lifetime residual to a recent message. Legitimate
   within-horizon residuals remain counted. No broad history/ledger reset occurs.
3. Missing-cache UI retries stop while hidden. Opening reloads the cache and
   requests collection; the 15-second background worker remains independent.
4. Visible dashboard copy uses shared translations and complete format keys.
   Period IDs remain stable. New translations use the normal catalog workflow;
   keys without a translation retain English.
5. All widget em dashes were removed. Unavailable values use ASCII `-`.
6. Hidden/idle pulse animation pauses without resetting its phase.
7. Non-Island custom entries are rejected before module-ID deduplication, while
   a valid custom Island module retains precedence.

The DST suggestion is intentionally unchanged; the function's AST matches the
pre-fix backup and the reported repeated-hour failure did not reproduce.

## Documentation and scope

Added docs/ai-usage.md to primary source and mirrored it to the fork. It covers
enabling and using the module, data sources, refresh lifecycle, local/account
semantics, API Value, storage and source locations. docs/structure.md links the
guide and maps the widget source. Root CHANGELOG.md remains byte-identical to
the task-start backup and retains the existing Added-only feature entry.

Tests and test adapters remain in primary/external validation locations. No
Rashin, package, CI, hook, upstream AGENTS.md or unrelated change was introduced.

## Verification

- 181 primary tests and 181 external fork cases pass.
- Shell fixtures, cache contracts and old/new output comparison pass.
- QML load lint and explicit duplicate-binding checks for 22 files pass.
- Delivery, WM isolation, source/fork parity, doc links and whitespace pass.
- Pulse phase and background timing are tested with the real Qt runtime.
- A regression counts exactly one integrated Claude transcript read.
- Accounting tests retain valid residuals and reject old/unknown-age residuals.
- A registry regression verifies both built-in fallback and custom precedence.

External adapters preserve the fork's CLI identity and omit the standalone-only
installer test from that fork fixture. The old deduplication test expectation
was updated because it asserted the behavior being fixed. No review-fix test
was disabled.

Synthetic comparison: 25,000 records, 11350280 bytes. A single run
measured 1.444s before and 1.370s after.
Tokens, hourly/daily history, periods, sessions, spending and diagnostics match.
This is not a general speedup guarantee; the structural result is one transcript
read/parse pass instead of two, without introducing an incremental index.

## Live delivery

Atomically installed 14 tested widget files and reloaded with ryoku-shell.
Opened the Desktop page, then closed it. All three caches updated repeatedly
during a 36-second closed-page observation, beyond Shima's unload deadline.
They remain valid JSON objects with mode 0600. No widget/type/reference errors
were found in the current shell logs. The shared registry fix is source-only;
no package-owned shell file was overwritten. No auth change, new paid prompt
or package upgrade occurred.

Observation: [{"elapsed": 0.0, "changed": ["opencode-usage", "codex-usage", "claude-usage"]}, {"elapsed": 7.0, "changed": ["opencode-usage"]}, {"elapsed": 9.0, "changed": ["codex-usage", "claude-usage"]}, {"elapsed": 22.0, "changed": ["opencode-usage"]}, {"elapsed": 23.0, "changed": ["codex-usage"]}, {"elapsed": 24.0, "changed": ["claude-usage"]}]

Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-fixes-20261110-163431/
Primary log: /tmp/ai-usage-pr779-primary-tests.log
Fork logs, benchmark and live observation: /tmp/ai-usage-pr779-validation/
