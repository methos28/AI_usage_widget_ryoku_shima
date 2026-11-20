# AI Usage project instructions

These instructions belong to this standalone repository. Resolve every path
below relative to the checkout root; never assume a particular username or
clone location.

## Start a session

1. Read `HANDOFF-CODEX.md`, `memory/current-state.md`, and `PLAN.md`.
2. Read `PROJECT_LOG.md` completely once per fresh project session. It is the
   append-only chronological record. Older reports and `memory/history/` are
   evidence, not permission to resume superseded waits, holds or rebuilds.
3. Check `git status -sb`, recent commits and remotes before editing. Verify
   the working tree against the current handoff. If records disagree, append
   the discrepancy to the log before choosing a source or deploying.
4. Load `.agents/skills/ai-usage-development/SKILL.md` for project work.

## Communication preferences

Load `.agents/skills/i-have-adhd/SKILL.md` and
`.agents/skills/caveman/SKILL.md`. They are always active for this project;
Caveman mode is **full**. Use the ADHD structure and Caveman compression.
Preserve full sentences for questions, security and destructive actions.
The user's explicit `normal mode`, `stop adhd mode` or `stop caveman`
instruction suspends the corresponding preference. These styles govern chat;
files, documentation and commit messages remain plain prose.

## Source and delivery

- `ai-usage/` is the canonical, self-contained application. Edit it first.
  `collector/` contains compatibility links, not independent implementations.
- The optional Ryoku mirror is on `methos28/ryoku:ai-usage-dashboard`, under
  `ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/`. Locate the checkout
  on the current PC; `RYOKU_TEST_SOURCE` may identify it. Keep deliberate
  runtime parity while preserving documented manifest/source/CLI labels.
- Keep standalone tests, reports and AI context here. The existing minimal
  Ryoku submission includes widget runtime and focused guide/changelog changes;
  do not add tests/CI, Rashin collectors, hooks or unrelated files to that port
  unless the user explicitly changes scope.
- On a Ryoku host, load `.agents/skills/ryoku/SKILL.md`, read that host's
  Rashin vault and use `ryoku owner` before desktop/config edits. Never edit
  shipped Quickshell files. Deploy through `install.sh` to the supported user
  copy at `~/.config/inir/widgets/ai-usage`, then reload and inspect it.
- A source-only PC does not need a Ryoku installation to read/edit the project
  or run supported non-GUI checks. GUI installation and full desktop validation
  require a compatible Linux Ryoku/Shima/Quickshell environment. Use Linux,
  WSL or a Linux VM for the POSIX collectors/tests; do not claim native Windows
  GUI compatibility.
- Run `test/run.sh`, applicable QML checks and data checks before live delivery.
  Keep tests isolated from real accounts, caches and persistent price ledgers.
  Back up a working live bundle before a preview. Never leave a live-only fix.

## Working rules

- Do the requested work without unrelated cleanup, refactors or optimizations.
- Append each code, requirement, diagnosis, validation and deployment change to
  `PROJECT_LOG.md`. State the evidence, current commit/publication status and
  uncertainties. Preserve old entries; append corrections.
- Keep `HANDOFF-CODEX.md`, `PLAN.md` and `memory/current-state.md` current at
  checkpoints. Put machine-specific observations in `memory/local-machine.md`.
- Do not commit or push until explicitly requested. `push to local` means
  commit only; `push to remote` pushes already-approved commits and does not
  independently authorize new ones. An explicit commit-and-publish request
  authorizes both within its named scope. Session authorization and user
  instructions take precedence; do not ask again for an already approved step.
- Never force-push, rewrite published history, bypass hooks or write upstream
  `Ryoku-dev/ryoku` without explicit instructions. A request for the user's
  Ryoku repo means their fork. Never create a PR or post review messages unless
  the user asks. Track user-provided PRs in `PR_TRACKER.md`.
- Runtime source data, credentials, databases, local cache/ledger snapshots,
  screenshots and raw logs do not belong in a public source checkpoint.

## Behavioral invariants

- Agents: OpenCode, Codex and Claude are supported. Earlier Claude hold-outs
  and demo-only states are historical.
- All agents use **API Value**. It is local API-equivalent work, not a bill,
  wallet balance or subscription charge. Unknown/partial pricing stays explicit.
- Preserve saved historical daily price dictionaries. Do not reprice old days
  using current rates. Let tests use throwaway state and disable price downloads.
- The widget invokes its own `bin/collect-usage` and private
  `~/.cache/ai-usage` caches. Do not restore old shared-service dependencies.
- Session running state needs actual lifecycle/process evidence. Cached stale
  activity is unknown, not proof that a task is still running.
- Retain message identity learned from matched copies; distinct third-store
  requests must stay distinct. Keep quota cache answers bound to login context.
- Reject future usage from current totals. Agent switches must publish only the
  selected snapshot and discard old/superseded asynchronous reads.
- All-time trend is a fixed 45-day view; Activity is a full 9-by-7 grid.
- Motion defaults are 360 ms for bars, 380 ms for numbers and 180 ms for fades,
  scaled by theme settings. Respect reduced motion and hidden surfaces.

Current user instructions outrank this file, bundled skills and historical notes.
