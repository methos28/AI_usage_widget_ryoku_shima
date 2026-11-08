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
