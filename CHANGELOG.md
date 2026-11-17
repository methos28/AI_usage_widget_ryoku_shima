# Changelog

## Unreleased

- Merge mixed OpenCode message stores without losing distinct legacy sessions
  or counting migrated copies twice.
- Invalidate Codex quota caches on login changes, exclude future usage from
  current totals, and preserve historical pricing snapshots.
- Clear stale running-session indicators and partially parsed dashboard state.
  Recover valid usage when malformed nested messages or cache rows are present.

- Use Codex's saved session names, including later renames, instead of the first
  prompt when a name exists. Retain prompt and directory fallbacks.
- Adopt upstream visible-only collection and the two-minute Codex quota cache.

- Fix merged dropdown highlights with one shared row background. Keep the
  selected-option checkmark while hovering other agent or period options.

- Show local reset dates/times and timezone instead of rounded hours. Clarify
  Desktop/CLI quota support and test CLI subscription resets without Desktop.

- Show Claude five-hour and weekly reset countdowns from validated Desktop
  usage-response caches. Preserve stale deadlines and explicit unavailable
  states; refresh OAuth once at a reset boundary. No credential decryption.

- Add a Sonnet-to-Haiku same-session counting regression covering cache writes,
  thinking/output separation and successive response checkpoints. Independent
  recount matches the dashboard; all 118 primary tests pass.

- Rename the spending label to API Value for OpenCode, Codex and Claude.

- Enable standalone Claude preview with observed Desktop account quotas, native
  session lifecycle and separate Sonnet 5.5 API-value estimates. Show quota
  capture age and unknown/partial data explicitly. Refresh Claude every five
  seconds without polling the other agents. Add Claude helper/integration/UI
  regressions; 117 primary tests and cache/QML gates pass.

- Correct Codex continuation overcounts, include request-only compactions, and
  reconcile request mirrors. Separate output, reasoning and cache-write counts.
  Repair affected history automatically while preserving saved daily prices.

- Bundle both collectors inside the widget and invoke them by local paths.
  Collect on first load and use private caches so older system collectors cannot
  overwrite widget data. Standalone installs no longer create service overrides.
- Add Codex Est. Spending with private monthly ledgers, saved daily public
  prices, deduplicated usage and visible incomplete or stale coverage.
- Preserve missing historical prices as unpriced; estimates do not represent
  bills, wallet balances, top-ups or additional subscription charges.
- Harden local Codex RPC reads, process cleanup, error redaction and atomic
  private cache writes. Suppress previous subscription quotas after switching
  to an API-key or Bedrock account.
- Fix desktop-tile bindings, the menu icon import, saved-agent fallback and
  compact caption/spending alignment. Share the dropdown component.
- Add isolated cache, quota, security, spending and QML regressions, with 59
  standalone tests plus the cache contract.
- Update installation and data-source documentation for the current collectors.

## 1.1.3

- Removed the stale-data line from the Limits card.
- Renamed the sessions card header to Sessions; sessions stay capped at two.
- Agent switches no longer flash the empty state and its refresh button while
  the new cache loads.

## 1.1.2

- The agent menu lists only agents with a usage cache on this machine.
- Card content is centred when a neighbouring card makes the row taller, so
  text no longer sticks to the top.
- Spending gets real padding above and below; in Claude/Codex the separator
  sits near the middle with one session and both cards grow evenly with more.

## 1.1.1

- Spending moved into the Now card for Claude and Codex, using the empty area and
  the same card layout as the standalone Spending card. OpenCode keeps the
  separate Spending card beside Now.

## 1.1.0

- Added an agent chip and menu to switch OpenCode, Claude Code and Codex on the card.
- Spending now shows this month's API cost from per-day cost buckets.
- Collector writes per-day cost, keeps day and hour history append-only, takes a lock and publishes atomically.
- Collector accepts `--version` and `--cache`; tests run against throwaway stores.
- Refresh runs the OpenCode collector directly, with the Ryoku service as a fallback.
- Split the 1,600-line page into one component per file under `ai-usage/components/`.
- Added `install.sh`, a systemd drop-in, collector fixtures and a lint script.

## 1.0.0

- First public version: OpenCode sessions, period tokens, models, trend and activity heatmap on the Shima Island.
