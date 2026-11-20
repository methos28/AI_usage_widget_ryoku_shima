# Codex usage mismatch: fix and compatibility results

Recorded: 2026-11-09 02:36 IST. All changes remain uncommitted.

## Result

The live Shima card now receives authenticated Codex limits with future reset
times, token history, sessions and estimated spending. The final inspected
card showed 16% used in the five-hour window and 29% weekly, with a valid
five-hour countdown. These are later observations during ongoing usage, not
values expected to remain equal to the original 02:14 screenshot.

The installed collector had reverted to a different version matching the
packaged collector. Its RPC initialization failed repeatedly, so the card
displayed historical rollout limits: 8% used with an expired reset. The project
collector already contains the compatible RPC implementation; restoring it
made a real authenticated refresh succeed. The process that replaced the
home-local collector has not been established.

Two delivery conflicts were also confirmed:

- Ryoku doctor removes commands under `~/.local/bin` when a Ryoku package
  supplies a command with the same name. That makes a standalone collector
  named `~/.local/bin/codex-usage` vulnerable to future cleanup.
- A pre-existing `ryoku-dev-bin.conf` service drop-in sorts after
  `override.conf` and replaces its commands with the local Ryoku launcher.
  Changing only `override.conf` therefore did not select the protected path.

## Delivered changes

The standalone installer now puts Codex at
`~/.local/libexec/ai-usage/codex-usage` and installs the project service
configuration as `zz-ai-usage.conf`. It sorts after the observed dev override.
OpenCode retains its distinct `opencode-usage-v2` name. Existing home-bin
copies and unrelated service overrides are preserved.

The live protected collector and later project drop-in match the tested
repository source. The original `override.conf` was restored byte-for-byte
from the backup after the new drop-in was installed. The dev override remains
untouched. A real service start reported exit status 0 for the protected Codex
collector and OpenCode v2; the five-minute timer is active. The published Codex
cache is `rpc`/Plus with valid future windows and mode 0600.

Repository edits cover `install.sh`, the service configuration, the existing
installer regression, README instructions and project records. No collector
algorithm or QML change was needed. No packaged file, shared Shima component,
Ryoku branch, upstream repository, commit or remote was changed.

## Automated verification

| Check | Result | Scope |
| --- | --- | --- |
| Standalone `./test/run.sh` | PASS: 44 tests | Six OpenCode, 32 Codex and six widget tests, plus lint and isolated cache contract |
| Fork regression suites | PASS: 46 tests | 31 Codex, seven widget and eight shared-loader/installation compatibility tests |
| Collector shell fixtures | PASS | Eight OpenCode assertions and six Codex assertions |
| Both isolated cache contracts | PASS | Required fields and history shape without caller account data |
| Qt6 fatal-QML lint | PASS | Standalone and fork widget components |
| QML binding gate | PASS: 40 files | Both widget trees and four shared host files |
| Delivery and WM isolation | PASS | Existing fork gates, without changes to their policy |
| Wayland component compilation | PASS: seven widget tests | Actual components against the fork imports, including the widget manager |
| Shell syntax and whitespace | PASS | Installer/test entry point and final working-tree diff |

The final standalone gate was rerun after the service filename change. The
fork source was unchanged throughout, so its earlier passing results still
apply. Raw Qt lint has existing advisory warnings; the fatal-load gate and real
component compilation passed.

The strengthened installer regression seeds both a legacy home-bin collector
and the competing dev-service override. It verifies the protected executable,
effective drop-in ordering, preservation of the dev file and legacy copy, and
successful collection after simulated removal of the old shadow. The revised
destination check failed against the original installer before the fix. The
existing private-stdio regression also rejected the faulty deployed collector.
Fixtures isolate state and disable live price fetching. No real doctor repair
or package upgrade was run as a test.

## Current Shima runtime checks

The tested desktop uses Hyprland v0.57.1, Quickshell 0.3.2-1.1, Qt 6.12 and
ryoku-shell 1.10.1.r5848.g4542802-1, with Shima selected. The observed output is
1920x1080 at scale 1.

Ten direct host dependencies match the installed official unstable baseline:
IrisStyle, IrisText, IrisSurface, MaterialSymbol, Directories,
IslandDesktopPage, IrisCustomModule, CustomWidgets, WidgetManagerPanel and
IrisOptions. The fork's existing loader changes were tested in its checkout;
they were not overlaid onto the running desktop. The full live widget still
matches the standalone source.

Inspected the repaired Codex layout, active session, reset countdowns and
estimated spending. Live checks also observed the supported-agent menu,
OpenCode switching, return to Codex, the Trend menu and the Today chart. The
last inspected card was restored to Codex and Last 7 days. Zero module-related
load errors, ReferenceError/TypeError diagnostics or binding loops appeared
in the inspected shell log tail.

Longer scripted input sequences sometimes closed the panel. Consequently,
all-period live click coverage and rapid-input/animation races remain
inconclusive. Automated tests execute the actual QML calendar/period bindings
across both supported time-zone fixtures; they do not prove those input races.
The final period was restored through the daemon's settings.patch writer,
confirmed in its store, and checked on screen. The temporary pointer helper
was stopped and the island closed after inspection.

This is not exhaustive platform certification: multi-monitor/scaling changes,
niri, real API-key/Bedrock accounts, real Claude data, a full system update and
new remote CI were not exercised. Account-mode and credential regressions use
isolated fake servers. The exact earlier replacement mechanism remains unknown.

## Records and recovery

Backup: `~/.local/share/ryoku/ai-usage-backup/unstable-fix-20261109-022043/`.
It contains the prior collector, both pre-fix Codex caches and the original
service override. The corrected local screenshot is stored there as
`final-codex-card.png`; it is not a published README asset.

Raw command outputs and temporary input probes are under
`/tmp/ai-usage-20261109-checks/`. Durable incident notes are in the Rashin vault
memory and journal. The fork checkout remains clean on `ai-usage` at
`9e4268ff2`; the official `~/ryoku-arch` checkout remains clean on
`unstable-dev` at `0749ec350`. No branch switch, commit or push was performed.

To undo this delivery, restore the saved collector and original service
configuration, disable the new `zz-ai-usage.conf` drop-in, and reload the user
service manager. That restores the faulty state too; the backup is for recovery,
not the recommended running configuration.
