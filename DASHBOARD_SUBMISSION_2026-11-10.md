# First AI usage dashboard submission

Completed 2026-11-10 12:43 IST.

Fork: https://github.com/methos28/ryoku.git
Branch: ai-usage-dashboard
Commit: 5c9d9f11cfcbf56de27d2f5433e37b1e95e40667
Fresh base: cd1a06478d5b7c8f952180c89c1f42576fad41da
Local checkout: /home/methos/ryoku-arch
Widget destination: ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/

One new commit from the actual fresh unstable-dev, with no old feature history
restored. The remote branch SHA matches local HEAD and local tracking is 0/0.
The worktree/index are clean. Only the requested fork branch was pushed.

## Submitted files

28 widget files, three required shared QML integration files and CHANGELOG.md.
The three QML files are CustomWidgets.qml (built-in discovery with user-copy
precedence), IrisOptions.qml (module choices) and IrisCustomModule.qml (loading).
The changelog adds four initial-feature lines exclusively under Added.
No Rashin source/service, test/CI, package, docs, hook, AGENTS.md, VERSION or
unrelated files changed. Final diff: 8,864 additions and 5 removals. Of the
additions, 6,753 are widget runtime, 2,046 the offline pricing catalog, 61 shared
wiring and 4 changelog lines.

## Validation

All 172 preserved regression cases pass using an external validation tree that
references this actual checkout. Codex shell fixtures and the private-cache
contract also pass, including source/package payload and fresh-profile module
discovery. All 21 changed QML files pass the load-error lint gate. Python, JSON
and shell syntax and final staged whitespace checks pass. Two empty EOF lines
in widget files were removed after tests; runtime behavior is unchanged.
Normal hooks pass: delivery, WM isolation, QML bindings, message checks, package
dependency resolution and vendored seam parity. ShellCheck is unavailable and
its optional hook check was skipped; no ShellCheck result is claimed. No new
remote CI result is claimed. Logs: /tmp/ai-usage-dashboard-validation-20261110/.

No live widget, ledger, cache, credentials, services or packages changed.

## PR handling

This is submission 1 and descriptions present the whole module as a new feature.
PR_TRACKER.md is the record for user-specified PRs. Local title/body drafts are
ready in RYOKU_PR_TITLE.txt and RYOKU_PR_BODY.md. No PR was opened. Do not create
a PR against Ryoku-dev/ryoku without explicit later user instruction.
