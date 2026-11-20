# Current AI Usage checkpoint

As of 2026-11-20, standalone `main` is the canonical source and includes the
approved runtime through `24b6db3`, plus this portable continuity package.
Use `git log` and a fresh remote fetch to identify the exact current commit.

## Repositories and paths

- Standalone: methos28/AI_usage_widget_ryoku_shima, main.
- Optional integration: methos28/ryoku, ai-usage-dashboard, f039733d7 at the last
  verified publication. Widget destination below a chosen Ryoku checkout:
  ryoku/shell/quickshell/inir/defaults/widgets/ai-usage/.
- Local source: ai-usage/. User install on a Ryoku host:
  ~/.config/inir/widgets/ai-usage/. Private runtime caches: ~/.cache/ai-usage/.
- Original upstream: Ryoku-dev/ryoku. PR #779 and #881 are merged. The motion
  delta was published on the fork; the agent did not open a new motion PR.

## Approved features and invariants

All three agents are selectable. Collectors are bundled; no shared Rashin
service is required by this widget. Saved Codex titles come from the native
session index. Old titles fall back to the user prompt or directory.

Usage merging preserves distinct native IDs and promotes learned IDs on
previously anonymous rows. Future requests wait for their timestamp. Account
quota caches track observable login context without opening credential-file
contents. Unknown quota data remains unavailable/last known.

API Value is local estimated work, with frozen historical daily rates and
explicit incomplete coverage. Native running state requires lifecycle/process
evidence; stale caches do not prove execution.

Motion uses 360-ms bars, 380-ms numbers and 180-ms fades with gentle easing.
First/context values snap; normal updates animate; hidden/reduced motion stops.
Switches mask old agent fields until matching data lands. Immutable read
snapshots, generation checks and latest-pending preference prevent flashes.

## Validation and remaining work

The portable checkpoint passed all 235 cases in both the working tree and a
fresh staged export with a clean HOME. Without Quickshell, 216 checks pass and
19 GUI/host-specific checks skip. All four bundled skills validate. The approved
app itself previously passed 233 cases per source copy. PERFORMANCE_2026-11-18.md records measured
hardware results and limits, not universal performance guarantees.

The code/audit/review/motion work is complete and approved. There is no active
preview publication hold. No outstanding code repair from the recorded audit
is awaiting implementation. Ask the user for their next goal.

The original host now reports Ryoku 1.1.0. Its 32-file custom widget was checked
read-only and exactly matches this source. See local-machine.md for the limits
of that observation; do not perform unrelated system actions during a clone.
