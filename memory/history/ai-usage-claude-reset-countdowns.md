## Current display update — 2026-11-09 19:42 IST

The user replaced relative countdowns with absolute local reset date/time and timezone for both Claude and Codex. Shared formatter is now resetAt, not resetIn. Examples:10Nov12:19AMIST and10Nov4:30PMIST. Past deadlines say reset was. Tooltip clarifies that Desktop is only the current data source; saved CLI subscription OAuth works independently without Desktop. Desktop-absent fixture verifies both reset windows. All126 tests and QML gates pass; native Qt timezone probes pass for Kolkata/NewYork. No backend/auth changes. New backup: ~/.local/share/ryoku/ai-usage-backup/absolute-reset-times-20261109-193709.

# Claude quota reset countdowns

Updated 2026-11-09T19:30:19.067829+05:30.

The standalone/live Claude limits card now shows real five-hour and weekly reset countdowns beneath the bars. The compact plan-usage-history.json omits resets_at; the complete Desktop HTTP usage response includes it. The new reader in ai-usage/bin/claude-quota.py reads only four known usage-endpoint cache keys for the bound organization, by hashed filename under ~/.config/Claude/Cache/Cache_Data. It never decrypts cookies or changes authentication.

Cache layout and filename derivation were verified against Chromium primary sources:
- https://raw.githubusercontent.com/chromium/chromium/main/net/disk_cache/simple/simple_entry_format.h
- https://raw.githubusercontent.com/chromium/chromium/main/net/disk_cache/simple/simple_util.cc

The reader validates version5 headers/footers, exact key, optional key SHA256, CRCs and successful HTTP200 metadata. It uses the HTTP Date as observation time, not file modification time. Identity/gzip/deflate and Python3.14 stdlib Zstandard bodies are bounded. Unsupported formats fall back to known percentages with an explicit reset-time-unavailable label. Existing account and organization checks still apply. Current response and compact history are selected by capture time; no percentages are combined with inferred reset schedules. Expired observations stay last-known; past deadlines are retained, never advanced by adding5h or7d. OAuth cooldown refreshes once across a known reset boundary and retains failed deadlines as stale.

The live card was inspected: five-hour and weekly countdowns render beneath their respective bars. Captured actual reset epochs were1794250199 (2026-11-09T18:49:59Z) and1794308400 (2026-11-10T11:00:00Z). Values are observations, not permanent defaults. Borrowed/shared-account usage remains global. All125 primary tests and QML gates pass; seven new quota cases cover compressed sources, corruption, identity/source precedence, timestamps and expired windows. Tests do not make authenticated network or model calls.

Source/live backup and evidence: ~/.local/share/ryoku/ai-usage-backup/claude-resets-20261109-192346. No fork, price dictionary, Codex/OpenCode collector, authentication, service, commit or push changes were made. The earlier fresh active-to-idle Claude observation is still separately pending.
