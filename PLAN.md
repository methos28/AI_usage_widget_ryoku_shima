Current submission (completed 2026-11-10 12:43 IST): ai-usage-dashboard is published as
5c9d9f11cfcbf56de27d2f5433e37b1e95e40667 on methos28/ryoku. Local checkout: /home/methos/ryoku-arch.
Exactly 28 widget files, three required QML wiring files and an Added-only
CHANGELOG.md entry. All 172 external regression cases and normal hooks pass.
This is submission 1; see PR_TRACKER.md. No PR opened. Never create an upstream
PR unless the user explicitly instructs it. The older plan entries below are
historical and do not change this active scope.

# AI usage widget — plan

Latest fork publication (2026-11-10 03:11 IST): the user approved commit and push of the
complete audited widget-only corrections and multi-model pricing. Published
b650d0c474553931ef551332051e46fe3d651d62 to methos28/ryoku:ai-usage.
The actual remote SHA and clean fork working tree are verified. All 172 local
tests for each delivery target and normal hooks pass. Protected ecosystem
paths match the original upstream review base. CI status is recorded separately
in the latest project log. No standalone, upstream or channel branch changed.

Full bug audit completed on 2026-11-10. All 172 primary and 172 fork tests,
static runtime checks, ShellCheck, QML/binding, delivery and isolation gates pass.
The tested repairs are installed live. Native Codex request/token components
match the pre-audit implementation for 1,151 requests. See BUG_AUDIT_2026-11-10.md
for defects, evidence and remaining manual/platform coverage. Fork corrections
remain staged and uncommitted; no push occurred. Protected ecosystem paths
still match the original upstream review base.

Latest pricing repair: Codex and Claude share a widget-owned catalog covering
65 OpenAI and 35 Claude IDs, including published snapshots and native legacy
models. Public provider docs and models.dev refresh automatically without
credentials. Offline bundled/last-good rates, context tiers and public service
tiers are supported. Today gains missing prices; today's stale provisional
rates can refresh; older daily rates remain frozen. This supersedes the prior
Sonnet-only Claude restriction below. All 147 primary and 151 fork tests pass. Independent live Claude arithmetic
matches and every observed model is priced. See the latest project log. All changes remain uncommitted and confined to widget scope.

Latest scope correction (2026-11-09 22:22 IST): the user requires widget-only collector
packaging. Keep original Rashin collectors and distro docs byte-identical to
the upstream review base. Keep only required built-in module wiring, focused
tests/CI and root CHANGELOG.md outside the widget. Remove generic installation
changes and system-lock coupling. The corrections are local and uncommitted;
the published branch still contains the earlier broader patch until updated.
See the latest project log for validation and publication status.

Latest fork publication (2026-11-09 20:39 IST): user approved
commit and push of the complete current port to methos28/ryoku:ai-usage.
Published eb91adfd3de6e963e4bd25a1156907a10563260e; remote head and clean
fork working tree verified. All134 local tests and required gates pass.
Other branches and standalone remote were not changed. Remote CI status is
reported separately; see the latest project log.

Dropdown highlight fix (2026-11-09): use one shared row background for hovered
or current selection. Preserve the current option's accent/checkmark and inset
the fill vertically so adjacent options cannot merge. The actual menu's Qt
pointer/render probe failed with two fills before repair and passes after it,
including agent/period rows, selection clicks and reopening.

Reset label update (2026-11-09): the user requests local reset dates/times
instead of relative hours. Shared Claude/Codex labels now include date, AM/PM
and timezone; past saved deadlines remain identified. Tooltip clarifies that
Desktop is the current source, while CLI subscription OAuth also works without
Desktop. No collector/auth changes. A Desktop-absent CLI fixture verifies both
reset windows; native Qt formatting is checked in Kolkata and New York.

Claude reset countdowns (2026-11-09): read exact five-hour/weekly deadlines from
the account-bound Desktop HTTP usage cache, preserving capture age and expired
deadline semantics. UI shows countdowns beneath both bars and an explicit
unavailable label when timestamps are absent. No cookies are decrypted, no new
login is required, and no reset schedule is inferred. All 125 tests and QML gates
pass; both countdowns are installed and visually verified in the live card.

Claude recount audit (2026-11-09): resumed at the user's request. Independent
raw counts match Sonnet 980,673 and Haiku 739,630, combined 1,720,303. Sonnet's
output gap is the explicit O/R split; Haiku's quoted 356,575/430,498 checkpoints
differ by exactly one later response of 73,923 tokens. No parser repair is
needed. Added a numeric model-switch regression. Haiku pricing remains
unsupported and the API Value subtotal is explicitly partial. See
CLAUDE_RECOUNT_AUDIT_2026-11-09.md.

Label update (2026-11-09): the user requested `API Value` for all agents,
superseding earlier `Spending` / `Est. Spending` label requirements. Values,
coverage markers and calculation rules are unchanged.

Claude Desktop repair (2026-11-09): three requested subagents implemented quota,
spending and lifecycle helpers, reviewed and integrated by the parent. All 117
primary tests, cache contracts and QML gates pass. Standalone/live delivery shows
real account quotas (latest 39%/52%) and $0.671057 local Sonnet 5.5 API value for
11 verified responses / 707,459 inclusive tokens. Native idle state is confirmed
with a live PID. A fresh active Desktop run is requested for final lifecycle
validation. The fork stays held out; no commit, push or auth change is authorised.

Current repair (2026-11-09): request accounting and automatic history/spending
migration are implemented, tested and deployed. All 59 primary and 61 fork tests,
cache/QML/delivery gates pass. The frozen 653-request snapshot matches exactly;
a later 718-request live snapshot independently matches raw components, day
buckets and spending. All saved daily prices are unchanged. The live widget and
both user-owned legacy ledger writers use the repaired collector. Service
settings remain intact. No commit or push was made. See
REQUEST_ACCOUNTING_REPAIR_2026-11-09.md and the latest project log entry.

Current implementation (2026-11-09): at the user's request, both collectors
now ship inside widget/bin and are invoked by their own paths. Private caches
under ~/.cache/ai-usage isolate the module from older system writers; startup,
visible refresh and lock/retry handling work without the optional collector
service. Legacy source paths are compatibility symlinks to the canonical scripts.
All 48 primary and 50 fork tests plus delivery/QML gates pass. The complete
widget was deployed and verified live; existing settings and global helper/service
files are unchanged. These changes are uncommitted in both repositories and are
not part of published head c2dbdc496. See BUNDLED_COLLECTORS_2026-11-09.md.

Latest fork publication (2026-11-09 03:07 IST): the new delivery regression is committed
and pushed to methos28/ryoku:ai-usage as c2dbdc496bd2b123f50ad01476541acc7ee9f3e3. The fork
working tree is clean and the remote head is verified. Nine shared tests and
normal commit/push hooks passed. The full 47-test result remains applicable.
This publication does not change official unstable-dev or the standalone remote.

Current delivery audit (2026-11-09): official unstable-dev at 0749ec350 does
not contain the feature. The user's unstable-dev at f26ede8ad lacks the final
built-in discovery fix; the complete ai-usage head 9e4268ff2 contains it. The
live API reports upstream PR 757 closed without merging. A new uncommitted
review-branch regression now stages both package and source delivery and checks
fresh-profile discovery plus guard/collector output. All 47 fork tests and 44
standalone tests pass, with the prior gates and focused Go update/service tests.
Normal official updates cannot deliver the feature until the complete changes
land in that tracked branch and pass its testing gate. See
DELIVERY_AUDIT_2026-11-09.md and DELIVERY_INVENTORY_2026-11-09.tsv.

Current local fix (2026-11-09): stale live Codex limits are repaired. The
standalone installer now uses ~/.local/libexec/ai-usage/codex-usage and a later
zz-ai-usage.conf service drop-in to survive doctor cleanup and the observed
dev-bin override. All 44 standalone and 46 unchanged-fork tests plus prior gates
pass. The effective service and current Shima card were verified. Source edits
remain uncommitted; no fork branch or upstream change is needed for this local
installation correction. See TEST_REPORT_2026-11-09.md for coverage and the
inconclusive scripted input-race checks.

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

- [x] Enrich `claude-usage` with sessions, days, hours and periods, additive to
      the existing cache keys.
- [x] Fixtures for the Claude store, pricing, quota, lifecycle and cache/UI contract.
- [x] Return Claude to the standalone/live widget menus and settings options.
- [x] Validate real Claude tokens, account limits, costs and idle lifecycle.
- [ ] Observe a fresh active Desktop turn with the repaired running indicator.
- [ ] Return Claude to the shipped fork after live validation is accepted.

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

## Current owner instruction: clean rebuild after backup (2026-11-10)

Freeze the old Ryoku port. Back up the standalone project, exact widget bundle,
three shared wiring changes and validation evidence outside both Ryoku clones.
Exclude Rashin collectors/services from the import. Keep tests/CI and historical
records separate. Wait for the user to delete/recreate their fork and clone a
fresh unstable-dev. Then create ai-usage from that fresh base and commit only
the minimal widget port after review and required checks. Do not cherry-pick
old commits, restore old merge history, deploy the whole desktop or push without
a new request. The current task ends when verified backups and handoff are ready.

Verified rebuild backup: /home/methos/Documents/ai-usage-rebuild-backup/20261110-121656. Read REBUILD.md there before any new port. Current stage: wait for user deletion and fresh clone.

## Active port authorization: ai-usage-dashboard (2026-11-10)

Clone methos28/ryoku unstable-dev freshly at /home/methos/ryoku-arch. Create,
validate, commit and push ai-usage-dashboard. Limit the submission to the 28
widget runtime files, three required QML integration files and root CHANGELOG.md
Added entry. Tests/CI remain external validation material. Treat this as the
first feature submission; see PR_TRACKER.md. Do not create any upstream PR
unless the user explicitly requests it later. No PR creation is authorized now.

## Current local enhancement: background refresh (2026-11-10)

Implemented, tested (174 primary cases) and deployed a widget-owned singleton
for all-agent refresh every 15 seconds after the first module load, plus an
earlier refresh on opening. It survives page destruction. No login-start
daemon is introduced. Source/fork/live match; no new commit/push/PR. Read
BACKGROUND_REFRESH_2026-11-10.md before publishing or modifying cadence.

## PR #779 fixes complete locally (2026-11-10)

Seven recommended findings are implemented source-first and mirrored. DST is
held. The user-authorized docs/ai-usage.md and docs/structure.md link are ready;
changelog remains unchanged in Added. All 181 primary/fork cases and gates pass;
14 widget files are delivered live. Shared registry fix remains source-only.
No new commit/push/review reply; read PR_779_FIX_RESULTS.md before publication.

Latest fork publication (2026-11-10 17:04 IST): 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1, pushed to ai-usage-dashboard and
verified on PR #779. Seven fixes, worker and guide are published. Fork is clean;
181-case validation for each target applies. DST remains unchanged.

## Second review complete locally

All six new PR #779 suggestions are addressed source-first and mirrored, with
190 primary/fork tests and relevant gates passing. The exact 24-hour data and
chart agree across all agents; OAuth cooldown survives credential gaps without
cross-account reuse. Eleven widget files are live. No new commit/push or PR
reply; published head is 2566ef372. See PR_779_SECOND_REVIEW_FIXES.md.

Latest publication (2026-11-10 19:36 IST): second-review fixes dad97d5ab07f6db20900742ddd6909251db9dbd9
are pushed and verified on PR #779. Fork is clean; all 190 cases per target
apply. Earlier pending publication statements are historical.

Latest publication: 5ca6583632e7bf086362feb395f80c87bf40f431; all six remaining findings fixed
and pushed to the existing PR #779 branch. Both 197-case suites and hooks pass.
Primary source and live widget are updated; fork checkout is clean.

## Current work: saved Codex session names (2026-11-17)

The user accepted staying on stable and authorized the title change. Use saved names from Codex session_index.jsonl, with existing prompt/directory fallbacks. Primary and ai-usage-dashboard now adopt upstream visible-only 15-second collection and 120-second quota RPC caching; these supersede the earlier background-refresh requirement for this delivery. The absent old custom install will be restored through the supported user-owned widget path after gates. No commit, push, package update or channel switch is requested. Validation and live verification are pending.

Saved Codex session names are now delivered and visually verified. All 204 primary cases passed across the full run and the explicitly enabled shared-host follow-up; 56 fork collector cases and QML gates pass. The supported user-owned copy is active on stable. Changes remain uncommitted and unpushed. See the latest PROJECT_LOG.md entry and /home/methos/.local/share/ryoku/ai-usage-backup/codex-session-titles-20261117-122321.

## Current audit result (2026-11-17)

The saved-title delivery is committed locally in primary 37db05d and fork aa11db313, with nothing pushed. The current-code audit reproduced ten edge cases across five areas; no fixes were applied. See BUG_AUDIT_2026-11-17.md and its evidence directory. The existing 204-case baseline passes including the separately enabled shared-host case. Future work should add each reproduction as a permanent regression and fix only the user-approved scope.

## Feature publication synchronized (2026-11-17)

Published e7297aec6 to methos28/ryoku:ai-usage-dashboard after merging official unstable-dev 0389a5e. GitHub verifies two commits ahead, zero behind and only three feature paths different. Fork working tree is clean; the existing title feature is published, while all bug-audit fixes remain pending. The user explicitly chose the existing ai-usage-dashboard name. See the latest log and evidence/branch-sync-2026-11-17.

## All current audit fixes validated (2026-11-17)

All ten findings are repaired, with 18 permanent regression cases including real Qt, overlap deduplication, login privacy and time-bound checks. Both primary and actual fork runtime suites pass all 222 cases without skips. The user-owned live module is updated, native data parity is verified and all 20 historical price dictionaries are unchanged. Publish the same feature branch under the earlier commit/push authorization; keep the fork delta limited to its eight runtime/guide/changelog paths.

## Audit fixes published (2026-11-17)

The complete audited repair is installed and published as d4df8688a on ai-usage-dashboard; primary code is committed as c9c3eef. All 222 primary and 222 fork-targeted cases pass. GitHub verifies three ahead, zero behind official unstable-dev, with eight related paths. No audited bug fix remains pending from BUG_AUDIT_2026-11-17.md. The earlier statements that findings were unfixed are historical.

## Active live preview: metric transitions (2026-11-17)

User approval is pending. The live module now previews 280-ms quota fills, 300-ms token/API Value interpolation and 150-ms state fades using Shima motion settings. Both 227-case runs and QML/integration checks pass. The supported live bundle matches primary; the feature-source mirror is uncommitted. Heads remain primary 72a6730 and fork 98058bcd8, with no new commit or push. Preserve this explicit hold until user visual approval. Full before-state backup and rollback instructions: /home/methos/.local/share/ryoku/ai-usage-backup/transitions-preview-20261117-151845.

## Live preview follow-up: agent-switch handoff (2026-11-17)

The user-reported stale-state flash is repaired and installed. Selected snapshots now carry read ownership/generation, newer queued versions supersede old ones, and the Island/tile mask prior-agent stats during loading. Retained quota rows and numeric transition state are cleared on switches; regular same-agent transitions remain enabled. All six directions and rapid/missing-cache cases pass in native frame tests. Both full suites pass 233 cases. Still no commit/push; user live approval remains pending. Preserve both preview backups.

## Latest live motion revision and measurements (2026-11-18)

User testing is still pending; no commit/push. Defaults are now 360/380/180 ms for bars/numbers/fades with gentle easing. Both 233-case suites and QML/integration gates pass. The live module matches source. Hardware rendering comparisons show unchanged 8-ms p95 frame intervals and small animation-only estimated average cost at 15-second refresh (0.013 percent total CPU, 0.033 percent GPU). Full open-shell baseline cost is larger and reported separately. Read PERFORMANCE_2026-11-18.md for measured figures and limits. Current-revision backup: /home/methos/.local/share/ryoku/ai-usage-backup/motion-tuning-20261118-134810.
