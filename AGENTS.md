# AI usage widget — project rules

This file is scoped to this widget project only: this repository, the live
widget under `~/.config/inir/widgets/ai-usage`, and the Ryoku branch that carries
it. It does not change rules for any other project.

## Read before acting (every agent, every session)

1. Read `PROJECT_LOG.md` completely. It is the chronological record: what was
   changed, what broke, what was diagnosed, and which requirements changed.
2. Read `PLAN.md`. It holds the current phase, the intended next steps, and what
   is explicitly out of scope.
3. Check the live state against the records before editing:
   - `git -C /home/methos/Documents/opencode_widget_ryoku_shima status -sb`
   - `git -C /home/methos/Projects/ryoku-unstable status -sb`
   - `diff -rq ai-usage ~/.config/inir/widgets/ai-usage`
   - cache shape: `~/.cache/{opencode,codex,claude}-usage.json`
4. If the records and the live state disagree, stop and record the discrepancy
   in `PROJECT_LOG.md`; do not silently pick one.

No agent may continue from memory or from a previous conversation alone. The
files are the source of truth for project history.

## Repository names

- "My ryoku repo" means `methos28/ryoku`, the user's fork. Local clone:
  `/home/methos/Projects/ryoku-unstable`, current review branch `ai-usage`.
- "Original ryoku repo" means `Ryoku-dev/ryoku`, the upstream source. It is
  read-only here: do not modify it, push to it, or open pull requests there
  unless the user explicitly asks for the original repo by name.
- When the user says "my ryoku repo", work only in the fork. Never treat it as
  shorthand for the upstream repository.

## Commit and push policy

- Do not commit, locally or remotely, until the user explicitly says so.
- "push to local" means: create the commit locally. It does not allow any
  network action.
- "push to remote" means: push the already-approved commits to GitHub. It does
  not authorise new commits.
- Never force-push, never rewrite published history, never run `--no-verify`.
- Keep work in the working tree until approval; the live widget may be updated
  for testing, but that is not a commit.

## Record every change

Every change to code, data shape, UI, requirements, or design must be appended
to `PROJECT_LOG.md` as it happens. A record entry states:

1. Date and time.
2. What changed (files, functions, cache fields, UI behaviour).
3. Why: requirement, bug, or diagnosis.
4. Evidence: commands, measured values, test results, or file:line references.
5. Whether the change is committed, uncommitted, or live-only.
6. What remains uncertain.

If a requirement changes, record the old rule, the new rule, and who asked for
it. Never rewrite earlier entries; append corrections with a timestamp.

## Delivery gate

1. Edit the repository copy first.
2. Run the gates: `test/run.sh`, QML lint, QML binding gate, and any cache or
   data check that applies.
3. Only after passing: copy the tested files into `~/.config/inir/widgets/ai-usage`
   and reload the shell (`ryoku-shell reload`).
4. Never edit only the live widget and leave the repository behind. If a live-only
   experiment is needed, record it and revert it.

## Scope rules

- No optimisation, refactor, or cleanup beyond the requested fix. Optimise later
  only when the user says so.
- Do not touch the upstream Ryoku `AGENTS.md`, its hooks, packaging, or
  unrelated files.
- The Ryoku branch is a downstream port, not the primary source while the user
  works on the module. Keep the two in sync deliberately and record every port.
- The user requested the `ai-usage` branch on 2026-11-07 for the upstream
  review. Use it for review fixes in the user's fork. Preserve `unstable-dev`;
  do not create other feature branches unless requested.
- Claude is intentionally held out of both the standalone and shipped PR widget
  menus until its collector publishes the same history as OpenCode and Codex and
  is validated with real usage data. Keep shared support for the later follow-up.

## Ownership map

- Main module repository: `/home/methos/Documents/opencode_widget_ryoku_shima`
- Live widget: `~/.config/inir/widgets/ai-usage` (user space, survives updates)
- My ryoku repo (user's fork): `methos28/ryoku`, current review branch
  `ai-usage`; `unstable-dev` retains the delivered module commits.
  Local clone: `/home/methos/Projects/ryoku-unstable`.
- Original ryoku repo (upstream): `Ryoku-dev/ryoku`, read-only reference.
- Live Codex collector copy: `~/.local/bin/codex-usage`
- Live OpenCode collector copy: `~/.local/bin/opencode-usage-v2`
- Caches: `~/.cache/opencode-usage.json`, `~/.cache/codex-usage.json`,
  `~/.cache/claude-usage.json`
- Systemd timer: `ryoku-ai-usage.timer` with drop-in
  `~/.config/systemd/user/ryoku-ai-usage.service.d/override.conf`

## Known traps

- The packaged `/usr/bin/opencode-usage` writes a thinner cache and can overwrite
  the enriched one; the timer must run the repository collector.
- Codex `_hours[].start` is milliseconds; older caches used seconds. The widget
  normalises both.
- Codex legacy costs stay `0`; `_spending` holds the separate local API-equivalent
  estimate. Label it `Est. Spending`, never a Plus charge or wallet balance.
  Missing estimates show an em dash; partial coverage has a tooltip and marker.
- Monthly spending ledgers and daily price snapshots are persistent state under
  `~/.local/state/ai-usage`, private mode 0600. Never reprice older days with
  today's rates. Tests must isolate state and disable live price fetching.
- "running" comes from the rollout turn lifecycle, not from recency.
- The All-time trend is a fixed 45-day window by requirement; it is not true
  lifetime history.
- `muse spark 1.3 contributor` exists in the model catalog as
  `commandcode/meta/muse-spark-1.3-contributor` with variant `xhigh`.
