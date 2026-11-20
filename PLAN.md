# Current project plan

Updated for the portable standalone checkpoint, 2026-11-20.
The previous long plan is preserved in
`docs/history/PLAN-through-2026-11-18.md`; PROJECT_LOG.md remains append-only.

## Completed

- Self-contained OpenCode/Codex/Claude collection, quota handling, request
  deduplication, historical pricing and native session lifecycle work.
- All November 17 audit fixes and PR #881 identity-promotion correction.
- User-approved motion preview and all-agent switch isolation, published to
  the Ryoku feature branch as f039733d7 after syncing upstream 3f4f6ee.
- Hardware performance measurements and safe user-owned live installation.
- Read-only verification on November 20 that the user widget survived the
  original host's Ryoku 1.1.0 update and still matches approved source.

## Portable checkpoint contents

This checkpoint packages current standalone code, tests, project records,
relevant skills, portable agent instructions and project-specific memory for
the standalone main branch. Credentials, runtime stores, raw evidence and
machine-wide config stay local. The user explicitly authorized this export's
commit and push; that is not permission for unrelated future publication.

## Next session

1. Clone/update standalone main and follow HANDOFF-CODEX.md.
2. Check the current PC's environment and run available tests before editing.
3. Ask for the next requested change; no audit fix or preview approval is pending.

Historical performance numbers apply to the recorded machine/workload, not every
PC. Live post-upgrade/system checks remain host-specific; do not copy the old
machine's bootloader preferences to another host.

## Checkpoint validation

All 235 cases passed in the working tree and a fresh staged export with a clean HOME. The source-only run without Quickshell passed 216 checks and skipped 19 GUI/host-specific checks without failures. All four skills validate. Staged contents contain no detected credential patterns or forbidden runtime files. Current validation is on the original host's installed Ryoku 1.1.0 imports; another PC still needs its own environment checks.

## Export complete

Continuity payload 71383fa is verified on standalone main, with all four prior application commits included. The completion record is committed as a documentation follow-up. Nothing remains to publish from this checkpoint; continue from the user's next goal after verifying the new checkout.
