# AI usage widget — project log

Append-only. Every entry records what changed, why, the evidence, and whether it
is committed, uncommitted, or live-only. Never rewrite history; add corrections
with a new timestamp. Read this file fully before continuing (see `AGENTS.md`).

Last updated: 2026-11-07 13:35 IST.

## Scope

The Shima AI usage module: widget QML, collectors that feed it, the live copy on
this machine, and the downstream Ryoku branch. Primary repository is
`/home/methos/Documents/opencode_widget_ryoku_shima`.

## 2026-11-06

### Repositories and baseline

- The module repository was renamed on GitHub to
  `methos28/AI_usage_widget_ryoku_shima`; local origin updated.
- The Ryoku target was cloned to `/home/methos/Projects/ryoku-unstable`, branch
  `unstable-dev`, and a feature branch `ai-usage-builtin` was created for the
  upstream attempt.
- Chosen approach: ship the module as a built-in Shima widget (option B).
  Upstream already had the collector units, `/usr/bin` install rules and a
  systemd timer, but no widget, so the port reused those seams.

### Licence

- MIT changed to GPL-3.0 to match Ryoku. Files: `LICENSE`, `README.md`,
  `CONTRIBUTING.md`. Commit `7f22a9d`, pushed before the later freeze.

### First Ryoku port (branch `ai-usage-builtin`)

- Collector adopted: the user's enriched OpenCode v2 reader replaced the upstream
  `opencode-usage`; upstream's store-layout test caught a missing schema-drift
  path, which was fixed.
- Widget copied into `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage`.
- Shipped-widget installer: `CustomWidgets` gained a defaults scan,
  `installShipped(id)` and `isInstalled(id)`; the widget panel's single
  example-only install button became one button per shipped widget.
- Tests: `tests/ai-usage-cache.py` and `tests/codex-usage.sh`, wired into
  `.github/workflows/ai-usage-collector.yml`.
- Codex collector gained per-day history, sessions, periods, generic windows,
  lifecycle-based running, and the RPC fix.
- Claude was held out of the shipped widget menu until its collector publishes
  the same history.
- Commits on that branch before the freeze: `548c14d73`, `c3a343763`,
  `facd5b691`, `accbd5e48`, `a2ebc932c`, `4b3602821`, `831cb1165`,
  `998c93c69`, `7babc74b3`, `feb78aa49`, `308c7abdb`, `6cff48603`.

### Diagnoses

1. **Codex cache kept losing enriched fields.** The packaged `/usr/bin/codex-usage`
   ran from the 5-minute timer and overwrote the enriched cache. Fixed by
   pointing the drop-in's Codex `ExecStart` at `~/.local/bin/codex-usage`.
2. **Codex RPC failed with `rpc error: initialize`.** Codex 0.167 removed
   `untrusted` from `-a`; the collector now uses `-a never`. A cold
   `account/read` could also exceed five seconds and abort the whole live read;
   it is now optional, with larger timeouts.
3. **Running sessions never cleared.** `running` was inferred from write recency
   (10 minutes) while the cache rebuilds every 5. Fixed by reading the rollout
   turn lifecycle (`task_started` vs `task_complete` / `turn_aborted` / `error`),
   with recency only as a fallback.
4. **Codex Free exposed only a 30-day window.** The widget hardcoded 5h/7d.
   Collectors now publish `_windows`, the widget renders whatever the plan
   reports and prints a reset line. Paid plans later showed 5h + weekly
   automatically.
5. **OpenCode sections disappeared.** Its cache was overwritten by the packaged
   `/usr/bin/opencode-usage` (`_source: storage`, no history). Running the
   repository v2 collector restored `_source: storage+v2`, 48 days and sessions.
6. **Token totals looked inflated.** Audit proved they are exact: every published
   value equals the rollout cumulative deltas to the token. The apparent jump was
   a stale baseline cache plus new work, not double counting.

### Restore to `42e7402`

- After a bad agent pass touched the widget, the user asked to return to
  `42e7402`. `main` was force-pushed back to that commit; the newer work was
  preserved on `backup/windows-1.2.0` (`c0b4406`). The live widget was replaced
  from the `42e7402` tree.
- Later commits on `main`: `c61f86b` (fixed trend slots and heatmap) and
  `bf0cfca` (Today label includes cached). Both were pushed before the freeze.

## 2026-11-07

### Requirements added by the user

1. No commits, local or remote, until explicitly asked.
2. "push to local" means commit only; "push to remote" means push only.
3. Record every change, requirement change, and diagnosis in this file.
4. Every later agent must read these records before continuing.
5. All-time trend must be capped at 45 days; other periods keep fixed spans.
6. Trend bar width must follow the Shima page width; 7-day must not look
   detached from the card edges; All-time must not look odd for short or long
   histories.
7. Codex Spending must show `$0.00` instead of disappearing when no cost exists.
8. Cards must stay compact like the Claude dashboard reference.
9. Do not let subagents introduce unnecessary bugs; test before live.
10. Enable project LSPs.

### Diagnoses and changes

- **Trend showed two bars.** The chart sliced the last N available rows; Codex
  had two recorded days. Fixed with calendar slots ending today: 7 and 30 fill
  their full spans; All-time is a fixed 45-day window (zeros before first use).
  Bar widths now fill the card, so they change with the Shima page width.
  Caption appends `last 45 days` for All-time.
- **Heatmap had invisible days.** Missing days were `null` and rendered
  transparent; leading all-empty weeks were removed. Now every elapsed day is a
  cell (zero days dim), only future days are transparent, full 13-week grid.
- **Codex Today/24h wrong.** `_hours[].start` was seconds while OpenCode/Claude
  use milliseconds. The widget normalises seconds to ms, the collector emits ms,
  and old seconds rows are migrated out of the cache on merge.
- **Period label was a dead control.** ~60x14px target, disabled when the card
  was collapsed. Now padded hit area, always accepts input: collapsed opens the
  card, expanded opens the period menu.
- **Refresh could stay locked for 10 seconds.** The reload timer now clears
  `refreshing` when the collector exits.
- **Spending missing for Codex.** It was gated on `hasCostHistory`, and Codex
  costs are all zero. Plan agents now always render the Spending block and show
  `monthly.current`, so Codex reads `$0.00 Nov`.
- **Cards too tall.** The explanatory "No cost recorded" line added a row that
  forced the taller half-split. Removed; keeps the $0.00 and returns the row to
  the Claude reference height.
- **Click audit.** Modal veil, chip disable during availability probe, animation
  grab races and island clipping remain hypotheses without a live repro; not
  changed. Only the provable period target and refresh lock were fixed.

### Token verification (Codex, 2026-11-07)

- Three rollouts, 76 `token_count` events, no duplicate session or response ids.
- Today 3,125,485 = 161,389 non-cached + 2,964,096 cached (94.8%).
- Sessions 342,637 = 73,193 + 81,468 + 187,976.
- All-time 5,640,173 = both day buckets and both model rows.
- Collector reads only `token_count`; summing it with `token_usage_record` would
  double everything, and it does not.
- Latent risks not observed: a shrinking rollout re-adds deltas; a resumed thread
  copied into a second file could count twice.

### Project records, rules and language servers (2026-11-07 13:35)

- Added project-scoped files: `AGENTS.md` (rules), `PROJECT_LOG.md` (this file),
  `PLAN.md` (phases), `HANDOFF-CODEX.md` (continuation prompt).
- Added `opencode.json` with:
  - `instructions`: `AGENTS.md`, `PROJECT_LOG.md`, `PLAN.md`.
  - LSP: QML (`/usr/lib/qt6/bin/qmlls`, imports from `/usr/lib/qt6/qml` and
    `~/.config/quickshell`), Python (`pyright-langserver`), JSON
    (`vscode-json-language-server`), Bash (`bash-language-server`); the object
    form keeps built-in YAML, Go (`gopls`) and C/C++ (`clangd`) enabled.
- Installed via npm into `~/.local` (no sudo): `pyright`,
  `vscode-langservers-extracted`, `bash-language-server`. qmlls comes from
  `qt6-declarative`; `yaml-language-server`, `gopls`, `clangd` were present.
- `opencode reload` completed after the config was written.
- No commits made.

## Project records and tooling (2026-11-07 13:35)

- Added project-scoped `AGENTS.md`: commit freeze, record discipline, delivery
  gate, ownership map, known traps, mandatory reading order for every agent.
- Added `PROJECT_LOG.md` (this file) and `PLAN.md` (phases and open work).
- Added `HANDOFF-CODEX.md`, the copy-paste prompt that continues this project in
  Codex, including the current state and test gates.
- Added project `opencode.json`: `instructions` loads the three records; LSP
  config starts QML (`qmlls`), Python (`pyright-langserver`), JSON
  (`vscode-json-language-server`) and Bash (`bash-language-server`), while the
  built-ins (YAML, Go, C/C++) stay enabled. `opencode reload` reported
  "Configuration reloaded".
- Installed the missing servers with npm into `~/.local` (no sudo): `pyright`,
  `vscode-langservers-extracted`, `bash-language-server`. No system packages
  changed.
- Nothing committed.

## Commit and branch inventory (as of this entry)
- `methos28/AI_usage_widget_ryoku_shima`
  - `main` = `bf0cfca`, clean vs origin.
  - `backup/windows-1.2.0` = `c0b4406` (rescued newer module work).
  - `readme/page-width-default` = `b153937`.
  - PR #1 (README) merged; did not modify code.
- `/home/methos/Projects/ryoku-unstable`
  - `ai-usage-builtin` = `6cff48603`.
  - Nothing pushed; no fork created.

## Uncommitted working tree (not committed by rule)

Widget repository (`ai-usage/`):
1. `IrisCompact.qml` — fixed day slots, All-time 45, dynamic widths, spend gate.
2. `UsageModel.qml` — hours seconds-to-ms normalisation, refresh release.
3. `components/AiUsageTrendCard.qml` — full-width bars, caption, period target.
4. `components/AiUsageSpendBody.qml` — always monthly value, $0.00 for Codex, no
   note row.
5. `components/AiUsageActivityCard.qml` — already committed in `c61f86b`; the
   working tree change is the 13-week/zero-fill patch on top of that commit.
6. `components/AiUsageLimitsCard.qml` — already committed in `bf0cfca`; label.
7. New project files: `AGENTS.md`, `PROJECT_LOG.md`, `PLAN.md`,
   `HANDOFF-CODEX.md`, `opencode.json`.

Ryoku checkout:
- `ryoku/rashin/usage/codex-usage` — milliseconds hours plus stale-seconds
  migration (uncommitted).

Live copy:
- `~/.config/inir/widgets/ai-usage` matches the working tree (verified by
  `diff -rq`), shell reloaded.

## Live state

- Caches at 2026-11-07 13:06:
  - OpenCode: `storage+v2`, 48 days, 10 sessions.
  - Codex: `rpc`, `plus`, 2 days, 3 sessions, 5h + weekly windows.
  - Claude: `stale` demo cache, 60 days, 3 sessions (no Claude CLI installed).
- `ryoku-ai-usage.timer` runs every 5 minutes; drop-in points Codex and OpenCode
  at `~/.local/bin`.
- Codex today is `0` after midnight rollover until the next prompt; yesterday's
  bucket remains at 2,514,688.

## Known open items

1. Claude collector still lacks history/sessions/periods; held out of the PR
   widget until enriched and tested.
2. Port the current widget fixes into the Ryoku branch and its tests.
3. Add fixtures for trend slots, heatmap zero-fill, hours unit normalisation,
   `$0.00` spend and the period hit target.
4. Click hypotheses H1/H3/H4/H5 need a live repro before code changes.
5. Latent Codex double-count risks (shrinking file, resumed thread) are not fixed.
6. Optimisation and refactoring are on hold until the user asks.

## Verification commands

```bash
cd /home/methos/Documents/opencode_widget_ryoku_shima
./test/run.sh
cd /home/methos/Projects/ryoku-unstable
RYOKU_QML_IMPORTS="$PWD/ryoku/shell/quickshell" \
  bin/ryoku-dev-lint-qml /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage
bin/ryoku-dev-verify-qml-bindings --quiet \
  /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage/*.qml \
  /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage/components/*.qml
bash tests/codex-usage.sh
python3 tests/ai-usage-cache.py
```

## 2026-11-07 13:23 IST — Codex handoff verification and baseline gates

- Read `AGENTS.md`, this log, and `PLAN.md` completely before checking state.
  The user then said "Go ahead" to the proposed live visual review. This does
  not record visual sign-off or authorise commits or pushes.
- Confirmed module `main` at `bf0cfca`, with four modified QML files and the
  five untracked project files listed in the handoff. `diff -rq ai-usage
  /home/methos/.config/inir/widgets/ai-usage` returned 0 with no differences.
- Record correction: the earlier uncommitted inventory mentions changes to
  `AiUsageActivityCard.qml` and `AiUsageLimitsCard.qml`; neither is modified
  relative to HEAD. No files were reverted or changed to reconcile the record.
- Confirmed Ryoku branch `ai-usage-builtin` at `6cff48603`, with only
  `ryoku/rashin/usage/codex-usage` modified.
- Caches at 13:17 IST: OpenCode `storage+v2`, 48 days and 10 sessions; Codex
  `rpc`, `_plan: plus`, 2 days and 3 sessions; Claude `stale`, 60 days and
  3 sessions. No Claude executable found on PATH. Cache timestamps differ
  from the earlier 13:06 snapshot; the reported shapes match the handoff.
- All five baseline gates passed: `./test/run.sh` (six collector tests),
  Ryoku QML lint with the specified import path, the quiet QML binding gate,
  `bash tests/codex-usage.sh`, and `python3 tests/ai-usage-cache.py`.
  The repository's raw qmllint step emitted warnings, including unused imports,
  unqualified accesses and missing properties; it exited successfully. These
  warnings were not changed or treated as visual verification.
- Live visual review remains unverified: `ryoku-shell --help` reported
  `daemon not reachable at /run/user/1000/ryoku-shell.sock`, and a `grim`
  capture attempt failed with `failed to create display`. No screenshot was
  produced. These errors establish lack of access from this session; they do
  not establish that the user's desktop is broken. Requested the user's live
  check of Codex/OpenCode cards, trends, heatmap, spend and row heights.
- Only this append-only record was edited. All changes remain uncommitted;
  no widget code, live copy, shell state, collectors or caches were changed.
  Phase 1 visual sign-off and live click reproductions remain open. Phase 2
  fixtures have not started.

## 2026-11-07 13:30 IST — Independent Codex token audit

- The user requested a fresh correctness audit of the Codex token calculator.
  This audit takes priority over visual review; it does not grant visual
  sign-off, authorise fixes, or change the commit freeze.
- Rechecked both working trees and live-widget equality. The live collector
  `~/.local/bin/codex-usage` is byte-identical to the uncommitted Ryoku
  collector. The systemd drop-in points to this live collector. Four rollouts
  now exist, including this Codex conversation; the extra session and growing
  totals are expected activity after the three-session handoff.
- Audited a stable cache/activity snapshot from 13:29:19 IST. Read each rollout
  only through its recorded activity-cache byte offset, avoiding new events
  generated by the audit itself. Both cache files remained unchanged during
  the comparison. No live collector, RPC, cache writer or refresh was invoked.
- Independent reconstruction: four files, 95 token_count events, 94 positive
  deltas and one unchanged snapshot; no malformed lines, repeated session IDs,
  repeated positive snapshots or cumulative counter decreases. Every raw
  `total_tokens` equals `input_tokens + output_tokens`, and cached input is a
  subset of input. Each positive cumulative delta also exactly equals that
  event's `last_token_usage.total_tokens`. Summed terminal cumulative totals,
  summed positive deltas and summed last-call totals all agree.
- Exact all-time inclusive totals per session: 3,155,784; 1,985,724; 498,665;
  853,766. Combined: 6,493,939 = 420,979 non-cached + 6,072,960 cached.
  Local day 2026-11-06: 2,514,688 = 181,248 + 2,333,440.
  Local day 2026-11-07: 3,979,251 = 239,731 + 3,739,520.
- All 23 comparisons passed: incremental state terminal totals, daily buckets,
  nonzero local-hour buckets, inclusive Today and rolling-hour counts, activity
  daily totals, recent days, non-cached session totals, and all five periods'
  non-cached totals, cache rates and model totals. The collector's pure
  `history_records()` reader, with snapshot reads mocked in memory, independently
  matched these reconstructed totals. The widget adds `tokens + cacheRead` for
  charts and uses inclusive model labels; session and period token totals
  exclude cached input by the current cache convention. This difference does
  not constitute double counting.
- Breakdown limitation: the raw events contain 9,206 reasoning output tokens.
  They are already part of output and total tokens. `history_records()` sets
  the separate reasoning field to zero, so the widget omits this breakdown;
  the total does not lose or double-count those tokens.
- Isolated experiments used a temporary directory inside the module repository
  and the existing collector functions, with no live state changes. A sequence
  ending at 3,000 tokens stayed at 3,000 after a repeated cumulative snapshot
  and an unchanged rescan. Three edge cases failed:
  1. Moving the same rollout from sessions to archived_sessions made the
     incremental Today count 6,000 while history remained 3,000. Incremental
     state identifies files by path, so a moved file is processed again.
  2. Truncating/replaying a previously processed file increased incremental
     Today from 3,000 to 4,000. Resetting the byte offset also resets last_total
     without removing previously recorded contributions.
  3. Keeping the same session rollout in both roots made history total 6,000
     instead of the logical session's 3,000. Session metadata merges by ID, but
     token records retain both files' contributions.
  These confirm replay/deduplication weaknesses; none was observed in current
  live data. Source: collector lines 583–642 and 718–853.
- Existing `tests/codex-usage.sh` and `tests/ai-usage-cache.py` passed. These
  baseline tests do not cover the three reproduced edge cases. Temporary
  experiments were removed automatically; no permanent fixtures were added.
- Verdict: current published token totals are correct to the token. The
  calculator is not robust against moved, truncated or duplicated rollouts.
  Only this log was changed, uncommitted. No code fixes, live copies, reloads,
  commits or pushes were performed. Visual review remains open.

## 2026-11-07 13:35 IST — Authorised Codex replay fixes and verified limit windows

The user requested fixes for the three reproduced token replay bugs and independent verification of the five-hour, weekly and Free-plan windows before implementation. This work now takes priority over the pending visual review. No commit or push is authorised.

Official documentation fetched: https://learn.chatgpt.com/docs/pricing and https://learn.chatgpt.com/docs/app-server (rate limits section). Pricing documents five-hour usage for Plus and Standard Business, possible weekly limits, and currently no five-hour limit for Pro. It does not establish a universal 30-day Free-plan cooldown. The app-server protocol defines usedPercent, windowDurationMins and resetsAt (Unix seconds); primary and secondary are not fixed-duration names. Local raw rollouts independently contain 34 Free snapshots with primary=43,200 minutes and no secondary, and paid snapshots with primary=300 and secondary=10,080. The current rpc cache reports Plus with those two paid windows. Free 30-day behaviour is supported by this account’s recorded payload, not asserted as a universal policy.

New discrepancy: this module’s restored UsageModel.qml does not parse _windows, and AiUsageLimitsCard.qml still hardcodes 5h/7d, despite earlier records claiming generic windows were live. The downstream checkout already has generic window presentation. Stop point recorded before code edits; resolve by bringing the needed window behaviour into this primary module while retaining its accepted Today label. Also, supplement_missing_general_windows_from_sessions can append historical paid windows to an authoritative RPC response for another plan; authoritative RPC omissions must be respected.

Implementation scope: add collector/codex-usage to the primary module from the named Ryoku checkout’s existing source baseline (not from a live edit); fix event replay identity for incremental and history readers; add focused regression tests; render server-reported limit/reset windows, including 30d when returned for Free. Gates precede deployment to the named live collector and widget paths. Do not port unrelated widget changes or start Claude work.

### 13:37 IST — First implementation, not yet delivered

Added the repository collector baseline and patched token-event identity using session ID, timestamp and cumulative usage, independent of path. Incremental state schema 4 rebuilds old schema-3 activity once from retained rollouts and retains event identities for the daily-history interval; history deduplicates the same logical event across copied rollouts. Local counters still advance when a replay is skipped, so later appended deltas retain their correct baseline.

UsageModel.qml now parses actual window lengths, percentages and Unix-second reset times; AiUsageLimitsCard.qml repeats those windows, and AiUsageWindowRow.qml shows the reset countdown. A reported 43,200-minute window renders 30d. An explicitly empty window array does not create 5h/7d rows; legacy named fields remain supported. Historical window supplementation is no longer called for either RPC or rollout fallback, preventing stale limits from a previous plan. Baseline helper definitions are retained to avoid unrelated cleanup. All edits are uncommitted and repository-only pending regression gates.

### 13:39 IST — Regression results before delivery gates

Added test/test_codex_usage.py and wired it into test/run.sh. Fourteen regression tests pass against the new primary collector: duplicate snapshots, unchanged refreshes, archive moves plus append, truncation/replay plus append, copied/shared-prefix rollouts, distinct sessions, genuine counter resets, schema-3 migration, previous-day replay after rolling-event pruning, Plus window units/percent/reset, Free switching without stale paid windows, weekly-only plans, rollout fallback and previous-plan fallback contamination. The test also executes the actual UsageModel JavaScript functions in Node.js for window labels and reset countdowns. README.md records this test dependency and window semantics.

Negative control: the same suite against the original Ryoku collector fails seven cases, including all three token bug paths, previous-day replay and paid-window contamination of Free for RPC and rollout fallback. The new collector passes all fourteen. No live copy yet.

### 13:41 IST — Delivery gates and installer correction

All original delivery gates passed after the collector/window changes (six existing module tests plus fourteen new tests, Ryoku QML lint, binding gate, Codex collector fixture and cache-contract gate). Raw repository qmllint continues to emit warnings while exiting successfully; the Ryoku QML gate is clean. A read-only live RPC attempt failed at initialize in this restricted session, so no new live server result is claimed. The shell socket exists, but connecting fails with PermissionError: [Errno 1] Operation not permitted; do not interpret that as a stopped daemon.

Found a delivery trap before deployment: install.sh installed only OpenCode, and the repository systemd drop-in selected /usr/bin/codex-usage. This would bypass the fixed collector on reinstall. Added repository Codex installation, selected %h/.local/bin/codex-usage in the drop-in, and updated the matching manual README steps. The live drop-in already uses that path and needs no edit. Added a fifteenth regression test that runs install.sh with a temporary HOME and stub service/shell commands, confirming the executable and selected collector without touching desktop state. Re-running the module gate for these added delivery changes.

### 13:42 IST — Final pre-copy validation

The final module gate passed: six OpenCode tests and fifteen Codex tests, including the temporary-HOME installer test. bash -n install.sh test/run.sh passed. QML files are unchanged since their clean Ryoku lint and binding gates; existing Ryoku Codex and cache gates also passed. An isolated dry run of the new collector against all real rollout files migrated a copy of schema-3 activity to schema 4, then repeated unchanged without adding tokens. Independent raw reconstruction through the recorded offsets matched Today, all-time days, model totals and non-cached period totals: 120 events, Today inclusive 7,196,620; all-time inclusive 9,711,308 = 507,212 non-cached + 9,204,096 cached. This includes tokens from the ongoing implementation, so it exceeds the earlier audit snapshot legitimately. Rate-window inputs for this dry run came from the existing rpc cache (300/10,080 minutes), not a new RPC read. Live caches were not overwritten by the dry run.

Proceeding with tested repository-to-live copies only: collector/codex-usage to ~/.local/bin/codex-usage and the three changed QML files to the matching ~/.config/inir/widgets/ai-usage paths. The already-correct live service drop-in remains untouched. The required reload will be attempted, but this session’s shell-socket connection is denied by its execution restrictions.

### 13:42 IST — Live files installed; reload blocked

Installed the fixed collector to ~/.local/bin/codex-usage and the three tested QML files to the live widget. cmp confirmed collector equality; diff -rq confirmed the entire live widget equals the primary repository. ryoku-shell reload failed with the same daemon-not-reachable message. The independently checked socket connection returns EPERM, so this session cannot complete or verify a shell reload. No attempt was made to bypass that restriction or start a second daemon.

The last observed real cache remains rpc/Plus with schema-3 activity (13:41:05 IST); live schema-4 migration is pending the next normal collector run. Cache schemaVersion stays 3 by contract; only the separate activity-state file changes to 4. No fake RPC data or dry-run cache was copied to live. PLAN.md now names the new primary collector, completed fixes/tests/copy and the pending reload, real refresh, visual review and later downstream port. The temporary module gate log was removed after recording its successful results. No commits, pushes, Claude changes or downstream source changes were made in this task.

## 2026-11-07 13:47 IST — Activity heatmap capped at 60 days

The user changed the heatmap requirement from a full 13-week grid to a maximum of 60 days to improve the Activity layout. The new view will cover today plus the preceding 59 calendar days, retaining locale-aligned week columns with transparent padding outside that range. Only those 60 dates get visible squares, including dim zero days. Existing full-history total and streak semantics stay unchanged. Active/busiest-day figures and colour thresholds follow the displayed window, as before. No collector changes are needed.

Before editing, both repository working trees match the last recorded code state and diff -rq confirms repository/live widget equality. Codex activity state is now schema 4 on the real machine, confirming that the normal timer ran the newly installed collector; the display cache remains rpc with two days and four sessions. This resolves the prior pending migration observation, without claiming a verified shell reload.

### 13:48 IST — 60-day implementation and checks

AiUsageActivityCard.qml now starts at today minus 59 calendar days and aligns the surrounding partial week columns to the locale. Dates before the start and after today are transparent padding; exactly 60 dated squares are emitted for any nonempty history. This takes nine or ten week columns instead of thirteen. No collectors, trends, full-history totals or streak logic were changed. PLAN.md replaces the superseded 91-cell fixture requirement with a 60-date cap; README.md describes the 60-day view and its maximum 137px heatmap width at default density.

One-off checks executed the actual map-binding JavaScript with short (2/48 days), 60-day and 120-day histories, empty history, all seven ending weekdays, Sunday/Monday locale starts, and dates spanning DST changes. Passed 252 combinations plus empty history in each of Asia/Kolkata and America/New_York. Confirmed exactly 60 distinct dates ending today, no older activity in active/busiest figures, dim zero-day data and at most ten aligned columns. No permanent tests were added for this reversible layout change. All five delivery gates passed, including all 21 module tests, Ryoku QML lint, binding gate, Codex collector and cache checks. Proceeding to copy only this tested Activity QML file to its named live path.

### 13:48 IST — Activity copy delivered

Copied AiUsageActivityCard.qml from the tested repository to the live widget. diff -rq confirms full widget equality. ryoku-shell reload remains inaccessible in this session and returned the prior daemon-not-reachable message; earlier socket checks established EPERM. The on-screen 60-day layout is pending a successful shell reload and user visual review. All changes remain uncommitted. No pushes or downstream port were performed.

## 2026-11-07 13:56 IST — Full 63-square Activity grid

The user supplied a screenshot of the 60-day heatmap and requested 63 days because the three missing squares looked odd. This supersedes the 60-day cap. To meet the visual requirement, the map will contain exactly nine full columns of seven past/present dates, ending today (today minus 62 days through today). Locale-aligned partial calendar weeks would still leave gaps even with a 63-day range, so the columns now group consecutive seven-day blocks without leading or future padding. No weekday labels are displayed. Zero days remain dim; full-history headline and streak logic remain unchanged. Repository/live widget equality and both working trees were checked before edits; cache shapes remain as last recorded.

### 13:56 IST — 63-square implementation verified

Changed AiUsageActivityCard.qml to today minus 62 days and nine full seven-day columns, without locale-start padding. PLAN.md and README.md now describe the 63-day grid; default-density width is 123px (nine 11px cells plus eight 3px gaps). The actual map-binding JavaScript passed 84 combinations plus empty history in each of Asia/Kolkata and America/New_York, covering all ending weekdays, short/long histories and DST dates. Every nonempty map has nine full columns, 63 unique consecutive dates ending today and no null squares. All five delivery gates passed, including 21 module tests, QML lint, binding, collector and cache checks. All edits are uncommitted; copying only the tested Activity QML file next.

### 13:56 IST — 63-square live copy

The tested Activity QML is installed at the named live widget path, and diff -rq confirms complete repository/live equality. The reload command still cannot access the shell socket from this restricted session and returned the previously diagnosed daemon-not-reachable message. User terminal reload and visual review remain needed for this version. No commits, pushes or downstream changes were made.

## 2026-11-07 14:02 IST — Prepare Claude hold-out for local commit review

The user asked to keep untested Claude out of the upcoming commit’s selectable agents, offered a menu-only change or per-agent file segregation, and explicitly required waiting for consent before any local commit. Chosen approach: remove Claude from the dashboard dropdown and widget-settings options, with an explanatory hold-out comment, rather than splitting the shared model or leaving commented-out code. Existing shared cache-reading support, demo helpers and collector service wiring remain available for a separately tested Claude follow-up. This changes the prior standalone policy, which offered Claude; the primary module and downstream PR now both withhold it.

Pre-edit checks: module/live widget identical, both working trees match recorded work, and cache shapes are unchanged. Prepare repository edits and gates only for review; do not stage, commit, push or deploy this menu change before the user reviews it.

### 14:03 IST — Claude hold-out ready for consent

Removed the Claude row from IrisCompact.qml agentCatalog and from widget.json tool options, added a hold-out explanation, and removed Claude from the manifest’s supported-agent description. Shared model labels, cache reader, availability probes, demo helpers and service commands remain unchanged. Updated AGENTS.md active scope, PLAN.md follow-up and README.md supported-agent settings and status. No agent-file split or commented-out implementation was introduced.

One-off execution of the actual catalog and reconcileAgent() logic passed all eight OpenCode/Claude/Codex cache-presence combinations; Claude never appears, and a previously stored Claude choice falls back to an available supported agent through the existing reconciliation. JSON settings expose exactly OpenCode and Codex. All five delivery gates passed, including the 21 module tests, QML lint, binding, Codex collector and cache checks. Raw repository qmllint continues to emit its pre-existing warnings while exiting successfully.

Ready for the user’s review and consent. No files staged, no commit, no push and no live deployment. The intended repository/live difference is limited to IrisCompact.qml and widget.json; earlier tested changes remain installed. The next local commit still requires the user’s explicit consent under the standing "push to local" policy.

## 2026-11-07 14:04 IST — Local commit consent received

The user explicitly said "push to local". This authorises local commits of the prepared module work only, with no network push. Rechecked the unstaged inventory against the records; the only intentional live-widget differences are the pending Claude menu and manifest changes. All five gates passed immediately before this consent and implementation files have not changed since. No new test run is needed for committing the same tested code.

Create logical commits for Codex collector/quota handling and installation/tests, trend/spending/input fixes, the 63-day heatmap, Claude menu hold-out, and project records/tooling. Keep the downstream Ryoku checkout untouched. Preserve all existing working-tree changes; no history rewrite or hook bypass.

### 14:05 IST — Local implementation commits created

Created the following local commits with normal git commit, without bypassing hooks:

- `85a426b codex: deduplicate rollout usage and follow account quota windows`
- `861e398 widget: fix trend spans, spending and period controls`
- `b5395e5 widget: render activity as a full 63-day heatmap`
- `fafe52b widget: withhold Claude until real-data validation`

The shared IrisCompact.qml edits were staged by concern so Claude hold-out remains its own commit. Working files were not rewritten during this split. The final documentation/tooling commit will include README.md, AGENTS.md, PLAN.md, PROJECT_LOG.md (including this entry), the original HANDOFF-CODEX.md snapshot and the previously prepared opencode.json LSP setup. PLAN.md records the user’s local approval and leaves remote push unapproved. Historical handoff snapshots remain historical; this log and PLAN.md carry current state.

All implementation code is the same tree that passed the last recorded gates. No live files were changed by this commit-only request; the known live differences remain IrisCompact.qml and widget.json from the withheld-Claude preparation. No network action, remote push or Ryoku downstream commit was performed. Confirm the final record commit ID with git log; embedding its own hash in this entry would change that hash.

## 2026-11-07 14:06 IST — Deploy the committed widget for visual review

The user explicitly requested updating the live widget to see the committed changes. Module HEAD is b599ff5, five local commits ahead; implementation files match HEAD and have not changed since the full passing delivery gates. Live comparison shows only IrisCompact.qml and widget.json differ, as recorded. The live Codex collector already matches the committed source. Reuse the existing passing gates for these identical files and copy only the two pending files. No new commit, push, settings rewrite or downstream port is authorised by this deployment request.

### 14:06 IST — Live copy complete; shell reload still blocked

Copied the committed IrisCompact.qml and widget.json to ~/.config/inir/widgets/ai-usage. diff -rq now confirms the entire live widget equals the committed source, including the Claude dropdown/settings hold-out and full 63-square heatmap. ryoku-shell reload still returns daemon not reachable at /run/user/1000/ryoku-shell.sock; the earlier direct socket check established EPERM from this execution environment. The shell is not claimed to have reloaded or the result visually verified. A terminal reload by the user remains necessary. Only this deployment record is uncommitted; source code remains at the approved commits. No new commit or remote push was performed.

## 2026-11-07 14:12 IST — Commit the deployment record

The user explicitly requested committing to the Git repository now. Only PROJECT_LOG.md was pending, containing the live deployment record and reload limitation. Commit these notes locally; no implementation changes, live deployment or remote push are part of this request. git diff --check passed. Tests are not rerun for this documentation-only change. The user also reconfirmed the existing plan to enable Claude later after collecting and validating real usage data; shared support remains retained for that follow-up. This entry is included in the same local documentation commit.

## 2026-11-07 14:13 IST — Remote push requested; network failure

The user explicitly requested "Push to remote now", authorising a push of the six existing local commits only. Verified main, clean initial working tree, origin https://github.com/methos28/AI_usage_widget_ryoku_shima.git and six commits ahead through 47b9395. git push origin main exited 128 before contacting GitHub: fatal: unable to access the repository URL: Could not resolve host: github.com. No remote push succeeded and no new commit was created. This push-attempt record remains uncommitted because push-only consent does not authorise another local commit. Retry the same push from a terminal with GitHub connectivity.

### 2026-11-07 14:15 IST — Retry with GitHub CLI credentials

The user reported changing the repository to private and completing gh auth login, and requested using that authentication for the already-authorised remote push. Retried with a command-scoped gh credential helper: git -c credential.helper= -c "credential.helper=!gh auth git-credential" push origin main. No global or repository credential configuration was changed and no secrets were printed. The push again exited 128 with Could not resolve host: github.com, before remote authentication could occur. gh auth status also reported its active account token invalid, but this network-restricted session cannot establish credential validity; no logout, token replacement or re-login was attempted. Six commits remain local. This retry record is uncommitted under the push-only policy.

### 2026-11-07 14:17 IST — Retry after reported public visibility

The user reported making the repository public again and explicitly requested another push attempt. Retried origin/main with the command-scoped GitHub CLI credential helper. The push again exited 128: Could not resolve host: github.com. The failure happens before authentication or repository visibility is evaluated. No remote changes or new commits were made; the attempt remains documented in the uncommitted log.

### 2026-11-07 14:18 IST — User completed terminal push

The user reported completing the terminal push. Local verification shows main and origin/main both at 47b9395, with no commits in origin/main..HEAD and no ahead/behind marker in git status. This confirms that local remote-tracking state reflects the reported push; no fresh network query was made from the restricted session. PROJECT_LOG.md is the only uncommitted file and contains the push-attempt and completion records. No additional commit or push was performed.

## 2026-11-07 15:03 IST — Ryoku downstream port and local commit authorised

The user requested committing the accepted module work locally for Ryoku/unstable-dev, followed by creating a PR. Work remains on the existing ai-usage-builtin feature branch, targeting unstable-dev through a PR, rather than committing onto the upstream channel branch. The named Ryoku checkout is at 6cff48603 with the previously recorded milliseconds/migration collector edit; module main and origin/main are at 47b9395 with only project-log notes pending.

Compared both widget trees and collector sources before editing. Preserve Ryoku-specific packaged opencode-usage lookup and RYOKU_AI_USAGE_COLLECTOR override, immediate fallback from unsupported saved agents, existing Claude hold-out, manifest version 1.2.0, shipped-widget installation and CI wiring. Port accepted calendar trends, 63-square heatmap, zero-cost spending, refresh release, hour normalization, server-authoritative windows and replay fixes only. Move the regression suite into Ryoku tests with paths adapted and the standalone install test omitted. Do not copy personal project docs, opencode.json, the standalone installer or user service overrides into Ryoku.

Read the contributor/hook instructions. This clone currently has no core.hooksPath override; configure it to the existing .githooks as required by docs/development.md, without editing or bypassing the hooks. Prowl outlined the known collector/widget sources; a semantic search initiated a one-time index rebuild, so use exact known-path comparisons for the remainder. All changes and results will continue to be logged here.

### 15:04 IST — Ryoku source port and CI fixtures

Ported the accepted collector to ryoku/rashin/usage/codex-usage, retaining the pre-existing milliseconds and old-cache migration edit. Ported only the matching module hunks into the shipped widget and copied the five accepted card components. Kept Ryoku’s immediate saved-agent fallback, packaged opencode-usage plus env override, existing Claude hold-out explanation and manifest version 1.2.0. The initial patch command used Git’s default strip level against labels without a/ prefixes and failed before changes; reapplying with -p0 succeeded.

Added tests/codex-usage-regression.py from the primary suite with repository paths adapted and the standalone installer test omitted. All fourteen tests pass against the downstream collector and QML functions. Wired the suite into the existing AI usage workflow, including a declared Node 22 runtime and test-file path triggers. Added focused root and shell changelog entries. No packaging, hooks, AGENTS.md, personal LSP config, service overrides or live files were edited. Existing .githooks were activated via this checkout’s core.hooksPath config as required by its contributor guide.

### 15:04 IST — User narrows delivery to local unstable-dev

The user clarified: commit to local unstable-dev for now, finish testing and present a test report, and only then ask for consent to create a PR. This revokes any inferred authorisation to fork, push or open a PR in the current task. Finish focused tests and normal hooks, preserve the tested work on ai-usage-builtin, then fast-forward local unstable-dev to it if ancestry permits. Keep the feature branch as a second reference to the same local commits. No remote mutation or PR creation before explicit later consent.

### 15:06 IST — Restrict Ryoku submission to required files

The user explicitly restricted local unstable-dev changes to the required module files and excluded README/CONTRIBUTING or other unrelated files. Verified the complete feature diff against origin/unstable-dev: only the widget, its loader/installer seam, usage collectors, tests and CI are present; README.md, CONTRIBUTING.md and AGENTS.md are unchanged. Removed my newly added root and shell changelog entries so documentation files are also excluded. This is a user-directed exception to the repository contributor guideline requesting changelog edits; user instructions take precedence. Keep detailed history and test reports in this primary module project only. No required implementation file changed during this restriction.

### 15:09 IST — Ryoku local commits and test report complete

All focused gates passed: fourteen ported regression tests; eight OpenCode assertions; six Codex rollout assertions; cache contract; shipped-widget QML lint and bindings; delivery and WM isolation; workflow parsing. Added checks for both existing loader/settings files under the same fatal-QML/binding criteria. One-off execution of actual trend/heatmap bindings passed 168 date/history combinations across two time zones. The actual shipped scanner, parser, installer command, installed-state lookup and repeated-install preservation check passed in temporary storage.

Created 28cea5d3a ([global] ai-usage: fix rollout counts and quota windows) and 8622b445b ([global] ai-usage: keep charts compact and activity complete). Both normal pre-commit and commit-message hooks passed. The optional rashin-reviewer executable is absent, so its optional stage did not run; no hook was bypassed or weakened. Fast-forwarded local unstable-dev from 3d0c497c3 to 8622b445b, preserving ai-usage-builtin at the same commit. Both tree hashes match and the Ryoku working tree is clean. Local unstable-dev is 14 commits ahead of its tracking reference (12 prior feature commits plus the two new commits).

Audited the full submission: 26 required files only, with no README, CONTRIBUTING, AGENTS, changelog, packaging or unrelated changes. Saved RYOKU_TEST_REPORT.md in this standalone module project, outside the Ryoku submission. The report distinguishes passing automated checks from unavailable fresh runtime visual verification and unrun GitHub CI. No upstream refresh, fork, remote push, PR, live deployment or package change was performed. Await the user’s consent after presenting the report before any PR step. These project records remain uncommitted; user consent covered the Ryoku implementation commits only.

## 2026-11-07 15:16 IST — Check the newly created fork base

The user reported creating methos28/ryoku and requested checking its unstable-dev branch for newer work before any PR. Attempted a read-only Git fetch from https://github.com/methos28/ryoku.git refs/heads/unstable-dev with the command-scoped gh credential helper. It failed with Could not resolve host: github.com. The web tool also could not retrieve the branch, commit list or branch API endpoint. No fresh fork head or behind count can be claimed.

Local unstable-dev remains clean at 8622b445b. Its cached original upstream origin/unstable-dev remains 3d0c497c3; local comparison gives 14 ahead and 0 behind that stale reference only, not the newly created fork. No remote was added, no merge/rebase or push occurred and no PR was opened. A successful terminal fetch of the fork branch into FETCH_HEAD is required for a fresh local ancestry comparison.

### 2026-11-07 15:23 IST — Fork fetch succeeds; branch is behind

After the user restarted Codex with additional arguments, the direct Git fetch of methos28/ryoku unstable-dev succeeded. Fetched fork head: 0749ec350 (release: bump unstable to 1.10.2). Local unstable-dev remains 8622b445b. git rev-list --left-right --count HEAD...FETCH_HEAD reports 14 local-only and 3 fork-only commits. The missing commits are c302ec734 (Fedora greeter skin fix), 454280228 (PR #743 merge) and 0749ec350 (version bump). The incoming change footprint is VERSION, two Fedora RPM specs and ryoku/lockscreen/CHANGELOG.md.

No merge, rebase, commit, push, remote configuration change or PR was performed. The Ryoku working tree remains clean. Existing passing test results apply to the previous base; bringing in these three newer commits requires another gate run before PR submission. Added this freshness finding to RYOKU_TEST_REPORT.md.

## 2026-11-07 15:25 IST — Sync and fork-target PR authorised

The user requested syncing the feature work with the new fork while retaining project files, then submitting a PR into the fork’s unstable-dev. This explicitly authorises merging the fork base, pushing the feature branch and creating the PR. The destination is methos28/ryoku:unstable-dev, not Ryoku-dev/ryoku. Keep the remote target branch unchanged; the PR head will be ai-usage-builtin. Continue excluding README, CONTRIBUTING, changelog, packaging and unrelated changes from the PR diff.

GitHub CLI authentication now succeeds. Initial Ryoku working tree is clean at 8622b445b, with both local branches at the same head. Add a named fork remote while retaining origin as upstream, fetch its current unstable-dev, merge it normally into the feature branch without rewriting existing commits, and fast-forward local unstable-dev to the result. Re-run gates on the merged tree before pushing and creating a draft PR.

### 15:26 IST — Fork base merged; gates pass

Added fork remote for methos28/ryoku while retaining origin=Ryoku-dev/ryoku. Fetched fork/unstable-dev at 0749ec350, switched to ai-usage-builtin and merged the three fork-only commits normally, without conflicts, creating e9778bb9e. Fast-forwarded local unstable-dev to the same head. The fork base is now an ancestor: 15 ahead/0 behind (14 project commits plus the sync merge).

Compared every project path against 8622b445b: no project content changed during the merge. The complete PR diff against fork/unstable-dev remains exactly 26 allowed widget/loader/collector/test/CI files. Incoming Fedora/version changes are already in the base and therefore excluded from the PR diff. No README, CONTRIBUTING, AGENTS, changelog, packaging or unrelated project edits appear.

Re-ran the fourteen Codex regressions, eight OpenCode fixture assertions, six Codex rollout assertions, cache contract, shipped-widget QML lint, widget and loader QML binding gate, delivery and WM-isolation gates on the merged tree; all passed. Preparing a draft PR targeting the user’s fork only. No direct push to either unstable-dev remote branch will be made.

### 15:30 IST — Draft fork PR created; CI exposes a fixture dependency

Normal push to fork/ai-usage-builtin succeeded, including the package-dependency and vendored-WM pre-push checks. Created draft PR https://github.com/methos28/ryoku/pull/1 targeting methos28/ryoku:unstable-dev. GitHub API confirms base/head, merged head e9778bb9e and exactly 26 required files. The target branch was not pushed or changed.

Initial GitHub AI usage CI failed at tests/ai-usage-cache.py: cache missing in its temporary output directory. The preceding collector fixtures and fourteen new regressions passed. Diagnosis: this existing contract test invokes the collector against the caller’s real OpenCode data directory rather than creating a fixture. Local runs passed because this machine has OpenCode data; a clean runner has none. Those earlier local results were real but did not establish runner independence. Fix the same already-scoped test file by constructing an isolated temporary SQLite fixture and overriding the collector data directory, then re-run it in normal and empty-home/UTC environments. No product-code or unrelated file changes are required.

### 15:31 IST — CI contract fixture fixed and pushed

Changed only tests/ai-usage-cache.py, already in the 26-file PR scope. It now creates temporary SQLite session_v2/session_message fixtures and explicitly isolates HOME and OPENCODE_DATA_DIR. Its original field/nesting/order checks remain in place. The contract passes both normally and with an empty caller HOME, missing caller store and UTC timezone. No live account/data is needed or read. Temporary storage is cleaned up.

Created 076d728bd ([test] ai-usage: isolate the cache contract fixture) on local unstable-dev through normal hooks, fast-forwarded ai-usage-builtin to it and pushed that feature branch normally. Both local branches now contain the same source and the fork base. Updated the existing draft PR #1 description with the CI diagnosis and test isolation. No new files were added to the PR diff; no README, CONTRIBUTING, packaging or changelog edits were introduced. Await the new collector CI result.

### 2026-11-07 15:32 IST — Fork PR verified; collector CI green

The updated AI usage collector workflow 42362143313 completed successfully on 076d728bd. GitHub API confirms draft PR #1 is open against methos28/ryoku:unstable-dev at 0749ec350, with ai-usage-builtin head 076d728bd and exactly 26 required files. Latest check rollup: five successful and three in progress, no failures on the latest head. Both local branches contain the fork base and all project work; the published feature branch tracks fork/ai-usage-builtin. The fork unstable-dev target was not pushed, and no PR merge was performed. Updated the local test report, PR body and plan. Project records remain uncommitted in the standalone module; the Ryoku working tree is clean.

## 2026-11-07 16:07 IST — Inspect accepted PR, missing-file report and failed jobs

The user reported accepting PR #1 but seeing failed checks and not finding the new files. GitHub confirms PR #1 merged successfully into methos28/ryoku:unstable-dev at 24b401eee4dc3230feb4d0539165ed09ddd96fa0. The version workflow subsequently advanced that branch to 674c62a3c (release 1.10.3). Fetched the fork branch and compared all project paths against tested PR head 076d728bd: no differences. The remote unstable-dev tree contains the full widget and all project work.

Verified the repository default branch is main. GitHub contents API returns the widget directory on unstable-dev, including AiUsageTile.qml, IrisCompact.qml, UsageModel.qml, components and widget.json; the same path on main returns 404. The PR targeted unstable-dev as requested, so browsing default main will not show these files. Direct link: https://github.com/methos28/ryoku/tree/unstable-dev/ryoku/shell/quickshell/inir/defaults/widgets/ai-usage. This explains the branch-specific file visibility without assuming which page the user was viewing.

Post-merge AI usage collector, QML Lint and Delivery check runs succeeded. Four other post-merge workflows failed on missing fork release infrastructure: Arch publisher 42363484099 requires R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY/R2_ENDPOINT/R2_BUCKET and GPG_PRIVATE_KEY; Void publisher 42363484122 requires the R2 fields plus VOID_REPO_SIGNING_KEY; Fedora publisher 42363484034 requires the R2 fields plus GPG_PRIVATE_KEY. Testing gate 42363483946 fails configuring the same missing R2 fields, then cannot find its Ryoku rclone remote. These are workflow configuration failures, not merge conflicts or evidence of missing module files. The older collector failure on pre-fix head e9778bb9e remains in run history but was fixed before the merge.

No source edit, new commit, push, workflow disable, secret change or branch switch was made during this inspection. Only fetched remote tracking data and appended project records. The Ryoku working tree remains clean.

### 2026-11-07 16:10 IST — Fork workflow options inspected

The user asked whether the failed checks can be resolved from our side. Re-read the four failing workflow definitions and queried their current GitHub states: all four remain enabled in methos28/ryoku. They publish signed Arch/Void/Fedora repositories or update the distribution testing pointer, and require R2/signing credentials that this development fork does not configure. The individual collector, QML, delivery and other validation workflows are separate and can remain enabled.

Proposed minimal fork-only configuration change for consent: disable testing-gate.yml, publish-repo.yml, publish-repo-void.yml and publish-repo-fedora.yml through GitHub workflow settings. This changes no repository files and prevents future runs of those distribution-publication jobs; it does not turn historical failed runs green. The alternative is provisioning the fork’s own release storage/signing infrastructure, a separate scope. No workflow, secret, branch protection or source setting was changed while answering the question.

## 2026-11-07 16:16 IST — Progress checkpoint requested by the user

The user requested recording all progress to this point. This entry consolidates the current state without rewriting earlier history. Updated PLAN.md and the test-report status to reflect the accepted PR and the pending workflow decision. This request authorises documentation updates only, not a commit, push, workflow disable or new PR.

### Delivered module work

- Codex token accounting was independently audited against raw rollouts. Current totals matched exactly; replay, archive-move and copied-rollout double-count bugs were reproduced and fixed. Activity state schema 4 records event identities; existing display-cache schema remains 3.
- Account quota windows use provider-reported percentages, durations and Unix-second resets. The recorded Free account returned 43,200 minutes; the UI shows 30d when reported rather than inventing a universal plan rule. Historical paid windows are not restored after a plan change.
- Accepted UI work includes fixed 7/30/45-day trends, full-width bars, compact zero-cost spending, refresh release and the period-label target. The Activity requirement changed from 13 weeks to 60 dates, then to the accepted full 9-by-7 grid of 63 dates ending today.
- Claude is absent from the dashboard/settings selectors. Shared support is retained for later enrichment and validation with real data. No Claude enrichment or optimisation work has begun.

### Git, deployment and PR state

- Standalone repository main and origin/main are at 47b9395. The six implementation/record commits were pushed after the user completed the initially network-blocked push from a terminal. Later project records remain uncommitted.
- The live widget and local Codex collector were deployed from tested repository sources. Earlier shell-reload attempts were blocked by socket permissions. The user exercised the desktop and provided heatmap feedback; no fresh runtime visual verification of the downstream checkout is claimed.
- Ryoku checkout: /home/methos/Projects/ryoku-unstable. Current checked-out branch is ai-usage-builtin; it and local unstable-dev are at 076d728bd. The Ryoku working tree is clean. origin points to Ryoku-dev/ryoku and fork points to methos28/ryoku.
- Fork PR https://github.com/methos28/ryoku/pull/1 was opened, then accepted and merged by the user at 24b401eee. The last fetched fork unstable-dev is 674c62a3c after its automatic release bump to 1.10.3. Local branches have not been advanced to those two later commits. All project paths on the merged fork are byte-identical to the tested PR head.
- The submitted diff contained exactly 26 required widget, loader/installer seam, collector, test and CI files. No README, CONTRIBUTING, AGENTS, changelog, packaging or unrelated edits were submitted. No upstream PR to Ryoku-dev/ryoku has been created.

### Validation and remaining decisions

- Local checks passed: fourteen downstream regressions, eight OpenCode assertions, six Codex rollout assertions, cache contract, QML lint/bindings, delivery and WM isolation. Extra checks covered 168 trend/heatmap date-history cases, loader discovery/install/reinstall behaviour, and normal commit/push hooks.
- GitHub first exposed a non-isolated cache-contract test. It was fixed in 076d728bd using temporary SQLite fixtures, then verified with an empty caller HOME/store and UTC. Collector, QML and delivery workflows passed on the merged fork.
- Four distribution-release workflows failed because the fork lacks R2 publishing/signing configuration. Proposed fork-only settings change: disable publish-repo.yml, publish-repo-void.yml, publish-repo-fedora.yml and testing-gate.yml while keeping validation workflows enabled. User has not approved this change; all four remain enabled as last checked. Historical failed runs would remain visible after disabling future runs.
- Permanent UI fixtures and click-input backlog remain in PLAN.md. Fresh final visual sign-off and real Claude data are still pending. Keep all new records outside the Ryoku submission, and request fresh consent for any new commits, PRs or workflow-setting changes beyond the already completed work.

## 2026-11-07 16:32 IST — Fork history reset and module re-landed as one commit

The user asked to remove PR #1 and every commit it added from the fork branch, with no revert commit and no visible history, then to replace the local Ryoku checkout with a clone of the fork, sync the fork to the original repository, and commit the module files to the fork's `unstable-dev`. The destructive scope was confirmed in chat before execution.

Backups made before deleting the old checkout: `~/.local/share/ryoku/ai-usage-backup/ai-usage-0749ec350-076d728bd.patch` (the tested 26-file diff) and `ryoku-unstable-mirror.git` (a local mirror of `/home/methos/Projects/ryoku-unstable`, including `ai-usage-builtin` and the old `unstable-dev`).

Actions, in order:

1. Fork remote `methos28/ryoku:unstable-dev` at `674c62a3c` was force-pushed to upstream `0749ec350` (`Ryoku-dev/ryoku:unstable-dev`). This removed 18 commits from the branch: the 12 earlier project commits, `28cea5d3a`, `8622b445b`, `e9778bb9e`, `076d728bd`, merge `24b401eee` and bump `674c62a3c`. No revert commit exists.
2. `/home/methos/Projects/ryoku-unstable` was deleted and replaced with a fresh clone of the fork at the same path. `main` remains `f7197d72d` and equals upstream `main`; `origin` is the fork and `upstream` is `Ryoku-dev/ryoku`.
3. The tested patch was applied to `0749ec350`. The staged index tree `3a4fe3908` is byte-identical to the tested tree of `076d728bd`, and the diff contains exactly the same 26 files.
4. Repo hooks were enabled with `core.hooksPath .githooks`. Commit `2877b9469` (`[global] ai-usage: add the AI usage widget`) was created with normal pre-commit and commit-msg hooks, both passing.
5. Gates on the committed tree: `tests/opencode-usage.sh`, `tests/codex-usage.sh`, `tests/ai-usage-cache.py`, `tests/codex-usage-regression.py` (14 tests), and `bin/ryoku-dev-lint-qml` on the shipped widget. All passed. Delivery and WM-isolation checks ran inside the pre-commit hook and passed.
6. Pushed normally to `fork/unstable-dev`. Remote head is `2877b9469`. GitHub compare against `Ryoku-dev:unstable-dev` reports ahead 1, behind 0, 26 files, and the widget directory is present on the branch.

State and limits:

- Fork `unstable-dev` now has exactly one commit on top of upstream, with no trace of the previous project commits in its history.
- PR #1 remains merged on GitHub and still shows head `076d728bd`; a merged PR cannot be un-merged or deleted. Its commits are no longer on the branch.
- The branch version is again 1.10.2, because the 1.10.3 release bump was among the discarded commits.
- No PR was opened against `Ryoku-dev/ryoku`; the user said they will create the pull request for their changes.
- No live widget, collector, cache or desktop state was changed in this task. The live widget remains identical to the standalone module tree.
- The old local branches `ai-usage-builtin` and the previous `unstable-dev` exist only in the backup mirror.

Remaining: user opens the PR, fresh visual sign-off, Claude enrichment and real-data validation, permanent UI fixtures, click backlog, fork workflow decision.

## 2026-11-07 16:44 IST — Recreated fork, module landed on unstable-dev only

The user deleted and recreated `methos28/ryoku`, then asked for only the module files required to make it work, no new branch, and a commit pushed straight to their fork's `unstable-dev`. The naming rule was also fixed in `AGENTS.md`: "my ryoku repo" means `methos28/ryoku`, and "original ryoku repo" means `Ryoku-dev/ryoku`, which stays read-only unless named explicitly.

- Recreated fork verified before work: `unstable-dev` at upstream `0749ec350`, `main` at `f7197d72d`, no module files. The previous fork commit `2877b9469` is preserved only in the local backup mirror as `relaunch-2877b9469`.
- Fresh clone replaced `/home/methos/Projects/ryoku-unstable`, with `origin` = fork and `upstream` = `Ryoku-dev/ryoku`.
- The same tested 26-file patch was applied to `0749ec350`; the staged index tree `3a4fe3908` is byte-identical to the tested tree of `076d728bd`. No extra files, no README, CONTRIBUTING, changelog or packaging edits.
- OpenCode and Codex remain the only agents in `agentCatalog` and in `widget.json` tool options. A third agent appears only as shared labels, support code and comments, with no menu entry.
- Gates passed on the staged tree: `tests/opencode-usage.sh`, `tests/codex-usage.sh`, `tests/ai-usage-cache.py`, `tests/codex-usage-regression.py` (14 tests), and `bin/ryoku-dev-lint-qml` on the shipped widget. Delivery and WM isolation passed inside the pre-commit hook.
- Commit `f0c5a4f0f` ([global] ai-usage: add the AI usage widget) was created directly on `unstable-dev` with normal hooks, no feature branch, and pushed normally. Remote head is `f0c5a4f0f`.

No live desktop files were changed in this task. The user will open the pull request. Branch version remains 1.10.2. The clone is clean and equal to its remote.

## 2026-11-07 16:53 IST — Phase 7 optimisation pass

The user asked for code optimisation as the next main task. Scope followed PLAN Phase 7: remove duplication, split large QML, optimise collector scans. No behaviour or visual redesign was intended.

Baseline measurements before editing: Codex `history_records()` 0.0357s and `scan_activity()` 0.024s on 8.9 MB of rollouts; OpenCode `load_messages(730d)` 0.207s for 5,795 rows; `period_stats` 0.0187s for all five periods. Runtime was already small, so the pass targeted duplication and line work rather than a hot loop.

Changes, applied to the primary module first:

1. New `ai-usage/components/AiUsageMenu.qml`: one dropdown implementation with options, current marker, hover, menu width, row height and a `picked` signal. The two near-identical menu blocks in `IrisCompact.qml` (agent and period) were replaced by two instances and one shared veil. `IrisCompact.qml` fell from 601 to 470 lines; the period menu keeps its 158 px width, 28 px rows and non-bold current row.
2. Removed dead properties `periodNoun`, `periodTokens` and `periodCacheRate` from `IrisCompact.qml`. `periodCost` stays because `hasSpend` uses it.
3. `collector/codex-usage`: `history_records()` now rejects lines whose event type cannot matter with substring tests before `json.loads`, and stops scanning `response_item` lines once the session title is known. The per-session `now_epoch()` call was hoisted out of the loop. Output is byte-identical to the previous collector for all 258 messages and 5 sessions; runtime fell from 0.0357s to 0.0331s on the current 8.9 MB data, and the gap grows with tool-output-heavy rollouts.

Evidence: `./test/run.sh` 15 tests pass; Ryoku QML lint and the binding gate pass on the module and the new component; raw `qmllint` exits clean. The same changes were ported to the fork checkout under `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage` and `ryoku/rashin/usage/codex-usage`, where the four module gates, shipped-widget QML lint and binding gate also pass.

Status: uncommitted in both trees. No live widget copy was made, because the menu component needs one on-screen check after a shell reload. No commit, push or PR was performed. Deeper options not taken: an incremental history cache and shared collector helpers, both of which need separate approval and heavier tests.

## 2026-11-07 16:57 IST — Progress checkpoint

Recorded at the user's request. This entry changes no code, live file, branch or remote.

Delivered today:

- The original fork was reset, deleted and recreated as `methos28/ryoku`. The module was re-landed directly on `unstable-dev` as `f0c5a4f0f` on top of upstream `0749ec350`, with OpenCode and Codex only. The branch was pushed and matches its remote.
- The local checkout at `/home/methos/Projects/ryoku-unstable` is the recreated fork, with `origin` = fork and `upstream` = `Ryoku-dev/ryoku`.
- Phase 7 optimisation is prepared: shared `AiUsageMenu.qml`, `IrisCompact.qml` down from 601 to 470 lines, three dead properties removed, Codex rollout line prefilter and hoisted clock. Output is identical and all gates pass. It remains uncommitted in both trees.

Current Git state:

- Module project `main` is `47b9395`. Working tree: `AGENTS.md`, `PLAN.md`, `PROJECT_LOG.md`, `ai-usage/IrisCompact.qml` and `collector/codex-usage` modified; `ai-usage/components/AiUsageMenu.qml`, `RYOKU_PR_BODY.md` and `RYOKU_TEST_REPORT.md` untracked.
- Fork checkout `unstable-dev` is `f0c5a4f0f`, equal to `origin/unstable-dev`. Working tree: `ryoku/rashin/usage/codex-usage` and the shipped `IrisCompact.qml` modified, `components/AiUsageMenu.qml` new.
- Live widget `~/.config/inir/widgets/ai-usage` is still the pre-optimisation module. The optimisation was not copied live and the shell was not reloaded.

Verification on the prepared trees: 15 module tests; 14 fork regressions; OpenCode and Codex fixtures; cache contract; shipped-widget QML lint; binding gate. All passed. Raw `qmllint` exits clean on the changed QML.

Backups and references: `~/.local/share/ryoku/ai-usage-backup/` holds the tested 26-file patch, a mirror of the old checkout with `relaunch-2877b9469`, and the older branch refs.

Open items, in order:

1. Commit the optimisation on the fork's `unstable-dev` after explicit approval.
2. Reload the shell, check both dropdowns and deploy the tested files to the live widget.
3. User opens the pull request from the recreated fork.
4. Claude collector enrichment plus real-data validation before it returns to the menus.
5. Permanent trend/heatmap/spend/period fixtures and the click-input backlog.
6. Decision on the four fork release workflows that fail without R2 and signing credentials.

## 2026-11-07 17:00 IST — Today caption overflow in the Limits card

The user reported the `tokens today · incl. cached` caption running past the card edge in the Codex primary row, with a screenshot. Cause: the metric and the caption shared one `Row` with no width limit, so `45.51M` plus the caption exceeded the card's inner width at the default 480 px module width.

`AiUsageLimitsCard.qml` now stacks the metric and caption in a `Column`. The caption takes the card width, stays on one line and elides if the card is very narrow. The card grows about 8 px, and the primary row already matches the tallest card. No other card or collector changed.

Evidence: QML lint and the binding gate pass in the module and the fork; raw `qmllint` on the changed file exits clean. Collector tests are unaffected and were not rerun.

Status: uncommitted in the module and the fork. Only `components/AiUsageLimitsCard.qml` was copied to the live widget for the user's reload. The rest of the live widget remains pre-optimisation. The shell was not reloaded from this session, so the on-screen result is pending a user reload.

### 17:08 IST — Compact caption correction

The user rejected the caption line under the metric: it made the primary row taller than the Claude reference. They asked for the two caption phrases stacked beside the number instead.

`AiUsageLimitsCard.qml` now keeps the metric and a two-line caption in one `Row`: `tokens today` above and `(incl. cached)` below, both 10 px muted text, vertically centred on the metric. The row height is the metric's height again, so the card and the primary row return to the original height. Caption lines take the remaining width and elide at very narrow cards.

Evidence: module `qmllint`, the fork binding gate and the shipped-widget QML lint all pass. The changed file was copied to the fork and to the live widget. Visual check still pending a shell reload.

### 17:11 IST — Caption width binding fix

The first stacked version showed no caption at all. The `Row` had no explicit width, so the caption column's width, computed as the row width minus the metric width, fed back into the row's own implicit width and collapsed to zero. The row now takes `parent.width` explicitly; the column gets the real remainder and the caption renders. Lint and binding gates pass, and the file is copied to the fork and the live widget. Reload still required.

## 2026-11-07 18:40 IST — Optimisation and caption fix committed and pushed

The user asked to commit the latest changes to the remote "my ryoku repo", which the project rules define as `methos28/ryoku`.

Two commits were created on `unstable-dev` with the repository hooks enabled:

- `31d36bef9` `[global] ai-usage: share one dropdown and trim rollout scan`: `AiUsageMenu.qml`, the `IrisCompact.qml` menu removal and the Codex rollout prefilter. Three files, 119 insertions, 148 deletions.
- `f9b7a7dc1` `[global] ai-usage: keep the today caption inside the card`: the stacked caption beside the metric and the explicit row width. One file, 23 insertions, 6 deletions.

Gates before committing: OpenCode fixtures, Codex fixtures, cache contract, 14 Codex regressions, QML lint and binding gate. All passed. Delivery, WM isolation, QML binding and the slop scan ran again inside the pre-commit hook and passed.

Pushed `f0c5a4f0f..f9b7a7dc1` to `origin/unstable-dev`. Remote head is `f9b7a7dc1`. GitHub compares the branch to `Ryoku-dev:unstable-dev` as ahead 3, behind 0, 27 files: the 26 module files plus `AiUsageMenu.qml`.

Deployed the committed optimisation to the live machine: `~/.local/bin/codex-usage` now matches the fork collector byte for byte; `IrisCompact.qml`, `components/AiUsageMenu.qml` and `components/AiUsageLimitsCard.qml` were copied to `~/.config/inir/widgets/ai-usage`. The live widget still differs from the fork only in `UsageModel.qml` and `widget.json`, which carry the standalone collector path and manifest, as before. Shell reload and the menu/caption visual check remain the user's step. No pull request was opened; the user said they will create it.

## 2026-11-07 18:55 IST — Read-only progress review: standalone/live difference recorded

The user requested a progress review and familiarity with the current module. Read the complete project log and plan, then checked both working trees and the live widget before any implementation work.

The fork checkout is clean on `unstable-dev` at `f9b7a7dc1`, matching its locally cached tracking reference. The standalone repository remains on `main` at `47b9395`, with the previously prepared optimisation, caption and project-record changes uncommitted, plus the untracked menu and report files. No fresh remote query is implied by these local checks.

`diff -rq ai-usage /home/methos/.config/inir/widgets/ai-usage` reports one difference: `IrisCompact.qml`. Its live `activeTool` binding immediately falls back to an available supported agent when the stored choice is unavailable; the standalone binding only handles the no-cache case. The live comment also uses the downstream wording. Earlier port records explicitly identify this as a downstream-specific fallback. This qualifies the source/live equality expectations: the live file contains downstream behaviour that is absent from the primary source, rather than an unexplained local edit.

Recorded the difference before proceeding with further read-only checks. No code was reconciled, copied or reloaded. This log entry is uncommitted. Current visual sign-off, fresh remote/PR state and the final test results of this review remain unverified at this point.

### 18:58 IST — Progress review results and current remote-state correction

Completed the read-only review of the widget shell, shared menu, cache reader, availability probe, collector entry points, rollout identity handling, installer and timer wiring.

Verification run in this review:

- Standalone `./test/run.sh` passed: six OpenCode tests and fifteen Codex tests. Raw Qt6 lint still exits zero with warnings.
- Fork `tests/opencode-usage.sh`, `tests/codex-usage.sh`, `tests/codex-usage-regression.py` (fourteen tests) and `tests/ai-usage-cache.py` passed.
- Ryoku QML lint and the QML binding gate passed on the standalone widget. `git diff --check` passed.
- `cmp` confirms the primary, fork and live Codex collectors are identical, and the live OpenCode collector matches the primary source. Live widget versus fork differences are the expected standalone `UsageModel.qml`, `widget.json`, and the standalone-only `test/` directory. The sole primary/live QML difference remains the recorded downstream agent fallback.
- Live caches at 18:55 IST: OpenCode `storage+v2`, 48 days, ten sessions; Codex `rpc`, Plus, two days, six sessions, reported 300/10,080-minute windows. Codex display schema is 3 and activity-state schema is 4. Claude remains a stale demo cache and is excluded from menus. The installed timer is configured for five minutes; no timer or collector was started by this review.

New finding: `ai-usage/components/AiUsageMenu.qml:70` uses `MaterialSymbol`, but its import list omits `inir.modules.common.widgets`, the module whose `qmldir` exports that type. The same file is deployed and committed in the fork. Direct Qt6 lint reports `MaterialSymbol was not found. Did you add all imports and dependencies? [import]`, while returning zero. The current Ryoku fatal-warning filter does not match this diagnostic, explaining why passing gates do not settle runtime loadability. Treat this as an unresolved dropdown/component load risk pending a focused fix and runtime check; no live failure or successful visual reload is claimed. No code was changed during this review.

Fresh GitHub API checks confirm fork `unstable-dev` at `f9b7a7dc1e00ed1ac17e0223805cb09024b6b2f7`, no open PRs, zero registered Actions workflows and zero Actions runs. The four release-workflow failures recorded before fork recreation belong to the deleted fork, not current runs on the recreated repository. PLAN.md's opening workflow-failure statement and Phase 4 branch references are historical and should not be read as current state. No workflow was disabled or changed, and no remote branch was mutated.

Remaining work: address the menu import risk; deliberately reconcile the primary/live fallback difference; obtain visual sign-off on menus, caption and row height; add the planned permanent UI fixtures and reproduce click hypotheses; enrich and validate Claude before enabling it; update README screenshots for user inspection; user creates the new PR when ready. Deeper optimisation remains a separately requested task. Only these append-only review notes changed, uncommitted; no implementation edits, deployments, reloads, commits or pushes occurred.

## 2026-11-07 19:05 IST — Module fixes and official-tree compatibility audit authorised

The user requested all necessary module fixes and an audit against the official `https://github.com/Ryoku-dev/ryoku` tree for changes that could affect other widgets. This authorises scoped implementation, tests and live delivery after gates; it does not authorise commits, pushes, upstream writes or unrelated desktop changes.

Fetched the official `unstable-dev` and `main` references read-only: `0749ec35005cdae3b5c925eb91c32a6904a998d5` and `f7197d72de8a21e44b0bea922bdd915f28f6b327`. The fork has 27 changed paths versus its official unstable base: 22 additions and five modified pre-existing files. Shared modifications are `CustomWidgets.qml`, `WidgetManagerPanel.qml`, `codex-usage`, `opencode-usage`, and the AI collector workflow; no theme, common widget primitive, compositor, boot, packaging or global settings changes are part of the module diff.

Confirmed additional faults before editing: `AiUsageTile.qml` reads `root.usage` even though `usage` is a QML id, not a root property; the shared loader removed upstream's `installExample()` entry point instead of retaining an additive compatibility wrapper. The new shipped installer also interpolates paths/id into shell code and lacks an in-flight guard. Scope the fixes to module imports, tile bindings/valid quota presentation, primary-source agent fallback, backward-compatible and argument-safe shipped installation, plus focused runtime/compatibility tests. Preserve upstream's existing discovery/configuration contracts and other user widget files. All changes remain uncommitted until explicit later approval.

### 19:18 IST — Source fixes and focused regression checks

Fixed the missing common-widgets import in both menu copies. Corrected desktop-tile reads to the `usage` QML id, showing the actual first reported quota window for a plan and local token counts when no quota exists. Added the already accepted downstream saved-agent fallback to the primary `IrisCompact.qml`; the prior primary/live behaviour difference is now deliberately reconciled in source.

The fork's shared loader again exposes `installExample()`, forwarding to `installShipped("example-widget")`. Shipped installation rejects invalid ids and in-flight replacement, passes paths as shell arguments, copies into a temporary sibling directory and publishes without replacing existing user folders or symlinks. Removed the panel's premature reload; the installer completion already owns that reload. Upstream discovery, widget configuration, create/remove code and common visual primitives are unchanged.

Added primary/fork UI regression checks using the actual QML expressions for 7/30/45-day trends, the complete 63-day heatmap, seconds/milliseconds, supported-agent fallback and desktop metric values. The Quickshell test compiles every module component in an isolated HOME/runtime without creating the services. An initial attempt to instantiate the real menu against an absent isolated daemon crashed inside Quickshell with `std::bad_function_call`; compilation-only checks avoid this environment failure and do not claim visual verification. The five primary UI tests pass, including real component compilation.

The standalone cache contract was still dependent on this user's real store, unlike its already fixed fork copy. Ported the existing isolated SQLite fixture into the primary test and added it plus UI tests to `test/run.sh`. Added fork compatibility tests for the original loader API, installation with literal shell-special paths, existing user content/symlinks, copy failure, and real collector output through the unchanged shared `AiUsage.qml` readers. The first shared run exposed JavaScript regex coercion accepting null as the string "null"; added an explicit string-type guard and rerunning. CI now watches the two shared loader/panel paths and invokes these checks. No global lint filter, upstream hook, packaging file, installed shared shell file, commit or remote was changed.

## 2026-11-07 19:20 IST — Fixes delivered and official-tree compatibility audit complete

Timestamp correction: the earlier source-fix checkpoint's 19:18 heading was an estimate; those source edits and early tests were completed before the 19:16 gate checkpoint. This entry uses the current machine clock.

All final checks passed. Primary: six OpenCode tests, fifteen Codex tests and five UI tests, plus the isolated cache contract. Fork: fourteen Codex regressions, five UI tests, five shared-compatibility tests, OpenCode and Codex shell fixtures, cache contract, QML lint, QML binding gate, delivery and WM isolation. The standalone contract also passes with an empty caller HOME, absent store and UTC. Temporary negative controls restore the old menu and tile one at a time; the new tests reject both.

The offscreen engine cannot compile the widget manager's PanelWindow-backed context menu because no Wayland backend is loaded. The permanent default check compiles all module files and the shared loader offscreen. `AI_USAGE_QML_PLATFORM=wayland python3 tests/ai-usage-widget.py` additionally compiled the actual widget manager successfully using the real display with an isolated HOME/config/runtime and no service creation. No production code was changed to accommodate the test environment.

After the gates, backed up and installed only `AiUsageTile.qml`, `IrisCompact.qml` and `components/AiUsageMenu.qml`. Backup: `~/.local/share/ryoku/ai-usage-backup/fixes-20261107-191709/`. `diff -rq` confirms the entire live widget equals the primary source. `ryoku-shell reload` succeeded at 19:17 IST; `ryoku-shell status` reports `shell: running`, with the new instance `w3y4myw4ot`.

Opened the desktop page by IPC and inspected a local screenshot: Codex has the compact stacked Today caption, reported 5h/7d windows, sessions, and integrated `$0.00` monthly spending. The new instance log contains no AI-usage component load/binding errors. Existing unrelated shell warnings remain outside this module fix. Closed the island after inspection. Final user visual approval and live dropdown clicks remain open; `/dev/uinput` is absent, so no pointer-input reproduction is claimed. The screenshot is a local diagnostic, not a README or published asset.

Created `RYOKU_COMPATIBILITY_REPORT.md` with the five modified pre-existing paths, exact official reference hashes, fixes, tests, live ownership audit and verification limits. Updated PLAN.md to remove obsolete fork workflow failures/branch references, mark the completed calendar/unit fixtures and successful reload, and retain the real pending items. Live shared loader/panel/cache-reader and visual primitives match official stable; the existing AI-panel text-anchor overlay is preserved. Shared loader compatibility fixes are only in the fork source, not overlaid onto installed Ryoku files.

No commits, staging, pushes, upstream writes, workflow setting changes or PRs occurred. Claude remains held out. Current source changes and records remain uncommitted for user review.

## 2026-11-07 19:26 IST — Spending billing capability reverified on user request

The user asked whether topping up an API balance and using Codex with that API key updates Spending. Verified that the current implementation does not provide this capability. `collector/codex-usage:861` assigns `cost: 0.0` to every token record. Day/period/session costs aggregate that zero; no pricing calculation, billed-cost request, prepaid balance read or top-up event is collected. `IrisCompact.qml:113` only sums the current month's `_days[].cost`. The earlier successful `$0.00` rendering check is not evidence of billing accuracy.

Read-only live-cache check: Codex is currently rpc/Plus with all daily and period costs zero. OpenCode has five nonzero-cost days and local period costs, read from its own stored message costs. Those OpenCode amounts are not an account-balance ledger. An isolated no-network regression fixture recorded 3,000 Codex tokens and still published day and all-period costs of zero, confirming the code path without spending money or touching live data.

Official documentation fetched and read: https://learn.chatgpt.com/docs/auth confirms API-key Codex usage is billed through the OpenAI Platform account at API rates; https://learn.chatgpt.com/docs/app-server identifies `account/rateLimits/read` as ChatGPT rate limits; https://developers.openai.com/api/reference/resources/admin/subresources/organization/subresources/usage/methods/costs documents the organization Costs API. These do not make the module's current rate-limit/cache reader an API billing integration. A top-up and usage expenses are separate concepts, and neither top-up changes nor remaining balances are read by this module.

Updated PLAN.md and the compatibility report to state this limitation explicitly. No implementation, live file, billing credentials, account setting, cache, commit or remote was changed. Unknown Codex cost currently appears as `$0.00`; presenting unavailable costs truthfully and adding actual or clearly labelled estimated API spending are follow-up implementation work, not already verified features.

## 2026-11-07 19:30 IST — Native Codex usage fields versus generated widget cache clarified

The user asked whether Codex's default cache indicates expenditure. Inspected native token_count records under ~/.codex/sessions and archived_sessions without printing message text, keys or account details. More than 300 inspected events expose total_token_usage, last_token_usage, last_usage_includes_reasoning and model_context_window. No cost/spent/price/billing/USD field was found in those token event payloads.

Additional detail: native rate_limits snapshots do include optional credits with has_credits, unlimited and balance. Observed Free snapshots have balance null and Plus snapshots have balance "0", with has_credits false. Official https://learn.chatgpt.com/docs/app-server calls these remaining workspace credit details in the ChatGPT rate-limit surface; they are not evidence of an OpenAI Platform prepaid API balance or an expense ledger. The collector currently drops those credit fields during bucket normalization.

Clarification to the prior answer: some native credit-status information is available; the generated ~/.cache/codex-usage.json does not preserve it. This cache is written by our collector rather than being a native Codex billing record. Native token usage, remaining workspace credits and actual billed API expense are separate data. The current cost: 0.0 records cannot tell whether a user incurred charges. Only this append-only diagnosis was changed; no implementation, live file, account, cache, commit or remote was modified.

## 2026-11-07 20:31 IST — Local-only spending approach and collector constraint

The user explicitly prefers existing local Codex data and does not want additional Python collection scripts. The user also excluded shared-key attribution policy from our scope. Record that constraint and do not keep proposing per-key isolation or a separate billing collector as the default design.

Read-only verification: native rollout token_count events contain input_tokens, cached_input_tokens, cache_write_input_tokens, output_tokens, reasoning_output_tokens and total_tokens; turn contexts identify the model. The existing collector already processes the relevant per-event token deltas. ~/.codex/models_cache.json has model metadata but no price/cost fields. Read-only state_5.sqlite schema inspection found thread model/provider/tokens_used fields, with no billing/cost/balance columns; no billing/pricing cache file names were found under ~/.codex/cache. These observations establish the available local data on this machine, not a guarantee about every future Codex version.

Best fit for the stated design: extend the existing collector/codex-usage to calculate explicitly labelled API-cost estimates using recorded token categories and an appropriate locally cached price table, then publish cost values through the existing day/session/period cache fields. No additional collector process or Python script is required. Correct model/pricing/processing-tier handling is necessary; unsupported pricing must stay unavailable. Exact billed charges, account adjustments, prepaid balances and top-ups cannot be extracted from the local records inspected. Official API pricing was fetched from https://developers.openai.com/api/docs/pricing and its separate token-category rates support this calculation approach.

The prior separate-collector recommendation was an option for authoritative remote billing, not a requirement for a local estimate. No cost implementation, live change, commit or push was performed in this feasibility turn.

## 2026-11-07 20:34 IST — Keeping local spending estimates compatible with price changes

The user asked how changing model prices would be handled. Proposed a price-cache refresh inside the existing collector, with a daily refresh interval, optional refresh on an unknown model, validation and last-known-good offline fallback. No additional Python collector or billing access is required for that approach. A machine-readable third-party catalog such as Models.dev exposes model/pricing JSON; it can lag provider updates and must not be described as authoritative OpenAI billing. Official OpenAI pricing remains the reference. Verified Models.dev's documented JSON endpoints and OpenAI's Models API schema; the latter does not return price fields.

Retain dated pricing versions and known effective dates rather than applying today's price to all historical activity. Observation time alone does not prove a price's actual effective date; uncertain historical rates remain labelled estimates. Match token categories and available model/tier/context metadata, preserve the last valid cache on refresh failure, and show unavailable prices instead of zero. Local usage calculation stays local; discovering price changes needs occasional external price data or updated shipped pricing. This is design guidance only, with no pricing feed, dependency, implementation or live change added.

## 2026-11-07 20:40 IST — Recommendation when choosing billing access versus price estimation

The user asked for an opinion after noting both approaches need occasional internet access and historical rate changes complicate estimates. Recommendation for actual spending is the official organization Costs API, integrated into the existing collector with a local last-successful cache. This avoids maintaining historical price tables. It is a recommendation rather than an approved implementation decision; the prior no-extra-Python-collector constraint still applies, and shared-key attribution remains out of scope.

Important access correction: this is not a ChatGPT model request using the ordinary Codex model key. The documented Costs API uses an Admin API key; the official Admin API guide specifies a separate administrative credential. Its daily reported cost buckets can drive monthly Spending, but this endpoint is not a remaining prepaid balance/top-up ledger. If billing access is unavailable, the app must say unavailable rather than fabricate zero or silently substitute estimates. Local token-based estimates remain possible if zero billing setup becomes the stronger requirement, but should be explicitly labelled and would retain pricing-maintenance uncertainty.

Read official Costs and Admin API documentation again in this turn. No implementation, credentials, account action, live change, commit or push was performed.

## 2026-11-07 20:54 IST — Credential/RPC audit and necessary collector hardening

The user requested verification that usage-limit RPC reuses their login safely and asked what protections exist. No billing integration or new credential was requested. The earlier authorisation to fix necessary module faults applies to the concrete hardening gaps found in this audit; do not add billing access or alter login configuration.

Read-only findings: Codex login status identifies ChatGPT; the live cache is rpc/Plus. Source, fork and live collectors initially matched. The collector launches /usr/bin/codex with argument-list Popen, read-only sandbox, never approvals, private stdin/stdout pipes and discarded child stderr. It requests initialize, account/read and account/rateLimits/read; it opens no network listener and sends no model task. Codex itself handles its saved login and any authenticated network request. Our Python code does not open auth.json or copy the returned account object into the published cache; only its plan fallback is used. The account result may contain email in process memory, but it is not published. The cache contains no credential-named fields. No credential values or auth-file contents were printed or read for this audit.

Permissions observed: home and .cache are 0700; auth.json is 0600. Usage/activity files were 0644 inside those private parent directories, so this was not evidence of exposure to other users on this machine. Still, the writer should enforce 0600 for portability. Also found initialization-failure paths that returned before child cleanup, and readline could wait beyond the intended timeout on a partial JSON line.

Primary collector fixes, then ported deliberately to the fork: explicitly select stdio transport; put all child request paths under one cleanup block, wait after terminate/kill and close pipes; enforce monotonic deadlines with bounded incremental frame reads; reject protocol errors without printing provider error bodies; write caches atomically through random 0600 temporary files with failure cleanup. No cache-schema or quota-calculation change was intended.

Added seven tests to the existing Codex regression file, with no new collector script. Coverage includes fake credential canaries excluded from argv/cache/error logs, exact RPC method sequence, explicit stdio, failed/closed initialization and rate-limit cleanup, incomplete-frame deadlines, buffered frames, response-size bounds, private file modes and atomic publish failure. The fake server and credentials live only in temporary test directories and make no network calls. Initial new regression run passed its displayed tests; full gates are running before live delivery. All changes are uncommitted; live collector not yet replaced at this checkpoint.

## 2026-11-07 20:58 IST — RPC hardening gates and live verification complete

Primary gates pass: six OpenCode, twenty-two Codex and five widget tests (33 total), plus the cache contract. Fork gates pass: twenty-one Codex, five widget and five shared-compatibility tests (31 total), OpenCode/Codex shell fixtures, cache contract, QML lint/bindings, delivery and WM isolation. Seven new security/lifecycle regression tests use only temporary fake credentials and a fake server. Both source copies match. No existing accounting or quota fixture regressed.

After passing gates, backed up the old live collector to ~/.local/share/ryoku/ai-usage-backup/rpc-security-20261107-205553/codex-usage and atomically installed the primary collector at ~/.local/bin/codex-usage. No QML change or shell reload is needed because the next collector invocation reads the new script.

The initial live verification in the restricted execution sandbox could not initialize Codex. A captured startup-only diagnostic, without account RPC or raw diagnostic output, confirmed exit 1 and a read-only-filesystem failure. The collector correctly fell back to local rollouts and published 0600 caches. Requested the required execution-sandbox escalation with that explicit reason; the user approved the named collector command prefix. One normal quota refresh outside the sandbox succeeded with no error output. The live cache is again rpc/Plus, and both usage/activity caches are mode 0600. The auth file remains mode 0600. No auth-file contents, token values or raw account response were printed.

Verified data path: quota percentages/reset windows come from the authenticated Codex app-server, while Sessions/Now activity comes from local rollout records. Codex uses its saved ChatGPT login; the widget does not receive a new billing credential. The collector requests only initialization/account metadata/rate limits, explicitly over stdio, and does not create a model turn or expose a TCP/WebSocket listener. No credential export path was found in the audited collector/cache flow. This is scoped verification, not a guarantee about all code running under the user's account or every Codex internal network behavior.

No billing integration, new Python collector, new API key, auth-setting change, commit, push or upstream mutation was added. New hardening code, tests and records remain uncommitted in both repositories.

## 2026-11-07 21:27 IST — User proposes a daily spending ledger with daily price snapshots

The user proposed keeping spending separated by day within each month: fetch fresh model prices daily, apply that day's prices to usage from that day, and accumulate a monthly total without repricing older days. They suggested a separate JSON/data file containing the spending records. This is a design proposal for feedback, not an instruction to implement it in this turn.

Recommended form: the existing Codex collector owns one persistent monthly ledger, for example ~/.local/state/ai-usage/spending-2026-11.json. Store each day's selected price snapshot, price source/fetch timestamp, per-model token-category totals, estimated daily cost and coverage/status. Use persistent state rather than disposable cache because lost historical price snapshots cannot necessarily be recovered. New data files do not require another Python collector.

Attribute each usage event to its local calendar day, including when a session spans midnight. Recompute the current day's subtotal from deduplicated usage or apply verified new-event deltas; never add the same cumulative session total on each poll. Preserve old days' chosen price snapshots. Late-arriving usage can update an older day's subtotal using that older snapshot, so freeze rates rather than forbidding all corrections. A missing daily price snapshot must remain visibly unavailable/stale, not silently create zero. Daily sampling remains a labelled estimate if provider prices change within the day or a historical effective date is unknown.

No new ledger file, implementation, price download, credential, live change, commit or push was created. Only this design record was appended.

## 2026-11-07 21:35 IST — Daily local spending estimates authorised for live preview

The user approved implementing the daily spending ledger and requested a live preview, using their ChatGPT Plus account with no wallet balance. They explicitly require a polished compact Codex-only label and preserved alignments. This authorises primary-source implementation, required tests and live delivery, not commits, pushes, billing access or new credentials. The existing collector remains the single collection script.

Implementation decision: publish a separate `_spending` estimate summary in the existing usage cache and keep private monthly ledgers under ~/.local/state/ai-usage. Save daily price snapshots from the public Models.dev OpenAI catalog, retain past snapshots, deduplicate event identities, retain already seen spending events, and split overnight sessions by event date. Rates are Standard API-equivalent assumptions, not Plus charges. Today's first observed prices cannot establish yesterday's prices: older days without saved snapshots remain unpriced and the displayed month is explicitly partial. This is recorded before implementation, rather than silently backdating today's rates.

The label will be `Est. API cost` for Codex only, with the same row height and a tooltip explaining Plus, daily coverage and freshness. Other agents retain Spending. No extra explanatory row is intended. Unknown price coverage must remain unavailable/partial rather than fake zero. Refresh uses a fixed public HTTPS catalog, no Authorization header, no login credentials, bounded reads and no redirects. Tests isolate state and disable live price fetching by default.

## 2026-11-07 21:54 IST — Daily estimate preview delivered and live alignment verified

Implemented in the primary repository only, then installed live after gates. The fork is intentionally unchanged for this preview. No commit or push is authorised.

Collector changes: the existing codex-usage script now fetches the fixed public Models.dev OpenAI pricing catalog without credentials, proxies or redirects; validates and bounds the response; snapshots rates per local date; stores monthly 0600 ledgers under ~/.local/state/ai-usage; retains deduplicated event identities and token categories; applies per-request context tiers and cache-write rates without adding reasoning output twice; preserves earlier snapshots and late-arriving usage; retains already observed events when rollouts disappear; marks missing/unsupported/stale pricing. A nonblocking collector lock protects the ledger/cache transaction. It still publishes legacy cost fields as before; `_spending` is a separate API-equivalent summary. Local token history can now supply estimates even when no quota snapshot/RPC is available.

UI changes: UsageModel reads `_spending`. Codex monthly figures use that summary, not legacy zero costs. The Codex-only title is `Est. API cost`; other tools keep `Spending`. Missing amounts show an em dash. `This month*` marks incomplete or stale coverage. Header width is bounded, the number keeps its month baseline and can fit narrow widths, and no extra card row was added. Hover text explains Standard API equivalence, Plus, saved prices and coverage. The user-approved new rule supersedes the older rule that Codex must always display `$0.00` when no cost was recorded; AGENTS.md and PLAN.md now state the new behavior.

Tests: 43 primary tests pass (six OpenCode, 31 Codex, six widget tests), plus the isolated cache contract. Nine new spending tests cover frozen daily prices, copied-rollout deduplication and retained events, rollover/late usage, no false historical price backfill, context-tier/cache-write/reasoning arithmetic, unavailable rates/tier, stale offline fallback and recovery, corrupt-ledger preservation, unauthenticated public requests with fake credential canaries, and local history without quota data. The new UI test checks Codex-only amounts, Plus explanation, partial coverage, invalid/old-month values and unchanged OpenCode totals. An initial UI-test failure was its date-format stub ignoring yyyy-MM; corrected the stub, not production logic.

QML compilation, Ryoku lint/binding gates, delivery and WM isolation pass. The fork's existing 21 collector regressions also pass against the new primary collector with live price fetching disabled. A temporary independent sum of real ledger events matched the published estimate to 0.000001 USD. Public rates for the three observed models were checked against their official OpenAI model pages; the estimator remains Standard-token-cost equivalence, not tool fees, account credits, tax or an invoice.

Installed collector and three QML files (UsageModel.qml, IrisCompact.qml, AiUsageSpendBody.qml) from the tested primary source. Backup: ~/.local/share/ryoku/ai-usage-backup/daily-spending-20261107-214452/. A normal authenticated collector refresh succeeded; it created the private spending-2026-11.json ledger and rpc/Plus cache. Shell reload succeeded. The full live widget matches the primary source.

The desktop locked during the first screenshot attempt. Requested an unlock asynchronously; no unlock bypass was attempted. A separate temporary layout probe could not create its runtime directory inside the restricted execution environment and was discarded; it was not counted as verification. After the user confirmed unlocking, opened the actual desktop page and inspected the live card. The preview showed $21.87 for Nov 7 API-equivalent token usage, with the title, month, amount and compact primary row aligned. No module-related runtime diagnostics or binding loops appeared. Saved the real preview at the backup directory's preview-codex.png. The island remains open for the user's inspection.

Coverage: Nov 7 has the first saved price snapshot. Nov 6 has 2,514,688 unpriced tokens and is excluded from the amount; the partial-month marker and tooltip disclose this. Today's total continues to grow with usage, so the screenshot amount is a checkpoint, not a frozen balance. The initial live collection reported $21.105826, the preview later showed $21.87, and a subsequent ledger read was $21.9618; the rising figures reflect ongoing recorded activity.

No billing endpoint, Admin API key, Codex credential extraction, new collection script, installed shared-shell overlay, upstream write, commit or push was added. All source changes and records remain uncommitted for the live review.

## 2026-11-07 22:04 IST — Codex label renamed; historical spending bootstrap discussed

The user requested `Est. Spending` instead of `Est. API cost` for Codex. Updated AiUsageSpendBody.qml in the primary source, plus the current requirement in AGENTS.md and PLAN.md. Other agents still use Spending. This is a text-only change inside the existing bounded header; no row, size, amount calculation or collector change is intended. Delivery gates and actual live alignment verification follow before reporting completion. The working tree remains uncommitted.

The user also proposed a one-time account lookup for users with months of pre-install history, then local estimates thereafter. This remains a design discussion, not authorisation for billing requests or credential handling. A wallet balance is not historical expenditure: deposits and remaining credit cannot determine past costs or historical model prices. A verified historical cost import could establish per-month opening expenditure, with an explicit coverage cutoff separating imported actual costs from subsequent local estimates. A single total cannot be treated as each month's expenditure. Provider reporting delays and overlapping coverage would need reconciliation before treating the import as final.

Official OpenAI Costs documentation describes dated cost buckets and an OPENAI_ADMIN_KEY, while Admin APIs documentation requires a separate Admin API key. The existing Codex login/local cache is not that billing credential. No request to the user's billing account is made. Plus usage remains a Standard API-equivalent estimate rather than a Plus charge. Missing historical dollar costs do not prove zero API spending, and the current login does not establish the auth method of all past sessions. Earlier days without saved historical rates remain unpriced; today's estimate uses today's saved rates. Fully retrospective estimates would require verified rates with historical effective dates, and the collector currently scans a bounded 95-day history rather than lifetime history.

## 2026-11-07 22:05 IST — Est. Spending label delivered and checked live

Passed test/run.sh (43 tests plus cache contract), Ryoku QML lint and the binding gate before delivery. Compared the source component against the live copy: the only new UI change is the requested Codex title. Backed up the prior live component at ~/.local/share/ryoku/ai-usage-backup/spending-label-20261107-220503/AiUsageSpendBody.qml and atomically installed the tested source. Shell reload succeeded; the complete live widget matches the primary source. The downstream fork remains unchanged by this label preview.

Opened the actual desktop page and inspected the live card. Est. Spending fits fully, This month* stays right aligned, and $22.47 retains its Nov baseline. Saved the inspected crop in the same backup directory as preview-codex.png. The amount is a live checkpoint, not a wallet balance. The recent shell log contains no AI usage component diagnostics or binding loops. The island remains open for the user's inspection. No billing call, credential change, collector change, shared-shell edit, commit or push was made. Historical import remains a proposal, not an implemented feature.

## 2026-11-07 22:07 IST — Historical billing import dropped by the user

The user said to forget the history-import proposal and keep Est. Spending. This closes the prior design discussion: retain the existing local estimates and daily price snapshots; do not add billing-history imports or balance lookups within the current scope. Updated PLAN.md to preserve that decision. Confirmed that the source and live component both already display Est. Spending. This turn changes records only, with no runtime change or tests needed. All changes remain uncommitted.

## 2026-11-07 22:20 IST — Verify login compatibility; suppress previous ChatGPT quotas for API-key accounts

The user requested another check that usage limits work with API keys, ChatGPT browser login and another remembered login method. Checked the current official OpenAI authentication and app-server documentation, installed Codex 0.167.0 login help, primary/live collector equality, the usage model, and the live cache. Browser and device-code login both produce managed ChatGPT authentication. The account/rateLimits/read RPC provides ChatGPT plan quota windows; API key request/token limits are a separate Platform concept and the module does not collect those. The current user's real rpc/Plus cache reports 5h and weekly windows. Host-managed external tokens, enterprise access tokens and Bedrock are other modes; do not claim universal compatibility or testing of credentials not available here. In-memory host credentials need not be visible to the collector's separately started Codex process.

Found a concrete fallback defect while checking: after account/read identifies apiKey or amazonBedrock, a failed quota RPC returned None and main could load a prior ChatGPT rollout's limits. Added a regression to the existing test/test_codex_usage.py using a fake server and fake key. Both account modes reproduced the defect before the fix, incorrectly showing the earlier Plus 5h window at 48%.

Updated fetch_rpc in the primary collector to treat these explicitly identified account types as an authoritative empty ChatGPT-quota result. It skips the unsupported quota RPC and suppresses fallback to older ChatGPT windows while keeping local token history and spending calculations. The fake fixture supplies account type through a test-only environment variable. The regression checks old-cache/rollout replacement, empty plan/windows/buckets, preserved local totals and spending summary, allowed RPC methods and no credential leakage. The fix is within the user's standing request to handle necessary app fixes; it adds no login flow, key extraction, API billing request or new script. Gates and live delivery follow; changes remain uncommitted.

## 2026-11-07 22:21 IST — Login compatibility guard verified and delivered

test/run.sh passes 44 tests (six OpenCode, 32 Codex, six widget) plus the cache contract. The new regression passes for both apiKey and amazonBedrock, after reproducing both failures before the guard. QML lint and binding gates pass. Backed up the old live collector to ~/.local/share/ryoku/ai-usage-backup/quota-auth-20261107-222135/codex-usage and atomically installed the tested primary collector. Source and live collector match; the live widget also still matches primary. No QML change or reload is necessary for a collector-only delivery. The fork has not received this local-preview change.

Ran the previously approved normal collector outside the read-only execution sandbox. It succeeded without error output. The refreshed private 0600 cache is rpc/Plus with the reported 5h utilization 0.56 and weekly utilization 0.20, and retains its API-equivalent spending summary. The shell remains running. These are current-user ChatGPT checks, not a real API-key/Bedrock/access-token account test; those account-switch cases were validated with isolated fake credentials and a fake server. Do not describe the module as compatible with every login or claim collection of Platform API request/token limits. Browser/device-code compatibility follows their documented shared managed ChatGPT auth path. Host-only ephemeral credentials are not automatically shared with the collector. No billing access, credential change, shared Ryoku file change, commit or push was made.

## 2026-11-07 22:26 IST — Remote Ryoku commit and push authorised; local preview ported

The user explicitly requested committing the completed work to their remote Ryoku repository. This supersedes the prior hold on creating or pushing commits for this delivery. Scope is methos28/ryoku on unstable-dev, not the standalone module remote, upstream Ryoku-dev/ryoku, main, or a new pull request. The phrase 'commit to my remote' authorises both creating the delivery commit and pushing it normally. Earlier requirements excluding README, CONTRIBUTING, changelog, packaging and upstream AGENTS changes remain in force.

Fetched origin unstable-dev and confirmed it matches local HEAD f9b7a7dc1 with zero divergence. Reviewed the nine existing working-tree paths from the earlier compatibility/security audit. Preserved a binary working-tree patch and both untracked test files under ~/.local/share/ryoku/ai-usage-backup/fork-port-20261107-222643/ before further edits.

Ported the tested primary Codex collector, daily estimate UI, Est. Spending label, and API-key/Bedrock quota-fallback guard into the fork's existing paths. Preserved the fork's manifest version 1.2.0, Claude hold-out commentary and agent behavior. Ported spending/security/account-switch tests into existing tests/codex-usage-regression.py; all 21 prior tests remain, with 31 tests total. Omitted only the standalone installer test, which does not apply to Ryoku packaging. Updated tests/ai-usage-widget.py from the shared source (six tests). Isolated tests/codex-usage.sh spending state and disabled live public-price requests, so fixture execution cannot modify caller state or depend on the network. Existing shared-loader, menu and desktop tile fixes remain part of this authorised delivery. No live data, private ledgers or credentials are copied into the fork. Gates and commit review follow; no commit or push has occurred yet.

## 2026-11-07 22:28 IST — Fork port review preserves packaged collector lookup

The first full fork gate pass succeeded (31 collector, six widget, five shared compatibility tests, both shell fixtures, cache contract, QML, delivery and WM isolation). Manual diff review caught an integration error before staging: copying the standalone UsageModel.qml also imported its home-local OpenCode collector path, replacing the fork's packaged opencode-usage lookup and RYOKU_AI_USAGE_COLLECTOR override. No live deployment, commit or push contained this transient error.

Added a seventh widget test that executes the actual collectorPath expression with default and overridden environments. It failed against the transient port, reporting /fixture/home/.local/bin/opencode-usage-v2 instead of opencode-usage. Rebuilt the fork UsageModel.qml from its HEAD version and applied only the four spending-state additions, preserving its packaged lookup, override and comments. Rerunning the affected widget and QML gates before staging. This correction keeps machine-specific standalone installation paths out of the shipped widget.

## 2026-11-07 22:30 IST — Fork delivery gates pass; commit prepared

The corrected fork passes 31 Codex collector tests, seven widget tests and five shared compatibility tests (43 total), plus the OpenCode and Codex shell fixtures, isolated cache contract, widget/shared QML lint, binding gate, delivery verification and WM isolation. The added packaged-collector regression now passes for the default binary and custom override; final UsageModel.qml diff contains only the four intended spending-state lines. All original fork tests are retained. No normal hook has been bypassed. The optional rashin-reviewer executable is absent and this clone does not require it; repository hooks will still run their available mandatory checks.

Reviewed the 13 intended delivery paths: existing AI usage workflow, Codex collector, six widget QML files, the two shared install QML files, three existing/new test suites and the Codex shell fixture. The manifest remains 1.2.0. Primary standalone state, reports and private data remain outside the fork commit. GitHub reports Actions enabled on the fork but zero registered runs before this push; any new CI result must be checked after pushing rather than inferred from local gates. A normal commit and normal push to origin unstable-dev are next.

## 2026-11-07 22:31 IST — Committed and pushed to the user's Ryoku fork

Created f26ede8ad40a73852a6094bc57d784f9e1443731, '[global] ai-usage: add daily spending and harden widget handling', on methos28/ryoku unstable-dev with the normal pre-commit and commit-message hooks enabled. Pushed with git push origin unstable-dev; normal pre-push checks passed. GitHub's refs API confirms the same full SHA. The fork's working tree is clean and HEAD equals origin/unstable-dev. No main branch, upstream repository, standalone remote or PR was changed.

The commit contains 13 reviewed paths: five module QML files, two shared install QML files, one Codex collector, one CI workflow and four test files. This corrects the earlier preparation entry's accidental count of six module QML files. All tests and gates recorded above passed on the delivered implementation, including the regression preserving the packaged OpenCode collector lookup. The commit includes no private data, spending ledger, credential, local project report, hook change, packaging change or unrelated widget file.

At post-push verification, GitHub Actions is enabled but reports zero workflow runs for unstable-dev and zero check runs for this commit. No remote CI success is claimed. Local 43 regression tests, collector fixtures, cache contract, QML, delivery, WM isolation and mandatory git hooks passed. This completes the requested fork commit/push. The primary standalone repository remains deliberately uncommitted because only the user's Ryoku remote was requested. Remaining click-input backlog and real credentials for other login modes are separate, unchanged limits.

## 2026-11-07 22:34 IST — Pull request branch practice discussed

The user asked whether to open an upstream PR directly from their fork's unstable-dev or first create a feature branch. This is a request for advice, not authorisation to create a branch, publish it or open a PR. Refreshed the read-only upstream unstable-dev reference and checked the current fork commit range. GitHub's fork PR documentation permits selecting a fork's compare branch and explains that later commits to the PR head update the PR.

Recommendation: create an ai-usage branch from the current fork unstable-dev head f26ede8ad, then target Ryoku-dev/ryoku:unstable-dev from methos28/ryoku:ai-usage. This preserves the existing four module commits and the same current diff while providing a dedicated branch for review fixes. A direct PR from unstable-dev is also valid, but later pushes to that branch enter the PR. No history rewrite, reset or cherry-pick is needed to create the proposed branch. No branch, PR, remote setting or source file was changed; existing branch preferences remain in effect until the user requests an action.

## 2026-11-07 22:36 IST — Dedicated AI usage review branch authorised and created

The user explicitly requested creating the additional branch recommended in the prior discussion. This permits the ai-usage branch and its publication to the user's fork for the planned PR; it does not authorise opening a PR or writing upstream. Confirmed a clean local unstable-dev at f26ede8ad40a73852a6094bc57d784f9e1443731 and the same remote unstable-dev head. Neither a local nor remote ai-usage branch existed.

Created and checked out ai-usage from unstable-dev with git switch -c ai-usage unstable-dev. All four module commits and the tested tree are preserved. Started a normal git push --set-upstream origin ai-usage with existing hooks enabled. Remote verification follows. This explicit branch request supersedes the previous preference to perform all module work directly on unstable-dev for this review branch. No reset, history rewrite, source-code change or new commit is involved.

## 2026-11-07 22:36 IST — Review branch published and verified

Normal pre-push hooks passed, including repository-wide ShellCheck, package dependency resolution and vendored WM seam verification for the new branch. Published ai-usage to methos28/ryoku and set origin/ai-usage as its tracking branch. A fresh git ls-remote confirms ai-usage and unstable-dev both point to f26ede8ad40a73852a6094bc57d784f9e1443731. Their local divergence is zero and the checked-out ai-usage working tree is clean.

Updated the primary AGENTS.md and PLAN.md to record the user's branch preference for subsequent review fixes. No source change or new commit required rerunning module tests; the branch references the previously tested commit. No PR was created and no upstream branch was changed. Branch: https://github.com/methos28/ryoku/tree/ai-usage .

## 2026-11-07 22:44 IST — Current upstream PR title and body prepared for the user

The user is opening the upstream pull request themselves and requested copy-ready title/description matching the displayed template. Read the fork's .github/PULL_REQUEST_TEMPLATE.md, CONTRIBUTING.md, current branch diff and recorded verification. The full ai-usage PR contains four commits and 29 changed paths, not only the latest 13-file delivery. Replaced the obsolete RYOKU_PR_BODY.md draft with the final widget/collector/install feature, daily estimates and security/compatibility behavior; saved the title in RYOKU_PR_TITLE.txt.

The draft reports 31 collector, seven widget and five shared compatibility tests (43 total), plus shell fixtures, contract, QML, delivery, WM isolation and normal hooks. It distinguishes the checked live standalone deployment from an unperformed full fork deployment, and fake-credential auth tests from real-account checks. It does not carry forward the old zero-cost Codex claim, old fork PR target, old test counts or historical CI success. Changelog and repository documentation checklist items remain unchecked because those files were deliberately not changed. The PR draft uses ordinary prose as required for external content. No source code, remote branch, PR or repository settings changed; the user retains submission control.

## 2026-11-07 22:55 IST — Explain the PR changelog and documentation checklist

The user asked why the two PR checklist items are unchecked and why a matching changelog is needed. Reconfirmed CONTRIBUTING.md lines 127 and 175-179 explicitly request an area changelog entry, and .github/PULL_REQUEST_TEMPLATE.md also asks for documentation when behavior/layout changes. 'Matching' identifies the changelog for the changed subsystem, such as ryoku/shell/CHANGELOG.md for the Shima widget; it does not mean copying implementation details. The existing Note: commit trailers feed generated release notes but do not remove the separately stated changelog expectation.

Both boxes remain unchecked because the submission intentionally left those files unchanged under the earlier scope. Recommend brief changelog and usage-documentation updates for an upstream submission that follows the template. This is an explanation and recommendation only; no new authorisation to modify, commit or push those files is inferred. No source, PR, branch or remote setting changed.

## 2026-11-07 22:58 IST — Add only the requested shell changelog entry

The user authorised a changelog update only and deferred other documentation changes. Added one entry under Unreleased in ryoku/shell/CHANGELOG.md on the ai-usage branch. It describes the Shima widget, supported agents, local history and available plan limits, OpenCode recorded costs, and Codex Est. Spending with daily saved prices, incomplete coverage and the distinction from bills or wallet balances. Existing changelog entries remain intact.

Confirmed a clean starting fork at origin/ai-usage, classified the source path as unmanaged, and passed git diff --check. The fork has exactly one changed file, the requested changelog. No application logic changed, so no runtime tests were repeated. The edit remains uncommitted and unpushed; the user requested this file edit but did not explicitly request another commit. No other documentation, PR, branch or remote setting changed.

## 2026-11-07 23:02 IST — Move changelog entry to repository Added section and publish it

The user pointed to the root CHANGELOG.md on their remote ai-usage branch, requested the Added section and asked why the earlier edit was not visible remotely. Clarified that the previous edit was only local in ryoku/shell/CHANGELOG.md, with no commit or push. The user's request to correct the location and make the expected remote change visible authorises publishing this changelog correction to the existing ai-usage review branch.

Removed only the five lines from our prior uncommitted shell-changelog edit and inserted the same entry under Unreleased / Added in the root CHANGELOG.md. The shell changelog now matches HEAD exactly; the root changelog is the only changed fork file. Refreshed origin/ai-usage, confirmed no branch divergence and passed git diff --check. No code or other repository documentation changed. A normal changelog-only commit and push follow; no PR is being created or edited.

## 2026-11-07 23:03 IST — Root Added entry committed, pushed and verified on GitHub

Created 8a3c43924b63aac431d90dffdb1f2bee71894675, '[docs] changelog: add the Shima AI usage dashboard', with normal hooks enabled. The commit changes only the root CHANGELOG.md, adding five lines beneath Unreleased / Added. Pushed normally to origin ai-usage; no upstream branch, unstable-dev or PR was changed. Both normal commit and push gates passed. No application tests were repeated for a prose-only addition.

Verified git ls-remote reports the same ai-usage SHA, the local working tree is clean, and GitHub's contents API returns the new entry in the remote root CHANGELOG.md under Added. Updated the local PLAN.md review head and checked the changelog item in the copy-ready PR body; the repository-documentation item remains unchecked as requested. Root changelog: https://github.com/methos28/ryoku/blob/ai-usage/CHANGELOG.md#added . This supersedes the prior local-only shell-changelog edit.

## 2026-11-07 23:11 IST — Verify Shima default activation after the PR

The user asked whether unstable-dev users get AI Usage selected automatically after the PR or must enable it. Inspected the submitted branch's CustomWidgets scan/install flow, _widgetDefaults and _seedMissingConfig, widget.json, WidgetManagerPanel, IrisCustomModule and IrisOptions. The PR adds shipped-widget discovery and a manual install action; scanning the shipped catalog does not install it. Installed custom desktop widgets default to enable:false. The Island 'Your modules' preference uses iris.bar.rightModules with fallback [], and the AI usage manifest does not override global Island selection.

Conclusion: after merge and delivery, AI Usage is available for manual installation and selection. The PR does not auto-install, auto-enable or replace existing Shima bar/Island choices. Users install the shipped widget, then select it for the Island desktop Modules block if desired. Existing installed widgets and configured choices are preserved. This is verified current behavior, not a request to alter defaults. No source, settings, branch, PR or remote changes were made.

## 2026-11-07 23:20 IST — Correct Shima module discoverability after an update

The user showed Shima Settings / Island / Desktop page / Your modules and challenged the prior explanation requiring a separate widget manager. They also asked whether the Ryoku Hub Add-ons page was the intended route. Clarified that Add-ons manages the RyoStore plugin/bundle system, a separate feature. The intended requirement is for bundled AI Usage to be offered directly in Your modules after a normal update, without a manual copy/install step. Activation remains optional, preserving existing Island selections.

Confirmed the delivery gap: CustomWidgets._parseShipped currently creates only an install catalog, while IrisOptions and IrisCustomModule resolve only CustomWidgets.widgets from the user's directory. Shipped files therefore do not appear in that settings list on a fresh profile. The earlier statement that users must manually install the widget describes the old implementation and is superseded by this corrected requirement.

Plan: mark the packaged AI Usage manifest as a built-in Shima module, expose a deduplicated module catalog combining installed widgets and explicitly built-in shipped modules, and use that same catalog for settings choices and the Island loader. Installed user copies keep precedence, the desktop-widget registry and install/delete behavior remain unchanged, and the list of enabled modules is never auto-selected. Add fresh-profile and user-override regressions using the actual scanner/manifest, settings choice function and loader expression. This is a downstream integration change in the user's ai-usage review branch, with no standalone collector or live settings change. A mistaken earlier fetch ran in the standalone repository and failed to find ai-usage; corrected by fetching the fork's origin, which confirms zero divergence. No remote state was changed by that failed read.

## 2026-11-07 23:25 IST — Built-in settings discovery implemented and verified

The fork marks only AI Usage's iris manifest as builtin:true. CustomWidgets now exposes irisModules, a deduplicated catalog of user-installed modules followed by explicitly built-in shipped modules. User copies override packaged ids, including a deliberate desktop-only copy. The shipped scanner records the built-in flag and packaged compact QML path. IrisOptions uses the catalog for Your modules and its visibility condition, and IrisCustomModule resolves the selected entry from the same catalog. The normal desktop widgets array, isInstalled, manual copy/remove paths, and enabled-module settings are unchanged. No automatic selection is written.

Added three meaningful regressions to existing tests/custom-widget-install.py: fresh-profile availability and a real packaged load path through the actual settings/loader expressions; user-copy precedence, no duplicates, unrelated widgets and fallback after removing an override; reactive catalog changes in a real isolated Quickshell typed-list runtime. The first two fail against the old code and pass after the fix. An initial test-helper parse error came from its missing var return-type stripping; fixed the helper before demonstrating the actual old visibility failure. Added both changed host QML files to existing component compilation coverage and CI path triggers. Updated the existing root Added changelog entry to describe direct activation from Island settings rather than a separate install step.

All 46 fork tests pass (31 collector, seven widget, eight shared compatibility), plus both collector shell fixtures, cache contract, QML compilation, fatal-QML lint for module/host, binding gate, delivery and WM isolation. The Qt runtime probe passes without importing live settings or services; it runs in a disposable HOME/config/state/runtime. Package payload inspection confirms the existing whole-quickshell copy includes the new manifest and changed host components, and Directories.payloadPath resolves shipped defaults from that installed payload. No packaging changes are needed.

This is a downstream built-in integration change, deliberately not added to the standalone manifest, whose user-installed delivery already works. No shipped live files or overlays were modified. Current live UI already contains the user's manually installed copy, so it is not used as proof of fresh-profile discovery. Preparing the normal review-branch commit/push for this necessary PR correction; no upstream PR or settings modification is being made.

## 2026-11-07 23:26 IST — Settings discovery fix pushed and remote head verified

Committed 9e4268ff2755c2b0a9878d0d03e1144e85591d1a, '[global] ai-usage: list the bundled module in Island settings', with the normal commit hooks. Pushed normally to origin ai-usage with the existing pre-push hooks. A fresh remote-ref query confirms the same SHA; the fork working tree is clean. The eight-file commit contains the module flag, shared catalog/settings/loader changes, existing CI and test updates, and the corrected root changelog entry. No other branch, upstream PR, live shipped file or live setting was changed.

Updated the primary plan and copy-ready PR description to describe direct settings availability and the 46-test verification rather than manual installation. The distinction is explicit: after merge and delivery, the module is offered automatically on the page the user showed, but is not forced into the user's active layout. Existing user-installed copies retain precedence. This supersedes the previous manual-install answer. Real runtime verification used an isolated typed-list QML fixture and the actual settings/catalog/loader expressions; no fresh live-system installation is claimed.

## 2026-11-07 23:33 IST — Updated PR description supplied after the discovery fix

The user requested the revised PR description. Confirmed the clean ai-usage branch is at 9e4268ff2, with the direct-settings discovery fix and root Added changelog entry. Prepared the full description around the resulting built-in dashboard, automatic availability with optional activation, local override precedence, daily estimated spending and preserved shared contracts. Explicitly reports all 46 tests (31 collector, seven widget, eight compatibility), fresh-profile/runtime validation and the limits of real-account/live-fork testing. The changelog checkbox is checked; separate repository documentation stays unchecked under the user's requested scope. Title remains '[global] ai-usage: add the Shima AI usage dashboard'. Updated the local draft's total test count for copy consistency. No remote PR, branch, source code or settings changed.

## 2026-11-08 00:05 IST — User submitted upstream PR 757 as a draft; base mismatch identified

The user reported submitting https://github.com/Ryoku-dev/ryoku/pull/757 and asked whether they or the repository owner should click Ready for review. Read the PR through gh: author methos28, head ai-usage at 9e4268ff2, isDraft true, base main. No comments, reviews or converted-to-draft timeline events were returned, so no claim is made that a maintainer or bot converted it. Official GitHub documentation confirms PR authors and users with write permissions can change review stage; the author can mark their draft ready without waiting for the repository owner.

Identified that the PR currently targets main rather than the agreed unstable-dev base. Advise correcting the base first, then clicking Ready for review to request maintainer attention. This does not merge the PR. Updated PLAN.md to replace the earlier no-PR state with the verified draft and target mismatch. No PR, review stage, base branch, source, commit or remote setting was changed by the agent. Sources: https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-stage-of-a-pull-request and the user's PR.

## 2026-11-08 00:27 IST — Stable host versus unstable PR compatibility re-audit

The user raised the difference between their stable Ryoku installation and the unstable-dev PR target. Confirmed installed Ryoku v1.0.7 and desktop/shell/rashin packages from f7197d7, with Quickshell 0.3.2 and Qt 6.12. Refreshed both official upstream refs: main f7197d72de8a21e44b0bea922bdd915f28f6b327, unstable-dev 0749ec35005cdae3b5c925eb91c32a6904a998d5. The ai-usage branch remains clean at 9e4268ff2, contains the exact latest unstable commit and is zero behind/six ahead. Its 32-file diff is against unstable, not stable.

Audited every pre-existing PR path and direct host dependencies. Nine checked Shima files are byte-identical between upstream stable and unstable: IrisStyle.qml, IrisText.qml, IrisSurface.qml, MaterialSymbol.qml, Directories.qml, IslandDesktopPage.qml, IrisCustomModule.qml, CustomWidgets.qml and WidgetManagerPanel.qml. Both existing collectors and the existing AI usage workflow are also unchanged between those upstream refs. Among shared runtime files modified by the PR, IrisOptions.qml differs between the upstream branches by one added Shortcuts entry; the PR retains that entry and changes only the module choices and visibility. The shared AiUsage.qml reader has a new pace helper on unstable; the PR does not overwrite it, and compatibility tests execute the current unstable reader. Nearby default-terminal-theme and recorder-persistence changes are also preserved and outside this PR. There are wider unstable changes, so these scoped comparisons do not claim that all Shima/runtime code is identical.

Reran target-source validation due to the newly raised integration concern: 31 collector, seven widget and eight shared compatibility tests pass (46 total), including real component compilation against the unstable checkout, actual settings/catalog/loader expressions, real QML typed-list runtime and current shared-cache readers. Both shell fixtures, isolated cache contract, fatal-QML lint, binding, delivery, WM isolation and whitespace gates pass. No code incompatibility was found in the checked paths; no application-source fix, commit or push is justified by this audit alone.

Read PR 757: the user has corrected the base to unstable-dev and marked it ready, head remains 9e4268ff2, and GitHub reports it mergeable. The successful checks are notification/triage jobs. The functional workflows, including AI usage collector, QML Lint and delivery, report action_required pending approval for the fork contribution. This is not a code-test failure or a successful functional CI run. Official GitHub documentation confirms maintainers with write access approve these workflow runs. No workflow approval or PR state change was attempted.

Remaining gap: tests and the live stable preview do not establish that a complete unstable desktop with its package versions, session startup, installation/update flow and interactions has been exercised. Recommend maintainer-approved CI and an unstable test session/VM before treating full runtime compatibility as verified. The user's daily stable installation has not been upgraded, restarted or modified. This audit is read-only apart from primary local records. Earlier broad claims of passing gates remain scoped to their local/source tests, not full unstable-system validation.

## 2026-11-08 10:52 IST — Latest standalone module publication authorised and prepared

The user requested pushing the latest module changes to their profile repository, https://github.com/methos28/AI_usage_widget_ryoku_shima . This explicitly authorises committing the already reviewed local changes and publishing them on its default main branch. Confirmed the exact origin URL and a fresh origin/main at 47b9395, with zero divergence. This action concerns the standalone repository, not the upstream PR or Ryoku fork.

Prepared the existing local widget/collector fixes, daily Codex estimates, quota/account-switch guard, security hardening, shared dropdown and regressions for publication. The standalone collector matches the fork's reviewed collector and the live widget matches the primary source. Retained standalone collector lookup and manual installation; built-in host discovery remains in the linked Ryoku PR rather than copying shared shell files into this repository. No version tag, release, new script or live deployment is involved.

Updated README.md to replace obsolete no-network/no-login claims, use the canonical repository URL, support either agent, explain quota authentication and unauthenticated public-price downloads, define Est. Spending/partial history, describe the persistent monthly ledger, distinguish the standalone installer from proposed built-in integration, and state the stable-live versus unstable-source verification limit. Corrected period-control guidance after reading its actual click handler: the first click expands a collapsed section, then the label opens the menu. Preserved existing preview images with an earlier-layout caption. Added an Unreleased changelog entry and updated current project rules/plan. Local PR drafts and audit report artifacts are excluded; the existing tracked project records remain included as before.

Reran test/run.sh: six OpenCode, 32 Codex and six widget tests pass (44), plus the isolated cache contract. Project QML lint and binding gates pass; git diff --check passes. Tests use temporary state and disable live pricing requests. No real credential or billing access was needed. Preparing a normal commit and push without bypassing hooks; remote verification follows.

## 2026-11-08 10:54 IST — Standalone profile repository updated and public contents verified

Created 1f4f3d4628c28431eb9ed8af41419bb7c14b62b3, 'widget: add daily Codex estimates and harden usage collection', on the standalone main branch with normal git behavior. Pushed to https://github.com/methos28/AI_usage_widget_ryoku_shima.git . GitHub refs and git ls-remote confirm the same application revision. The repository is PUBLIC and main is its default branch.

Verified the remote tree contains the new shared dropdown component, widget regression suite, updated Codex collector, README and changelog. The remote README blob equals the committed local blob. Local RYOKU_PR_BODY.md, RYOKU_PR_TITLE.txt, RYOKU_TEST_REPORT.md and RYOKU_COMPATIBILITY_REPORT.md remain unpublished; no RYOKU_ artifact is in the remote tree. Existing tracked AGENTS.md, PLAN.md and PROJECT_LOG.md were updated along with application source and tests, matching this repository's established record-keeping practice.

All 44 standalone tests, isolated cache contract, QML gates and whitespace checks passed before the application commit. No runtime or source change follows those gates; this entry and the plan update document completed publication. No live desktop files, Ryoku fork branch, upstream PR, release tag or repository visibility setting was changed. The complete graphical unstable-runtime limitation remains documented. A final documentation commit records this verified result without changing application behavior.

## 2026-11-09 02:20 IST — Stale Codex limits on the updated desktop

The user reported the first unstable-dev bug: the Shima card shows 8% used and an expired five-hour reset while Codex status shows 100% remaining. They requested the prior regression gates and current Shima compatibility checks, with notice before modifications. No commit or push is authorised.

Pre-edit checks found a discrepancy with the last deployment record. The complete live widget still matches the standalone repository, and the standalone collector matches the fork's reviewed collector. However, ~/.local/bin/codex-usage is now byte-identical to /usr/bin/codex-usage and the official checkout at ~/ryoku-arch, rather than the project collector. The live copy uses the obsolete -a untrusted argument and lacks the project history/spending changes. The user service drop-in still selects that home-local collector. Recent real service logs repeatedly report rpc error: initialize; the published cache is _source: rollout with five-hour utilization 0.08, an expired reset, and weekly utilization 0.27. The replacement mechanism is not established; package upgrades occurred shortly before the report, which is correlation only.

The fork checkout remains clean on ai-usage at 9e4268ff2, not unstable-dev; its collector already contains the CLI compatibility fix. The official ~/ryoku-arch checkout is clean on unstable-dev at 0749ec350 and remains read-only. No branch or source reconciliation was performed. The installed shell package is now 1.10.1.r5848.g4542802-1 with Quickshell 0.3.2-1.1, so previous stable-runtime claims do not describe this current environment.

Reported the required change to the user before editing: validate and restore the existing tested primary collector to the unmanaged ~/.local/bin/codex-usage path, then refresh real limits. No Shima host/source change is justified by the evidence so far. Both the collector and this log are classified unmanaged by ryoku owner. This append-only discrepancy record precedes further implementation or deployment, as required by AGENTS.md. All work remains uncommitted.

### 02:26 IST — Current Shima checks and update-safe standalone installation

The complete prior checks passed: 44 standalone tests, 46 fork tests, both collector shell fixtures, isolated cache contracts, QML lint, duplicate-binding checks on 40 files, delivery and WM isolation. The faulty live collector failed the existing private-stdio regression; the primary collector passed. Restored the tested collector to the old live path after backing up the binary and both caches under ~/.local/share/ryoku/ai-usage-backup/unstable-fix-20261109-022043. An authenticated refresh succeeded as rpc/Plus with future resets, history and spending. The real current Shima card was inspected with these restored fields. Percentages changed during ongoing work and are not frozen to the original screenshot. Additional Wayland component compilation passed seven fork widget tests. Ten direct installed Shima dependencies match the official unstable checkout baseline; the fork's shared-host changes remain only in its source checkout.

A further compatibility audit found a concrete future-update trap in ryoku/cli/internal/doctor/reconcile_dev_residue.go: the doctor removes every ~/.local/bin entry with a Ryoku-packaged /usr/bin twin. It can therefore remove this standalone project's codex-usage override. This establishes an update risk, not the exact mechanism that replaced the reported binary. Told the user before additional source edits. Revised the installer regression first; it fails against the old installer because the protected collector destination is absent.

Changed the standalone install.sh, service drop-in, manual README commands and ownership note to install Codex at ~/.local/libexec/ai-usage/codex-usage. OpenCode's distinct home-bin name remains unchanged. The installer preserves existing home-bin copies. The regression seeds an old shadow, checks the new executable and service target, removes the old temporary shadow to simulate doctor cleanup, then runs the protected collector against isolated data. No collector algorithm, QML, shared Shima file, packaged file, fork branch, commit or remote is changed. Delivery to the new live path is pending the repeated gates. All source and record edits are uncommitted.

### 02:36 IST — Effective service verified; final compatibility report

The first service verification exposed an additional discrepancy: ryoku-dev-bin.conf sorts after override.conf and resets ExecStart to ~/.local/bin/ryoku-ai-usage. Thus the initial libexec service edit was not effective. Reported that finding and the needed correction before changing the installer destination to zz-ai-usage.conf. Strengthened the existing installer regression with the dev override and systemd's command-reset ordering. All 44 standalone tests and the cache contract passed again; shell syntax and whitespace checks also passed.

Installed the tested protected collector and later project drop-in. Restored the earlier override.conf byte-for-byte from its backup, preserving ryoku-dev-bin.conf and the home-bin copies. Reloaded the user service manager and started the actual service. Effective ExecStart now includes ~/.local/libexec/ai-usage/codex-usage and ~/.local/bin/opencode-usage-v2, both with exit status 0; the timer is active. The live cache is rpc/Plus with future windows, history, spending and private permissions. The installed protected collector/drop-in and the unchanged live widget match tested source. No collector algorithm or QML edits were required.

Basic live checks observed the agent menu, OpenCode switching, return to Codex, the Trend menu and Today chart. Longer scripted click sequences closed the panel, so all-period click coverage and rapid-input races are inconclusive. Restored period 7 through the daemon's settings.patch writer, confirmed Codex/Last 7 days in the store and on the final card, stopped the temporary input helper and closed the island. The inspected runtime log tail contains no module-related load errors, binding loops, ReferenceError or TypeError diagnostics. Automated actual-QML binding tests cover period/calendar behavior independently of those input limits.

Saved TEST_REPORT_2026-11-09.md, updated the current plan and ownership notes, and wrote the durable vault memory and dated journal. Backup directory is ~/.local/share/ryoku/ai-usage-backup/unstable-fix-20261109-022043. All prior 46 fork tests, shell fixtures, cache contracts, QML/binding, delivery and WM-isolation gates passed against its unchanged source; seven additional Wayland widget tests passed. The official and fork checkouts remain clean on their original branches. No commit, push, source branch switch, package upgrade, doctor repair or shared-bar deployment was performed. The earlier binary replacement mechanism remains uncertain. All standalone implementation and record changes remain uncommitted.

## 2026-11-09 02:56 IST — Audit the actual unstable update branch and complete delivery path

The user clarified that current Shima means the actual unstable-dev Ryoku desktop and requested a full placement, update-install and fresh-profile discovery cross-check. Earlier passing review-branch tests are not proof that the official tracked branch contains the feature. The machine's recorded repository is ~/ryoku-arch, origin is Ryoku-dev/ryoku, tracked channel is unstable-dev and deployed commit is 0749ec350. Fresh upstream and fork fetches succeeded without changing working branches.

Confirmed delivery discrepancy before further edits: official upstream/unstable-dev remains 0749ec350 and has no defaults/widgets/ai-usage directory or built-in discovery changes. The user's origin/unstable-dev is f26ede8ad, with the enhanced collectors/widget but without the later discovery commit. Only origin/ai-usage at 9e4268ff2 contains the complete built-in discovery fix. The live custom widget is a manual installation, so its presence in the user's screenshot does not prove availability on a clean unstable profile. GitHub's authenticated live API reports PR 757 closed, merged=false, merged_at=null, closed_at=2026-11-08T12:36:17Z. The web rendering returned an older Open snapshot; the fresher API and Git refs are the audit evidence.

The source update code redeploys its tracked checkout; deploy.sh copies the collectors into ~/.local/bin and writes ryoku-dev-bin.conf to select that directory. The previously faulty collector matches the source of the official tracked branch. This is the direct source/deployment explanation for why switching to official unstable can replace a manually installed enhanced collector; the exact previous command invocation is not logged. Important refinement to the prior cleanup note: reconcileDevResidue explicitly skips source-checkout machines. Its removal risk applies to packaged installs or transitions back to them, not the normal source-tracked unstable update.

Reported these findings and the need for a staged delivery regression before source edits. Add the check only to the user's existing ai-usage review branch: execute the actual package/source delivery snippets in temporary storage, use the real collector package install script, exercise fresh-profile settings/loader discovery and run the staged collector through its real guard with isolated data. Preserve all current source/live edits and do not deploy the checkout, upgrade packages, switch branches, change update tracking, commit, push, reopen a PR or write upstream. No production-code incompatibility has been reproduced in the complete review tree.

### 03:02 IST — Staged delivery and branch negative controls complete

Added test_update_payload_delivers_module_and_matching_guard_collectors to the fork's existing tests/custom-widget-install.py. It stages the relevant actual Quickshell copy/collector install/dev-unit instructions and executes the actual ryoku-rashin package installer with placeholders only for unrelated compiled applications. In both modes it checks all module files, four guard/collector scripts, service and timer, fresh-profile settings and loader discovery, and actual staged-guard output from isolated rollouts. A helper now accepts a staged Quickshell root so it tests installed paths instead of only the review source tree. No production code or CI policy changed; the existing workflow already runs the test file.

All 47 fork tests pass: 31 collector, seven widget and nine shared compatibility tests. Both collector shell fixtures, cache contract, fatal-QML lint, 22-file binding gate, delivery and WM isolation also pass. Repeated the primary standalone gate: all 44 tests and cache contract pass. Focused existing Go updater channel/gating, host service-manifest and doctor AI usage/Rashin/dev-residue tests pass. Existing Qt advice and fixture cleanup ResourceWarnings remain in logs without suppressing or weakening gates.

For the negative control, exported the actual origin/unstable-dev files into a temporary directory and ran the current fresh-profile discovery regression against them. It fails at the visibility assertion, false !== true. The review tree passes; official unstable has no bundled module directory. The faulty incident collector is byte-identical to official unstable's collector. These checks establish the branch/deployment gap rather than guessing from commit labels.

Confirmed live placement: the official checkout, packaged config and installed shipped Quickshell tree lack the bundled module; the manual user widget and protected collector override remain present. The current protected collector matches review source and publishes rpc/Plus with history and spending fields. This audit made no live change. Saved DELIVERY_AUDIT_2026-11-09.md, the 31-file DELIVERY_INVENTORY_2026-11-09.tsv, current plan and vault notes. The new fork test and records remain uncommitted. No branch switch, commit, push, PR action, update, deployment or upstream write occurred. Official automatic delivery remains unfulfilled until the complete feature enters the tracked branch and passes its testing gate.

## 2026-11-09 03:06 IST — Fork ai-usage publication authorised

The user requested pushing any current code changes to their fork's ai-usage branch. This authorises the necessary local commit and normal push of the prepared delivery regression to methos28/ryoku:ai-usage. It does not authorise publishing the standalone installer changes, moving either unstable-dev branch, reopening a PR or writing upstream.

Pre-commit review confirms the fork has exactly one changed file, tests/custom-widget-install.py: the staged package/source delivery regression and its shared path helper. A fresh fetch confirms HEAD and origin/ai-usage both at 9e4268ff2 with zero divergence. The nine shared compatibility tests pass again; the previously recorded full 47-test result and unchanged production-source gates remain applicable. The live widget still matches primary source and its collector reports rpc/Plus with history/spending. Commit and push will use the existing normal hooks without bypasses.

## 2026-11-09 03:07 IST — Delivery regression committed and pushed to fork ai-usage

Created c2dbdc496bd2b123f50ad01476541acc7ee9f3e3, '[test] ai-usage: verify update payload delivery', with the normal pre-commit and commit-message hooks. The commit contains only tests/custom-widget-install.py: 95 insertions and six deletions. Nine shared compatibility tests passed immediately before committing; mandatory delivery/WM checks ran in the commit hook. Normal pre-push hooks passed.

Pushed normally to methos28/ryoku:ai-usage, advancing 9e4268ff2 to c2dbdc496. A fresh git ls-remote confirms the full remote SHA equals local HEAD, and the fork working tree is clean. No other branch, upstream repository, PR, live configuration or standalone remote was changed. The standalone installer/source fixes and local audit records remain uncommitted under their existing separate scope. The official unstable delivery gap remains unchanged; this action publishes the review-branch regression only.

## 2026-11-09 03:17 IST — Updated paste-ready PR description

The user requested a fresh PR description reflecting the current application. Verified the clean ai-usage fork at c2dbdc496, its seven feature/test commits, the 32-file diff and a matching live remote head. Rewrote the existing local RYOKU_PR_BODY.md around the full feature, conditional availability after unstable delivery, 47 target-source tests and the new package/source staging regression. Preserved optional activation, user-copy precedence, Claude hold-out, estimate limitations, real-account/runtime test boundaries and the unchecked separate-documentation item. The title is unchanged.

This is local drafting only; no PR, branch, source implementation, commit, push or live configuration was changed. Existing local audit and installer changes remain under their earlier separate scope.

## 2026-11-09 03:43 IST — Bundle collectors with the widget, authorised architecture change

The user requested placing both collectors inside the iNiR widget directory and invoking them by their own paths. This replaces the prior module rule of using packaged collector lookup and the system service for Codex. Reported the necessary changes before editing: canonical executable scripts in widget/bin, a local launcher resolved from QML, isolated widget caches so older system writers cannot overwrite them, and startup/visible refresh without requiring ryoku-rashin. Preserve the explicit OpenCode collector override and existing system command entry points. No new commit or push is authorised by this change request.

Move each repository's existing scripts into its widget/bin directory and leave relative source symlinks at the prior collector entry points. Package/source install already dereferences those entry points into standalone executable files, so other bar readers keep their existing collectors and shared caches. The widget launcher writes ~/.cache/ai-usage instead. It shares the legacy Codex lock while updating the existing spending ledger, preserving historical prices and preventing concurrent ledger writes across the two cache destinations. No package dependency or pricing/account algorithm change is intended; Python already belongs to ryoku-desktop.

Both working trees match the recorded state. Fork ai-usage is clean at c2dbdc496; primary retains the earlier uncommitted local installer/docs changes. Pre-change patches and the primary widget are backed up at /home/methos/.local/share/ryoku/ai-usage-backup/bundled-collectors-20261109-034353. All changed source/widget directories are classified unmanaged by ryoku owner. Tests and gates precede any live copy.

### 2026-11-09 04:03 IST — Bundled collector implementation and pre-deployment gates

Both canonical collectors now live in ai-usage/bin with a local collect-usage launcher. Relative symlinks retain the earlier source entry points in both repositories; byte comparisons confirm each collector body is unchanged from its own repository HEAD. The existing package/source install commands dereference those links into regular system executables. The widget launcher instead writes ~/.cache/ai-usage and invokes its own executable paths resolved from Qt.resolvedUrl, preserving a literal OpenCode override argument. No service fallback remains in UsageModel. Startup and visible minute refresh run even without a cache; other bars retain their existing shared caches and service behavior.

The launcher takes the legacy Codex lock before the private collector lock to serialize the shared persistent spending ledger. A busy lock returns a retry status; the model retries and waits for a completed collection before rewriting a saved agent. Availability publishes complete probe batches. Added native-store, private-cache/old-system-command isolation, lock, relative-path/override and real QML cold-start tests. The runtime fixture includes the real availability component and actual agent reconciliation code, both native stores, a busy legacy lock and a saved Codex choice. An early probe omitted its menu context; corrected that fixture and added explicit runtime-error assertions. The final negative control removes only the readiness guard and reliably detects the saved-agent reset.

Final gates pass: 48 primary tests (six OpenCode, 32 Codex and ten widget), 50 fork tests (31 Codex, ten widget and nine shared compatibility), collector shell fixtures, cache contracts, QML compilation/lint, the 36-file binding gate, delivery, WM isolation, shell syntax and whitespace. The staged source/package regression now runs both the installed system guard and the widget-owned launcher, verifies private output and unchanged shared cache, and checks the same spending summary without repricing. Existing fixture ResourceWarnings remain visible.

Simplified the standalone installer to copy the complete widget only and reload the shell. It no longer creates global collector copies or a service override; the obsolete source drop-in was removed. Existing live global helper/service customizations will be preserved for other consumers. Updated installation/data-source/uninstall documentation, ownership rules and both changelogs. Source and records remain uncommitted. Proceed only with backed-up user-owned widget deployment after these passing gates; no system package or source-checkout deployment is needed.

### 2026-11-09 04:07 IST — Self-contained widget deployed and verified live

After final gates and the corrected runtime/negative-control probes, backed up the live widget and atomically replaced only ~/.config/inir/widgets/ai-usage with the tested primary bundle. A hidden previous directory is retained beside it for rollback; the custom scanner ignores hidden names. Reloaded the shell successfully. The complete deployed widget matches source.

Opening the actual desktop page created both private caches through the widget-owned launcher. Codex reports authenticated rpc/Plus with future resets, history, sessions and spending. OpenCode reports storage+v2 with 50 days and ten sessions. Both caches are mode 0600. Inspected the live card with valid quota rows, active session and Est. Spending; no module-related runtime errors appeared in the inspected log tail. The saved widget configuration is byte-equivalent as parsed, including Codex/Last 7 days. Hash checks prove all prior global collector files and service overrides are unchanged. No package upgrade or official source deployment occurred.

Saved BUNDLED_COLLECTORS_2026-11-09.md, updated current plan/ownership/install documentation and wrote the dedicated vault memory note. Backup is ~/.local/share/ryoku/ai-usage-backup/bundled-collectors-20261109-034353, including the old widget, settings, file hashes and inspected screenshot. All source and record changes remain uncommitted; no new push, branch change or upstream write. The published branch remains c2dbdc496 and still describes the previous architecture until this working tree is approved for publication.

## 2026-11-09 13:40 IST — CodexBar source comparison and new token audit

The user requested studying steipete/CodexBar and verifying the local collectors after comparing Sol input/output with DeepSeek Flash through Command Code. This is investigation and reporting, not an implementation or deployment request. Read the project records, verified both working-tree inventories and confirmed the complete primary/live widget equality. Preserved all existing uncommitted bundled-collector work.

Cloned CodexBar read-only to /tmp/codexbar-audit-20261109 at 7447bc77c2497323d9c41e40164ce705533493c8. Reviewed Codex quota sources, native request-ledger/mirror/continuation handling, models.dev and fallback pricing, the separate OpenAI organization billing provider, and OpenCode/Command Code source boundaries. Fetched official OpenAI reasoning, token-counting and exact Sol model documentation. No Swift compiler is installed, so no CodexBar build or test success is claimed.

Audited the stable private widget cache at updated_at 13:24:17 through the activity file's recorded rollout offsets: 11 physical files, seven session IDs, 659 cumulative events, 652 positive cumulative deltas and 653 unique native request records. Both widget caches stayed unchanged during reconstruction. Found four continuation pages with session_meta.history_base whose inherited cumulative baseline is counted again because both scan_activity and history_records initialize per-file counters at zero. Existing timestamp/cumulative event hashes cannot remove these new-timestamp inherited baselines. This is new observed inflation; earlier November 7 correctness conclusions do not establish correctness for today's expanded history.

Sol current/reconstructed unique-request values: uncached input 2,761,528/1,753,628; cache reads 191,386,752/133,322,880; output including reasoning 780,579/518,489; inclusive total 194,928,859/135,594,997. Native reasoning is 270,089, leaving 248,400 non-reasoning output. The collector sets reasoning to zero and includes it in output, unlike OpenCode's separate fields. The model row combines 198 high-effort and 380 xhigh requests. One native compaction request, 453,353 total tokens including 5,327 output, has a matching compaction_response_id but no token_count mirror, so the collector also misses it. Summing only last_token_usage would still omit that request.

Using the retained daily price snapshots and exactly the same cache cutoff, the published partial Standard API-equivalent subtotal of $52.926383 reconstructs to $33.327711. November 6 remains unpriced in both. Multiplication agrees with the saved rates; faulty token records and false context tiers cause the discrepancy. Background shared-ledger updates after the cutoff were excluded from this comparison. The estimate is not a verified charge or remaining balance.

OpenCode target row is reproduced from 1,264 stored DeepSeek records plus the existing session-aggregate residual adjustment: input 4,048,762, output excluding reasoning 325,276, reasoning 593,042, cache reads 228,237,952. No comparable replay inflation was demonstrated for that row; residual timestamp/model attribution and provider invoice accuracy remain unverified. Installed OpenCode is v2.2.6.

Existing collector tests pass: six OpenCode and 32 Codex. Three temporary correct-behavior tests fail against unchanged code: continuation expected 4,000 but returned 7,000; request-only compaction expected 1,234 but returned zero; reasoning expected 400 but returned zero. Additional source limitations: nested native thread_settings_applied is not parsed by the top-level settings branch; all 106 inspected settings are default, so no live Fast discrepancy was measured. Cache-write display counts are hardcoded zero; inspected native write counts are zero. Monotonic cache merging and retained spending events will require a coordinated correction to prevent old inflated figures surviving a parser fix.

Saved CODEXBAR_TOKEN_AUDIT_2026-11-09.md with exact tables, source links, method, tests and proposed repair/migration scope. Temporary numeric evidence and reproductions remain beside the temporary clone. No collector/QML code, live copy, cache, ledger, credential, setting, service, branch, commit, push, PR or package was changed. Only this report and append-only project/vault notes were authored, uncommitted. Implementation and migration remain outstanding pending a user request.

## 2026-11-09 13:55 IST — Request accounting repairs authorised

The user explicitly requested applying the audited repairs and further comparison with CodexBar spending. Scope: native request deduplication with legacy continuation fallback, compaction coverage, consistent output/reasoning/cache-write breakdowns, actual settings envelopes, automatic usage/activity/spending correction while preserving saved daily prices, tests, deliberate downstream port and tested live delivery. No commit, push, billing integration, new credential or upstream write is authorised. Existing uncommitted bundled-collector changes and complete primary/live equality were rechecked. Prowl has no primary-project index, so exact known-path reads are used. Source backups: /home/methos/.local/share/ryoku/ai-usage-backup/request-repair-20261109-135529. Implementation and migration are not yet delivered.

### 14:03 IST — Request repair and frozen-source parity

Implemented one canonical native request ledger with response identity, legacy mirror reconciliation, continuation baselines, ownership boundaries, validated components and retained records in activity schema 5. O now excludes reasoning; R and cache writes are preserved; pricing includes all output once and context includes cache writes. Actual nested settings are parsed. The migration replaces reconstructed old identities, retains unavailable historical records and all saved rates, and saves a private before-request-accounting ledger backup. Exact day/hour replacement applies only to reconstructed dates. Added ten collector regressions, including delayed mirrors discovered in real data. All 42 primary collector tests pass. Three representative tests fail against the old backed-up collector. A frozen 653-request replay matches every audited Sol count and $33.327711 on two refreshes, with identical daily prices. Ported only the canonical collector and new tests into the existing fork ai-usage working tree; updated focused docs/changelogs. Source changes are uncommitted. Full gates and live delivery are pending.

### 14:45 IST — Final delivery gates and shared-writer audit

All 59 primary tests and cache contracts pass. The fork passes 42 collector, ten widget and nine shared-delivery/compatibility tests (61 total), Codex shell fixtures, cache contract, QML lint/bindings, delivery and WM isolation. Added a split-file request/mirror test and retained snapshot aliases, bringing the new collector regressions to eleven. Existing raw QML warnings remain visible; the fatal-QML gate is clean. Primary and fork collector bodies match. The actual service still selects ~/.local/libexec/ai-usage/codex-usage and shares the same historical ledger as the widget. Its code and the earlier home-bin copy must be updated with the same tested collector to prevent an old writer restoring obsolete cumulative identities. Service configuration will be preserved. Backups and atomic source-to-live updates follow under the existing locks, then a normal quota refresh and independent live token/price verification. No commit, push, upstream or billing action is part of delivery.

### 14:48 IST — Request repair delivered and verified live

After all delivery gates passed, acquired the existing shared and private Codex locks, backed up live collectors/caches/monthly ledger and daily price dictionaries under ~/.local/share/ryoku/ai-usage-backup/request-repair-live-20261109-144515, and atomically installed the tested collector into the user widget, protected libexec service path and earlier home-bin path. All five source/live copies, including the fork, match SHA-256 56009a8696fb6d8c25e5fcff668bcf711fdaf7826a28f0462ba73e23c3b5721e. Service configuration is unchanged. The protected and home-bin copies were included because an old shared-ledger writer could otherwise reintroduce obsolete event identities.

The first restricted collection reported rpc error: initialize. The approved bundled launcher outside that startup restriction completed normally with the existing login. The private cache is rpc/Plus, accounting version 2; activity schema is 5. Automatic historical correction and the private before-request-accounting monthly backup succeeded. Every saved daily price dictionary is unchanged; private cache/activity/ledger modes remain 0600.

Independently parsed raw native requests for a stable live snapshot of 718 records. Every request's input/cache/output/reasoning components match activity state; daily inclusive totals match the request sum; independent pricing matches the published $36.917120 partial estimate. The frozen earlier 653-request audit remains exactly $33.327711, so later amounts reflect newly recorded work rather than a comparison-cutoff change. Shell reload succeeded. Opened the actual desktop page and inspected its compact card, valid provider quota rows and Est. Spending around $37.10 after ongoing activity. The recent runtime log has no AI usage load/binding errors. Saved preview-codex.png in the live backup directory.

Saved REQUEST_ACCOUNTING_REPAIR_2026-11-09.md and updated plan/memory/journal. Full tests: 59 primary, 61 fork, plus cache contracts, Codex shell fixture, QML lint/bindings, delivery/WM isolation and whitespace checks. CodexBar's current dashboard explicitly labels local values Estimated spend and separately shows provider Plan metered values. Its OpenAI provider reads reported organization costs with an Admin API key; no such billing integration or credential was added here. Retained the requested Est. Spending label and saved-daily-price policy. All changes are uncommitted; no push, branch switch, upstream mutation or package upgrade occurred.

## 2026-11-09 15:26 IST — Claude Desktop preview authorised

The user requests a live standalone Claude preview before running their new Sonnet 5.5 medium-effort prompt. This supersedes the menu hold-out only for this preview; no fork release, commit or push is authorised. Primary/live equality was checked. One real desktop transcript exists with nine assistant rows for four Sonnet 5.5 responses, all high effort. No CLI is on PATH and no .credentials.json exists. Prepare local-only usage, history and sessions without changing authentication or sending a model prompt. Quotas, costs and running-state validation remain unavailable. An initial source backup stopped at its missing test subdirectory; that directory was created and the backup completed before modifying existing source. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/claude-preview-20261109-152534. The new claude-usage source is not yet deployed.

### 15:27 IST — Claude local-history preview prepared and deployed

Added bundled bin/claude-usage using read-only native desktop transcripts and the existing bundled history schema/publisher. It deduplicates request/message snapshots, handles partial JSON tails, records input/output/thinking/cache reads/writes, and publishes sessions/daily/hourly/period/model history to a private cache. The launcher discovers CLAUDE_CONFIG_DIR/projects without a CLI. No credential, model call, remote quota probe, cost calculation or desktop auth change is used. Enabled Claude (preview) in the standalone menu/settings; its spending is unavailable rather than fabricated zero. The original fork hold-out is unchanged pending the new user-run prompt.

All 62 primary tests and cache contracts pass, including three new Claude fixtures for deduplication/copies/streaming/invalid tails/privacy/empty quota behavior. QML fatal lint and bindings pass. The existing desktop baseline independently matches four high-effort claude-sonnet-5-5 responses: input 8, cache creation 72,377, cache reads 190,297, output including thinking 3,612 (thinking 1,182), inclusive total 266,294. Saved the baseline in /home/methos/.local/share/ryoku/ai-usage-backup/claude-preview-20261109-152534. Source files were copied to the user-owned live bundle after the gates. Refresh/reload and final live readiness check follow. No commit, push or fork modification.

### 15:28 IST — Claude preview ready; awaiting user prompt

Claude Desktop local-history preview is installed in the user widget. All 62 primary tests, cache contracts, QML lint and bindings pass; primary/live widget equality and shell reload/status are verified. Private Claude cache is mode 0600 with four Sonnet 5.5 high-effort responses and 266,294 inclusive tokens. New requested run is Sonnet 5.5 medium effort and has not been run by the agent. No CLI, credential access, auth change, model request or remote usage call was needed. Preview quotas, spending and running-status validation remain unavailable. Do not use the old shared demo Claude cache or old /usr/bin/claude-usage as evidence: the widget uses its new bundled collector and private cache.

Next: after the user runs a new desktop prompt, inspect metadata/usage only, compare against the saved baseline at ~/.local/share/ryoku/ai-usage-backup/claude-preview-20261109-152534/claude-baseline.json, verify medium effort, streaming/final counters and request deduplication. Do not publish or enable Claude in the fork until live validation is accepted. All standalone edits remain uncommitted/unpushed.

## 2026-11-09 15:35 IST — Claude medium-effort live token validation

The user reported the desktop session live. New local session 2a1d8d9b-1bab-4749-93ca-dcf13812ccbf is claude-sonnet-5-5 with medium effort. It grew from three to four distinct responses during observation. Independent raw reconstruction at the four-response checkpoint: uncached input 8, cache writes 62,880, cache reads 180,125, output including thinking 1,486, thinking 348; inclusive total 244,499. Together with the old high-effort baseline, eight responses total 510,793 tokens. Model totals, daily totals and non-cached session totals agree with raw records. The existing automatic private cache had already discovered the new session before manual refresh.

A first repeat-check compared a stale pre-refresh cache to current data and failed; this was a diagnostic setup error, not evidence of duplicate counting. The corrected check refreshes twice around source signatures. Local counts are verified for the observed records, but quota/cost access and the running indicator remain unimplemented. The preview currently marks every session not running, so the Sessions card does not establish whether the user's model is active. No source, authentication, configuration, commit or remote changes were made during this observation. Further responses may arrive after these checkpoints; re-read the live source before comparing later totals.

## 2026-11-09 15:36 IST — Completed Claude medium-effort session reconciled

The user confirmed the new desktop session finished. Independently reconstructed seven Sonnet 5.5 medium-effort responses from repeated native assistant blocks. Final new-session counts: input 14, cache creation 66,018, cache reads 372,631, output including thinking 2,502, thinking 481 (non-thinking output 2,021); inclusive total 441,165. The earlier high-effort baseline remains 266,294 across four responses. Combined dashboard model history is 707,459 across eleven responses and two sessions; 23 assistant rows are not 23 separate model requests. No malformed records were found. Raw token sums match model, session and daily totals; a second refresh with unchanged source hashes leaves period totals unchanged. Saved numeric evidence as claude-final-validation.json in the Claude preview backup directory. No model requests or source/authentication/settings changes were made during validation. Subscription quota, cost and running-state support remain unfinished; this validates the observed desktop token history only. All project edits remain uncommitted/unpushed.

## 2026-11-09 15:44 IST — Claude limits, costs and lifecycle repair authorised

The user requested Claude account limits in Now, repaired spending and running sessions, and explicitly requested three subagents with parent review. This extends the local-history preview in the standalone/live widget; the fork remains held out and no commit or push is authorised. Baseline and completed medium session were reconciled before this scope. Work is split into isolated Claude quota, spending and session helper/test files; the parent owns main collector/UI integration and reviews all changes. Shared-account quotas must come from observed account data and must never default to zero or local-token budgets. Research found native Desktop plan-usage history and native session status metadata. Pricing research distinguishes API-equivalent local value from actual subscription charges and checks separate 5-minute/1-hour cache writes. Source/test/live backups: /home/methos/.local/share/ryoku/ai-usage-backup/claude-complete-20261109-154352. No authentication change or model prompt is authorised. Tests and live delivery remain pending.

### 15:58 IST — Claude helpers reviewed and integration implemented

Reviewed all three isolated helpers and their regression suites. Quotas bind native Desktop version-2 history to the current Desktop account UUID and local OAuth organization; observed account percentages are 18% and 50%, not invented token budgets. The UI shows capture age and explicit last-known/unavailable states; reset times are not present in the native history. Optional existing OAuth credentials are read-only, redirects are denied, secrets are not emitted, and successes/failures are credential-bound and throttled for five minutes.

Spending now preserves independent input/output/thinking/cache-read/5m-write/1h-write counters and uses a separate private Claude monthly ledger with frozen daily official Sonnet 5.5 prices. The parent found and repaired null TTL fields for zero-write responses. Unknown rates remain unpriced; old days are not backfilled. CodexBar confirms response deduplication, explicit incomplete placeholders, distinct 1h cache pricing and local API-equivalent value rather than subscription charges. Current 11-request evidence is 707,459 inclusive tokens and $0.6710568 value.

Session integration uses native registry PID/starttime and lifecycle, supports a session before its first assistant response, retains titles without extracting prompt text, and prioritizes running sessions over bounded idle history. Parent review identified stale working/idle ordering; the session agent added status clock ordering, machine/boot checks and four regressions that reproduced seven failures before repair. Twenty session tests now pass. Claude-only five-second refresh avoids starting Codex/OpenCode. Added integration/UI/launcher regressions and wired all helper suites into the primary test entry point. Source changes are uncommitted; full gates and live deployment are pending.

### 15:51 IST — Combined Claude delivery gates passed

Time correction: the preceding implementation entry labelled 15:58 IST was written around 15:50 IST. All 117 primary tests now pass (6 OpenCode, 7 Claude integration, 16 quota, 20 session, 13 spending, 43 Codex, 12 widget), plus cache contracts, fatal QML lint, QML binding gate and whitespace check. Existing nonfatal qmllint/resource warnings remain unchanged. Parent replayed all real native responses independently using final cumulative counters, rather than relying solely on helper tests: 11 requests, 707,459 inclusive tokens, exact value $0.6710568, 18%/50% account limits. A repeat collection leaves tokens and spending unchanged. Temporary-state evidence is /tmp/claude-integrated-review-_cv0y47n. Sandbox session PIDs are unavailable; completed sessions correctly remain inactive, and the normal host collector must verify actual process visibility after deployment. All source/live changes remain uncommitted. Proceeding with tested standalone delivery only; no fork, auth, model prompt or network publication changes.

### 15:54 IST — Standalone Claude repair delivered and inspected

Atomically copied ten tested source files into the user-owned widget and verified all source/live code hashes. The approved host collector refresh completed normally; it can verify the Desktop session process as alive while native idle correctly keeps running false. The latest Desktop account capture independently changed to 39% (5h) and 52% (7d), while local usage stayed 707,459 tokens / $0.671057. Account limits and local values therefore remain separate. Cache and Claude ledger are private; Codex collector/state were not modified. Reload succeeded and the actual Desktop page visibly shows both quotas, capture age, no running session and Est. Spending $0.67. Saved preview-idle.png and gate logs in the backup. Current shell runtime shows no AI widget load/binding errors; unrelated existing shell warnings remain.

Requested one optional new user-run Desktop task to observe a fresh active/idle lifecycle transition. The agent did not send a model prompt. Documentation now describes the native Desktop source, shared-account scope, missing reset times, exact Sonnet-only verified prices and stale/partial coverage. The standalone preview remains uncommitted; no fork mutation or publication.

## 15:57 IST — Claude limits, spending and session repairs deployed

Three user-requested subagents implemented isolated quota, spending and session helpers; the parent reviewed every helper, requested stale-status ordering fixes, corrected zero-write TTL integration, and deployed the tested standalone/live bundle. All 117 primary tests, cache contracts and QML gates pass. The actual card shows account-wide quotas 39%/52%, capture age and Est. Spending $0.67 for the existing 11 local responses / 707,459 inclusive tokens. No extra Desktop login is required. Native PID verification confirms that the open but completed Desktop session is idle. A new active Desktop turn remains unobserved: the three-minute watch had no new prompt. Do not claim that final live transition is validated. Fixtures cover active/start/stop/stale status ordering.

Desktop version-2 plan-usage history is account/org-bound; stale samples are labelled, missing limits remain unavailable, and reset times are not invented. Claude costs use exact Sonnet 5.5 rates verified 2026-11-09, independent 5m/1h cache writes, native output once, separate private monthly ledgers and frozen daily rates. Unknown rates/TTL and old days without snapshots stay unpriced; later dates mark this snapshot stale. Values are local API equivalents, not shared-account charges. Optional scoped OAuth fallback is read-only and throttled five minutes. No model prompt, auth change, service change, fork edit, commit or push occurred.

Report: /home/methos/Documents/opencode_widget_ryoku_shima/CLAUDE_REPAIR_2026-11-09.md. Backup/evidence: ~/.local/share/ryoku/ai-usage-backup/claude-complete-20261109-154352. Source/live code parity is verified, cache/ledger mode0600, and existing Codex/OpenCode collector bytes are unchanged. The fork remains held out until live validation is accepted.

## 2026-11-09 15:59 IST — API Value label requested

The user requested API Value for every agent. Replaced the conditional Est. Spending/Spending title in the shared AiUsageSpendBody.qml with API Value, covering standalone OpenCode and integrated Codex/Claude cards. This supersedes the prior label requirement; calculation, coverage and tooltips remain intact. Updated current README, plan, changelog and project label rule; historical audit entries retain the labels used at the time. Source/live parity was clean before editing. All changes are uncommitted; validation and live delivery follow.

### 2026-11-09 15:59 IST — API Value label delivered

All agents now use the shared API Value title. All 117 tests, cache contracts, fatal QML lint, QML bindings and whitespace checks pass. Copied the tested component atomically to the live widget with a backup and verified identical bytes. Calculations and data are unchanged. The requested label supersedes Est. Spending and Spending in current UI/docs. No commit, push or fork change.

## 2026-11-09 16:29 IST — User paused Claude recount review

The user reports Sonnet/Haiku model-counter discrepancies after switching from Sonnet 5.5 medium to Haiku 5.5 high within the same chat session. They explicitly prohibit continuing until they say continue after the 5-hour reset, reporting a 13% allowance state. Saved the supplied recount, timing/scope caveats and both screenshots without investigating or changing code. Resume context: /home/methos/.local/share/ryoku/rashin/memory/ai-usage-claude-recount-pending.md. Original screenshot copies and context: /home/methos/.local/share/ryoku/ai-usage-backup/claude-recount-pending-20261109-162937. This pause also holds the previously pending fresh lifecycle check. No collector, test, model, reload, commit, push or fork action was performed.

## 2026-11-09 19:12 IST — Claude recount review resumed

The user explicitly said Continue, revoking the pause. Checked project/fork status and primary/live source parity before the audit. Independent final-response parsing finds 25 unique responses across 51 native assistant rows in two files; all repeated counters for each response are identical. Sonnet total 980,673 comprises input32, output7,522 (thinking1,705/nonthinking5,817), reads831,602 and writes141,517. The output difference is the explicit thinking split, not streaming. Haiku total356,575 at10:40:46.131Z becomes430,498 at10:51:49.944Z after exactly one73,923-token response (input2/output672/read72,544/write705). Both figures include cache writes. Current Haiku739,630 plus Sonnet980,673 equals the private cache1,720,303. All period totals agree; model switching within the same session is preserved. API Value remains the explicitly marked partial Sonnet-only estimate because Haiku has no configured verified price. No application code or live cache was changed during diagnosis. Focused regressions and a permanent numerical report follow; no model invocation or authentication change is needed.

### 19:14 IST — Recount regression reproduces both checkpoints

Added one metadata-only numeric regression to test_claude_usage.py. It replays the observed 15 Sonnet and10 Haiku response counters, repeats each native block to exercise deduplication, keeps the first four Sonnet responses in the older session and switches the continuing session from Sonnet medium to Haiku high. It confirms Sonnet O5.8K/R1.7K, both-session Sonnet scope, single-session Haiku scope, cache-write inclusion, and the exact356,575→430,498→739,630 Haiku checkpoints. All eight Claude integration tests pass. Independent numeric evidence and a frozen sanitized cache are saved privately at /home/methos/.local/share/ryoku/ai-usage-backup/claude-recount-audit-20261109-191418. Source hashes were stable during the audit and every current period/model total matches raw counts. No application code or live cache changes are needed; full regression suite follows.

## 2026-11-09 19:16 IST — Claude recount resolved; no parser repair needed

The user resumed the saved review. Independent raw metadata reconstruction of25 distinct responses across51 assistant records exactly matches every period/model total: Sonnet980,673; Haiku739,630; combined1,720,303. Sonnet inclusive output7,522 is nonthinking5,817 plus thinking1,705; the dashboard intentionally displays O/R separately. Haiku356,575 and430,498 are consecutive five/six-response prefixes; the exact gap73,923 is one later response with input2/output672/cache-read72,544/cache-write705. Cache writes are included. Both quoted rounded values are reproduced; expanded historical screenshot timing cannot independently be proven from the supplied collapsed images. The continuing session switches models without misattribution; the older session contributes only Sonnet.

API Value$0.724512 remains explicitly partial: Sonnet priced, all739,630 Haiku tokens unpriced because no verified Haiku price is configured. No rate dictionary was guessed or changed. Added one sanitized numeric regression for real model-switch counters and three checkpoints; all118 primary tests and cache contracts pass, whitespace check clean. Source/live application parity is unchanged; no runtime code, production cache/ledger, authentication, service, fork, commit or push changes were made. No Claude prompt was run. The fresh active-to-idle live observation remains a separate pending check. Report: /home/methos/Documents/opencode_widget_ryoku_shima/CLAUDE_RECOUNT_AUDIT_2026-11-09.md. Private evidence and gate output: /home/methos/.local/share/ryoku/ai-usage-backup/claude-recount-audit-20261109-191418.

## 2026-11-09 19:23 IST — Claude reset countdowns authorised

The user requests reset counters under both Claude limit bars, matching Codex. The existing UI already renders resetTs, but native plan-usage-history version2 omits deadlines. The existing OAuth fallback has no credential file on this Desktop setup. Found account-bound successful usage HTTP responses in Desktop Chromium Simple Cache; current bodies are Zstandard-compressed and contain exact five_hour/seven_day resets_at. Read only metadata and specific usage bodies, without decrypting cookies, reading credential values, changing auth or calling Claude. Chromium header/footer/hash format was verified against primary Chromium source. Implement a bounded, CRC/key-validated read of only hashed usage endpoint entries, preserving capture age and account/org binding. No inferred reset schedule or percentage resets are allowed. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/claude-resets-20261109-192346. Source/live parity was clean; no fork, commit or push is authorised.

### 19:26 IST — Reset source implemented and focused tests pass

Claude quota helper now reads only four known account-usage endpoint entries by Chromium SHA1 filename, validates exact bound URL/key, version5 header/footer, optional key SHA256 and stream CRCs, requires HTTP200 and a valid HTTP Date, and decompresses bounded identity/gzip/deflate/Zstd bodies. No cookie or auth value is read. The complete response supplies both utilization and resets_at without mixing stale percentages with guessed cycles; newer history is never replaced by older cache data. Passed cached deadlines remain last-known and are not advanced into fabricated new windows. OAuth reuse now preserves a passed deadline and refreshes once at that boundary rather than showing old usage as current during cooldown.

The existing UI renders real countdowns; Claude alone now has an explicit reset-time-unavailable fallback. Added seven quota regressions covering compressed source formats, source precedence, corruption/wrong key/status/account/org, timestamp bounds, expired windows and OAuth reset/cooldown behavior. All23 quota tests pass. A read-only local smoke found a newly captured Desktop response with8% five-hour and62% weekly utilization plus real reset epochs1794250199 and1794308400; the native history file alone still lacks these epochs. Full delivery gates and deployment follow; no model prompt, auth or price change.

### 19:28 IST — Reset delivery gates passed and files installed

All125 primary tests, cache contracts, fatal QML lint, QML bindings and whitespace checks pass. The optional zstd fixture now degrades cleanly on older Python while exercising zstd on this Python3.14 host; all23 focused quota tests also pass after that portability adjustment. Atomically installed the tested quota helper and limits card into the user-owned live widget, with matching source/live bytes and backup under claude-resets-20261109-192346. Normal collector refresh, reload and visual countdown verification follow. Existing OpenCode/Codex collectors, pricing dictionaries and fork remain untouched.

## 2026-11-09 19:30 IST — Claude reset countdowns delivered

The requested five-hour/weekly reset countdowns are now rendered from the native Desktop cached usage response, without decrypting cookies or requiring another login. The account-bound response contains real resets_at missing from compact history. All125 primary tests and both QML gates pass. Installed the quota helper and card atomically; inspected the actual live Claude card showing both timers and real8%/62% account values. Cache remains0600. The five-hour reset is2026-11-09T18:49:59Z; weekly reset is2026-11-10T11:00:00Z. These are captured deadlines, never inferred from local token activity or advanced into a guessed new cycle. Passed captures remain last-known; missing timestamps show unavailable.

Seven new quota regressions cover compressed/validated native sources, wrong account/key/CRC/status, source ordering, invalid timestamps and expired windows/OAuth boundary cooldown. Shortened the added tooltip into separate lines after visual inspection to avoid an overlong line. Backup/evidence: ~/.local/share/ryoku/ai-usage-backup/claude-resets-20261109-192346. Details in memory/ai-usage-claude-reset-countdowns.md. No Claude prompt, auth change, pricing change, fork mutation, commit or push occurred.

## 2026-11-09 19:37 IST — Absolute reset times and CLI clarification requested

The user requests actual reset dates/times instead of relative hours, and asks whether Desktop is required. Change the shared Claude/Codex reset labels to local date/time with timezone, preserving past-deadline and unavailable states. Simplify the source tooltip to distinguish the current Desktop source from CLI subscription-login support and account-wide shared usage. Existing collector already supports scoped saved CLI OAuth credentials without Desktop; add a focused Desktop-absent fixture to verify both deadlines. No auth or data-source changes are required. Source/live parity was clean. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/absolute-reset-times-20261109-193709. Uncommitted, no fork/commit/push.

### 19:40 IST — Local-time formatting and CLI independence verified

Replaced resetIn with resetAt and updated the shared card call. Both agents now show local dates/times plus timezone; past timestamps say reset was rather than being projected forward. Simplified the Claude tooltip to identify current source, support for Desktop/CLI subscription logins, account-wide usage and local timezone; stale wording appears only for stale captures. Added a CLI OAuth fixture with Desktop metadata absent; both real-format reset windows and percentages are returned.

The first full gate failed because the existing Codex QML test still looked up resetIn and expected relative strings. Updated that existing parser/formatter test for absolute timestamps and invalid/past input. A one-off native Qt probe initially timed out because Qt.quit was called before the event loop; moving the probe to a Timer fixed the harness. The actual shipped formatter passes native headless checks for Asia/Kolkata (10Nov12:19AMIST) and America/New_York (9Nov1:49PMEST). No data-source, credential or model changes. Full suite rerun and deployment follow.

## 2026-11-09 19:42 IST — Absolute reset times delivered; CLI support clarified

Installed the tested UsageModel.qml and limits card atomically and reloaded successfully. Both shared Claude/Codex reset rows now show local dates/times and timezone, rather than rounded hours. The actual Claude card was visually checked with resets10Nov12:19AMIST and10Nov4:30PMIST; no related runtime binding errors appeared. All126 primary tests, cache contracts, fatal QML lint, bindings and whitespace checks pass. Native Qt tests also verify Kolkata/NewYork timezone conversion and past-deadline formatting. The old countdown test was updated to the new requested semantics.

CLI subscription quota support is independent of Desktop: a new fixture with Desktop account metadata absent returns both percentages and reset timestamps via the existing saved OAuth path. The current real data is from Desktop; the tooltip now clearly states support for both Desktop and CLI subscription logins, account-wide shared use, and local time. API-key/cloud-provider logins do not expose these subscription windows through this reader. No CLI login was performed or real credential used in fixtures. No collector/auth/data/pricing/fork changes, commit or push. Backup and preview: ~/.local/share/ryoku/ai-usage-backup/absolute-reset-times-20261109-193709. Source/live code parity is verified.

## 2026-11-09 19:58 IST — Dropdown highlight overlap repair authorised

The user reports adjacent dropdown highlights morphing together while moving through options. AiUsageMenu.qml currently draws per-row fill for current OR hovered, so selected and hovered adjacent rows can both have touching fills. Replace these with one shared, non-animated row background; retain current-option accent/checkmark and add a small vertical inset. The shared component covers agent and period menus. Source/live parity is clean; backup: /home/methos/.local/share/ryoku/ai-usage-backup/menu-highlight-20261109-195824. Verify real pointer movement in an isolated Qt menu, then repository gates before live delivery. No collector, data, fork, auth, commit or push change is part of this UI fix.

### 20:01 IST — Pointer/image probe reproduces and verifies highlight repair

Used QtQuickTest with the actual AiUsageMenu.qml and isolated style/service stubs. Real mouse movement plus rendered-pixel checks reproduces two simultaneous backgrounds before repair (selected Claude plus hovered row); the expected-single-background assertion fails. After replacing per-row backgrounds with one shared, vertically inset rectangle and stable hovered/current selection, the same probe passes. It sweeps all three agent rows, checks selected value stays fixed during hover, verifies picked value and menu close on click, reopens the menu, and sweeps five period rows. Selected text/checkmark bindings remain intact. No position/color animation is added. Probe uses temporary HOME/config/cache and no collectors, authentication or model calls. Saved isolated QML/style fixtures and before/after output in the backup. Full primary/QML gates and live installation follow.

## 2026-11-09 20:02 IST — Dropdown highlight fix delivered

All126 primary tests, cache contracts, fatal QML lint, bindings and whitespace checks pass. The independent Qt pointer/render probe also passes after reproducing two filled rows before the repair. Installed the tested AiUsageMenu.qml atomically with matching source/live bytes. Agent and period menus now draw one background at a time, retain the selected text/checkmark, and reset hover state on close/reopen. The highlight is inset within the target row and has no animated geometry that could merge adjacent fills. Backup/evidence: ~/.local/share/ryoku/ai-usage-backup/menu-highlight-20261109-195824. No collectors, tokens, account data, authentication, fork, commit or push changes. Shell reload follows.

### 20:03 IST — Menu reload verified

Shell reload completed successfully and status is running. The latest runtime log has no AiUsageMenu/AI widget binding/type/reference errors. Final application source/live parity is clean. The isolated pointer/image fixture and before/after outputs remain in the menu-highlight backup for reproduction.

## 2026-11-09 20:10 IST — Claude display name accepted

The user considers the Claude section ready and requests the name Claude instead of Claude (preview). Updated the primary agent menu and widget settings manifest, retaining the stable claude value and existing settings. Current README selector names match. This is a display-name change only; remaining documented validation/pricing limits and the separately held downstream fork are not silently changed. Source/live parity was clean before editing. No collector, data, login, commit or push changes. Gates and live delivery follow.

### 2026-11-09 20:11 IST — Claude name delivered

Both the agent dropdown and widget settings now say Claude. All126 tests, cache contracts, QML lint/bindings and whitespace checks pass. Atomically copied both tested files to the live widget and verified source/live bytes. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/claude-label-20261109-201131. Stable claude values and settings are unchanged. All edits remain uncommitted.

## 2026-11-09 20:23 IST — Fork ai-usage publication preparation authorised

The user requests publishing the current code to methos28/ryoku on ai-usage. Verified the exact origin URL, checked both working trees/indexes, and fetched the branch: local/remote head is c2dbdc496bd2b123f50ad01476541acc7ee9f3e3. Prowl wip confirms only the previously recorded widget work. The new request supersedes the prior Claude downstream hold for preparing this accepted code. Ported current widget code/helpers while preserving the fork built-in flag/version line and its stronger OpenCode storage-schema compatibility. Set the downstream widget version1.3.0 and added Claude settings. Did not copy the obsolete standalone live-cache test artifact or private audit files. Ported four Claude suites and current widget/absolute-time checks, with an OpenCode fixture adapted to the fork public source/version names. Pre-port working-tree patch and source backup: /home/methos/.local/share/ryoku/ai-usage-backup/fork-publication-20261109-202349. Delivery/CI checks and final staged review follow. No commit or push has occurred; the explicit separate commit-approval rule remains in force.

## 2026-11-09 20:34 IST — Fork publication staged and verified; commit approval pending

The complete port is staged on methos28/ryoku:ai-usage with30 files. All134 fork tests, shell/cache fixtures, package/source delivery, QML gates, WM isolation, staged whitespace and manual normal pre-commit/commit-message checks pass. Runtime files match canonical standalone code except preserved built-in metadata/version1.3.0 and stronger downstream OpenCode compatibility. CI now includes the added suites on ai-usage using Python3.14. Source/pre-port patch, staged patch, proposed message and gate logs are backed up at ~/.local/share/ryoku/ai-usage-backup/fork-publication-20261109-202349. Review summary: FORK_PUBLICATION_READY_2026-11-09.md. No primary or fork code commit and no push has occurred. The project rule explicitly says remote pushes do not authorize new commits, so creation of the reviewed commit needs the user's explicit approval before the already-requested push. No upstream/channel/live/auth changes occurred.

## 2026-11-09 20:36 IST — Fork commit and push explicitly approved

The user explicitly authorises creating the reviewed commit and pushing it to the fork ai-usage branch. Rechecked origin=https://github.com/methos28/ryoku.git, local branch ai-usage, remote head c2dbdc496bd2b123f50ad01476541acc7ee9f3e3 and exact staged-patch equality with the tested/reviewed port. All134 local tests and required gates remain applicable; no code changed after them. Proceeding through normal commit/push hooks without force or bypass.

## 2026-11-09 20:39 IST — Fork ai-usage committed and pushed

Following the user's explicit commit-and-push approval, created eb91adfd3de6e963e4bd25a1156907a10563260e ([global] ai-usage: bundle collectors and add subscription tracking) using normal hooks, then pushed origin HEAD:refs/heads/ai-usage without force or bypass. GitHub's actual remote head matches the local commit exactly; the fork working tree is clean and tracks origin/ai-usage. All134 prior local tests and package/source/QML/delivery gates apply to the exact published staged patch. Only the fork ai-usage branch was advanced; no standalone, upstream or channel branch was pushed. Commit: https://github.com/methos28/ryoku/commit/eb91adfd3de6e963e4bd25a1156907a10563260e. The first GitHub Actions run query returned no runs; no remote CI success is claimed.

## 2026-11-09 20:46 IST — Current-state PR description refreshed

At the user's request, rewrote RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md for the published fork ai-usage state at eb91adfd3de6e963e4bd25a1156907a10563260e. The draft now covers Claude CLI/Desktop collection and quotas, native session detection, API Value semantics and pricing gaps, repaired Codex accounting, bundled collectors, shared module discovery, local reset times and the dropdown repair. It records the 134 passing local tests, live/fixture coverage and remaining manual checks without claiming remote CI success. Rechecked the clean fork and exact commit; GitHub Actions still reports no runs for it. These are local draft and record changes only. No runtime code, GitHub PR, commit or remote branch changed.

## 2026-11-09 22:22 IST — Scope correction: widget-only collectors

The user rejects replacing Rashin's collector executables or modifying distro documentation. Restored the fork's ryoku/rashin/usage/opencode-usage and codex-usage as regular files from the original upstream review base (0749ec35005cdae3b5c925eb91c32a6904a998d5), restored docs/structure.md, removed the added docs/ai-usage.md, and restored WidgetManagerPanel.qml. Removed the expanded generic widget installation API while retaining only bundled Island module discovery/load/settings wiring. Widget bin/ remains self-contained; direct collector defaults now use private caches and the launcher no longer takes the system cache lock. Delivery/regression fixtures now exercise only the installed widget bundle, with failing global collector stubs and preserved global-cache sentinels. This supersedes earlier decisions to alias Rashin entry points and share their lock. Changes are local and uncommitted; tests and final scope review are in progress. No installed Rashin files, system service, remote branch or existing user state were edited.

## 2026-11-09 22:26 IST — Widget-only scope correction verified

The final staged review diff against original upstream 0749ec35005cdae3b5c925eb91c32a6904a998d5 contains 41 paths: 26 widget files and 15 required wiring/check/changelog paths. The entire docs/ and ryoku/rashin/ trees, original collector workflow and WidgetManagerPanel.qml match upstream exactly, including regular executable modes for Rashin's collectors. The generic example installer is preserved. Added a separate widget CI workflow rather than changing Rashin's workflow. All 131 fork tests and 127 primary tests pass, as do cache contracts, shell fixtures, QML lint/bindings, delivery, WM isolation, staged whitespace and the normal pre-commit hook. A private-lock bootstrap test initially exposed a missing retry status after removing the shared lock; the bundled Codex executable now returns 75 for its own lock contention. Tightened the bootstrap fixture to wait for the selected cache instead of accepting the intentionally retained prior-agent display; three repeated native QML runs pass. Installed only the three tested collector/launcher scripts into the user-owned live widget, without changing installed Rashin files, services or credentials. Updated local PR drafts to describe this narrowed scope. Backup and review evidence: /home/methos/.local/share/ryoku/ai-usage-backup/widget-only-scope-20261109-222610. Corrections remain staged and uncommitted; remote ai-usage still points to eb91adfd3de6e963e4bd25a1156907a10563260e.

## 2026-11-09 23:16 IST — Multi-model API Value implementation requested

The user explicitly requires API Value across Codex and Claude models, superseding the previous Sonnet-only Claude pricing scope. Official OpenAI and Anthropic pricing pages were fetched before implementation. Added widget-owned model-pricing.py and model-prices.json with 64 OpenAI and 32 Claude model IDs, public metadata refresh with bounded credential-free downloads, offline fallback, exact ID/provider-prefix matching, context and service tiers. Claude now includes Haiku 5.5's per-request 100,000-token threshold, cache TTL rates and supported Opus Fast pricing. The Codex estimator shares the pricing helper and supports published Fast/Priority, Flex, Batch and Ultrafast rates. Today's snapshots gain missing models and service tiers without changing saved rates; earlier daily snapshots remain frozen. Work is in progress and uncommitted. No Rashin files or distro documentation were changed. Tests, live totals and fork port follow.

## 2026-11-09 23:30 IST — Public pricing refresh and mixed-model checks

Live public-only probes successfully refreshed both provider catalogs from their official pricing markdown, retaining 64 OpenAI and 35 Claude model IDs. No account credentials or usage were sent. Added regression coverage for native current/legacy models, published Claude snapshot IDs, exact matching, Haiku cache-inclusive 100k boundaries, OpenAI Fast/Priority/Flex/Batch/Ultrafast and long-context boundaries, Opus Fast, new-model refresh, offline fallback, failure throttling, private catalog writes and frozen-price extension. Existing Sonnet-only daily snapshots gain Haiku automatically without a cache reset. Found and preserved the existing behavior allowing today's stale provisional rates to refresh while retaining prior-day prices. Mixed-family Claude arithmetic and Codex service-tier suites pass; full primary/fork gates are running. Corrected two test adaptations for the changed tooltip and downstream QML source path. No Rashin files, original collector CI, distro docs or system services changed.

## 2026-11-09 23:40 IST — Multi-model API Value verified and delivered

The shared catalog now includes 65 OpenAI and 35 Claude IDs, including the published legal-model configuration, snapshot aliases and native legacy models. All 147 primary and 151 fork tests pass, along with cache contracts, shell fixtures, QML lint/bindings, delivery, WM isolation, staged whitespace and the normal pre-commit hook. Both public pricing feeds were probed successfully without credentials. Installed only tested widget files/helpers/catalog and reloaded the shell. An independent Decimal recount over 25 native Claude responses matches USD 0.750554: Sonnet USD 0.7245122 and Haiku USD 0.02604219. All 1,720,303 tokens are priced, with zero unpriced tokens and unchanged token totals. The live Codex cache prices all three observed model IDs; its remaining 2,514,688 unpriced tokens are 29 requests from 2026-11-06, a day with no saved price snapshot. That pre-existing historical cutoff is preserved rather than assigning current rates retrospectively. A live quota RPC initialization attempt fell back to existing rollout limits; pricing updated independently and the quota code was unchanged. The final staged review diff contains 44 paths, all within the widget or the required wiring/check/changelog allowlist. Rashin files, distro docs, original collector workflow and WidgetManagerPanel match the original upstream base. No installed Rashin files, services or credentials changed. Runtime source/fork/live parity is verified. Backup, independent arithmetic and staged patch: /home/methos/.local/share/ryoku/ai-usage-backup/multi-model-pricing-20261109-233156. Updated the local PR draft and plan to supersede Sonnet-only limitations. Changes remain staged and uncommitted; no push or GitHub PR mutation occurred.

## 2026-11-10 01:00 IST — Claude quota freshness diagnosis after reset

The user observed 97 percent at the old 00:20 IST five-hour deadline until opening Claude Desktop. Read-only inspection confirms the current quota source is desktop-cache, observed at 2026-11-10 00:56:24 IST; Desktop plan-usage-history.json has the same modification time, and the widget cache was published at 00:56:33 IST. The refreshed five-hour window reports 2 percent and a 05:20 IST deadline. No readable CLI OAuth credentials file exists in the active Claude config directory. Thus background widget polls can reread Desktop captures but cannot independently refresh the provider account with this login source. collect_quota uses fresh Desktop data first, tries saved CLI OAuth for stale/missing captures, and preserves last-known measurements when no fresh authenticated source is available. A passed deadline marks captures stale; the UI is intended to show Last known and reset was rather than invent a zero percentage or future reset. Opening Desktop refreshing its own account response explains the observed update; the exact previous event sequence cannot be independently replayed after its cache is overwritten. No code, authentication, account or remote changes made.

## 2026-11-10 01:16 IST — Live CLI OAuth quota refresh verified

The user installed Claude Code CLI and requested checks while a prompt was active. /usr/bin/claude is present. The active config now has a readable subscription OAuth credential with user:profile scope, expiring at 2026-11-10 09:08:50 IST. No credential contents were printed or changed. Invoked the installed quota helper with the real saved credentials, Desktop redirected to an empty temporary path, PATH excluding CLI executables, and subprocess.Popen blocked. One authenticated usage GET succeeded independently: source oauth, current five-hour 5 percent (reset 05:20 IST), weekly 75 percent (reset 16:30 IST). A second helper call five seconds later reused the measured result with no second request. The real CLI prompt was not stopped or relaunched; the test proves no CLI executable invocation or Desktop capture is required by the quota reader, rather than observing an actual closed CLI process. A normal bundled collector refresh still selected a recent Desktop capture, matching the documented fresh-Desktop-first policy; it reported the same percentages. Source preference can retain a Desktop capture for up to 20 minutes, while OAuth requests use a five-minute cooldown and a reset-boundary retry. Automatic collection runs on module load and while visible. Installation alone does not authenticate: saved valid subscription credentials are required, and the widget does not renew expired login credentials. Native session rows currently report process-unverified/unfinished-turn-unverified for the new CLI run; active-session verification was not established in this quota test. No runtime code, configuration, auth state, process, commit or remote changes were made. Normal private usage caches refreshed through the existing bundled launcher.

## 2026-11-10 01:30 IST — Full module bug audit started

The user requests a full codebase bug test before developer review. Audit scope covers widget collectors, accounting/pricing/quotas/session lifecycle, QML state and interaction, packaging and failure paths. Reproducible defects may be repaired, with focused regressions and full gates before live delivery. Existing staged fork work and primary widget sources are backed up at /tmp/ai-usage-full-audit-20261110; no history will be rewritten or commit/push performed. Rashin files and distro docs remain protected. The new CLI registry uses a different PID namespace from the agent sandbox, explaining process-unverified in sandbox-produced caches; this is not evidence of a host session-detection defect. Baseline 147-test run is in progress.

## 2026-11-10 02:56 IST — Full audit repairs and regression evidence

Reproduced and repaired: OpenCode cache reads omitted from the cache-inclusive header; 32-bit QML token overflow and reset timestamps; invalid top-level cache shapes accepted as data; future file timestamps treated as fresh; predictable OpenCode temporary/lock symlinks and non-private/non-atomic publication; NaN source costs producing invalid JSON; lock contention returning success instead of retry; unescaped SQLite URI paths and adaptive schema reads failing without a timestamp column; active Codex/OpenCode sessions hidden by the recent-idle cap; truncated model counts; DST Today charts losing the final hour and calendar period cutoffs shifting; malformed frozen pricing/bundled catalogs and large context thresholds; Claude token collection blocked by unavailable pricing state; malformed nested ledger dates; late Claude model metadata and empty synthetic usage records; failed standalone installation deleting the previous widget. Installer staging/rollback/reload failure and lock FD inheritance are now tested; the FD test caught and corrected a lock-inheritance issue in the initial repair before deployment. Removed the obsolete runtime diagnostic that invoked a shared global collector. The demo utility now requires an explicit output directory and refuses existing caches rather than overwriting shared state. Static Ruff runtime checks pass after removing five dead locals; production SQLite handles were already closed, and the remaining fixture connection warning was fixed. Empty-history reset, malformed Codex activity-state containers, and host CLI idle/PID verification passed without needing logic changes. Native pointer/render tests pass at densities 0.75, 1 and 1.5. Real Codex request IDs and every token component match the pre-audit implementation for 1,151 requests (0.263s before, 0.258s after, read-only extraction). Complete primary/fork runs pass before the final standalone installer FD regression; no live delivery or commit/push has occurred for these audit changes.

## 2026-11-10 03:01 IST — Audit integration gates and report prepared

Complete source/fork suites pass. Native Qt pointer/render probes pass at three densities; isolated Ruff runtime checks and ShellCheck warning gates pass. ShellCheck requested an explicit empty CDPATH assignment; the launcher now uses CDPATH='' with unchanged behavior. The final standalone installer lock-inheritance regression passes after closing that descriptor only in the reloader child. Detailed findings and validation limits are recorded in BUG_AUDIT_2026-11-10.md. Final normal pre-commit and complete primary recheck are finishing; live delivery remains pending those results. No commit or push.

## 2026-11-10 03:05 IST — Full audit complete; tested repairs delivered

All 172 primary and 172 fork tests pass; shell fixtures, cache contracts, isolated Ruff runtime checks, ShellCheck warning gate, QML lint/compilation/bindings, delivery, WM isolation, staged whitespace and the normal pre-commit hook pass. Native menu pointer/render probes pass at densities 0.75, 1.0 and 1.5. Read-only extraction preserves all 1,151 real Codex request identities and token components. Installed 12 tested runtime files atomically into the user-owned widget, removed the obsolete shared-cache diagnostic and reloaded the shell successfully. Ran the delivered collector outside the sandbox in the desktop namespace: all three caches are valid JSON with mode 0600, Codex quota source is rpc, and no auth or model prompt was changed or launched. 4 earlier dated price dictionaries remain byte-value identical after the live refresh. The apparent CLI PID issue was sandbox namespace isolation; host idle/alive verification passed earlier. No new paid Claude start-to-finish run or full cross-platform desktop installation was performed; detailed scope/limits are in BUG_AUDIT_2026-11-10.md. Protected Rashin/docs/original CI/widget-manager paths remain unchanged against upstream review base. Updated local plan and PR draft to match the audited state. Final backup/evidence: /home/methos/.local/share/ryoku/ai-usage-backup/full-bug-audit-20261110-030253. Fork changes remain staged; no commit, push, GitHub PR or upstream mutation occurred.

## 2026-11-10 03:08 IST — Audited fork push requested; separate commit approval required

The user requests pushing the current state to methos28/ryoku:ai-usage. Verified origin, branch and actual remote head eb91adfd3de6e963e4bd25a1156907a10563260e. No unpublished commit exists; all changes are staged. The exact index matches the audited ready-to-commit.patch (SHA256 991fc01ac2dc0ec5fb0ba009bef9423689bab5bdb5b03ca7cca7b30b8bbbd1ad), both 172-test logs pass, no unstaged fork changes exist, and protected ecosystem files match the original upstream review base. Prepared /tmp/ai-usage-ready-commit-message.txt for [global] ai-usage: isolate collectors and fix usage reporting. The project's explicit commit policy says remote push requests do not authorize new commits, so commit creation requires separate approval. No commit, push or remote mutation has occurred.

## 2026-11-10 03:11 IST — Audited widget committed and pushed after explicit approval

The user explicitly approved creating the reviewed commit and pushing it. Revalidated the exact audited staged patch, fork origin and ai-usage branch, created b650d0c474553931ef551332051e46fe3d651d62 ([global] ai-usage: isolate collectors and fix usage reporting) through normal hooks, then pushed origin HEAD:refs/heads/ai-usage without force or bypass. GitHub's actual remote head matches the local commit exactly. The fork working tree/index are clean and track origin/ai-usage. Protected Rashin, distro docs, original collector CI and desktop widget-manager paths still match the original upstream review base. All 172 local tests for each delivery target remain applicable to the exact committed patch. Only the fork ai-usage branch was pushed; no standalone, upstream or channel branch changed. Commit: https://github.com/methos28/ryoku/commit/b650d0c474553931ef551332051e46fe3d651d62. GitHub workflow Shima AI usage widget started for this exact SHA, run 42704607503; its result is being checked.

## 2026-11-10 03:11 IST — Published fork CI passed

GitHub Actions Shima AI usage widget run 42704607503 completed successfully for published commit b650d0c474553931ef551332051e46fe3d651d62. Verified with gh run watch --exit-status and run metadata. Remote CI: https://github.com/methos28/ryoku/actions/runs/42704607503. Publication is complete; fork working tree is clean.

## 2026-11-10 03:20 IST — Published-state PR description rewritten

At the user's request, rewrote the local RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md around the full branch diff at b650d0c474553931ef551332051e46fe3d651d62. The draft now leads with the optional self-contained Shima dashboard, all three agents, private bundled collectors, multi-model API Value, account limits, audited fixes and minimal shared wiring. It cites the successful exact-commit CI run, 172 fork tests, native GUI probes and real-data verification, and retains material source/auth/pricing/manual-validation limits. No distro docs, runtime code, fork working tree, GitHub PR, commit or branch changed.

## 2026-11-10 12:03 IST — New unstable-dev commits checked; no widget port needed

The user requested checking new unstable-dev work for widget impact and replicating it to ai-usage and this PC if needed. Fetched upstream unstable-dev and fork ai-usage/unstable-dev. The upstream and remote fork unstable-dev heads are cd1a06478d5b7c8f952180c89c1f42576fad41da; ai-usage remains b650d0c474553931ef551332051e46fe3d651d62 locally and remotely. Three upstream-only commits update the bug-report form, retire two project-management workflows and their advisory CI entries, and bump VERSION to 1.10.3. Five incoming paths have zero overlap with the feature's 44 paths. The widget workflow, runtime, loader/settings, collectors and delivery paths are unchanged. A conflict-free merge-tree simulation preserves every feature path; no merge was applied because the conditional impact requirement was not met. All 172 fork tests plus Codex shell fixtures and the cache contract pass again. Source/live runtime parity holds, excluding generated Python bytecode; all three private caches are valid JSON objects with mode 0600. Fetch observed a prior remote force-update of fork unstable-dev from f26ede8ad to official upstream; local unstable-dev and the complete ai-usage feature history remain preserved. No code, branch tips, installed files, services, credentials, commits or remote branches changed. Audit records are uncommitted. Full evidence: UPSTREAM_CHECK_2026-11-10.md; test logs: /tmp/ai-usage-upstream-check-20261110/. The review branch remains three upstream commits behind intentionally; local and remote ai-usage are synchronized.

## 2026-11-10 12:06 IST — Explicit branch synchronization requested

The user now requests synchronizing ai-usage with the latest unstable-dev commits, superseding the earlier conditional decision to leave unrelated upstream work unmerged. This authorizes the normal merge needed for branch synchronization while preserving all existing feature history. Refetched both remotes: upstream and origin unstable-dev remain cd1a06478, and origin ai-usage remains b650d0c47. Saved an independent Git bundle and exact pre-merge/tree manifest at /tmp/ai-usage-sync-20261110/. Staged a normal non-fast-forward merge without conflicts. The five staged changes exactly match upstream, and all 44 feature paths are byte-identical to the published widget revision. Regression and repository gates are running before finalizing the merge. No package, live shell, service, collector, credential or standalone source changes are needed. Only the fork ai-usage branch is the synchronization target.

## 2026-11-10 12:07 IST — ai-usage synchronization completed and published

Created normal merge commit 4df46ffca777856ad13c04bbdf5b9363b9fd1e67 with parents b650d0c474553931ef551332051e46fe3d651d62 and cd1a06478d5b7c8f952180c89c1f42576fad41da, then pushed only origin ai-usage without force or hook bypass. Actual GitHub remote head matches the local commit; worktree/index are clean, and HEAD..upstream/unstable-dev contains zero commits. All 44 widget feature paths remain byte-identical to pre-sync HEAD. The merged tree passes all 172 fork tests, Codex shell fixtures, isolated cache contract, CI-gate shell syntax, delivery, WM isolation, staged whitespace and normal pre-commit/commit-message/pre-push gates. Local unstable-dev stays preserved at f26ede8ad and remote unstable-dev stays cd1a06478. No runtime widget changes or live deployment were necessary. No package upgrade, boot configuration, standalone implementation, services, credentials or upstream remote was changed. Backup bundle, pre-merge manifest and test logs are at /tmp/ai-usage-sync-20261110/. Audit notes remain outside the fork and uncommitted. Detailed report: UPSTREAM_SYNC_2026-11-10.md.

## 2026-11-10 12:15 IST — Clean rebuild preparation requested; old port frozen

The user wants the widget project and complete bundle separated temporarily before deleting ~/ryoku-arch and the fork with its branches. They request recording only required changes to Ryoku defaults, excluding Rashin's opencode-usage and codex-usage. The next port must start from a fresh unstable-dev checkout, recreate ai-usage, and commit the minimal reviewed result. Do not restore old branch history or cherry-pick the historical commits. Current task is backup and handoff only: report readiness, then wait for the user's deletion and fresh clone. No deletion, clone, branch creation, commit or push is part of this preparation phase. Preserve the existing live widget and private data. Widget-owned bundled collectors remain part of the self-contained module; no source file under ryoku/rashin/usage or its systemd units belongs in the rebuild payload. Keep historical tests/CI and project records separate from the runtime import, and do not automatically restore changelog entries or unrelated repository changes. The measured current tip diff is 12,245 additions/5 deletions: 6,755 widget runtime lines, 2,046 price-catalog lines, 3,295 test lines, 69 CI lines, 19 changelog lines and 61 shared-wiring additions/5 deletions. This records the size without silently dropping working features or claiming the full preserved bundle is 5,000 lines.

## 2026-11-10 12:18 IST — Independent rebuild backup verified; waiting for fresh clone

Saved /home/methos/Documents/ai-usage-rebuild-backup/20261110-121656 and its sibling .tar.gz archive with SHA-256 sidecar, outside ~/ryoku-arch and ~/Projects/ryoku-unstable. The runtime import contains exactly 28 widget files. wiring.patch records only CustomWidgets.qml, IrisOptions.qml and IrisCustomModule.qml; saved upstream defaults plus previous results and verified applying the patch reconstructs the exact intended files. Eleven tests and one widget CI file are preserved separately, not in runtime. The entire current standalone working project (70 source/record files including untracked work and two internal relative compatibility symlinks) is preserved without Git history or generated bytecode. No Rashin source/service paths, old branch history, release/tooling changes or changelog patch are in the import. Both source variants are preserved: standalone versus fork differs only in OpenCode CLI/source labels and built-in manifest metadata (version, description, builtin flag), with exact diff recorded. Live matches standalone. Verified source bytes, executable modes, internal symlink targets, and archive extraction against every manifest entry. Old clone worktrees and live widget remain untouched. No deletion, clone, branch creation, commit or push performed. User may now delete the intended clones/fork and provide the fresh checkout before the separately authorized minimal ai-usage branch recreation and commit. Runtime size has not been reduced by this preservation task; test/catalog/runtime counts are recorded in REBUILD.md for the later scope review.

## 2026-11-10 12:36 IST — Fresh fork port, commit and push explicitly authorized

The user supplied https://github.com/methos28/ryoku.git and requested a fresh unstable-dev clone, required widget integration, and commit/push as ai-usage-dashboard. The new checkout is /home/methos/ryoku-arch; the older /home/methos/Projects/ryoku-unstable is frozen historical context and must not be used or pushed. Use only the saved 28-file widget runtime payload, the three required shared QML wiring changes, and a new initial-feature entry under Added in root CHANGELOG.md. Do not restore old fixes/changelog sections, test/CI additions, Rashin collectors/services, old commits or unrelated files. Validate using the separately preserved checks outside the actual submission. This supersedes the prior wait phase and old ai-usage branch name. The user requires submission descriptions to treat this as the first PR/new feature until they explicitly say otherwise; track each PR they identify. No PR currently exists for this fresh submission, and no PR may be created against Ryoku-dev/ryoku without the user's explicit later instruction. No PR creation of any kind is requested in this task. Commit and push only the fork's ai-usage-dashboard branch after validation.

## 2026-11-10 12:39 IST — Minimal fresh port staged and validated

Fresh methos28/ryoku unstable-dev clone at /home/methos/ryoku-arch has base cd1a06478d5b7c8f952180c89c1f42576fad41da, matching the actual official upstream head. Created ai-usage-dashboard directly from it. Copied only the saved 28-file widget runtime to ryoku/shell/quickshell/inir/defaults/widgets/ai-usage and applied only the three-file wiring patch. Root CHANGELOG.md gains exactly four lines in Added, describing the initial feature. The exact stage allowlist is 32 paths, 8,866 additions and 5 removals. Tests, CI, Rashin, package rules, docs, hooks and upstream AGENTS.md remain untouched. All 172 preserved fork regression cases plus shell/cache checks pass against the actual new source through an external validation tree at /tmp/ai-usage-dashboard-validation-20261110/tree. All 21 changed QML files pass fatal-load lint, and Python/JSON/shell syntax and staged whitespace pass. ShellCheck is unavailable on PATH; its optional hook check is not claimed as run. No runtime logic or live widget data changed. Normal commit and push remain pending; no PR has been created.

## 2026-11-10 12:40 IST — Commit preparation corrections

Correction to the preceding entry: the staged whitespace check initially failed on one empty EOF line in each of AiUsageEmptyCard.qml and AiUsageWindowRow.qml; removed those two empty lines only, preserving all code and comments. The check now passes. An attempted commit before completion of that check stopped without creating a commit because the fresh clone lacked author identity. Copied the existing user's repository-local methos28 noreply identity to the new clone; no global identity changed. Updated the commit message to satisfy the repository's attribution-term gate. Regression/runtime code is unchanged from the passing 172-case run, and all other staged paths remain the same. Final staged size is 8,864 additions/5 deletions. Normal hooks still run for the actual commit.

## 2026-11-10 12:43 IST — Fresh ai-usage-dashboard committed and published

Created 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667 ([global] shima: add bundled AI usage dashboard) as one direct child of fresh fork unstable-dev cd1a06478d5b7c8f952180c89c1f42576fad41da. Normal pre-commit, commit-message, post-commit and pre-push hooks passed, including delivery, WM isolation, QML binding checks, package dependency resolution and vendored seam parity. The optional ShellCheck executable is absent and is not claimed as run. Pushed only methos28/ryoku:ai-usage-dashboard without force. GitHub's actual head equals local HEAD, the fork's unstable-dev remains unchanged, and the new checkout is clean with 0/0 divergence from origin/ai-usage-dashboard. Configured the single-branch clone to fetch the new branch so local tracking works. Exact final submission: 32 files, 8,864 additions and 5 removals: 28 widget files including private bundled collectors/catalog, three QML discovery/settings/loading changes, and four new lines only in CHANGELOG.md Added. No Rashin collectors/services, tests/CI, package rules, upstream docs/AGENTS/hooks, VERSION, old history or other files changed. All 172 external regression cases plus collector/cache checks and QML fatal-load lint passed against this source; only two empty EOF lines were trimmed after the semantic tests. No live widget redeploy, data collection, account operation or package upgrade occurred. Local RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md describe the whole new feature as submission 1. PR_TRACKER.md records the published branch; no PR has been created, and none against Ryoku-dev/ryoku is authorized unless the user explicitly requests it later. Detailed evidence: DASHBOARD_SUBMISSION_2026-11-10.md and /tmp/ai-usage-dashboard-validation-20261110/.

## 2026-11-10 12:56 IST — Fifteen-second background refresh requested

The user requests automatic refresh every 15 seconds, plus an earlier refresh when opening the dashboard. Existing UsageModel polls only while visible (60 seconds for most agents and 5 seconds for Claude); Shima also unloads the whole page 20 seconds after closing. Move collection into a widget-owned QML singleton so it survives page unloading for the rest of the shell session, refreshes all agents regardless of selected tab, and coalesces overlapping requests. The worker begins when the module first loads; a module that has never loaded in a new shell session cannot instantiate its own singleton. This lifecycle limit must be stated rather than claiming a login-started daemon. Keep the immediate open request and existing private collector/caches; Claude quota-source limitations remain unchanged. No Rashin/service/shared desktop changes or new branch tests/CI are authorized or needed. The prior commit/push task is complete; this new runtime enhancement will remain uncommitted unless separately requested. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/background-refresh-20261110-125642.

## 2026-11-10 13:04 IST — Fifteen-second background refresh implemented and verified live

Moved collection from each visible UsageModel into widget/refresh/UsageRefresh.qml, registered by a local qmldir as an engine-lifetime singleton. Its 15,000 ms timer runs after the first module load even when no UsageModel/page survives. It always invokes the complete bundled batch, so all installed agents refresh regardless of selected tool; open requests trigger an earlier run and share an active process rather than overlap. Private collector lock contention retries after two seconds even with the page closed. Each UsageModel retains its existing cache parsing/loading and listens for shared completion. Reopening reads the singleton readiness state. The worker begins on the first module load in each shell session; it is not a login daemon and does not run before that. No Rashin, services or shared shell files changed. The fork contains only UsageModel.qml, two refresh-module files and the existing Added feature-entry wording as this enhancement's delta; no test/CI changes were copied into the fork. Updated primary tests/docs and first-feature PR draft only outside the submission.

All 174 primary tests pass via test/run.sh, including two new real-Qt checks for the 15-second interval after page destruction, refresh on reopening before the next tick, background retry and process coalescing. Initial probe timeouts were a test harness calling Quickshell.quit instead of Qt.quit; correcting that harness made both probes pass. Sixteen fork UI and five shared discovery/delivery checks pass externally against the actual fork source. QML load lint, two-file bindings, delivery, WM isolation and whitespace checks pass. Normal commit hooks were not invoked because no new commit was requested. Atomically installed exactly three tested runtime files into the user-owned live widget and reloaded through ryoku-shell. Opened the Desktop page once, closed it, and observed all three real private caches updating for 43 seconds, beyond Shima's 20-second page-unload timeout. Changed-agent samples: [{'elapsed': 0.0, 'changed': ['opencode-usage', 'codex-usage', 'claude-usage']}, {'elapsed': 1.0, 'changed': ['opencode-usage']}, {'elapsed': 3.0, 'changed': ['codex-usage', 'claude-usage']}, {'elapsed': 15.0, 'changed': ['opencode-usage']}, {'elapsed': 16.0, 'changed': ['codex-usage', 'claude-usage']}, {'elapsed': 29.0, 'changed': ['opencode-usage']}, {'elapsed': 30.0, 'changed': ['codex-usage', 'claude-usage']}]. All three caches are valid JSON with mode 0600; source/fork/live runtime bytes match. Claude quota cooldown/auth/Desktop-source limitations are unchanged. No paid model prompt, credential, package or legacy service changes were made. Changes remain local and uncommitted/unpushed; published head is still 5c9d9f11c and no PR was created. Report: BACKGROUND_REFRESH_2026-11-10.md.

## 2026-11-10 13:20 IST — First-feature PR description aligned with published branch

The user requested the initial PR description. Verified the actual published ai-usage-dashboard head remains 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667. Rewrote RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md as the first introduction of the whole module: supported agents, local usage/history/sessions/models/activity, account quota windows, local API Value, private bundled collectors and required Shima integration. Description cites the 172-case validation applicable to the published source and excludes the pending local 15-second worker, which has not been committed/pushed. No prior-attempt/fix narrative, issue number or PR number was invented. No runtime, commit, push or GitHub PR change occurred.

## 2026-11-10 16:27 IST — Primary source synchronization reaffirmed and checked

The user explicitly requires app changes in opencode_widget_ryoku_shima as well as the ai-usage-dashboard port. Verified both widget trees have the same 30 runtime files. The 15-second enhancement's UsageModel.qml, refresh/UsageRefresh.qml and refresh/qmldir are byte-identical across primary, fork and live copies. Existing differences are limited to documented OpenCode source/CLI labels, built-in manifest metadata, and two EOF blank-line differences from the port whitespace gate; no refresh fix exists only in the fork. Reaffirmed the source-first rule in project AGENTS.md: change application code/tests in the primary project, mirror required runtime changes to the fork, and retain only Ryoku integration/metadata differences. No application code was changed by this verification. PR #779 findings remain unapplied; this instruction does not authorize those fixes.

## 2026-11-10 16:34 IST — PR #779 fixes and app documentation authorized

The user authorizes applying the seven recommended findings to primary source and mirroring them into ai-usage-dashboard; the unproven DST suggestion remains on hold. They also explicitly authorize a focused docs/ai-usage.md and linking it from docs/structure.md, superseding the earlier blanket exclusion of distro docs only for these two relevant files. Preserve the existing initial Added-only changelog wording. Keep tests in the primary project/external validation tree; do not modify Rashin, unrelated shared files, packaging, hooks or CI. Preserve the existing uncommitted 15-second worker. No new commit/push, PR creation or review-thread reply is requested. Backup of current primary project, fork widget and relevant shared/doc files: /home/methos/.local/share/ryoku/ai-usage-backup/pr779-fixes-20261110-163431.

## 2026-11-10 16:59 IST — Seven PR #779 fixes and focused app docs completed

Implemented source-first and mirrored all application changes to ai-usage-dashboard. Claude usage/lifecycle now share a TranscriptState populated in the original transcript pass; the independent lifecycle helper retains a compatible scan path. A counted-read regression proves one transcript open, and old/new isolated 25,000-record outputs match for tokens, days, hours, periods, sessions, API Value and diagnostics. Single timing samples were 1.444s before and 1.370s after on 11350280 bytes; no general speedup factor is claimed. OpenCode reconciles positive lifetime residuals only when the session's recorded creation date is within the loaded horizon, preventing old/unknown-age totals from entering recent messages while preserving legitimate residual coverage. The six-second missing-cache reader now runs only while visible and reloads on opening; the independent 15-second worker stays active. Dashboard labels, whole formatted messages and relative/reset text use shared translation keys; period IDs remain unchanged and missing catalogs fall back to English. Removed all six widget em-dash occurrences, using ASCII dash placeholders and permitted prose punctuation. The pulse pauses when hidden/idle while retaining phase across cache-state changes. CustomWidgets now rejects non-Island entries before reserving IDs. The DST function remains AST-identical because its reported bug did not reproduce.

Added canonical primary docs/ai-usage.md and mirrored it into the Ryoku fork; linked it in docs/structure.md's documentation map and source-tree explanation. Root CHANGELOG.md is byte-identical to the task-start backup and remains exclusively the existing Added feature entry. No Rashin, package, CI, hook, upstream AGENTS.md or other unrelated files changed; tests remain primary/external. Updated the external fixture's CLI-name expectation to match the intentional port identity, used its existing fork Codex fixture rather than the standalone installer test, and changed the old deduplication expectation that encoded the reported bug. No test was disabled for these review fixes.

All 181 primary tests and all 181 external fork cases pass, including real Qt timing/pulse probes and the shared-registry regression; shell fixtures and cache contracts pass. QML load lint, explicit binding checks for 22 files, delivery, WM isolation, documentation links, source/fork parity, unchanged changelog, ASCII-punctuation scan and whitespace checks pass. Installed exactly 14 changed tested files atomically into the user-owned live widget and reloaded the shell. Opened and closed the dashboard; all three private caches kept updating over a 36-second closed-page observation, including after unload. Caches remain valid JSON with mode 0600, and the current shell log showed no widget/type/reference errors. The shared registry source fix is validated but was not copied into the package-owned live shell. No account changes, paid model prompts or package upgrade occurred.

Verified PR #779 remains open at published head 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667. Current changes, including the earlier 15-second worker, remain local and uncommitted/unpushed; no PR/thread message was created. Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-fixes-20261110-163431/. Results: PR_779_FIX_RESULTS.md; logs: /tmp/ai-usage-pr779-validation/ and /tmp/ai-usage-pr779-primary-tests.log.

## 2026-11-10 17:02 IST — Fix commit and existing-PR push authorized

The user requested committing and pushing the reviewed changes as a fix. They initially named ai-usage; read-only verification showed no such fork branch and PR #779 follows ai-usage-dashboard. The user explicitly selected updating the existing PR on ai-usage-dashboard. Refetched that head and verified it remains 5c9d9f11c. Staged exactly 19 reviewed paths: widget changes including the existing 15-second worker, required registry correction, the focused guide/structure link, and the already-reviewed Added-only changelog text. Source/port parity and both 181-case validation results remain applicable. Prepared a fix commit with normal hooks and an exact staged-patch backup at /tmp/ai-usage-pr779-validation/ready-fix.patch (SHA256 bf562fa7715a86ad828a86abccfccc335690722df7b4c30f472d052fbf85e1cd). Only the fork branch commit/push is authorized; no standalone commit, new branch, new PR or review-thread reply is needed.

## 2026-11-10 17:04 IST — Review fix committed and pushed to existing PR #779

After explicit user authorization and branch clarification, created 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1 ([global] shima: fix AI usage dashboard review findings) through normal hooks and pushed origin HEAD:refs/heads/ai-usage-dashboard without force. The committed 19-file patch exactly matches the saved reviewed stage (SHA256 bf562fa7715a86ad828a86abccfccc335690722df7b4c30f472d052fbf85e1cd); both 181-case validation results remain applicable. GitHub's actual fork head matches the commit, and PR #779 now uses the same new SHA on ai-usage-dashboard. The working tree/index are clean with 0/0 divergence. The commit includes the seven fixes, tested background worker and focused guide/structure link; changelog remains the existing Added entry and the unproven DST suggestion is unchanged. No Rashin, unrelated files, new branch, force push, standalone commit/push, new PR or review-thread message occurred. Primary app source retains the same application changes; standalone project records and prior changes remain uncommitted in that separate repository. New remote review/CI approval is not claimed.

## 2026-11-10 18:48 IST — Second PR #779 review fixes authorized

The user requests fixing all six new suggestions. Implement source-first, mirror application changes to ai-usage-dashboard and preserve scope. Correct the true rolling 24-hour cutoff across all agents and publish matching chart bins rather than changing totals alone. Preserve OAuth cooldown in both top-level/nested previous-cache shapes across temporarily unavailable credentials, while retaining fingerprint/account guards. Reset reused lifecycle running state; gate only the UI ticker on visibility; add the redundant merged-split guard as defensive hardening; replace decorative/en-dash glyphs in widget comments and ranges as cosmetic cleanup. The reported split crash and punctuation gate violation were not reproduced, so do not mislabel those as proven production bugs. Security summary claims remain unsubstantiated by the current collector. Preserve the earlier held DST function, Rashin, unrelated files, test/CI exclusion and Added-only changelog. No new commit/push or PR/review-thread message is requested. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/pr779-second-review-20261110-184845.

## 2026-11-10 19:10 IST — All six second-review suggestions addressed locally

Implemented source-first and mirrored to ai-usage-dashboard. The 30-second relative-time UI ticker now requires visibility while the separate 15-second collector stays active. Reused TranscriptState clears derived running before recomputation. Added a redundant numeric-split guard before merged cache split summation as defensive hardening, without claiming the earlier unproven crash. Cosmetic en-dash/box-drawing separators in widget source are now ASCII; existing mechanical rules did not require that broader cleanup, but the user explicitly requested all suggestions. OAuth probe handling now accepts both top-level and nested state, preserves the prior probe when credentials temporarily become unavailable in either Desktop-available branch, and retains credential-fingerprint guards; the same login recovers its cooldown and a changed login requests independently.

Last 24 hours now means the exact current timestamp minus 86,400 seconds. A shared rolling-history.py helper supplies both period stats and 24 trailing hourly bins from the same one-pass filtered stream, including boundary records and excluding future/outside records. OpenCode and Codex use it directly; Claude reuses the bundled shared entry. The chart prefers the exact period bins, uses full date/time boundaries for rolling captions and preserves legacy-cache fallback. Today stays on local calendar-hour bins, and the earlier held DST function is unchanged. Updated the focused app guide only; changelog bytes remain unchanged in Added. No Rashin, shared shell, test/CI, packaging or unrelated changes in the fork.

All 190 primary and 190 external fork cases pass. New regressions cover both previous-cache cooldown shapes and token switches, reused lifecycle state, missing merged splits, exact endpoint/model/cost/bin agreement at different minute positions, timezone/DST duration boundaries, one-pass stream consumption, Qt date-label arity and hidden/resumed ticker behavior. The former shorter-window expectation was updated to include the partial first hour and assert matching bins. An early ticker fixture needed an actual offscreen Window for effective visibility; an early direct Qt-label probe quit before the engine installed its quit receiver, corrected by callLater in the retained test. QML lint, bindings for all 19 widget QML files, delivery, WM isolation, Python parsing, source/fork parity, ASCII cleanup, protected paths and whitespace checks pass. Existing cache publication remains private/atomic; unsupported security-summary claims did not justify a rewrite.

Atomically installed 11 tested runtime files, publishing the shared helper before its callers, then reloaded and opened/closed the dashboard. All three real private caches kept updating over 36 seconds while closed; each has an exact 86,400,000-ms period, 24 contiguous matching bins, and sum(bin.tokens)==period.tokens. Caches are valid and mode 0600. The active shell is running and its log has no widget/type/reference errors. No authentication change, paid prompt or package upgrade occurred. Current changes are uncommitted/unpushed; published PR head remains 2566ef372. No PR creation or review-thread message. Report: PR_779_SECOND_REVIEW_FIXES.md. Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-second-review-20261110-184845/.

## 2026-11-10 19:35 IST — Publication of second-review update requested

The user requests pushing the completed fixes. Prepare the necessary fix commit and publish it to the already-confirmed ai-usage-dashboard branch for existing PR #779. Verified unchanged local/remote base 2566ef372, source/fork parity, both 190-case results and exactly 12 allowed staged paths. Changelog and protected areas are untouched. Saved /tmp/ai-usage-pr779-second-validation/ready-publish.patch with SHA256 a250083fed5078a017157ed135973e0b22c291f3bf07bee4a6bd9f2d6b624d65. Normal hooks will run; no standalone publication, new branch, new PR or review reply is part of this request.

## 2026-11-10 19:36 IST — Second-review fixes committed and pushed

The user requested publication. Created dad97d5ab07f6db20900742ddd6909251db9dbd9 ([global] shima: fix rolling usage and quota refresh state) with normal hooks, then pushed only methos28/ryoku:ai-usage-dashboard without force. The exact 12-file committed diff matches the staged reviewed patch at /tmp/ai-usage-pr779-second-validation/ready-publish.patch (SHA256 a250083fed5078a017157ed135973e0b22c291f3bf07bee4a6bd9f2d6b624d65). Both 190-case results apply to the published code. Actual remote and existing PR #779 head match the commit. Fork tree/index are clean and 0/0 with origin. Changelog, Rashin, tests/CI, packaging, hooks and unrelated files remain unchanged by this commit. Primary app source retains the same implementation, and the tested widget files are already live. No standalone commit/push, new PR, review reply, auth operation or package upgrade occurred. Remote review/CI approval is not claimed.

## 2026-11-10 20:35 IST — Fresh single-pass evidence requested

The user requests logs supporting the Claude performance fix. Re-ran three focused primary regression tests against the actual published-checkout collector/helper at dad97d5ab07f6db20900742ddd6909251db9dbd9. The integrated caller test measured exactly one transcript open and preserved 1,600 synthetic tokens plus completed lifecycle; helper no-rescan and reused-state cases also pass. Saved fresh log, pinned caller references, suggested reply and source hashes at /home/methos/Documents/opencode_widget_ryoku_shima/evidence/pr-779-claude-single-pass/20261110-203556. No application code, commit, push, account or GitHub thread changes occurred.

## 2026-11-10 21:09 IST — Remaining six threads: fix, commit and push authorized

The user explicitly authorizes fixing all six unresolved PR #779 findings, committing and pushing to the existing ai-usage-dashboard branch. Scope: the remaining ancient/undated aggregate-only fallback, stale-cache history recovery with accurate freshness, highest applicable pricing tier, Claude login/session metadata without projects (without generating a fake Claude cache on every machine), readiness-aware tile agent fallback and translated quota percentage. Edit primary application source first and mirror runtime changes to the fork; keep tests external to the fork, protected paths unchanged and changelog in Added. No new PR or review-thread replies/resolution are authorized. Fresh local/remote base is dad97d5ab. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/pr779-unresolved-six-20261110-210951.

## 2026-11-10 21:20 IST — Remaining six fixes validated and staged for publication

All six findings are implemented source-first and mirrored; all 197 primary and 197 external fork cases pass, including legacy/new stale recovery, old/unknown/recent aggregate-only stores, highest-tier resolution without changing rates, credential-only bootstrap and alternate-profile isolation, native Qt readiness-aware tile fallback and translated quota word order. QML lint/bindings, delivery, WM isolation, source/fork/live parity, protected paths and whitespace pass. Six tested runtime files were installed atomically and the shell reloaded; the guide documents bootstrap and fallback. Changelog is unchanged. Staged exactly seven reviewed widget/guide paths. Backup/evidence: /home/methos/.local/share/ryoku/ai-usage-backup/pr779-unresolved-six-20261110-210951; staged patch: /tmp/ai-usage-pr779-unresolved-validation/ready-publish.patch, SHA256 fda8224feddaf942a77d57635090be945715fb4e3feb41357beebb2d45af9d82. Explicit user authorization covers fix, commit and push to the existing PR branch; normal hooks will run.

## 2026-11-10 21:23 IST — Remaining six PR #779 fixes committed and pushed

Completed all six findings source-first and mirrored application code to ai-usage-dashboard. The aggregate-only fallback now requires known session history within the loaded horizon, matching the existing residual guard; recent dated aggregate-only stores remain supported. OpenCode stale publication preserves its source with _stale=true; UI freshness recognizes that flag and history merges also accept legacy _source=stale caches. Highest applicable price tiers are selected before checking unsupported status, preserving the rate tables. Claude collection starts from active login/session/profile metadata even without projects, while avoiding empty caches on machines with no Claude state and avoiding borrowed default metadata for alternate profiles. The tile has collection/readiness-aware fallback, keeps available saved choices and does not overwrite selection. Quota percentage copy uses a translated whole-format key. The existing app guide describes bootstrap/fallback.

All 197 primary and 197 external fork cases pass, including current/legacy stale recovery, old/unknown/recent aggregate-only stores, highest-tier/service selection and table immutability, no-project bootstrap, alternate-profile isolation, native Qt tile fallback and translated percentage ordering. QML lint/bindings, delivery, WM isolation, protected paths, source/fork/live parity, unchanged Added-only changelog and whitespace pass. Installed six tested widget files atomically and reloaded; all three live caches remain valid/private. No Rashin, tests/CI, packaging, hooks, unrelated files, account changes or new paid prompt.

Explicit user authorization included commit and push. Created 5ca6583632e7bf086362feb395f80c87bf40f431 ([global] shima: fix agent startup and usage history recovery) through normal hooks and pushed only origin ai-usage-dashboard without force. Exact committed seven-file patch matches /tmp/ai-usage-pr779-unresolved-validation/ready-publish.patch (SHA256 fda8224feddaf942a77d57635090be945715fb4e3feb41357beebb2d45af9d82). Actual remote and PR #779 head are verified at the new SHA; fork tree/index are clean and 0/0 with origin. No new PR, review reply or thread resolution was performed. Primary app files remain updated in the separate standalone working tree without a standalone publication. Remote review/CI approval is not claimed. Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-unresolved-six-20261110-210951/. Report: PR_779_REMAINING_SIX_FIXES.md.

## 2026-11-17 12:23 IST — Codex session title change authorized; live/source discrepancy

The user authorized using the saved Codex session name shown in the terminal instead of the first prompt, following a read-only stable/unstable audit. Keep stable v1.0.9 (08ff328); no channel switch, package upgrade, commit, push or PR is authorized. The current live bundle is the package-owned built-in, not the earlier user-installed widget, which is absent. Its 31 files match upstream 0389a5e exactly. The primary and historical ai-usage-dashboard sources lack upstream visible-only collection (63c2ed1d6) and 120-second quota RPC caching (070aa9d89); record this discrepancy before reconciling. Backups: /home/methos/.local/share/ryoku/ai-usage-backup/codex-session-titles-20261117-122321.

The local Codex session_index.jsonl maps this session to Verify Codex session naming. state_5.sqlite threads.name agrees; threads.title still contains the first prompt. Read names from the native session index without changing Codex state. Preserve prompt/directory fallbacks when a name is unavailable. Reconcile the four upstream runtime files and documentation in primary source first, mirror the scoped runtime into the existing ai-usage-dashboard branch, test both copies, and deploy through the supported user-owned Shima widget path. Preserve upstream visibility and quota cooldown behavior.

### 12:25 IST — Source implementation and negative control

Reconciled UsageModel.qml, AgentAvailability.qml, UsageRefresh.qml and codex-usage with upstream installed-stable behavior in primary first, then mirrored runtime and the guide to the existing ai-usage-dashboard source branch. No channel branch was edited. Added session_names() in the existing Codex collector: stream the native index read-only, skip malformed/partial/non-string/blank records, use the last valid saved name per exact session ID, and reread on each history scan. Preserve full Unicode names and existing first-prompt/directory fallbacks. No SQLite, auth or accounting changes are needed. The new integration test failed before the change (First prompt versus Verify Codex session naming). Added rename, archive/Unicode, missing/unreadable/corrupt index and quota cooldown regressions. Updated the native Qt timing expectations to upstream visible-only polling rather than the superseded hidden polling rule. README, guide, changelog and plan reflect current behavior. All edits are uncommitted; validation/deployment remain pending.

## 2026-11-17 12:29 IST — Saved Codex names delivered and visually verified

The primary suite ran 204 cases: 203 passed and its shared-host case initially skipped without RYOKU_TEST_SOURCE. Rerunning that case with /home/methos/ryoku-arch passed, so all 204 cases have passing results. The actual fork collector separately passes all 56 Codex cases. Fatal QML lint, real component compilation, QML binding checks and both whitespace gates pass. The timing probes verify 15-second visible polling, stop after page destruction, immediate reopening and no hidden retry. Quota regressions verify the upstream two-minute success/failure cooldown. A read-only before/after comparison preserved all 1,460 current request records and every session field except title.

Ran the existing standalone install.sh after gates. It installed all 31 tested files under ~/.config/inir/widgets/ai-usage, preserving the package-owned built-in and the current stable channel. The supported user copy overrides the built-in under the same module ID and survives package updates. Source/live parity is exact, and all four reconciled runtime files match the fork source. The shell reloaded successfully; opening the actual Island Desktop page refreshed the cache and visibly displayed Verify Codex session naming. The real cache reports that title for the current active session. No module errors appear in the inspected current 200-line shell log tail. Preview and gate logs are saved in /home/methos/.local/share/ryoku/ai-usage-backup/codex-session-titles-20261117-122321.

Final status: stable Amaterasu v1.0.9, installed 08ff328; no package or boot changes. Primary and ai-usage-dashboard working trees retain the edits uncommitted. No new commit, push, PR, review message, authentication change or paid model prompt was created. The source checkout is on the existing ai-usage-dashboard branch for this scoped port; its unstable-dev branch is preserved. Earlier records claiming the old custom copy was still installed and background polling was current are superseded by this entry.

## 2026-11-17 12:32 IST — Local commits and current-code bug audit authorized

The user explicitly requested a local commit followed by broad bug testing and a findings report. Commit the runnable current standalone module, its required bundled helpers, tests, guide and tracked project records; older uncommitted application work is part of this current snapshot because the saved-title enhancement depends on it. Keep private audit drafts and evidence outside the commit. Commit the six-file scoped mirror separately on ai-usage-dashboard through normal hooks. No network push, new PR, package/channel change or production bug repair is authorized by the audit request. Tests already passed for the exact runtime code being committed. The subsequent audit will use isolated data and public source inspection, retain reproducible findings and distinguish them from unverified risks.

## 2026-11-17 12:43 IST — Local application commits and read-only bug audit completed

Created primary 37db05d1f8ff1c3ccd7c056d9551e33b0374ff5b (54 application/helper/test/guide/record paths), and scoped Ryoku mirror aa11db31362d4e53f6831ce9139766e86112dea8 (six paths), with normal available hooks. Neither was pushed. The primary commit includes older pending runtime work required by the runnable current module; private reports/drafts/evidence remain outside it.

Re-ran the existing 204-case suite; its optional host case passed with the explicit source environment. Added isolated audit evidence outside the production test entry point: ten expected-correctness checks reproduce ten failures across mixed OpenCode store omission, account-unbound Codex quota caching, future usage contamination in all three agents, stale running-session display, and four malformed nested-data cases. Actual isolated Qt confirms stale running and partial parse state. The account-switch probe passes against the pre-cooldown backup and fails on current code; the other affected functions match the pre-title-work snapshot. Saved detailed triggers, priorities, source locations and suggested fixes in BUG_AUDIT_2026-11-17.md, with reproducible scripts/logs under evidence/bug-audit-2026-11-17. No production fixes, live collector/cache/ledger writes, authentication changes, paid model prompts, package/channel changes, push, new PR or review messages occurred. Runtime source is unchanged after the commits; new audit records are uncommitted.

## 2026-11-17 13:07 IST — Feature branch synchronization and remote push authorized

The user requested a local commit and remote feature-branch push after synchronizing with the latest unstable-dev, with a review diff containing only their work. They explicitly clarified ai-usage-dashboard (the existing branch); ai-dashboard-usage does not exist and will not be created. Verified origin is methos28/ryoku and remote feature head remains 5ca658363. Official latest unstable-dev is 0389a5edddbd8b9dbc96c9cadff5a85beaee5864; the fork's stale unstable-dev remains 926d6c4a2 and is not a push target. Preserved the feature history in /tmp/ai-usage-sync-20261117-before.bundle.

A normal no-fast-forward merge of official unstable-dev into local aa11db313 is staged. Runtime and guide merge cleanly. The one changelog conflict is resolved from upstream plus saved-title wording only in the existing module Added entry. The exact feature diff against latest unstable is three paths: bundled codex-usage, docs/ai-usage.md and root CHANGELOG.md. Every widget runtime byte is preserved relative to the tested aa11db313. Scoped whitespace and actual merged-source QML lint pass; the Codex regression suite is running. A full incoming-merge whitespace check flags two upstream TSV trailing tabs (empty final columns); no upstream table changes are made to hide that inherited condition. Normal hooks remain enabled. No bug fixes, primary-main push, upstream push, fork unstable-dev push, new PR or channel/package change are authorized or needed.

## 2026-11-17 13:09 IST — Synced feature branch committed, pushed and verified

Completed normal merge e7297aec62c2f36cd39b424a7abc418b02439279 with parents aa11db31362d4e53f6831ce9139766e86112dea8 and official unstable-dev 0389a5edddbd8b9dbc96c9cadff5a85beaee5864. Runtime code is byte-identical to the tested pre-merge feature; the changelog preserves upstream and changes only the module's saved-title wording. Actual fork-source Codex regressions pass all 56 cases, merged-source fatal QML lint and feature whitespace pass, and normal commit/pre-push hooks pass, including package dependency resolution and vendored WM parity. ShellCheck was unavailable and is not claimed.

Pushed only origin HEAD:refs/heads/ai-usage-dashboard, without force or bypass, advancing remote 5ca658363 to e7297aec6. GitHub's actual branch head matches. Its official cross-fork compare confirms status ahead, two commits ahead, zero behind, and exactly three changed files (CHANGELOG.md, docs/ai-usage.md, bundled codex-usage), with 31 insertions and three deletions. The feature checkout is clean and equals origin/ai-usage-dashboard. Official unstable-dev was rechecked and remains 0389a5e. Existing history is preserved; no branch was renamed or created. The fork's other branches, primary main remote, upstream repository, existing PR, installed stable desktop, packages, authentication and live data were not changed. The audit findings remain unfixed; their reports/tests stay local.

Evidence: /home/methos/Documents/opencode_widget_ryoku_shima/evidence/branch-sync-2026-11-17. Correct comparison: https://github.com/Ryoku-dev/ryoku/compare/unstable-dev...methos28:ai-usage-dashboard . Primary audit/publication records remain local and uncommitted; no source code change is pending in either committed runtime.

## 2026-11-17 13:23 IST — All current audit bug fixes authorized

The user explicitly requested applying the bug fixes in BUG_AUDIT_2026-11-17.md. Scope: all ten reproductions across the five reported areas, with primary-first changes, permanent regression coverage, deliberately mirrored runtime/guide/changelog on ai-usage-dashboard, full validation and tested user-owned live delivery. Preserve historical price snapshots, native stores, existing settings and private cache isolation. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/audit-fixes-20261117-132318. The initial source/live states match the recorded delivery; the fork is clean at published e7297aec6. No fix is yet implemented at this checkpoint.

### 13:30 IST — Audit fixes implemented and mirrored

OpenCode now merges all three native stores using native message IDs and one-to-one cross-store fingerprints only where IDs are absent; equal requests within one store and different IDs remain distinct. Aggregate residual guards remain per-session. Login-context-bound Codex RPC caching uses auth/config file metadata and opaque inherited API-key/base-URL fingerprints without reading credential files; unknown contexts are rechecked, and a context change during a read suppresses that stale answer. All three agents filter future usage before current accounting, and spending helpers defer future events without changing historical rate tables. Invalid retained-map/hour rows and malformed OpenCode messages recover without blocking valid data. QML clears partial parse state, gates running sessions on freshness, ages freshness on its visible ticker and labels stale activity unavailable.

All ten original failures now pass in permanent tests, with added store-overlap/multiplicity, native Qt aging/parse, credential privacy/environment changes, concurrent login changes, unknown login and clock-catch-up checks. The first full run used two already-loaded test function lists that lacked the new updateFreshness helper; the source harness lists are corrected and the final full run will follow. Read-only actual-store comparisons preserve all 6,049 OpenCode records and their 31,001,572 uncached tokens, plus all 1,534 Codex canonical requests. Runtime and the focused guide are mirrored to ai-usage-dashboard; its original CLI/source labels and manifest identity are preserved. No live copy has been changed yet.

### 2026-11-17 13:35 IST — Full validation and live delivery passed

All 222 primary cases and all 222 cases with actual fork runtime overrides pass, with no skips. Fatal QML lint, real component compilation, both binding checks, delivery, WM isolation and whitespace pass. The known port source/CLI naming differences are asserted explicitly in tests rather than rewriting the port identity. Installed the tested complete primary widget through install.sh; source/live parity is preserved. Actual caches are valid private JSON (0600), Codex quota source is rpc, and the real card visibly retains Verify Codex session naming with current quota/token/API Value data. The inspected current log has zero module errors. All 20 saved historical daily price dictionaries are unchanged after the real refresh. Synthetic native Qt tests confirm fresh active sessions remain visible, stale/aged sessions stop claiming execution, and a parse exception clears partial state.

The user's apply-the-bug-fixes-too request extends the existing commit-and-push task for this same PR branch. After review, publish the eight scoped runtime/guide/changelog paths on ai-usage-dashboard through normal hooks; no new permission question is needed under the earlier explicit authorization. The initial commentary saying this turn would add no commit/push was an unnecessary limitation and is superseded by carrying the requested fixes into the same branch. No primary-main remote push, new PR, force push, package upgrade or channel switch is in scope. Evidence: /home/methos/Documents/opencode_widget_ryoku_shima/evidence/bug-fixes-2026-11-17.

## 2026-11-17 13:39 IST — Audit fixes committed, installed and published

All ten current audit findings are repaired and covered by 18 permanent regression cases. Both primary and actual fork-targeted suites pass all 222 cases, with no skips; QML compilation/fatal lint, binding checks, delivery, WM isolation and whitespace pass. Read-only native-data parity preserves 6,049 OpenCode messages and 1,534 Codex requests; actual live source parity, healthy private caches and all 20 historical daily rate dictionaries are verified. Installed through the standalone user-widget command and reloaded; inspected the real saved-title card without module log errors.

Created primary c9c3eefd786a4093ea80d9b24dec8b20d7b7c2e6 and fork d4df8688ae6106ec47427b1d1e662578b49ca122 through normal available hooks. Pushed only origin HEAD:refs/heads/ai-usage-dashboard normally; actual GitHub branch head equals d4df8688a, checkout is clean and equals origin. GitHub compares the branch against official unstable-dev as three commits ahead, zero behind, and exactly eight related paths: six widget runtime files, the focused guide and root changelog. The original names enhancement remains included. Official base is 0389a5e; no history rewrite, other-branch push, primary-main remote push, new PR, review message, package/channel switch or authentication edit occurred. Local audit/publication records are separate from the minimal remote port.

Evidence: /home/methos/Documents/opencode_widget_ryoku_shima/evidence/bug-fixes-2026-11-17. Current regression command: python3 test/test_bug_regressions.py. Original failing probe scripts are retained as historical evidence; the current permanent fixture models an account switch through observable fake login-file metadata and verifies environment changes, unknown contexts and login changes during reads. No credential contents are opened by the quota-cache fingerprint. The initial no-commit/push commentary was corrected by carrying this requested extension into the previously authorized same-branch publication.

The local PR title/body drafts now describe the final saved-title and audit-fix scope, including the eight-file diff and 222-case validation, rather than the earlier three-file title-only change. No remote PR was created or edited.

## 2026-11-17 13:47 IST — PR #881 review finding independently reproduced

The user requested checking whether the reviewer's merge_message_stores identity-promotion finding is real. Both current primary and fork merge functions collapse the supported three-store sequence [anonymous], [A], [B] with equal fingerprints into one retained request instead of two. The actual loaders reproduce this with an ID-less v2 row, filesystem request A and distinct legacy SQLite request B: 120 tokens returned instead of 240. The alias map remembers A, but the retained row stays anonymous, letting B match it again. The reviewer's suggested rows[match]["_message_id"] = mid assignment was tested only in memory and passes five identity cases, including repeated A, distinct B, anonymous copies and already identified rows. No production code, native stores, caches, authentication, commit, remote or PR review state was changed; only these local verification records were appended. The earlier 222-case suite lacks this specific three-store identity-promotion case.

## 2026-11-17 13:49 IST — PR #881 identity-promotion fix and push authorized

The user explicitly requests fixing the confirmed review finding and pushing it to the existing remote feature branch. Both copies are at the reviewed d4df8688a runtime and the fork is clean and matches the actual remote. Add direct three-store identity/multiplicity and real loader regressions before changing the matched retained row. Change primary first, mirror the one-line fix and existing changelog entry only, run both full suites, deploy the tested user copy, then commit and push normally. No review-thread reply, new PR, history rewrite, package/channel or unrelated change is requested. Backup: /home/methos/.local/share/ryoku/ai-usage-backup/pr881-identity-20261117-134905.

### 13:51 IST — PR #881 fix passes full gates

Added two permanent regressions: a five-case identity-promotion matrix, including anonymous/A/B and repeated A, and an actual three-store collector fixture. Both tests fail before the fix and pass after assigning rows[match]["_message_id"] = mid alongside the alias map. All 224 primary and 224 actual fork-targeted cases pass, without skips. Both QML gates and whitespace pass. A read-only comparison against the pre-fix collector preserves all 6,049 actual OpenCode records and 31,001,572 uncached tokens exactly. The mirror contains only the one-line collector change and a line in the existing changelog entry. Test evidence: /tmp/ai-usage-pr881-before.log and /tmp/ai-usage-pr881-{primary,fork}-tests.log. Proceeding with tested user-widget installation, normal local commits and the explicitly requested same-branch push.
