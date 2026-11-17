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
   - widget cache shape: `~/.cache/ai-usage/{opencode,codex}-usage.json`
   - legacy shared caches may also exist at `~/.cache/<tool>-usage.json`.
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
- Claude is enabled in the standalone/live widget as an explicit user-requested
  preview (2026-11-09). Real token history, Sonnet 5.5 API-equivalent costs and
  Desktop account quotas are validated. Native lifecycle/PID fixtures pass;
  a fresh active Desktop run is still pending. The user accepted the Claude
  display name and requested publication to the fork's ai-usage branch on
  2026-11-09, superseding the previous downstream hold for that branch.

## Ownership map

- Main module repository: `/home/methos/Documents/opencode_widget_ryoku_shima`
- Live widget: `~/.config/inir/widgets/ai-usage` (user space, survives updates)
- My ryoku repo (user's fork): `methos28/ryoku`, current review branch
  `ai-usage`; `unstable-dev` retains the delivered module commits.
  Local clone: `/home/methos/Projects/ryoku-unstable`.
- Original ryoku repo (upstream): `Ryoku-dev/ryoku`, read-only reference.
- Widget collectors: `~/.config/inir/widgets/ai-usage/bin/`, invoked by the
  local `collect-usage` launcher resolved from UsageModel.qml.
- Canonical source: `ai-usage/bin/`. Earlier `collector/` entry points are
  relative source symlinks. Keep Ryoku's `ryoku/rashin/usage/` files unchanged.
- Widget caches: `~/.cache/ai-usage/{opencode,codex,claude}-usage.json` and the private
  Codex activity file beside them. Other shell panels retain their shared caches.
- The widget does not use `ryoku-ai-usage.timer` or a service override.
  Earlier home-bin/libexec collectors and service drop-ins may remain for other
  consumers; do not remove those user-owned files during this migration.

## Known traps

- Never fall back to system collectors or shared cache paths inside the widget.
  An older system collector can overwrite its own shared cache; widget data is
  isolated under `~/.cache/ai-usage`.
- Widget collectors use their own private cache locks. Never replace Rashin's
  collectors, acquire its global cache locks, or modify distro documentation.
  Fork changes stay within the widget, required discovery/loading/settings wiring,
  focused tests/CI and root CHANGELOG.md (user scope correction, 2026-11-09).
- Codex `_hours[].start` is milliseconds; older caches used seconds. The widget
  normalises both.
- Codex legacy costs stay `0`; `_spending` holds the separate local API-equivalent
  estimate. Label it `API Value` for every agent, never a Plus charge or wallet balance.
  Missing estimates show a plain ASCII dash; partial coverage has a tooltip and marker.
- Monthly spending ledgers and daily price snapshots are persistent state under
  `~/.local/state/ai-usage`, private mode 0600. Never reprice older days with
  today's rates. Tests must isolate state and disable live price fetching.
- "running" comes from the rollout turn lifecycle, not from recency.
- The All-time trend is a fixed 45-day window by requirement; it is not true
  lifetime history.
- `muse spark 1.3 contributor` exists in the model catalog as
  `commandcode/meta/muse-spark-1.3-contributor` with variant `xhigh`.

## Current submission override (2026-11-10)

The active Ryoku fork checkout is /home/methos/ryoku-arch and the active branch
is ai-usage-dashboard. Earlier ai-usage and Projects/ryoku-unstable references
above are historical. The user authorizes commit and push of this fresh port.
Only widget runtime, three required QML wiring files and an initial Added entry
in root CHANGELOG.md belong in this submission. No tests/CI or Rashin changes
in the port; run preserved tests outside the submitted tree.

Track user-specified PRs in PR_TRACKER.md. Treat this submission as the first
PR and describe the whole module as a new feature until the user says otherwise.
Do not describe unpublished module repairs as upstream fixes. Never create a
PR against Ryoku-dev/ryoku without explicit later user instruction. The current
task authorizes no PR creation, only fork branch commit and push.

## Source-first synchronization reaffirmed by the user

The standalone project /home/methos/Documents/opencode_widget_ryoku_shima is
the primary application source. Every app-code change must be made there and
mirrored deliberately into the active Ryoku ai-usage-dashboard branch at
/home/methos/ryoku-arch/ryoku/shell/quickshell/inir/defaults/widgets/ai-usage.
Never leave an app fix only in the Ryoku port. Keep primary tests and records
here; retain the existing minimal-file policy for the Ryoku submission.
Only Ryoku-specific integration and intentional built-in metadata belong solely
in the port. Validate both copies before deploying tested primary runtime files.
The request to keep copies synchronized does not authorize applying the pending
PR #779 findings; those remain under assessment until the user authorizes fixes.

## Authorized PR #779 review work and guide

On 2026-11-10 the user authorized the seven recommended fixes in
PR_779_REVIEW_ISSUES.md, with the unproven DST change held. They also authorized
docs/ai-usage.md and its link/source-map entry in docs/structure.md in the Ryoku
fork; this is a scoped exception to the older docs exclusion. Keep changelog
copy exclusively in the existing Added feature entry. This authorization does
not request commit, push, new PR creation or review-thread messages.
