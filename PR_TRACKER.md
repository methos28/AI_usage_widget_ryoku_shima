# Ryoku widget PR tracker

Owner instruction recorded 2026-11-10: treat this as the first PR/new-feature
submission until the user explicitly says otherwise. Track every PR the user
provides. Historical attempts are not the current submission narrative.

## Submission 1: AI usage dashboard

- Status: PR #779 is open; review fixes committed and pushed, awaiting re-review.
- PR: https://github.com/Ryoku-dev/ryoku/pull/779
- Fork: https://github.com/methos28/ryoku.git
- Base: unstable-dev
- Head: ai-usage-dashboard
- Commit: 5ca6583632e7bf086362feb395f80c87bf40f431
- Branch: https://github.com/methos28/ryoku/tree/ai-usage-dashboard
- Local checkout: /home/methos/ryoku-arch
- Description: initial self-contained Shima dashboard for OpenCode, Codex and
  Claude, with only required built-in wiring. Describe resulting features and
  validation, not the development history or unpublished fixes.
- Changelog: only a new feature entry in Added.
- Authorization: clone, implement required integration, commit and push head.
- PR creation: not requested. Never create a PR against Ryoku-dev/ryoku unless
  the user explicitly instructs it later.

Local title/body drafts: RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md.

Validation: 172 local regression cases run externally against the fresh source;
QML load checks, syntax/whitespace and normal commit/push hooks pass.
Only 32 required paths are committed. No remote CI result is claimed here.

## Pending local enhancement, 2026-11-10

Submission 1 is still the same initial feature. Added 15-second background
refresh after first module load and immediate refresh on open, verified live
and with 174 primary cases. Changes are local and uncommitted/unpushed. The
local PR description includes the behavior; no PR has been created.

## Current description scope

The title/body drafts now describe the actual published 5c9d9f11c branch as the
first feature submission. The pending 15-second worker is excluded until it
is published. Earlier text saying the draft includes it is superseded.
No PR has been created or numbered.

## PR #779 review implementation

The user authorized seven fixes and the focused app guide plus structure-map
link. Implemented and validated with 181 tests in each source target. DST is
held. PR head is still 5c9d9f11c; no new commit/push or GitHub reply occurred.
This remains the first feature submission. See PR_779_FIX_RESULTS.md.

## Latest publication (2026-11-10 17:04 IST)

Published fix commit 2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1 to the same ai-usage-dashboard branch.
PR #779 head and actual remote SHA are verified; local tree is clean and in sync.
Both 181-case results apply to the exact committed patch; normal hooks pass.
This supersedes earlier pending/uncommitted statements. No new PR or reply.

## Pending second-review update

All six new suggestions are addressed in primary and fork, including adapted
24-hour and OAuth behavior. All 190 cases per target pass and widget files are
live. No new commit/push; published PR head remains 2566ef372. This remains
submission 1. See PR_779_SECOND_REVIEW_FIXES.md before publication.

## Latest publication (2026-11-10 19:36 IST)

Second-review fix commit dad97d5ab07f6db20900742ddd6909251db9dbd9 is published on ai-usage-dashboard.
Actual fork and PR #779 heads are verified; the checkout is clean and 0/0.
All 190 cases for each target and normal commit/push hooks pass. Earlier
pending second-review statements are historical. No new PR/review reply.

## Latest publication (2026-11-10 21:23 IST)

All six remaining findings are published in 5ca6583632e7bf086362feb395f80c87bf40f431. The existing
PR #779 head is verified; checkout is clean and 0/0 with origin. Both 197-case
suites and normal hooks pass. Review threads were not resolved or replied to.
See PR_779_REMAINING_SIX_FIXES.md. This remains submission 1.

## 2026-11-17 status correction

GitHub confirms PR #779 merged on 2026-11-10 at 19:53:49 UTC, merge commit 068f782b3de2cf572ea376c56332f8dba5ce4296. It is included in installed stable 08ff328. The current saved-Codex-name enhancement and upstream refresh/RPC reconciliation are local, uncommitted changes on the existing ai-usage-dashboard source branch; no new PR, push or review message was created.

## 2026-11-17 saved-title branch publication

Published saved-title commit aa11db313 and synchronization merge e7297aec6 to the existing ai-usage-dashboard branch. PR #779 stays merged; no new PR or review reply was created. Official unstable-dev remains 0389a5e; GitHub compares the feature as two commits ahead, zero behind, exactly three changed files. The full former feature is already upstream, so the current review diff contains only saved-title code, its guide and changelog. Compare: https://github.com/Ryoku-dev/ryoku/compare/unstable-dev...methos28:ai-usage-dashboard . Audit findings remain unfixed.

## 2026-11-17 audit fixes added to the same branch

Published d4df8688ae6106ec47427b1d1e662578b49ca122 with all ten audit repairs. Both 222-case suites and QML/integration/hooks pass. GitHub verifies ai-usage-dashboard three commits ahead, zero behind official unstable-dev 0389a5e, with eight relevant files changed. The branch now includes saved titles and the bug fixes. No new PR or review message was created. Existing PR #779 remains merged; any new PR using this head receives the fix commit automatically. Compare: https://github.com/Ryoku-dev/ryoku/compare/unstable-dev...methos28:ai-usage-dashboard .

## 2026-11-17 13:47 IST — PR #881 and confirmed identity-promotion finding

The user supplied https://github.com/Ryoku-dev/ryoku/pull/881. GitHub confirms it is open against unstable-dev, head d4df8688ae6106ec47427b1d1e662578b49ca122, title [global] shima: fix session titles and usage accounting. Review comment: https://github.com/Ryoku-dev/ryoku/pull/881#discussion_r4596929076 . The three-store anonymous/A/B identity-promotion bug is confirmed in both source copies and in the actual loaders with temporary stores: expected two requests/240 tokens, actual one/120. The suggested retained-row ID assignment passes five isolated identity scenarios when evaluated in memory. No code fix, commit, push, PR edit or review reply was requested or performed in this verification.

## 2026-11-17 13:54 IST — PR #881 finding repaired

Published 98058bcd8395fdf855771d01ff03b49972e3a956 to the existing ai-usage-dashboard branch. GitHub confirms this exact PR #881 head. The retained matched row now keeps its learned native ID, so a distinct third-store request remains distinct. Both full suites pass 224 cases and the installed collector passes the two new regressions. Checkout is clean; no review message was posted and the thread was not resolved by the agent.

## 2026-11-18 14:16 IST — Motion preview publication after PR #881 merge

GitHub confirms PR #881 is merged at 316f05e811a3515b70ccfdfe00ca768a887fa3ee. Published the user-approved motion/switch preview as feature 81c0f0e58 and normal upstream sync merge f039733d746563dd4a291484fce603ba62cfa854 on ai-usage-dashboard. Official base is 3f4f6ee; cross-fork compare is two ahead, zero behind, eleven feature paths. No new PR was created or existing review state modified. Draft title/body now describe only the motion and cache-handoff delta. Compare: https://github.com/Ryoku-dev/ryoku/compare/unstable-dev...methos28:ai-usage-dashboard .
