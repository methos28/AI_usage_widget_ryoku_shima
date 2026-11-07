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
