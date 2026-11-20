# PR #779 review issues and proposed handling

Recorded: 2026-11-10 16:25 IST.

PR: https://github.com/Ryoku-dev/ryoku/pull/779

This is the first feature submission, from `methos28/ryoku:ai-usage-dashboard`
to `Ryoku-dev/ryoku:unstable-dev`. The reviewed commit is
`5c9d9f11cfcbf56de27d2f5433e37b1e95e40667`.

## Status and scope

The review contains eight unique findings. Its three optional nitpicks repeat
the daylight-saving, pulse animation and widget-filter findings. The user later
authorized implementation: seven recommendations are now implemented and locally
verified in both sources. The DST suggestion is held unchanged. No commit,
push, GitHub reply or PR creation was requested for this implementation.

The separately implemented 15-second background worker is local and unpushed.
It is not included in the commit reviewed by Mika. The worker starts on the
first module load in each shell session and survives page destruction. That
existing change is separate from these eight unapplied review findings.

Keep future fixes within the widget and required integration files. Do not
change Rashin collectors/services or unrelated Ryoku files. Keep changelog
wording in the initial feature's Added entry, without narrating unpublished
module repairs. Never create a PR against Ryoku-dev/ryoku without explicit
later user instruction.

Paths below are relative to `/home/methos/ryoku-arch`. Widget paths use the
prefix `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/`.

## 1. Performance: repeated Claude transcript scans

- Reviewer severity/effort: major, high effort.
- File: widget `bin/claude-sessions.py`, reviewed lines 153-160.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361412
- Assessment: confirmed. `claude-usage` scans project transcripts for usage,
  then `collect_sessions` scans the same transcripts for lifecycle information.
  The published implementation schedules visible Claude collection every five
  seconds. The local 15-second worker reduces frequency but retains duplication.
- Effect if fixed correctly: fewer repeated reads and JSON parses, less CPU
  work, and potentially faster collection for large histories. Token counts,
  session lifecycle and account quota behavior should remain identical.
- Recommendation: highest priority. Prefer sharing one transcript pass before
  introducing a persistent incremental index. Preserve user/system lifecycle
  events, timestamps, copied-record handling and native process verification.
  Do not reduce work by dropping older history.
- Performance caveat: no slowdown magnitude has been measured on this PC.
  Disk caching can reduce physical reads but does not remove JSON parsing.
  Long batches can delay subsequent background refreshes.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 2. Performance: missing-cache retry while hidden

- Reviewer severity/effort: minor, low effort.
- File: widget `UsageModel.qml`, reviewed lines 345-349.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361408
- Assessment: confirmed. The six-second cache reload timer runs whenever the
  cache is missing, including while the view is hidden. The local worker change
  does not remove this reader-side timer.
- Effect if fixed: hidden views stop redundant missing-file checks; showing the
  view reloads its cache.
- Recommendation: apply to the UI cache reader only. Preserve the independent
  15-second background collector, hidden lock retries and refresh on opening.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 3. Possible Bug: literal English dashboard copy

- Reviewer severity/effort: minor, medium effort.
- File: widget `IrisCompact.qml`, reviewed lines 75-80, plus other visible copy.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361403
- Assessment: confirmed for menu/card text. Some shared chip components already
  translate their labels; `IrisText` and the dashboard menu do not automatically
  translate every assigned string.
- Effect if fixed: English remains the fallback; other locales can show
  translated labels when catalog entries exist. Wrapping strings alone does
  not create translations.
- Recommendation: route untranslated visible copy through the existing shared
  i18n runtime. Preserve internal period IDs, config keys, paths and model IDs.
  Avoid unnecessary double wrapping where a shared component already translates.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 4. Maintainability: em dashes in added widget files

- Reviewer severity/effort: minor, low effort.
- File: widget `AiUsageTile.qml`, reviewed line 3, and other added occurrences.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361398
- Assessment: the characters are present. This is a style issue, not a token
  accounting defect. CONTRIBUTING.md prohibits em dashes in text; the current
  pre-commit character scan does not cover every QML/Python occurrence.
- Effect if fixed: punctuation and unavailable-value markers change. Collection,
  calculations, identifiers and timing should remain unchanged.
- Proposed handling discussed with the user:
  - Inspect each occurrence in our added widget files.
  - Replace prose/comment punctuation with commas, colons or full stops.
  - Replace unavailable-value placeholders with a plain ASCII dash (`-`).
  - Do not run a blind replacement over unrelated upstream files or alter
    mathematical signs and meaningful string content.
- Recommendation: apply as a small scoped cleanup after authorization.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 5. Performance: Stop the pulse when inactive

- Reviewer severity/effort: minor, low effort; also repeated as an optional nitpick.
- File: widget `components/AiUsageNowCard.qml`, reviewed lines 87-89.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361435
- Assessment: the constant animation runs while hidden or idle. However, its
  source comment records why it was made constant: clearing session state during
  cache parsing previously restarted the pulse and made it appear too fast.
- Effect if fixed correctly: hidden/idle cards stop unnecessary animation work
  while an active session retains a steady pulse.
- Recommendation: address the work, but do not blindly restore the suggested
  `running: liveDot.visible && liveDot.live` binding. It could restore the old
  restart behavior. Preserve animation phase, for example through a tested pause
  strategy, and verify behavior across cache updates and visibility changes.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 6. Bug suggestion: Preserve repeated daylight saving hours

- Reviewer severity/effort: minor, low effort; also repeated as an optional nitpick.
- File: widget `bin/opencode-usage`, `hour_start_ms`, reviewed lines 556-558.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361431
- Assessment: not reproduced in the read-only repeated-hour test. On this
  machine's Python, the existing naive local datetime retains the fold through
  the current replacement operation.
- Evidence: for America/New_York, 2026-11-01 01:30 with fold 0 and fold 1,
  current bucket starts were 1793509200000 and 1793512800000 milliseconds,
  exactly one hour apart. The proposed timezone-aware expression returned the
  same two values.
- Effect of the supplied replacement in that test: none.
- Recommendation: hold until a failing case is demonstrated. Further evaluation
  can cover other timezones, non-hour DST transitions and supported runtimes.
  Do not call this a confirmed repair based only on the review assertion.
- Status: unapplied; this is the one finding recommended for deferral.

## 7. Bug: Avoid applying lifetime totals to partial history

- Reviewer severity/effort: minor, low effort.
- File: widget `bin/opencode-usage`, reviewed lines 466-470.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361416
- Assessment: confirmed for incomplete historical sessions. Per-message loading
  uses a 730-day horizon, while session aggregates can include lifetime totals.
  `balance_session` assigns positive residuals to the newest loaded message.
- Read-only synthetic reproduction: 100 recent input tokens plus a lifetime
  aggregate containing 9,000 older tokens resulted in 9,100 recent tokens.
  The suggested snippet kept the recent total at 100 in that example.
- Risk in the supplied snippet: it removes balancing for all sessions with
  message rows, including complete histories with legitimate missing usage.
  Another synthetic case expected 41,000 cache-read tokens; current balancing
  retained 41,000, while the snippet returned 40,000. The existing regression
  `test_aggregate_residual_is_added_once` checks this type of residual.
- Effect if fixed correctly: older usage no longer inflates recent totals;
  affected period token and API Value figures may decrease to their correct
  values. Legitimate residual accounting must remain supported.
- Recommendation: use a tested completeness-aware guard rather than removing
  reconciliation globally. Verify horizon, partial-history and complete-history
  cases before choosing the implementation.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## 8. Bug: Filter non-Island widgets before deduplication

- Reviewer severity/effort: minor, low effort; also repeated as an optional nitpick.
- File: `ryoku/shell/quickshell/inir/services/CustomWidgets.qml`, reviewed line 16.
- Finding: https://github.com/Ryoku-dev/ryoku/pull/779#discussion_r4522361438
- Assessment: confirmed. A user widget without `irisQmlPath` reserves its ID
  before being rejected, so a bundled Island module with the same ID is rejected
  as a duplicate too.
- Read-only reproduction: a desktop-only custom `ai-usage` entry followed by
  the bundled Island entry produced zero offered modules with the current
  predicate and one with the proposed predicate.
- Effect if fixed: a desktop-only custom copy no longer hides the bundled
  dashboard. A valid custom Island module still takes precedence.
- Recommendation: apply the validity check before adding the ID to `seen`.
- Status: implemented in primary source and mirrored to the fork; locally verified, committed and pushed in `2566ef372`.

## Suggested priority

1. Duplicate Claude scans, incomplete-history accounting and module deduplication.
2. Translation support, hidden UI retries and phase-preserving animation gating.
3. Scoped em-dash cleanup.

Hold the daylight-saving suggestion until reproduced. Seven findings are worth
addressing; the pulse and lifetime-history snippets need adaptation.

Preserve the intended design throughout: token history counts recorded local
usage regardless of account ownership; quota bars use measured account-wide
data from supported CLI/Desktop sources; background collection continues after
the first module load even with the dashboard closed.

## Original read-only validation record

The assessment read all eight inline comments, the one submitted review and the
one PR discussion summary through the GitHub API. It compared the published
commit with current local code. Accounting, DST and deduplication examples ran
in memory, without reading or rewriting live usage data. No review fixes were
applied, no full repair test suite was run, and no GitHub reply was posted.

Full review: https://github.com/Ryoku-dev/ryoku/pull/779#pullrequestreview-5838416482

Generated review summary:
https://github.com/Ryoku-dev/ryoku/pull/779#issuecomment-6762079968

## Implementation completed

Updated 2026-11-10 16:59 IST. Seven recommendations are implemented, with 181 primary
and 181 fork tests passing. See PR_779_FIX_RESULTS.md for the exact fixes,
benchmark, documentation, test adaptations and live delivery record. The guide
and structure-map link were explicitly authorized by the user. The changelog
is unchanged from task start. No commit/push or GitHub review reply occurred.

## Fix publication

At 2026-11-10 17:04 IST, the user-authorized fix commit 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1 was
pushed to ai-usage-dashboard and verified on existing PR #779. Seven fixes and
the related documentation/worker are published. DST remains held; no new PR
or review-thread reply was created. Earlier uncommitted status is historical.

## Second review completed locally

The user subsequently authorized all six new suggestions. They are addressed
in both sources, with the 24-hour and OAuth changes adapted rather than copied
literally. All 190 primary and fork cases pass. See
PR_779_SECOND_REVIEW_FIXES.md for scope, caveats, tests and live verification.
This second update is uncommitted/unpushed; first-review fixes remain published.

## Second-review publication

At 2026-11-10 19:36 IST, second-review commit dad97d5ab07f6db20900742ddd6909251db9dbd9 was pushed
to the existing ai-usage-dashboard PR branch. PR #779 head is verified. All
six new suggestions are published, with 190 cases per target passing.

## Remaining six threads: published fixes

At 2026-11-10 21:23 IST, commit 5ca6583632e7bf086362feb395f80c87bf40f431 addressed the remaining aggregate
fallback, stale-history recovery, tier resolution, Claude bootstrap, tile
fallback and percentage translation. All 197 cases per target pass. See
PR_779_REMAINING_SIX_FIXES.md. Thread state awaits reviewer confirmation.
