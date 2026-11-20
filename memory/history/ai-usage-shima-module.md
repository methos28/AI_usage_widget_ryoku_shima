# AI usage Shima module

Durable note for the island AI usage widget. Last updated 2026-11-06.

## Where it lives

- Repo: `~/Documents/opencode_widget_ryoku_shima`
  (`https://github.com/methos28/opencode_widget_ryoku_shima`, branch `main`)
- Live widget: `~/.config/inir/widgets/ai-usage/`
- Collector: `~/.local/bin/opencode-usage-v2` (v2.2.0)
- Service drop-in: `~/.config/systemd/user/ryoku-ai-usage.service.d/override.conf`
  (uses `%h/.local/bin/opencode-usage-v2`; `ryoku update` leaves it alone)
- Version: `1.1.3`

Install from the repo with `./install.sh`; test with `./test/run.sh`.

## Structure

`IrisCompact.qml` is only the page shell (widget properties, data model,
menus, row layout). The cards and primitives live in
`ai-usage/components/`, one component per file:

- `AiUsageLimitsCard`, `AiUsageNowCard`, `AiUsageSpendCard`,
  `AiUsageSpendBody`, `AiUsageTrendCard`, `AiUsageModelsCard`,
  `AiUsageActivityCard`, `AiUsageEmptyCard`
- `AiUsageWindowRow`, `AiUsageModelRow`
- `AiUsageGlassPane`, `AiUsageGlassCard`, `AiUsageFoldHeader`
- `AgentAvailability`

`UsageModel.qml` reads `~/.cache/<tool>-usage.json`. `AiUsageTile.qml` is the
plain desktop tile; unchanged and not part of the island layout.

## Behaviour decisions

- Agent switch is a chip/menu at the top of the card. Only agents with a usage
  cache on this machine are listed. If the selected agent loses its cache, the
  page falls back to the first available agent (OpenCode first) and writes the
  config once.
- Sessions header says "Sessions"; the list is capped at two; the live dot
  pulses only while a session runs.
- Claude and Codex: Limits + Sessions in one row; Spending uses the full
  Spending-card layout inside the Sessions card, with 14px vertical padding and
  a hairline separator near the card middle with one session.
- OpenCode: no Limits; Sessions and a separate Spending card side by side.
  Spending is vertically centred when Sessions grows with two sessions.
- Stale-data text was removed from the Limits card; no refresh mention.
- Switching agents keeps the old card visible until the new cache loads; the
  empty state and its refresh button are suppressed while switching.

## Collector

`opencode-usage-v2` writes the shared cache the shell AI panels also read. It
adds daily/hour history, periods, sessions and per-day cost while keeping the
legacy fields. Day and hour history is append-only; aggregate residuals are
added once on the newest record, never rescaled. It takes a `flock`, publishes
atomically, and supports `--version` and `--cache`.

Refresh from the card runs the collector directly for OpenCode; Claude and
Codex still go through `ryoku-ai-usage.service` so its install guards apply.
The systemd timer remains the background cadence.

## Tests and gotchas

- `./test/run.sh` runs `test/lint.sh` plus six collector fixtures
  (`test/test_collector.py`); `test/cache_contract.py` runs the repo collector
  against a temp cache.
- `/usr/bin/qmllint` on this machine is a broken Qt5 build and exits 255 on any
  file with `pragma ComponentBehavior: Bound`. Use
  `/usr/lib/qt6/bin/qmllint -I ~/.config/quickshell`.
- Demo Claude and Codex caches are currently in `~/.cache/` so all three agents
  appear: `claude-usage.json`, `codex-usage.json` (marked `_source: demo`).
  Remove them when real agents are not installed.
- Opening the island for screenshots: `qs ipc -i <instance> call iris page
  desktop`; find the live instance under `/run/user/1000/quickshell/by-pid/`.
  There is also an `iris` IPC target with `open`, `page <name>`, `close`,
  `toggle`, `card`, `theme`.
- Heartbeat animation: cache refreshes used to empty `sessions`, which flipped
  `liveDot.live` and restarted the pulse. The pulse now runs on a constant
  clock; never tie it back to data changes.
- `/dev/uinput` has an ACL for user methos; a raw uinput mouse helper can drive
  clicks for screenshots. `wtype` is available for keys.

## Pending / deferred

- README previews: the old GitHub attachment previews are still there. The user
  asked for new screenshots (two per row: all agents, sessions/no session,
  collapsed/expanded, agent menu, trend menu) and wants the README for
  inspection before it is published. Work was stopped by the user on
  2026-11-06 before any README edit.
- Moving Claude/Codex to a desktop widget and making the island OpenCode-only:
  deferred until the user says go.
- Ryoku upstream contribution: deferred; the recorded plan is at
  `~/.opencode/plan/ai-usage-upstream-record.md`.

## Working style the user asked for

Use subagents with the same model for large tasks; act as orchestrator, review
their diffs, run tests, and only then commit. Do not push README changes before
the user inspects them.
