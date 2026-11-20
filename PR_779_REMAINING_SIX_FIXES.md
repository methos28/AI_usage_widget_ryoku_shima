# PR #779: remaining six findings fixed and published

Completed 2026-11-10 21:23 IST.
Commit: 5ca6583632e7bf086362feb395f80c87bf40f431
Branch: methos28/ryoku:ai-usage-dashboard
Existing PR: https://github.com/Ryoku-dev/ryoku/pull/779

## Fixes

1. Avoid applying lifetime totals to partial history: old/unknown-age aggregate
   fallback rows no longer enter the recent window without message evidence.
   The earlier guard for sessions with message rows remains. Recent dated
   aggregate-only stores still work.
2. Preserve history after stale reads: source provenance is retained with a
   separate stale flag, UI freshness honors it, and both day/hour merges recover
   published buckets, including older caches tagged with source=stale.
3. Resolve the highest applicable price tier: choose the applicable threshold
   before rejecting unsupported rates. A later supported rate is reachable;
   a highest unsupported rate still remains unpriced. Rate tables are unchanged.
4. Run Claude collection without local projects: active login/session/profile
   metadata can bootstrap account collection. No unconditional empty Claude
   entry is created on unrelated machines; alternate profiles stay isolated.
5. Tile agent fallback: wait for collection/readiness, retain a valid selection
   or choose an available agent. This does not overwrite saved preferences.
6. Translate the quota percentage label: the complete percentage phrase is a
   shared translation key, permitting translated words and word order.

All app changes are in the primary project and mirrored to the fork; only
intentional built-in metadata and CLI/source labels differ. The focused guide
was updated. Changelog is unchanged in Added. No unrelated or Rashin changes.

## Validation and delivery

All 197 primary and 197 external fork cases pass. New cases exercise legacy and
current stale recovery, old/unknown/recent aggregate-only stores, tier/service
selection without mutating rates, credential-only collection and default-profile
isolation, native Qt tile fallback and translated percentage ordering.

QML load/binding gates, delivery, WM isolation, source parity and whitespace
pass. Normal commit/push hooks pass. Six tested widget files were installed
atomically, the shell reloaded, and all three live caches remain valid JSON
with mode 0600. No auth change, paid model prompt or package upgrade occurred.

Published seven-file diff: 32 insertions, 14 deletions. Its exact pre-commit
patch is saved at /tmp/ai-usage-pr779-unresolved-validation/ready-publish.patch,
SHA256 fda8224feddaf942a77d57635090be945715fb4e3feb41357beebb2d45af9d82.
Actual remote and PR head match the commit; the fork checkout is clean and
synchronized. No force push, new PR, review reply or thread resolution occurred.
Review threads await reviewer confirmation; no new remote CI result is claimed.

Primary log: /tmp/ai-usage-pr779-unresolved-primary-final.log
Fork logs: /tmp/ai-usage-pr779-unresolved-validation/
Backup: ~/.local/share/ryoku/ai-usage-backup/pr779-unresolved-six-20261110-210951/
