# Ryoku AI usage port: local test report

Current status (2026-11-07 18:40 IST): the fork was recreated and the module re-landed directly on `unstable-dev` as `f0c5a4f0f`. The optimisation pass and the Limits-card caption fix are committed as `31d36bef9` and `f9b7a7dc1` and pushed; remote head is `f9b7a7dc1`. OpenCode and Codex remain the only agents. Earlier sections record the previous fork state and are kept as history.

Recorded: 2026-11-07 15:09 IST
Checkout: `/home/methos/Projects/ryoku-unstable`
Current branch: `unstable-dev`
Commit: `8622b445bda13b2cde4e1868ba3ab11fb0997250`
Preserved feature branch: `ai-usage-builtin`, at the same commit and tree.
Local tracking base: `origin/unstable-dev` at `3d0c497c3`.

## Outcome

All focused automated checks passed. Two new commits were created with the
normal repository hooks, then local `unstable-dev` was fast-forwarded to the
same tested tree. Its working tree is clean. The branch is 14 commits ahead
of the local upstream tracking reference: 12 existing feature commits plus
these two accepted-fix commits:

- `28cea5d3a` - fix rollout counts and quota windows.
- `8622b445b` - keep charts compact and activity complete.

No fork, remote push, PR creation, live deployment, package upgrade, or change
to the upstream channel was performed.

## Automated checks

| Check | Result | Coverage |
| --- | --- | --- |
| `python3 tests/codex-usage-regression.py` | PASS, 14 tests | Replayed, moved, copied and truncated rollouts; duplicate snapshots; genuine counter resets; separate sessions; activity-state migration; previous-day replay; paid/Free quota windows; reset fields; plan changes; actual QML parser functions |
| `bash tests/opencode-usage.sh` | PASS, 8 assertions | OpenCode 2.x store, schema drift, legacy table, file store and stale-cache fallback |
| `bash tests/codex-usage.sh` | PASS, 6 assertions | Real rollout shape, plan, 30-day reported window/reset, daily deltas, sessions/lifecycle and periods |
| `python3 tests/ai-usage-cache.py` | PASS | Published cache contract |
| `bin/ryoku-dev-lint-qml` on shipped AI usage widget | PASS | Project fatal-load criteria with checkout imports |
| QML binding gate on widget, CustomWidgets and WidgetManagerPanel | PASS | Duplicate properties and handlers |
| QML lint on CustomWidgets and WidgetManagerPanel | PASS | Same fatal-load criteria as the project lint gate |
| `bin/ryoku-dev-verify-delivery --quiet` | PASS | Existing package/deployment coverage |
| `bin/ryoku-dev-verify-wm-isolation --quiet` | PASS | No compositor-specific leaks |
| Workflow YAML parsing | PASS | New regression suite wired into existing CI; Node 22 explicitly configured |
| Normal pre-commit and commit-message hooks | PASS, both commits | Existing hooks enabled; none bypassed |
| `git diff --check` | PASS | No whitespace errors |

Raw qmllint can emit advisory warnings; the project fatal-QML gate passed.
The optional `rashin-reviewer` executable is not installed in this checkout's
environment. Its optional hook stage therefore did not run; the remaining
normal hooks ran and passed. No reviewer or hook configuration was weakened.

## Additional focused experiments

- Executed the actual trend and heatmap bindings in Node in 168 date/history
  combinations across Asia/Kolkata and America/New_York, including DST dates.
  Verified fixed 7/30/45-day trend lengths and the full 63-square Activity grid.
- Exercised the actual shipped-widget scanner, catalog parser, install command,
  and installed-state lookup in temporary storage. An initial install worked;
  a repeated install preserved a local edit instead of overwriting it.
- Confirmed Ryoku's packaged OpenCode collector lookup, environment override,
  immediate saved-agent fallback, Claude hold-out and manifest version 1.2.0
  were preserved.
- Compared both branch tree hashes: `unstable-dev` and `ai-usage-builtin` are
  identical. The tested implementation did not change during the fast-forward.

## Scope audit

The full submission against the local tracking base contains 26 required
files: the shipped widget, its discovery/install seam, the two collectors,
focused tests and existing AI usage CI workflow. README.md, CONTRIBUTING.md,
AGENTS.md, changelogs, packaging and unrelated files are unchanged.
Changelog additions were removed at the user's explicit scope request.
This report and the development history are stored only in the standalone
module project, outside the Ryoku submission.

Changed files:

- `.github/workflows/ai-usage-collector.yml`
- `ryoku/rashin/usage/codex-usage`
- `ryoku/rashin/usage/opencode-usage`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/AiUsageTile.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/IrisCompact.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/UsageModel.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AgentAvailability.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageActivityCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageEmptyCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageFoldHeader.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageGlassCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageGlassPane.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageLimitsCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageModelRow.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageModelsCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageNowCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageSpendBody.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageSpendCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageTrendCard.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/components/AiUsageWindowRow.qml`
- `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/widget.json`
- `ryoku/shell/quickshell/inir/modules/background/widgets/WidgetManagerPanel.qml`
- `ryoku/shell/quickshell/inir/services/CustomWidgets.qml`
- `tests/ai-usage-cache.py`
- `tests/codex-usage-regression.py`
- `tests/codex-usage.sh`

## Limits of this report

This session cannot access the live shell socket or Wayland display, so a fresh
on-screen run of the Ryoku checkout is not claimed. The standalone module was
previously exercised by the user, including screenshot feedback, but that is
not a new end-to-end visual test of this checkout. Live card height, animation,
and click-input backlog still need human review. GitHub CI has not run on this
unpublished branch, and the remote base was not refreshed during this local
port. No Claude real-data validation was attempted.

## Approval boundary

Local work and tests are complete. Creating a fork, pushing the feature branch
and opening a draft PR against Ryoku-dev/ryoku:unstable-dev require the user's
next explicit consent. Nothing has been submitted remotely.

## Fork freshness check: 2026-11-07 15:23 IST

A fresh fetch from methos28/ryoku unstable-dev now succeeds. The fork is at `0749ec350`; local unstable-dev is still `8622b445b`. There are 14 local-only and 3 fork-only commits. The missing commits are `c302ec734` (Fedora greeter skin fix), `454280228` (merge of PR #743) and `0749ec350` (release bump to 1.10.2). No integration was performed. The automated results above remain valid for the previously tested local tree; update the base and rerun the required gates before submitting a PR.

## Synced fork PR: 2026-11-07 15:32 IST

Draft PR: https://github.com/methos28/ryoku/pull/1

Base: methos28/ryoku:unstable-dev at 0749ec350. Head: ai-usage-builtin at 076d728bd. Local unstable-dev points to the same head. The fork base is included without rewriting the project commits; no project files were lost or altered by the base merge. GitHub confirms the PR contains only the same 26 required files. README, CONTRIBUTING, changelog and packaging changes remain excluded.

All focused local gates passed again after the base merge. Normal pre-push package-dependency and vendored-WM checks also passed. The first GitHub collector run found the pre-existing cache-contract test relied on a real caller OpenCode store. Commit 076d728bd fixes only that existing test with isolated SQLite fixtures. It passes locally with a normal environment and with an empty caller HOME, missing caller store and UTC timezone. The updated GitHub AI usage collector workflow is green: https://github.com/methos28/ryoku/actions/runs/42362143313. At the last PR query, five checks succeeded and three were still running, with no failures on the latest head. Fresh checkout visual verification remains unperformed. No PR merge was requested or performed.

## Accepted PR verification: 2026-11-07 16:07 IST

PR #1 merged into the fork’s unstable-dev at 24b401eee; its version bot then created 674c62a3c. All project files are identical to PR head 076d728bd. The new widget is present at https://github.com/methos28/ryoku/tree/unstable-dev/ryoku/shell/quickshell/inir/defaults/widgets/ai-usage. The repository default main branch does not contain it because that was not the PR target.

Collector, QML and delivery checks passed after the merge. Arch, Void and Fedora publisher failures report missing R2 credentials and signing keys. Testing gate also fails on missing R2 configuration. These four workflow failures do not alter or remove merged files. No project source or fork settings were changed during diagnosis.

## Fork reset and re-land: 2026-11-07 16:32 IST

At the user's request, PR #1 and all 18 commits it added to `unstable-dev` were removed with a force-push, not a revert commit. The fork branch was synced to upstream `0749ec350`. The old checkout at `/home/methos/Projects/ryoku-unstable` was backed up (patch plus a local mirror under `~/.local/share/ryoku/ai-usage-backup/`), deleted, and replaced with a fresh clone of the fork.

The tested 26-file patch was applied to `0749ec350`; the staged tree was byte-identical to the tested `076d728bd` tree. Commit `2877b9469` was created with the repository hooks enabled and pushed normally. On the committed tree, all four module test suites and the shipped-widget QML lint passed; delivery and WM isolation ran in the pre-commit hook and passed. GitHub compares the branch to `Ryoku-dev:unstable-dev` as ahead 1, behind 0, 26 files.

The new pull request is for the user to open. PR #1 remains marked merged and still shows `076d728bd` as its head, because GitHub does not un-merge or delete merged PRs. Branch version is again 1.10.2. Fresh visual sign-off, Claude validation, permanent fixtures and the fork workflow decision are unchanged.

## Authorised remote delivery: 2026-11-07 22:30 IST

The user requested committing and pushing the full current AI usage work to methos28/ryoku:unstable-dev. The complete local preview is now ported: daily public-price snapshots and private monthly spending ledgers, the Codex-only Est. Spending display, RPC/cache hardening, suppression of previous subscription quotas for API-key/Bedrock accounts, and the audited shared-widget installation fixes. Preserved packaged collector lookup, RYOKU_AI_USAGE_COLLECTOR overrides, manifest 1.2.0, and the agent hold-out. Billing imports and wallet lookups remain excluded.

Fork validation: 31 collector tests, seven widget tests and five shared compatibility tests pass, plus both collector shell fixtures, the isolated cache contract, fatal-QML lint for module and changed shared components, the binding gate, delivery and WM isolation. One new portability regression rejected a transient standalone path copied during the port; corrected before commit. The final change does not alter hooks, packaging, system configuration, themes or unrelated widgets. The live primary preview was checked earlier, including the Est. Spending alignment and a real rpc/Plus refresh. This is not a new live deployment of the fork checkout or a real API-key credential test. Commit, push and remote checks follow.

## Remote delivery verified: 2026-11-07 22:31 IST

Committed and pushed f26ede8ad40a73852a6094bc57d784f9e1443731 to methos28/ryoku:unstable-dev. Normal commit and push hooks passed. GitHub confirms the same branch SHA and the fork working tree is clean. The 13-file delivery contains five module QML files, two shared installer QML files, the Codex collector, the CI workflow and four test files. No upstream, main, PR, package or standalone remote change was made.

All local gates above passed. GitHub reports no workflow or check runs for the new head, so CI success is not claimed. Commit: https://github.com/methos28/ryoku/commit/f26ede8ad40a73852a6094bc57d784f9e1443731 . Primary source and local records remain uncommitted outside this fork delivery.

## Built-in Shima discovery correction: 2026-11-07 23:25 IST

Corrected a delivery gap identified from the user's Shima Settings screenshot: packaged AI Usage is now offered directly in Island / Desktop page / Your modules, without copying it through a separate widget manager or RyoStore Add-ons. The built-in manifest flag and module catalog are downstream integration additions. Settings and Island loading use the same catalog; installed user copies win, and existing enabled-module choices remain untouched. Shared desktop widgets and manual installation behavior retain their old registry.

All 46 tests pass, including three new fresh-profile/override/real-QML-runtime cases, plus shell fixtures, cache contract, QML lint/compilation/binding, delivery and WM isolation. Both new visibility tests fail against the prior implementation. The package's existing full Quickshell payload copy delivers the changed host files and bundled manifest. This adds two shared host files to the earlier audited set: IrisOptions.qml and IrisCustomModule.qml. Their changes only switch the module choices/lookup to the shared catalog and clarify the row text. No live shipped-file edits, packaging changes, activation changes, billing access or standalone collector changes are included.

## 2026-11-08 00:27 IST — Stable host versus unstable PR compatibility re-audit

The user raised the difference between their stable Ryoku installation and the unstable-dev PR target. Confirmed installed Ryoku v1.0.7 and desktop/shell/rashin packages from f7197d7, with Quickshell 0.3.2 and Qt 6.12. Refreshed both official upstream refs: main f7197d72de8a21e44b0bea922bdd915f28f6b327, unstable-dev 0749ec35005cdae3b5c925eb91c32a6904a998d5. The ai-usage branch remains clean at 9e4268ff2, contains the exact latest unstable commit and is zero behind/six ahead. Its 32-file diff is against unstable, not stable.

Audited every pre-existing PR path and direct host dependencies. Nine checked Shima files are byte-identical between upstream stable and unstable: IrisStyle.qml, IrisText.qml, IrisSurface.qml, MaterialSymbol.qml, Directories.qml, IslandDesktopPage.qml, IrisCustomModule.qml, CustomWidgets.qml and WidgetManagerPanel.qml. Both existing collectors and the existing AI usage workflow are also unchanged between those upstream refs. Among shared runtime files modified by the PR, IrisOptions.qml differs between the upstream branches by one added Shortcuts entry; the PR retains that entry and changes only the module choices and visibility. The shared AiUsage.qml reader has a new pace helper on unstable; the PR does not overwrite it, and compatibility tests execute the current unstable reader. Nearby default-terminal-theme and recorder-persistence changes are also preserved and outside this PR. There are wider unstable changes, so these scoped comparisons do not claim that all Shima/runtime code is identical.

Reran target-source validation due to the newly raised integration concern: 31 collector, seven widget and eight shared compatibility tests pass (46 total), including real component compilation against the unstable checkout, actual settings/catalog/loader expressions, real QML typed-list runtime and current shared-cache readers. Both shell fixtures, isolated cache contract, fatal-QML lint, binding, delivery, WM isolation and whitespace gates pass. No code incompatibility was found in the checked paths; no application-source fix, commit or push is justified by this audit alone.

Read PR 757: the user has corrected the base to unstable-dev and marked it ready, head remains 9e4268ff2, and GitHub reports it mergeable. The successful checks are notification/triage jobs. The functional workflows, including AI usage collector, QML Lint and delivery, report action_required pending approval for the fork contribution. This is not a code-test failure or a successful functional CI run. Official GitHub documentation confirms maintainers with write access approve these workflow runs. No workflow approval or PR state change was attempted.

Remaining gap: tests and the live stable preview do not establish that a complete unstable desktop with its package versions, session startup, installation/update flow and interactions has been exercised. Recommend maintainer-approved CI and an unstable test session/VM before treating full runtime compatibility as verified. The user's daily stable installation has not been upgraded, restarted or modified. This audit is read-only apart from primary local records. Earlier broad claims of passing gates remain scoped to their local/source tests, not full unstable-system validation.
