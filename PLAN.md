# AI usage widget — plan

Current standalone publication (2026-11-08): the user authorised publishing
the latest module, collectors, tests and updated README/changelog to
`methos28/AI_usage_widget_ryoku_shima:main`. All 44 standalone tests, cache
contract and QML gates pass. The Codex collector matches the reviewed Ryoku
fork, while standalone collector lookup and manual installation are retained.
Local PR drafts and audit reports are outside this publication.
Published application revision: `1f4f3d4628c28431eb9ed8af41419bb7c14b62b3`.
Normal commit/push succeeded, GitHub's remote head and README blob were
verified, and the repository is public. The publication record is included
in the following documentation commit.

History: module main was previously pushed through 47b9395. The user recreated
`methos28/ryoku` on 2026-11-07; the module was re-landed directly on its
`unstable-dev` as one commit, `f0c5a4f0f`, with no feature branch. The local
checkout at `/home/methos/Projects/ryoku-unstable` is a clean clone of that
fork. Only OpenCode and Codex appear in the agent menus. Module, QML and
delivery checks pass. The recreated fork has no registered Actions workflows
or runs; the earlier four publishing failures belonged to the deleted fork.
The Phase 7 optimisation
and caption fix are committed on the fork as `31d36bef9` and `f9b7a7dc1` and
pushed. The user will open the new pull request. Owner decisions override this
plan; record any change in `PROJECT_LOG.md`.

## Current work — module fixes and official-tree compatibility audit

The user requested a dedicated PR branch on 2026-11-07. `ai-usage` is created,
pushed and checked out in the fork, tracking `origin/ai-usage` at `9e4268ff2`.
It retains all four original module commits, the root changelog entry and the
built-in discovery fix requested by the user. Use `ai-usage` for review fixes.
The user opened https://github.com/Ryoku-dev/ryoku/pull/757, then changed its
base to `unstable-dev` and marked it ready for review. GitHub reports the
current head `9e4268ff2` as mergeable. The agent has not edited the PR or its
review stage. Functional workflows currently require maintainer approval;
the green checks are notification/triage jobs, not functional CI success.

Stable/unstable re-audit on 2026-11-08 confirms the branch contains the latest
upstream unstable base `0749ec350` with zero commits behind and six feature
commits ahead. Nine checked direct Shima components are identical between
installed stable `f7197d72d` and unstable. The PR preserves unstable's extra
settings entry. All 46 target-source tests and source gates pass again.
Full graphical/runtime testing on an unstable installation remains unverified.

- [x] Fetch the official main and unstable-dev references and audit every changed shared file.
- [x] Fix the menu import, desktop model bindings and quota display, and standalone agent fallback.
- [x] Preserve the original installExample API and make shipped installs preserve existing user content.
- [x] Add calendar/unit/fallback/component and shared-loader/cache-reader regressions.
- [x] Pass module/fork checks, QML compilation/lint/bindings, delivery and WM isolation.
- [x] Deploy the tested module, reload successfully and inspect the live Codex layout.
- [x] Audit credential handling, harden RPC/cache writes, and verify a live authenticated quota refresh.
- [x] User accepted the live preview and authorised remote delivery.
- [ ] Complete the remaining live menu/click-input checks when requested.

The user authorised a commit and push to methos28/ryoku:unstable-dev on
2026-11-07. The complete local preview and compatibility fixes are delivered
as `f26ede8ad40a73852a6094bc57d784f9e1443731`. Normal commit/push hooks and
local gates passed; GitHub confirms that remote head and the fork is clean.
The initial fork delivery had no CI runs; the submitted upstream PR now has
functional workflows awaiting maintainer approval. The live widget matches the primary
source. The shared Ryoku paths and compatibility checks are documented in
`RYOKU_COMPATIBILITY_REPORT.md`; installed shared loader/panel/cache-reader and
visual primitives still match official stable. That delivery concerned the
Ryoku fork; standalone publication is now separately authorised as above.
Upstream Ryoku remains read-only.

Bundled AI Usage now appears directly in Shima Settings / Island / Desktop
page / Your modules after the updated payload is delivered. No separate
widget-manager or Add-ons install is required. Users still select whether to
enable it. Installed custom copies take precedence; existing selections and
the normal desktop-widget registry are preserved. All 46 fork tests and
QML/delivery gates pass, including fresh-profile and real-QML runtime checks.

Codex daily spending estimates are now implemented in the primary repository
and deployed live for preview. The existing collector stores private monthly
ledgers with daily price snapshots, retains deduplicated events, and publishes
`_spending` in the usage cache. The Codex-only title is `Est. Spending`.
This compares token usage with Standard API rates; it is not Plus charges,
prepaid balance or top-ups. Earlier days without a saved price snapshot remain
unpriced, with a partial-month marker. OpenCode still displays its recorded
local costs. The fork carries this change at `f26ede8ad`.

The user dropped the historical billing-import proposal on 2026-11-07.
Keep the existing local daily estimates and `Est. Spending` label; billing
history imports and balance lookups are outside the current scope.

Quota compatibility: browser and device-code ChatGPT logins use the same plan
quota RPC. API keys and Bedrock do not supply these ChatGPT quota windows;
confirmed account types suppress historical ChatGPT fallback. Platform API
request/token limits are not collected. Other credential modes require local
availability to the collector and have not been verified with real credentials.

## Live preview — daily estimated API cost (2026-11-07)

- [x] Extend the existing collector; add no separate collection script or credential.
- [x] Store daily prices/events/subtotals in a private persistent monthly JSON ledger.
- [x] Cover deduplication, rollover, late events, offline rates, unknown prices and corrupt state.
- [x] Keep Codex's label and amount on the existing compact rows; preserve other-agent labels.
- [x] Pass 43 primary tests, contract, QML and delivery gates, plus existing fork compatibility tests.
- [x] Deploy, refresh live, reload and inspect the card after the user unlocked the desktop.
- [x] User accepted the live preview and requested a downstream commit and push.
- [x] Pass fork gates, commit with normal hooks, push and verify the remote head.

RPC security checkpoint: the collector now explicitly uses stdio, cleans up
children on every failure path, bounds response reads/timeouts, redacts provider
error bodies and publishes 0600 caches. Seven new regression tests pass. The
live cache was verified as rpc/Plus after an approved normal refresh outside
the read-only execution sandbox. No billing credential or auth configuration
was added. The fork changes are committed and pushed in `f26ede8ad`; the
standalone changes are included in the separately authorised publication.

## Current work — Codex correctness (requested 2026-11-07)

- [x] Verify official quota-window field definitions and plan documentation.
- [x] Fix moved, truncated/replayed and copied rollout double counting.
- [x] Render reported quota windows and reset times, including a reported 30d window.
- [x] Prevent historical paid windows from appearing after a plan change.
- [x] Add 15 regression tests and run all delivery gates.
- [x] Install the tested primary collector and widget files to the named live paths.
- [x] Confirm a successful live reload and compact Codex layout (19:17 IST).
- [x] Observe the next real collector refresh migrating activity state to schema 4.
- [ ] Confirm the resulting live layout; existing visual sign-off remains pending.

The primary Codex collector now lives at `collector/codex-usage`. The live
collector matches it. The downstream Ryoku collector now includes the accepted
fixes on the recreated fork's local unstable-dev. The old ai-usage-builtin
reference exists only in the backup mirror. Free-plan 30d windows
were observed in this account's rollouts, but official documentation does not
establish a universal Free reset schedule. Window length and reset time follow
the account response rather than a plan-name rule.

## Phase 1 — Stabilise the live widget

- [x] Trend periods use fixed calendar slots ending today.
- [x] All-time is a fixed 45-day window, zero-filled.
- [x] Bar widths scale with the Shima page width; 7-day fills the card.
- [x] Heatmap covers 63 days ending today in a full 9 × 7 grid; zero days are dim
      (replaces the earlier 60-day cap, per the user's screenshot feedback).
- [x] Codex `_hours` uses local clock hours in milliseconds; widget normalises old
      second-based caches.
- [x] Codex Spending always renders, `$0.00` when the cache has no costs.
- [x] Compact the Now/Sessions row back to the Claude reference height.
- [x] Period label is a real target in both collapsed and expanded states.
- [x] Refresh lock clears when the collector exits.
- [ ] User visual sign-off on the live dashboard.
- [x] Inspect the compact primary-row height and stacked caption after live reload.

## Phase 2 — Tests and records

- [x] Fixture: 7/30/45-day trend slot counts with a 2-day cache.
- [x] Fixture: heatmap exactly 63 dated cells in nine full columns, zero days dim, no future dates.
- [x] Fixture: hours keys in seconds and milliseconds both normalise.
- [x] Fixture: Codex estimate amount and unavailable states; compact live row inspected.
- [ ] Fixture: period label click target reaches both states.
- [x] Update `PROJECT_LOG.md` with the completed checks and their limits.

## Phase 3 — Commit approval

- [x] Prepare Claude hold-out: only OpenCode/Codex in the primary dropdown and settings.
- [x] User says "push to local"; commit the widget changes with one logical
      commit per concern.
- [x] User says "push to remote"; push `main` only after the local commit is
      approved.
- [ ] Never force-push.

## Phase 4 — Ryoku branch

- [x] Port the accepted widget fixes to
      `/home/methos/Projects/ryoku-unstable`; the recreated fork's `unstable-dev`
      is committed through `f9b7a7dc1`, with the compatibility fixes uncommitted.
- [x] Keep the branch's Claude hold-out and its newer collector work intact.
- [x] Run its gates: QML lint, binding gate, `tests/opencode-usage.sh`,
      `tests/codex-usage.sh`, `tests/ai-usage-cache.py`.
- [x] Record the port in `PROJECT_LOG.md` and `RYOKU_TEST_REPORT.md`.

## Phase 5 — Claude follow-up

- [ ] Enrich `claude-usage` with sessions, days, hours and periods, additive to
      the existing cache keys.
- [ ] Fixtures for the Claude store and cache contract.
- [ ] Return Claude to the standalone and shipped widget menus and settings options.
- [ ] Test with real Claude data before enabling.

## Phase 6 — Pull request

- [x] User created `methos28/ryoku` from `Ryoku-dev/ryoku`.
- [x] Push `ai-usage-builtin`, open draft PR #1 against the fork's `unstable-dev`.
- [x] Body: what ships, what is held back (Claude), CI coverage, follow-ups.
- [x] User accepted and merged fork PR #1; verified every project path is intact.
- [x] On user request, reset PR #1 out of `unstable-dev`: fork force-synced to
      upstream `0749ec350`, module re-landed as `2877b9469`, old checkout
      replaced with a fork clone.
- [x] User recreated `methos28/ryoku`; module re-landed directly on its
      `unstable-dev` as `f0c5a4f0f`, with no feature branch.
- [x] Diagnose the failed post-merge jobs: publishing credentials, not module tests.
- [ ] User opens the new pull request from the fork.
- [x] Recheck after fork recreation: zero workflows/runs; the earlier failures are historical.
- [ ] A PR to Ryoku-dev/ryoku itself remains a separate, unapproved step.

## Phase 7 — Optimisation (unlocked 2026-11-07)

- [x] Extract the duplicated agent and period dropdowns into `AiUsageMenu.qml`;
      `IrisCompact.qml` falls from 601 to 470 lines and three dead period
      properties are gone.
- [x] Prefilter Codex rollout lines before JSON parsing and hoist the clock out
      of the session loop; output identical, 0.0357s to 0.0331s on 8.9 MB.
- [x] Committed on the fork as `31d36bef9` and `f9b7a7dc1`, pushed to
      `unstable-dev`; remote head `f9b7a7dc1`.
- [ ] Deeper pass, only if asked: incremental history cache, shared collector
      helpers, refresh-cadence review.

## Click-input backlog

- [ ] Reproduce H1: menu veil closes instead of the trigger toggling.
- [ ] Reproduce H3: chip disabled during availability probe.
- [ ] Reproduce H4: press/release dropped during page/scale animation.
- [ ] Reproduce H5: menu or card clipped at narrow island widths.
- [ ] Fix only what reproduces; record evidence first.
