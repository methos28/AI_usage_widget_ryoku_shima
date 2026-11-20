# AI Usage: actual unstable branch and delivery audit

Recorded: 2026-11-09 03:02 IST. Fresh Git refs and live GitHub API were checked.

## Decision

The complete AI Usage review implementation is compatible with the current
unstable Shima source and passes staged delivery tests. It is **not present in
the official unstable-dev update branch**, so a normal official update cannot
currently install the module or its improved collectors for other users.

This machine's working widget is a manual custom installation. Seeing it in
Shima Settings / Island / Desktop page / Your modules does not demonstrate that
a fresh profile receives it from the official update.

## Exact branch inventory

| Source | Fetched head | Improved collector/widget | Automatic Your modules discovery |
| --- | --- | --- | --- |
| Ryoku-dev/ryoku:unstable-dev | 0749ec350 | Absent; existing collector is older | Absent; bundled widget directory does not exist |
| methos28/ryoku:unstable-dev | f26ede8ad | Present | Missing the later built-in catalog fix |
| methos28/ryoku:ai-usage | 9e4268ff2 | Present | Present and validated on a clean profile |

The audit covers 31 module, host, collector, scanner and service files. Their
hashes and branch-by-branch presence/content comparisons are in
[the placement inventory](DELIVERY_INVENTORY_2026-11-09.tsv).

The live GitHub API reports PR 757 closed without merging: merged=false,
merged_at=null, closed_at=2026-11-08T12:36:17Z. The PR head remains 9e4268ff2.
The web tool's rendered PR page returned an older Open snapshot; the current
API and freshly fetched source refs are the evidence used here.
[Live PR API](https://api.github.com/repos/Ryoku-dev/ryoku/pulls/757),
[PR 757](https://github.com/Ryoku-dev/ryoku/pull/757).

## Why the older collector ran

The machine records /home/methos/ryoku-arch as its update repository. Its origin
is the official Ryoku-dev/ryoku repository, its tracked channel is unstable-dev,
and its deployed commit is 0749ec350. It does not track the user's ai-usage
review branch or the user's fork's unstable-dev branch.

The source-channel updater runs ryoku/shell/deploy.sh from its tracked checkout.
That script installs its collectors to ~/.local/bin and creates
ryoku-dev-bin.conf to select its local guard. The pre-fix collector saved in
the incident backup is byte-identical to the collector in official unstable-dev.
It lacks the project's enhanced history/spending behavior and uses the older
RPC implementation. Its live initialization failed and rollout fallback supplied
the expired quota. Missing _spending caused the dash by design.

This establishes that the normal source deployment can replace the manually
installed collector with the official branch's older version. The exact previous
invocation was not captured in a deployment log, so it is not independently
claimed as a witnessed command execution.

Correction to the earlier cleanup risk discussion: reconcileDevResidue skips
source-checkout machines. Removal of home-bin package shadows applies to
packaged installations or transitions back to them. The immediate source-update
hazard is deploy.sh copying the tracked branch's collector over that path.

Earlier checks covered the review candidate and its components. They did not
establish that the reviewed feature had entered the actual tracked update
branch. That distinction should have been checked before the earlier broad
answer about the deployment problem.

## Complete candidate delivery path

The existing complete review branch already has all four discovery changes:

1. The AI Usage manifest sets iris.builtin=true.
2. CustomWidgets exposes a combined irisModules catalog for bundled and user
   modules, retaining user-copy precedence and preventing duplicates.
3. IrisOptions uses that catalog for Your modules.
4. IrisCustomModule uses the same catalog to resolve the compact QML entry.

Packaged delivery copies the full Quickshell tree into
/usr/share/ryoku/config/quickshell; normal materialization exposes it under
~/.config/quickshell. The ryoku-rashin payload installs the matching collector
guard and scripts under /usr/bin, plus the service and timer under
/usr/lib/systemd/user. The existing service manifest and doctor own timer
activation. Users who intentionally removed the optional ryoku-rashin package
retain that choice; the package is the collector provider.

Source-channel delivery copies the Quickshell tree to ~/.config/quickshell,
installs all four guard/collector scripts together in ~/.local/bin, copies the
service/timer, creates the dev override and enables the timer. The guard chooses
collectors beside itself, so source and package paths remain distinct without
introducing standalone home paths into packaged code.

Once these complete changes exist in the tracked branch **and the unstable
testing gate permits that commit**, the normal update path can deliver the
module without a separate custom-widget installation. It will be offered in
Your modules; existing activation choices remain preserved.

## New permanent regression and results

Added test_update_payload_delivers_module_and_matching_guard_collectors to the
existing tests/custom-widget-install.py on the user's existing ai-usage branch.
The existing workflow already runs and watches that file. No CI policy or
production source was changed.

The new fixture executes the actual relevant Quickshell copy instructions and
source collector-install/dev-unit instructions in temporary directories. It
executes the actual ryoku-rashin package install script, using placeholders only
for unrelated compiled applications. It checks every module file, all four
collector/guard scripts and both unit files against source, exercises the real
staged scanner/settings/loader expressions with no installed user widget, then
runs the staged guard and verifies enriched Codex history, limits and spending
fields from isolated rollout data. Both package and source scenarios pass.

This is a staged delivery test, not a full system install or a rebuild of all
desktop applications. It does not execute the full privileged deploy script or
start a second desktop session.

| Check | Result |
| --- | --- |
| Fork Codex regressions | PASS: 31 tests |
| Fork widget regressions and component compilation | PASS: seven tests |
| Shared installation/discovery/reader tests | PASS: nine tests, including both staged delivery modes |
| Standalone gate | PASS: 44 tests plus cache contract |
| OpenCode/Codex shell fixtures and fork cache contract | PASS |
| Fatal-QML lint and 22-file binding gate | PASS |
| Delivery, WM isolation and whitespace gates | PASS |
| Existing Go updater channel/gating tests | PASS |
| Existing Go host service-manifest tests | PASS |
| Existing Go doctor AI usage/Rashin/dev-residue tests | PASS |

Negative control: extracted the actual f26ede8ad fork unstable-dev files into a
temporary tree and ran the current fresh-profile discovery regression against
them. It fails at the visibility assertion (false !== true). This confirms the
older fork branch is missing the fix, rather than relying only on a branch name
or commit message. Official unstable lacks the module files altogether.

Existing Qt advisory warnings and Python fixture cleanup ResourceWarnings are
retained in the raw logs; no gate was weakened to suppress them. Rapid-click
race coverage remains inconclusive as documented in the prior runtime report.

## Current placement and remaining delivery requirement

Current official checkout: bundled AI Usage absent.
Current installed shipped Quickshell tree: bundled AI Usage absent.
Current packaged config tree: bundled AI Usage absent.
Current ~/.config/inir/widgets/ai-usage: manual module present.
Current protected libexec collector and zz-ai-usage.conf: present and working.

The live protected collector matches the review collector and publishes rpc/Plus
data with the history/spending fields. No live files, desktop settings, update
tracking or service configuration were changed during this audit.

The necessary next delivery step is to land the complete ai-usage feature in
the intended update branch and pass its testing gate. The current official
branch cannot deliver unmerged code. The user's fork unstable-dev would also
need the later discovery commit before it satisfies the fresh-profile contract.

The existing manual module and standalone service override intentionally retain
precedence. A later migration of this machine to the fully managed built-in
should be reviewed after the upstream feature is delivered; removing the
workaround now would restore the missing/older official implementation.

The new review-branch test and local records remain uncommitted. No branch
switch, commit, push, PR action, system update, package build/deployment or
upstream write was performed. Raw logs are in /tmp/ai-usage-20261109-checks/.
