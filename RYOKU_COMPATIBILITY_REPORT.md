# AI usage module: official Ryoku compatibility audit

Reviewed 2026-11-07 against freshly fetched official references:

- `Ryoku-dev/ryoku:unstable-dev`: `0749ec35005cdae3b5c925eb91c32a6904a998d5`.
- `Ryoku-dev/ryoku:main`: `f7197d72de8a21e44b0bea922bdd915f28f6b327`.
- Fork committed head: `methos28/ryoku:unstable-dev`, `f9b7a7dc1`.

The comparison base is the official unstable branch, which the fork extends.
Comparing the entire fork to stable main also includes upstream's unrelated
unstable changes; those are not changes introduced by this module.

## Existing shared files changed by the module

Exactly five pre-existing paths differ from the official unstable base. The
remaining paths are additions scoped to the module and its tests.

| Path | Purpose and impact | Checks and fixes |
| --- | --- | --- |
| `ryoku/shell/quickshell/inir/services/CustomWidgets.qml` | Discovers shipped widgets and installs a selected widget. Other Shima custom widgets share this singleton. | Restored the original `installExample()` API as a wrapper. Existing discovery, configuration, create and remove behavior is unchanged. New installs validate ids, reject overlapping requests, pass paths as arguments, stage copies, and preserve existing folders and symlinks. |
| `ryoku/shell/quickshell/inir/modules/background/widgets/WidgetManagerPanel.qml` | Offers an install button per shipped widget instead of only the example. | The example stays discoverable. Removed an immediate reload that raced installation; the installer reloads when copying ends. QML compilation on Wayland and binding checks pass. |
| `ryoku/rashin/usage/opencode-usage` | Adds history, sessions and periods to the cache also read by other AI panels. | Retains legacy fields and store-layout support. Existing store fixtures, isolated cache contract, and the unchanged shell's actual legacy parser all pass. No further collector edits were needed in this fix pass. |
| `ryoku/rashin/usage/codex-usage` | Adds history and replay protection while preserving quota buckets and cache schema 3. | Fourteen replay/window regressions, rollout fixtures, and actual shared-shell parser checks pass for Plus and a reported Free 30d window. No further collector edits were needed in this fix pass. |
| `.github/workflows/ai-usage-collector.yml` | Runs the module's collector and compatibility checks. | Watches the two shared QML paths and new regression files. Adds calendar/component/loader/cache-reader checks. It changes no runtime or release-publishing policy. |

Official source: <https://github.com/Ryoku-dev/ryoku/tree/0749ec35005cdae3b5c925eb91c32a6904a998d5>.

The module does not change shared themes, `MaterialSymbol`, `IrisSurface`, the
shared `AiUsage.qml` reader, compositor configuration, boot configuration,
packaging, hooks, or unrelated widget implementations.

## Module-local faults fixed

- The extracted menu omitted the module exporting `MaterialSymbol`. It now
  imports `inir.modules.common.widgets`.
- The desktop tile used `root.usage`, although `usage` is a QML id. It now reads
  the model directly. Plan tiles use the actual reported first window; local
  usage without a quota displays tokens rather than an invented percentage.
- The standalone page now immediately falls back from an unavailable stored
  agent, matching the accepted downstream behavior.
- The standalone cache-contract test now creates its own SQLite data, matching
  the already isolated downstream test. It passes with an empty caller HOME,
  absent caller store and UTC.

## Installed desktop audit

The installed `CustomWidgets.qml`, `WidgetManagerPanel.qml`, shared
`shell/services/AiUsage.qml`, `MaterialSymbol.qml`, and `IrisSurface.qml` are
byte-identical to official stable main. They have no user overlays. The shared
loader fixes remain in the fork working tree for future delivery; this task
does not replace installed shared shell files.

One relevant older overlay exists:
`~/.config/ryoku/user_edits/quickshell/shell/modules/bar/barstyles/qsbar/panels/AiUsagePanel.qml`.
Its only differences from official stable are a meter id and anchors for the
detail text below the meter. This is the recorded text-overlap fix, not a
shared visual primitive change. It was preserved.

The live Codex collector matches both source copies, and the live OpenCode
collector matches the primary source. The user service drop-in intentionally
selects these enriched collectors. No cache schema change was introduced by
this task. Other AI panels' actual parsers accept the resulting fixture caches.

## Verification and delivery

- Primary: 26 tests across OpenCode, Codex and UI suites, plus the isolated
  cache contract. Raw Qt lint still emits advisory warnings; it exits zero.
- Fork: 14 Codex regressions, five UI tests, five shared-compatibility tests,
  OpenCode/Codex shell fixtures, and the cache contract.
- QML lint, binding checks, delivery verification and WM isolation pass.
- Every module QML file compiles in an isolated Quickshell engine. The shared
  loader also compiles there. The widget manager's context-menu backend needs
  Wayland; that component was separately compiled successfully on Wayland with
  an isolated HOME/config/socket directory.
- Negative controls restore the old menu and tile individually in temporary
  storage. The new tests reject both faults.
- The tested tile, page and menu were deployed. The complete live widget now
  equals the primary source. Backup:
  `~/.local/share/ryoku/ai-usage-backup/fixes-20261107-191709/`.
- `ryoku-shell reload` succeeded at 19:17 IST; shell status is running. The
  live Codex page renders the stacked caption, actual windows, sessions and
  compact `$0.00` spending. No AI-usage component errors appeared in the new
  instance log.

Live pointer tests and final user visual sign-off remain open. `/dev/uinput`
is unavailable in this session, so no click-input hypothesis is presented as
reproduced or fixed. Claude remains held out pending real usage validation.
No claim is made that unrelated upstream shell warnings were fixed.

Billing clarification from the subsequent verification: the `$0.00` check
above verified presentation only. The Codex collector sets per-record costs to
zero and does not read billed API expenses, prepaid balances or top-ups. The
current card therefore does not establish that API usage was free. OpenCode
costs come from its local usage store rather than provider billing. Live
pay-as-you-go expense tracking is not implemented for Codex.

All new source changes are uncommitted. No commit, push, upstream write,
release setting change or pull request was performed.

## Subsequent RPC and credential audit

The later security audit confirmed the live login is ChatGPT and that quota
refresh uses Codex's own authentication over local stdio. The collector does
not open the auth file, pass login secrets in command arguments, publish the
account object, or start model turns. No billing key or billing request was
introduced. The installed Codex executable resolves to `/usr/bin/codex`, and
no custom ChatGPT base URL is configured.

Hardened the existing Codex collector in both source trees: explicit stdio,
cleanup on initialization failures, process reaping/pipe closing, bounded
response framing with effective timeouts, redacted provider error bodies, and
atomic 0600 usage/activity files. Private home/cache directories already
protected the prior 0644 files here; this audit found no credential export
path in the inspected collector/cache flow.

Seven new tests use fake credentials and a temporary fake server. Current
primary suites pass 33 tests plus the contract; fork suites pass 31 tests plus
collector fixtures, the contract and all previously listed gates. After
installation, an initial sandbox run correctly fell back to rollouts because
Codex startup hit a read-only filesystem. The user approved a normal quota
refresh outside that sandbox; it succeeded and restored rpc/Plus data.
Both live caches are 0600 and the auth file remains 0600. No credential values
were printed. Code and records remain uncommitted.

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
