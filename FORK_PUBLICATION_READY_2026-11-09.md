# Audited corrections published

Published b650d0c474553931ef551332051e46fe3d651d62 to methos28/ryoku:ai-usage on 2026-11-10 03:11 IST
after explicit commit-and-push approval. The remote head matches and the fork
working tree is clean. Normal hooks and 172 local tests for each delivery target
pass. CI is reported separately in the latest project log. Earlier preparation
and publication notes below are historical.

# Widget-only scope correction prepared

The user rejected the broader Rashin collector and distro documentation changes after the earlier publication. Those changes have now been restored to the original upstream review base in the local fork working tree/index. Only the widget bundle, three required shared wiring files, focused tests/CI and root CHANGELOG.md differ from that base. All 131 fork tests and 127 primary tests pass. The corrections are staged but not committed or pushed. See RYOKU_PR_BODY.md and the latest PROJECT_LOG.md entry for the current state. Earlier publication details below are historical.

# Published status

Published after explicit approval on 2026-11-09 20:39 IST.
Commit: [eb91adfd3](https://github.com/methos28/ryoku/commit/eb91adfd3de6e963e4bd25a1156907a10563260e).
Remote branch head verified; fork working tree clean.
The preparation record below is historical.

# Ready to publish: methos28/ryoku ai-usage

The current widget port is staged in `/home/methos/Projects/ryoku-unstable` on
`ai-usage`. Origin is `https://github.com/methos28/ryoku.git`. The local and
fetched remote head is `c2dbdc496bd2b123f50ad01476541acc7ee9f3e3`.
No new commit or push has been made.

## Staged result

- Built-in widget version1.3.0 offers OpenCode, Codex and Claude.
- Collectors ship with the widget, use private caches and retain compatibility
  entry points. Native Codex request accounting and saved-price migration are
  included from the previously reviewed work.
- Claude has native history, model-switch accounting, account quotas, captured
  reset deadlines, process/lifecycle session state and partial local API value.
- All agents use API Value. Reset rows use local date/time and timezone. Agent
  and period dropdowns draw one highlight and retain the selected checkmark.
- The fork's built-in discovery flag, stronger OpenCode schema support, existing
  installed-copy precedence and package/source delivery are preserved.
- CI runs the new regression suites on ai-usage with Python3.14. No runtime
  Prowl dependency or private account data is added.

The30 staged files include the module, two compatibility aliases, regression
suites, CI and public usage documentation. Runtime module code matches the
accepted standalone source, with intentional differences only for built-in
metadata and the downstream OpenCode compatibility implementation. The obsolete
standalone live-cache diagnostic and private audit notes are not published.

## Validation

All134 fork tests pass:6 OpenCode,42 Codex,8 Claude integration,24 Claude quota,
20 Claude lifecycle,13 Claude spending,12 widget and9 shared-delivery tests.
Store-layout/rollout shell fixtures and cache contract pass. QML fatal lint,
bindings, delivery, window-manager isolation, staged whitespace and normal
pre-commit/commit-message checks pass. Package and source fixtures run the
installed Claude helper bundle without a real login or model invocation.

Existing resource warnings are nonfatal. Remote CI is not claimed green because
nothing has been pushed yet. Pricing remains deliberately limited to verified
models; unknown rates are partial. The separate fresh Desktop active-to-idle
manual observation remains pending and is documented.

## Proposed commit

`[global] ai-usage: bundle collectors and add subscription tracking`

The complete proposed message and staged patch are saved in
`~/.local/share/ryoku/ai-usage-backup/fork-publication-20261109-202349/` as
`proposed-commit-message.txt` and `ready-to-commit.patch`.

The widget project's AGENTS.md says a remote push does not authorize new
commits. Explicit approval to create this commit is the only outstanding step.
After approval, use the normal commit and push hooks, fast-forward only to
`origin ai-usage`, then verify GitHub's remote head. No upstream or channel
branch is part of this publication.
