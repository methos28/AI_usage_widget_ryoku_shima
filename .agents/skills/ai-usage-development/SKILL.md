---
name: ai-usage-development
description: Develop, test, review, or port this repository's AI Usage Shima widget and its optional Ryoku mirror. Use the project handoff and native fixtures; this skill does not authorize deployment or publication by itself.
---

# AI Usage development

Use HANDOFF-CODEX.md and memory/current-state.md from the repository root for
current state. AGENTS.md contains the project policies. Historical vault notes
and reports are evidence; completed waits and preview holds are not active.

The canonical app is ai-usage/. Its bin/ helpers own collection and persistent
pricing; UsageModel.qml owns cache-read state; components/ owns presentation.
The optional mirror is the widget path below a user-selected Ryoku checkout.
Locate that checkout instead of assuming the original PC's home directory.

Preserve native request IDs, cross-store multiplicity and learned ID promotion.
Reject future usage from current accounting. Keep quota answers tied to login
context. Preserve frozen historical prices and explicit unknown coverage.
Agent selection must publish only matching snapshots and reject old generations
or superseded reads. First values and agent changes must not interpolate from
another agent's data. Normal updates respect theme and reduced-motion policy.

Edit primary source first. Add a reproducing fixture for a confirmed defect;
use temporary HOME/cache/state and fake accounts, never a paid prompt or live
ledger as a test. Run test/run.sh and the current host's available QML checks.
Without Quickshell, native GUI cases are skipped and remain unverified.
See docs/continuing-development.md for dependencies and full validation.

Mirror relevant runtime intentionally, preserving documented port metadata and
CLI/source labels. Keep standalone tests and AI context out of the minimal
Ryoku port. Before live desktop work, use the bundled ryoku skill and the
current host's vault/ownership commands. Deploy via the repository installer
to the supported user-owned widget only after checks and the user's authorized
scope are clear. Back up known-good code; preserve newer runtime data.

Record work and evidence in PROJECT_LOG.md. Refresh the handoff/current memory
at checkpoints. Existing user authorization governs commits/pushes; do not add
approval gates to actions they already requested. Do not publish or message
external services outside that scope.
