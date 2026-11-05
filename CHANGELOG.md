# Changelog

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
