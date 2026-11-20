# Continue development on another PC

## Clone and recover context

```bash
git clone https://github.com/methos28/AI_usage_widget_ryoku_shima.git
cd AI_usage_widget_ryoku_shima
```

Open AGENTS.md and HANDOFF-CODEX.md, then memory/current-state.md and PLAN.md.
PROJECT_LOG.md keeps the complete history. Bundled skills are in .agents/skills;
CLAUDE.md and opencode.json route other coding agents to the same instructions.
The new checkout does not need the original username or home directory.

## Development dependencies

Use a POSIX Linux environment for collector tests, or Linux under WSL/VM on
another OS. Python 3.10+, Node.js 18+, Bash, flock, Git and normal Linux command
line tools are required. The app uses Python's standard library; no account
credentials or production data are needed for its fixtures.

Full native GUI validation and installation require Ryoku/Shima, compatible
Qt 6 QML modules and Quickshell (qs). Without qs, native GUI tests report skips;
that permits source/collector work but does not establish desktop compatibility.
Optional qmllint checks also report when the tool is absent.

```bash
bash test/run.sh
```

At this checkpoint, the full environment passes 235 cases. A simulated
source-only environment without qs passes 216 and skips 19 GUI/host-specific
checks. Skips identify missing validation rather than a desktop compatibility
claim.

For an optional Ryoku checkout, point checks at paths on this PC:

```bash
export RYOKU_TEST_SOURCE=/path/to/your/ryoku-checkout
export RYOKU_QML_IMPORTS="$RYOKU_TEST_SOURCE/ryoku/shell/quickshell"
bash test/run.sh
"$RYOKU_TEST_SOURCE/bin/ryoku-dev-lint-qml" "$PWD/ai-usage"
```

The shared-host test skips unless RYOKU_TEST_SOURCE is set. The optional runtime
mirror uses AI_USAGE_TEST_WIDGET, CODEX_USAGE_TEST_COLLECTOR,
OPENCODE_USAGE_TEST_COLLECTOR, OPENCODE_USAGE_TEST_SOURCE and
CLAUDE_USAGE_TEST_COLLECTOR. Set them deliberately for the selected target;
do not infer fork parity from a primary-only run.

## Optional editor language servers

opencode.json uses tools/lsp.py to find language servers on PATH, in the
current user's .local/bin/.npm-global/bin, and common Qt installations.
It honors RYOKU_QML_IMPORTS and passes paths as arguments without shell expansion.
Start the coding agent from the repository root. It does not install tools.

For example, with npm available, install pyright,
vscode-langservers-extracted and bash-language-server using your preferred
user-managed Node setup. Obtain qmlls/qmllint from the current distribution's
Qt development packages. Existing OpenCode language servers not overridden by
this config remain under OpenCode's own defaults.

## Optional Ryoku mirror

The feature branch is methos28/ryoku:ai-usage-dashboard. Its current published
reference at export is f039733d7. It was synchronized with upstream 3f4f6ee;
fetch fresh refs before future work. PRs #779 and #881 are merged. Never treat
the user's fork as permission to write upstream or open a new PR.

The mirror path below a selected Ryoku root is
ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/. Preserve built-in
manifest metadata and OpenCode CLI/source labels. Keep tests, raw evidence and
this continuity package in the standalone repo, following the established
minimal port scope.

## Live installation

On a compatible Ryoku host, inspect that host's vault and ownership rules,
back up the current user widget, validate the source, then run:

```bash
bash install.sh
```

The installer atomically publishes ~/.config/inir/widgets/ai-usage and reloads
the shell, with rollback on failure. It does not provision Ryoku, authenticate
providers, migrate another machine's credentials, or restore usage ledgers.
Use the current user's own provider logins and native stores.

The original PC's custom copy survived Ryoku 1.1.0 and matched source on the
read-only export check. That observation is not a promise about every future
package update or host configuration.

## Public checkpoint contents

Project code, tests, design/audit reports, instructions, skill snapshots and
project memory are versioned. Historical reports retain their original paths
and dates. Raw evidence screenshots/logs/cache snapshots, native databases,
account files and generated system vaults stay local. Reproduce current
behavior through the permanent isolated tests instead of copying old live data.
