Latest publication: 2026-11-10 19:36 IST. Commit dad97d5ab07f6db20900742ddd6909251db9dbd9 is pushed
to ai-usage-dashboard and verified as PR #779's current head. Normal hooks pass;
the fork checkout is clean and synchronized. The local-only statements below
record the pre-publication verification snapshot.

# PR #779: second review fixes

Completed 2026-11-10 19:10 IST. These changes are local, uncommitted and unpushed.
Published head remains 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1.

Primary source: /home/methos/Documents/opencode_widget_ryoku_shima
Fork: /home/methos/ryoku-arch, branch ai-usage-dashboard

## All six suggestions addressed

1. Stop the ticker when hidden: the UI relative-time ticker requires both loaded
   data and visibility. The independent background collector still runs.
2. Reset running before recomputing session activity: reused lifecycle state
   clears its derived running flag before native/transcript evaluation.
3. Preserve OAuth cooldown after credential failures: both top-level and nested
   probes survive temporary credential loss, whether Desktop has a stale capture
   or no capture. Existing fingerprint checks prevent cross-account reuse.
4. Guard incomplete merged cache splits: added numeric validation before summing
   merged splits. This is defensive hardening; the initially claimed crash was
   not reproduced through the existing parser.
5. Correct Last 24 hours: all agents use an exact trailing duration and matching
   chart bins. One shared helper filters once and supplies both the period
   summary and 24 bins. Captions show the full start/end dates. Today and the
   legacy-cache fallback retain their existing behavior.
6. Punctuation cleanup: decorative/en-dash separators in widget source now use
   ASCII. The review's broad gate claim was unsupported, but cleanup was
   explicitly requested and does not alter calculations.

The earlier first-review DST suggestion remains unchanged because it did not
reproduce. The new rolling duration works across DST independently of it.

## Scope and validation

All application changes were made in the primary project and mirrored into the
fork, preserving only the intentional built-in metadata and CLI/source labels.
Added bin/rolling-history.py; the existing payload copies deliver it with the
module. Updated the focused docs/ai-usage.md in both sources. Changelog is
byte-identical to task start and remains the existing Added feature entry.
No Rashin, shared shell, packaging, hooks, test/CI or unrelated fork changes.

All 190 primary and 190 external fork cases pass. Coverage includes quota
cooldown recovery/account switches, reused state, incomplete split metadata,
exact 24-hour boundary inclusion/exclusion, bin/model/cost agreement, timezone
and DST duration checks, streaming, native Qt captions and visibility. Normal
source/package delivery fixtures and private-cache contracts pass. QML load
lint and binding checks cover all 19 widget QML files; delivery, WM isolation,
Python syntax, parity, punctuation and whitespace checks pass. No new commit
hooks or remote CI result is claimed because this update is not committed.

The old shorter-window test was updated to expect the previously omitted
partial first hour and verify that chart bins sum to the same total. The Qt
ticker fixture uses an offscreen window so visibility is meaningful.

## Live verification

Installed 11 tested files atomically with the new helper first, reloaded through
ryoku-shell, opened the dashboard and closed it again. All three private agent
caches refreshed during 36 seconds while closed. Each period spans exactly
86,400,000 ms, contains 24 bins ending at the same timestamp, and has
sum(bin.tokens)==period.tokens. All cache files remain valid JSON and mode 0600.
The active shell is running, with no scoped widget/type/reference log errors.
No credential change, paid model prompt, package upgrade, PR creation or
review-thread message occurred. Existing private atomic publication was retained.

Observation: [{"elapsed": 0.0, "changed": ["opencode-usage", "codex-usage", "claude-usage"]}, {"elapsed": 11.0, "changed": ["opencode-usage"]}, {"elapsed": 13.0, "changed": ["codex-usage", "claude-usage"]}, {"elapsed": 26.0, "changed": ["opencode-usage"]}, {"elapsed": 28.0, "changed": ["codex-usage", "claude-usage"]}]

Primary log: /tmp/ai-usage-pr779-second-primary-final.log
Fork logs: /tmp/ai-usage-pr779-second-validation/
Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-second-review-20261110-184845/
