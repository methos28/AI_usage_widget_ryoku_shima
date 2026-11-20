# AI Usage audit fixes, 2026-11-17

All ten failures reported in BUG_AUDIT_2026-11-17.md are repaired. The fixes are
implemented in the primary application, mirrored to the existing Ryoku feature
branch and installed through the supported user-owned Shima widget path.

## Resulting behavior

1. OpenCode merges v2, filesystem and legacy SQLite history. Stable native
   message IDs deduplicate migrated copies. One-to-one cross-store matching
   handles rows without IDs while preserving distinct requests and multiplicity.
   Existing guards against assigning ancient lifetime residuals to recent days
   remain intact.
2. Codex quota caches follow login context. Auth/config file metadata and opaque
   environment fingerprints invalidate a prior account's answer without reading
   credential-file contents. Unobservable contexts are rechecked. A login change
   during an RPC prevents publication of that now-stale quota.
3. All agents exclude future requests from current accounting. Requests become
   eligible when their timestamps are reached. Spending helpers defer future
   events without changing saved historical rates.
4. Stale cached sessions stop claiming live execution. Freshness also ages on
   the existing visible ticker, and the card shows session status unavailable.
5. Malformed retained maps, published hour rows and OpenCode messages no longer
   block valid usage. A dashboard parse failure clears partially assigned state.

## Verification

- All 222 primary cases and all 222 cases with actual fork runtime overrides
  pass, with no skipped tests. Eighteen permanent audit regressions cover the
  original ten failures plus overlap, login privacy, login races, clock catch-up
  and native Qt freshness/parse behavior.
- Fatal QML lint, actual component compilation, QML binding checks, delivery,
  window-manager isolation and whitespace gates pass.
- Read-only comparison preserves all 6,049 real OpenCode messages and their
  31,001,572 uncached tokens, plus all 1,534 observed Codex canonical requests.
- The live module was installed with the primary install.sh and reloaded.
  All three caches are valid JSON with mode 0600. The real card retains the
  saved Codex title, current account windows and API Value. No module errors
  appeared in the inspected runtime log tail.
- All 20 saved historical daily price dictionaries remain unchanged after the
  real refresh. No native source store, authentication, package or desktop
  channel was changed. Ryoku remains on stable.

The fork delta for this fix is six runtime files, the focused guide and the
existing module changelog entry. Tests and private evidence stay in the primary
project. Normal commit/push hooks remain enabled; publication status and exact
commit IDs are recorded in PROJECT_LOG.md and PR_TRACKER.md.

Evidence is retained in `evidence/bug-fixes-2026-11-17/`. The pre-change backup is
`~/.local/share/ryoku/ai-usage-backup/audit-fixes-20261117-132318/`.

## Publication verified

Primary: `c9c3eefd786a4093ea80d9b24dec8b20d7b7c2e6`. Published Ryoku branch: `ai-usage-dashboard` at `d4df8688ae6106ec47427b1d1e662578b49ca122`. GitHub confirms three commits ahead, zero behind latest official `unstable-dev` (`0389a5e`) and eight related files changed. The fork checkout is clean; other branches and the primary main remote were not pushed. All audited fixes are now included in the published feature branch.

## PR #881 follow-up

The reviewer found one additional three-store identity-promotion case missing from the earlier suite. It is fixed and published as 98058bcd8395fdf855771d01ff03b49972e3a956, primary 72a6730. Two new regressions cover the direct identity matrix and actual loaders. Both full suites now pass 224 cases without skips. The fix is also installed and tested locally.
