# AI usage widget — plan

Status: phase 1 in progress. The prepared batch received local commit approval
on 2026-11-07 via "push to local"; remote push remains unapproved.
Owner decisions override this plan; record any change in `PROJECT_LOG.md`.

## Current work — Codex correctness (requested 2026-11-07)

- [x] Verify official quota-window field definitions and plan documentation.
- [x] Fix moved, truncated/replayed and copied rollout double counting.
- [x] Render reported quota windows and reset times, including a reported 30d window.
- [x] Prevent historical paid windows from appearing after a plan change.
- [x] Add 15 regression tests and run all delivery gates.
- [x] Install the tested primary collector and widget files to the named live paths.
- [ ] Reload the live shell; this session cannot connect to its socket (EPERM).
- [x] Observe the next real collector refresh migrating activity state to schema 4.
- [ ] Confirm the resulting live layout; existing visual sign-off remains pending.

The primary Codex collector now lives at `collector/codex-usage`. The live
collector matches it. The downstream Ryoku collector has not received these
new fixes yet; the later deliberate port remains open. Free-plan 30d windows
were observed in this account's rollouts, but official documentation does not
establish a universal Free reset schedule. Window length and reset time follow
the account response rather than a plan-name rule.

## Phase 1 — Stabilise the live widget

- [x] Trend periods use fixed calendar slots ending today.
- [x] All-time is a fixed 45-day window, zero-filled.
- [x] Bar widths scale with the Shima page width; 7-day fills the card.
- [x] Heatmap covers 63 days ending today in a full 9 × 7 grid; zero days are dim
      (replaces the earlier 60-day cap, per the user's screenshot feedback).
- [x] Codex `_hours` uses local clock hours in milliseconds; widget normalises old
      second-based caches.
- [x] Codex Spending always renders, `$0.00` when the cache has no costs.
- [x] Compact the Now/Sessions row back to the Claude reference height.
- [x] Period label is a real target in both collapsed and expanded states.
- [x] Refresh lock clears when the collector exits.
- [ ] User visual sign-off on the live dashboard.
- [ ] Final pass on card height against the Claude reference.

## Phase 2 — Tests and records

- [ ] Fixture: 7/30/45-day trend slot counts with a 2-day cache.
- [ ] Fixture: heatmap exactly 63 dated cells in nine full columns, zero days dim, no future dates.
- [ ] Fixture: hours keys in seconds and milliseconds both normalise.
- [ ] Fixture: plan agent with no cost shows `$0.00` and the compact row height.
- [ ] Fixture: period label click target reaches both states.
- [ ] Update `PROJECT_LOG.md` with every result.

## Phase 3 — Commit approval

- [x] Prepare Claude hold-out: only OpenCode/Codex in the primary dropdown and settings.
- [x] User says "push to local"; commit the widget changes with one logical
      commit per concern.
- [ ] User says "push to remote"; push `main` only after the local commit is
      approved.
- [ ] Never force-push.

## Phase 4 — Ryoku branch

- [ ] Port the accepted widget fixes to
      `/home/methos/Projects/ryoku-unstable` branch `ai-usage-builtin`.
- [ ] Keep the branch's Claude hold-out and its newer collector work intact.
- [ ] Run its gates: QML lint, binding gate, `tests/opencode-usage.sh`,
      `tests/codex-usage.sh`, `tests/ai-usage-cache.py`.
- [ ] Record the port in `PROJECT_LOG.md`.

## Phase 5 — Claude follow-up

- [ ] Enrich `claude-usage` with sessions, days, hours and periods, additive to
      the existing cache keys.
- [ ] Fixtures for the Claude store and cache contract.
- [ ] Return Claude to the standalone and shipped widget menus and settings options.
- [ ] Test with real Claude data before enabling.

## Phase 6 — Pull request

- [ ] Fork `Ryoku-dev/ryoku` only when the user says so.
- [ ] Push the branch, open a draft PR against `unstable-dev`.
- [ ] Body: what ships, what is held back (Claude), CI coverage, follow-ups.
- [ ] Respond to review without changing scope silently.

## Phase 7 — Optimisation (on hold)

- [ ] Only after the user asks: remove duplication, split large QML components,
      optimise collector scans, harden latent double-count paths.

## Click-input backlog

- [ ] Reproduce H1: menu veil closes instead of the trigger toggling.
- [ ] Reproduce H3: chip disabled during availability probe.
- [ ] Reproduce H4: press/release dropped during page/scale animation.
- [ ] Reproduce H5: menu or card clipped at narrow island widths.
- [ ] Fix only what reproduces; record evidence first.
