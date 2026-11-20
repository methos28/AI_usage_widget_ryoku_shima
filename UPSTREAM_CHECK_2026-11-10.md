# unstable-dev compatibility check, 2026-11-10

Checked at approximately 12:03 IST against freshly fetched GitHub branches.

## Result

The three new upstream commits do not affect the AI usage widget, its bundled
collectors, discovery/settings/loading integration, packaging or focused CI.
No replication or live deployment is needed for the user's conditional request.
The local ai-usage branch already matches its published remote exactly and is
clean. It intentionally remains three upstream commits behind; this check did
not merge the unrelated repository tooling and version changes.

## Revisions and changes

- ai-usage: b650d0c474553931ef551332051e46fe3d651d62.
- Upstream unstable-dev and the fork's remote unstable-dev:
  cd1a06478d5b7c8f952180c89c1f42576fad41da.
- Common ancestor: 0749ec35005cdae3b5c925eb91c32a6904a998d5.

| Commit | Change | Widget impact |
| --- | --- | --- |
| 3db7be318 | Add edition, compositor, channel and version fields to the bug-report form | None |
| f11c4a6ac | Delete Project Auto Add and Project Triage workflows and remove their advisory entries from bin/ryoku-ci-gate | None; the Shima widget workflow and its required tests are unchanged |
| cd1a06478 | Bump VERSION from 1.10.2 to 1.10.3 | Release metadata only |

Five incoming paths have zero overlap with the 44 feature paths. A read-only
git merge-tree simulation completed without conflicts, and comparing its tree
against HEAD across all feature paths found no changes. No merge was applied.

Fetching reported that origin/unstable-dev had been force-updated remotely
from the earlier feature-bearing f26ede8ad to the official upstream head. This
was a pre-existing remote change observed by fetch, not a reset performed here.
Local unstable-dev remains preserved at f26ede8ad, and ai-usage retains every
published feature commit. Do not reset ai-usage to unstable-dev to synchronize it.

## Verification

Re-ran the complete .github/workflows/ai-usage-widget.yml command set on
ai-usage. All 172 unittest cases, the Codex shell fixtures and the isolated
cache contract pass. Counts: OpenCode 12, Codex 48, Claude usage 11, quota 25,
sessions 20, spending 19, pricing 16, widget 16 and custom installation 5.
Logs: /tmp/ai-usage-upstream-check-20261110/.

The live user-owned widget equals the primary module source byte-for-byte,
excluding generated Python __pycache__ artifacts. All three private usage
caches parse as JSON objects with mode 0600. No real-data collection, login,
service changes, package upgrades or shell restart were needed. No new visual
session test was performed because runtime files did not change.

Only Git remote-tracking references and audit records were updated. No source
files, local branch tips, commits, pushes or installed desktop files changed.
