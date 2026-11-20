# AI usage background refresh

Implemented and installed 2026-11-10 13:04 IST.

The former UsageModel timer ran only while visible: 60 seconds for most agents,
5 seconds for Claude. Shima also destroys its page 20 seconds after closing.
An unconditional page timer would therefore still stop after unloading.

The new widget-owned UsageRefresh singleton survives page destruction for the
engine lifetime. It starts when the module first loads, collects all agents
every 15 seconds, refreshes earlier when opened, shares an active process and
retries private-lock contention after two seconds. Existing cache readers and
collector bodies remain unchanged. No Rashin or shared system service is used.

Lifecycle limit: each new shell session must load the module once to start its
singleton. It is not running at login before any module load. A blocked/slow
collection is allowed to finish rather than starting overlapping processes.
Claude account-source freshness/cooldowns are unchanged by the local cadence.

## Changes

Runtime: UsageModel.qml, refresh/UsageRefresh.qml, refresh/qmldir, in primary
source, the fork's existing widget destination, and the user-owned live copy.
The fork also updates only the existing initial Added changelog description.
New/updated tests and docs stay in the primary project, outside the fork.
No Rashin, shared shell files, services, packaging, tests/CI or credentials
changed in the fork. No commit, push or PR was created for this enhancement.
The existing published branch remains at 5c9d9f11c.

## Verification

All 174 primary tests pass. New Qt probes destroy the view, verify the next
15-second collection, reopen before the following deadline and verify an early
collection; another checks hidden lock retries and overlapping-view coalescing.
The fork's 16 UI plus 5 discovery/delivery checks pass using external tests.
QML load lint, bindings, delivery, WM isolation and whitespace checks pass.

Installed only tested runtime files atomically, reloaded the shell, opened the
page once and then closed it for 43 seconds. All three private caches changed
repeatedly after closure, including after the page-unload deadline.
Observed changes: [{"elapsed": 0.0, "changed": ["opencode-usage", "codex-usage", "claude-usage"]}, {"elapsed": 1.0, "changed": ["opencode-usage"]}, {"elapsed": 3.0, "changed": ["codex-usage", "claude-usage"]}, {"elapsed": 15.0, "changed": ["opencode-usage"]}, {"elapsed": 16.0, "changed": ["codex-usage", "claude-usage"]}, {"elapsed": 29.0, "changed": ["opencode-usage"]}, {"elapsed": 30.0, "changed": ["codex-usage", "claude-usage"]}]
All caches parse as JSON objects and remain private mode 0600. Runtime byte
parity holds across source, fork and live copies. No new paid prompt was run.

Logs: /tmp/ai-usage-background-primary-tests-final.log and
/tmp/ai-usage-background-live-events.json.
Backup: ~/.local/share/ryoku/ai-usage-backup/background-refresh-20261110-125642/.
