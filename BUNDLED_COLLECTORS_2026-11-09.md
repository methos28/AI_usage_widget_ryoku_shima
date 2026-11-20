# Widget-owned collectors

Implemented and verified live on 2026-11-09. Changes are uncommitted in both
repositories; published fork ai-usage remains at c2dbdc496.

## Result

Both executable collector scripts now ship inside the AI Usage widget:

```
ai-usage/bin/collect-usage
ai-usage/bin/opencode-usage
ai-usage/bin/codex-usage
```

UsageModel resolves the launcher relative to its own QML URL and executes that
path. It no longer invokes the system collector service or searches PATH for
the collector binaries. The explicit RYOKU_AI_USAGE_COLLECTOR override remains
available for OpenCode and must accept --cache.

The widget collects on first load and every minute while visible, including
when it has no cache yet. Availability publishes complete probe batches; saved
agent reconciliation waits for a completed collection. If the legacy Codex
collector holds its lock, the launcher returns a retry status and the model
retries without resetting the saved agent.

Data is isolated under ~/.cache/ai-usage. Older system collectors can continue
writing their shared caches without replacing widget output. The persistent
spending ledger and saved historical prices remain under their existing state
directory. The launcher takes the legacy Codex lock before the private collector
lock so both cache destinations cannot update that ledger concurrently.

## Source and delivery

The scripts inside each repository's widget/bin directory are the canonical
sources. Previous collector source paths are relative symlinks to those files.
Their bodies match the respective repository HEAD byte-for-byte; no token,
quota, authentication or price calculation was changed.

Existing Ryoku package/source install commands dereference the source links
into ordinary executables for other bar widgets. The complete Quickshell copy
also delivers the widget directory with its own executables. The new module
therefore works without the optional ryoku-rashin package or system timer.
Python is already a ryoku-desktop dependency; Bash and flock are runtime
requirements of the launcher.

The standalone installer copies only the complete widget and reloads the shell.
It no longer installs separate global collectors or creates service overrides.
The obsolete repository drop-in was removed. Earlier live helper binaries and
service overrides were preserved for other consumers.

## Verification

- All 48 standalone tests pass: six OpenCode, 32 Codex and ten widget tests.
- All 50 fork tests pass: 31 Codex, ten widget and nine shared compatibility
  tests. Existing collector fixtures and cache contracts also pass.
- Actual bundled scripts run from a copied directory containing spaces and
  shell-special characters. Tests place failing system-collector/service
  commands on PATH and verify those are not called.
- Real isolated OpenCode and Codex stores produce private caches while a stale
  legacy shared cache remains unchanged.
- Lock tests verify that the widget cannot update the shared spending ledger
  while the legacy collector holds its lock.
- The real QML cold-start probe loads the model and availability component,
  executes the actual agent reconciliation code, starts without private caches,
  seeds both tools and temporarily holds the legacy lock. The saved Codex choice
  survives collection and retry. The negative control removes only its readiness
  guard and detects the premature saved-agent change.
- Package/source staging exercises both the installed system guard and the
  widget-owned launcher, preserving shared caches and the same spending summary.
- QML compilation/lint, the 36-file binding gate, shell syntax, delivery,
  WM isolation and whitespace checks pass. Existing fixture ResourceWarnings
  remain visible; no gate was disabled or weakened.

## Live deployment

Backed up and replaced only the user-owned ~/.config/inir/widgets/ai-usage
directory, then reloaded the shell. The deployed directory matches the primary
widget source exactly. Both private caches are mode 0600.

The real Codex collection returned rpc/Plus with future reset times, four days
of history, seven sessions and its spending summary. OpenCode returned
storage+v2 with 50 days and ten sessions. Inspected the actual Codex card with
limits, sessions, estimated spending and Last 7 days. No module-related runtime
errors appeared in the inspected log tail.

The saved widget settings are unchanged, including tool=codex and period=7.
Hashes confirm the existing global collectors and all prior service drop-ins
are unchanged. No package upgrade, official checkout deployment, upstream write,
branch switch, commit or push occurred.

Backup directory:
~/.local/share/ryoku/ai-usage-backup/bundled-collectors-20261109-034353/.
It includes pre-change patches, the earlier widget, settings, global file hashes
and the inspected bundled-live-card.png. A hidden prior live directory is also
retained beside the active widget for rollback; the scanner ignores it.

Restore that saved widget directory and reload the shell to undo the live change.
Private caches and historical spending state can remain in place.

Official delivery still requires these complete feature changes to enter the
tracked upstream branch and pass its release/testing gate. The earlier published
PR description describes the prior system-collector architecture and must be
updated before submitting this new working-tree implementation.
