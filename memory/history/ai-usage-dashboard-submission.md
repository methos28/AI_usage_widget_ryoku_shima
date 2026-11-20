# Active AI usage dashboard submission

Updated 2026-11-10 12:43 IST. This supersedes the old review checkout/ai-usage history and
backup wait phase. Active checkout: /home/methos/ryoku-arch, branch
ai-usage-dashboard, fork https://github.com/methos28/ryoku.git.
Published commit: 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667. Parent/base: cd1a06478.
Actual remote verified; clean checkout and 0/0 remote divergence.

The user requires only 28 widget runtime files at
ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/, three shared QML wiring
files, and an initial feature entry only under Added in CHANGELOG.md. No Rashin
collectors/services or tests/CI/unrelated changes in the port. Keep this scope.
All 172 existing regression cases ran externally against the new source; QML
load, parsing, whitespace and normal hooks pass. ShellCheck was unavailable.
No live deployment/data or package changes occurred.

Treat this as the first feature submission until the user explicitly says
otherwise. Track every PR the user provides in the primary project's
PR_TRACKER.md. No PR has been created; no URL/number is assigned. Never create
a PR against Ryoku-dev/ryoku unless the user explicitly instructs it later.
Do not frame internal pre-publication repairs as upstream bug fixes.

Primary records: ~/Documents/opencode_widget_ryoku_shima/
DASHBOARD_SUBMISSION_2026-11-10.md, PR_TRACKER.md, PROJECT_LOG.md.
Local first-feature title/body drafts: RYOKU_PR_TITLE.txt, RYOKU_PR_BODY.md.
The older ~/Projects/ryoku-unstable is frozen historical context. Do not push it.

## Current uncommitted enhancement: 15-second background refresh

See primary BACKGROUND_REFRESH_2026-11-10.md. UsageModel delegates to a local
engine-lifetime UsageRefresh singleton in widget/refresh/. It collects all
agents every 15 seconds after the first module load, even after the page is
destroyed, plus an early run when opened. It starts only on first module load
each shell session, not at login. In-flight requests coalesce; locks retry
while hidden. Claude account-source/cooldown limits are unchanged.
All 174 primary tests, 21 external fork UI/discovery tests and relevant gates
pass. Three runtime files are deployed; real all-agent cache updates were
observed for 43 seconds while closed, beyond the page-unload deadline. The
fork delta is only three widget files and existing Added-entry wording.
No new commit/push/PR; published head remains 5c9d9f11c. Primary docs/tests
remain separate from the fork's minimal runtime submission.

## Owner reminder: primary app source must always be updated

The user reaffirmed that all application changes must be made in
~/Documents/opencode_widget_ryoku_shima and mirrored to the active fork; never
make an app-only fix solely in ai-usage-dashboard. The primary/fork/live copies
of all three background-refresh files were verified byte-identical. Keep tests
and records in the primary project and the fork submission minimal. PR #779
findings remain unapplied until explicit fix authorization.

## PR #779 review fixes implemented locally

The user created https://github.com/Ryoku-dev/ryoku/pull/779, the first feature
submission. Seven recommended findings are implemented in primary and fork,
with 181 tests each. DST remains unchanged. Claude shares a transcript pass,
OpenCode guards old/unknown session residuals, hidden UI retries are gated,
visible copy is translated, em dashes are removed, pulse phase survives pauses,
and invalid custom entries no longer suppress built-ins. The user explicitly
authorized docs/ai-usage.md and the docs/structure.md link, a scoped exception
to the old docs exclusion. Changelog stays as the existing Added entry.
Fourteen tested widget files are live; the managed shared registry was not
overwritten. Changes remain uncommitted/unpushed, including the 15-second worker.
PR head remains 5c9d9f11c. No new PR or review-thread message was created.
Read primary PR_779_FIX_RESULTS.md and PR_779_REVIEW_ISSUES.md for details.

## Latest publication: review fixes pushed

At 2026-11-10 17:04 IST, explicit commit/push authorization and branch clarification led to
2566ef3721dd9e7efc6f1a06d5972b8a55d3e2d1 on methos28/ryoku:ai-usage-dashboard.
Actual remote and PR #779 head are verified. Fork is clean and 0/0 with origin.
Seven fixes, the 15-second worker and focused docs are published; DST is held.
Both 181-case results apply; normal hooks pass. Older uncommitted-fork status
is superseded. The primary standalone source remains updated but uncommitted
in its own repo. No new branch/PR or review-thread message was created.

## Pending second-review fixes

All six new PR #779 suggestions were explicitly authorized and addressed in
primary/fork sources. Exact trailing 24-hour totals and chart bins share a
small rolling-history.py helper across all agents. OAuth cooldown survives
temporary credential gaps in either previous-state shape, with fingerprint
guards. Reused running state clears; UI ticker is visible-only; merged splits
have a defensive numeric check; decorative/en dashes are ASCII. The old DST
function stays unchanged. Changelog remains unchanged in Added; only the app
guide was updated. All 190 primary and fork cases plus relevant gates pass.
Eleven tested runtime files are live, and all three private caches were verified
with matching exact 24-hour bins during closed-page background collection.
No new commit/push/PR/review reply. Published head is still 2566ef372.
Primary report: PR_779_SECOND_REVIEW_FIXES.md.

## Latest publication: second review fixes

At 2026-11-10 19:36 IST, published dad97d5ab07f6db20900742ddd6909251db9dbd9 on
methos28/ryoku:ai-usage-dashboard. Actual remote and PR #779 head match.
The fork is clean and synchronized; both 190-case results apply and normal
hooks pass. The six second-review updates, including exact rolling bins and
OAuth state preservation, are published. Older pending statements are
superseded. The standalone primary source still has its app changes in its
own working tree; no standalone publication or new PR/review reply occurred.

## Latest publication: six remaining findings

At 2026-11-10 21:23 IST, published 5ca6583632e7bf086362feb395f80c87bf40f431 on ai-usage-dashboard and
verified actual remote and PR #779 head. Old/undated aggregate-only rows are
guarded; stale history/source freshness recover; highest tiers resolve; Claude
login/profile metadata bootstraps before projects without phantom entries;
tile fallback is readiness-aware; quota percentage is translated. Primary/fork
code match apart from intentional port details. Both 197-case suites and hooks
pass. Six widget files are live. Changelog stays unchanged in Added; no Rashin,
test/CI or unrelated fork changes. Checkout is clean/0:0. No new PR, review
reply or thread resolution. Primary report: PR_779_REMAINING_SIX_FIXES.md.

## 2026-11-17 publication: saved session titles and upstream sync

The user explicitly selected the existing ai-usage-dashboard branch after initially reversing its name. Saved-title commit aa11db313 and normal upstream merge e7297aec62c2f36cd39b424a7abc418b02439279 are pushed to methos28/ryoku:ai-usage-dashboard. Official unstable-dev is 0389a5e. GitHub verifies two commits ahead, zero behind and only CHANGELOG.md, docs/ai-usage.md and the bundled codex-usage differ (31 insertions, three deletions). Checkout is clean and matches origin. Existing history is preserved; no force push, new branch, upstream write, PR creation or reply occurred. All 56 actual fork Codex tests, merged-source QML and normal commit/push hooks pass. Other branches and the installed stable desktop are unchanged. Primary audit records are still local; all reported bugs remain unfixed. Evidence is in the primary project evidence/branch-sync-2026-11-17.

## 2026-11-17 publication: all current audit fixes

Published d4df8688ae6106ec47427b1d1e662578b49ca122 on the existing ai-usage-dashboard branch after the user explicitly requested the bug fixes too, extending their earlier commit/push request. The branch includes saved titles and all ten audit repairs. Both 222-case suites and QML/integration/hooks pass; live user bundle is updated and all 20 historical price dictionaries are unchanged. GitHub confirms three commits ahead, zero behind unstable-dev 0389a5e and exactly eight related files. Checkout is clean. Source-first primary commit is c9c3eef. No new PR, upstream push, other-branch mutation, package/channel or authentication change. Earlier pending-audit statements are superseded.

## User-approved publication, 2026-11-18 14:16 IST

The user explicitly approved committing to remote. The previous preview hold is released for this delivery. Primary 24b6db3fcecb5b17e1fc52424efba0d7bce6b428 saves the approved source/tests locally; feature 81c0f0e58 and normal sync merge f039733d746563dd4a291484fce603ba62cfa854 are pushed to the existing ai-usage-dashboard branch. Official latest unstable-dev is 3f4f6ee and already contains merged PR #881. GitHub verifies two ahead, zero behind and only eleven motion/switch preview files. The fork is clean and matches origin. The exact tested runtime survives the merge; 233-case results apply, and merged-source five switch/four motion cases plus QML/hooks pass. No new PR, review reply, other-branch push, primary-main remote push, package/channel/auth/data change or history rewrite. Live approved code and backups remain intact. Read latest PROJECT_LOG.md and PR_TRACKER.md; old pending-preview messages are superseded.
