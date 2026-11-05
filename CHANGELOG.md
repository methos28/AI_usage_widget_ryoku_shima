# Changelog

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
