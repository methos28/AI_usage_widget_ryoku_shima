# Continue this project from any checkout

This repository is the standalone source of truth for the AI Usage Shima
module. Start from the repository root, regardless of the PC or username.

## Read first

Read `AGENTS.md`, `memory/current-state.md`, `PLAN.md`, and the complete
`PROJECT_LOG.md`. The project skill is
`.agents/skills/ai-usage-development/SKILL.md`. Bundled communication and Ryoku
skills are under `.agents/skills/`; no copy of the original home directory is
needed to recover the instructions.

## Verify the checkpoint

```bash
git status -sb
git log -5 --oneline
git remote -v
git fetch origin main
git rev-list --left-right --count HEAD...origin/main
```

Expected standalone origin:
`https://github.com/methos28/AI_usage_widget_ryoku_shima.git`, branch `main`.
The runtime includes all approved work through source revision `24b6db3`.
The most recent continuity commit may be newer; use Git rather than a frozen
self-referential hash in this document.

## Current approved behavior

- All three agents, private bundled collectors, local history and API Value.
- Saved Codex session titles, mixed-store deduplication with identity promotion,
  login-bound quotas, future-time filtering and malformed-data recovery.
- Gentle 360/380/180-ms bar/number/fade transitions, correct first values,
  reduced motion, hidden-state stopping and smooth mid-animation retargeting.
- All six agent switch directions are guarded: matching snapshot ownership,
  neutral loading, old read generations and newer queued cache versions.
- The optional Ryoku feature branch is `ai-usage-dashboard`, published as
  `f039733d7`. It was synced with upstream `3f4f6ee` on November 18. Fetch fresh
  refs before future synchronization; that is not a claim about today's tip.
- PRs #779 and #881 are merged. No new motion PR was created by the agent.
  The local title/body drafts describe the motion and switch-handoff delta.

The motion preview was approved and published. Earlier instructions to wait
before committing that preview are superseded. Do not interpret completed
publication approval as permission for unrelated future work.

## Work on another PC

Follow `docs/continuing-development.md` for dependencies, optional language
servers, test commands, Ryoku mirror discovery and installation boundaries.
Full GUI checks require compatible Ryoku imports and Quickshell. Source work
and non-GUI checks can run in a POSIX development environment without changing
that PC's desktop. Never import the original PC's boot or account configuration.

## Where we left off

The requested code, audits, review fix, motion tuning and performance work are
complete. The original host now has Ryoku 1.1.0; its user-installed widget still
matches all 32 approved source files. No reinstall or desktop change is part
of this checkpoint export. Machine-specific follow-up is described separately
in `memory/local-machine.md`.

There is no active preview hold or unimplemented item from the November 17
bug audit. Ask for the user's next project goal instead of redoing old phases.
When making new changes, preserve the source-first workflow and append evidence
to the project log.
