# AI usage clean rebuild: pending fresh clone

Current owner instruction (2026-11-10 12:18 IST) supersedes restoring the old review branch.
The user will delete ~/ryoku-arch and their fork/branches, then clone a fresh
unstable-dev. Wait for their completion message. Only then recreate ai-usage
from the fresh base and commit the minimal reviewed port. No old cherry-picks,
merge history or broad restore. No remote push in the backup phase.

Verified independent backup: /home/methos/Documents/ai-usage-rebuild-backup/20261110-121656
Archive: /home/methos/Documents/ai-usage-rebuild-backup/20261110-121656.tar.gz
SHA-256: b53479f4afb52ead78d2901dcc61e78c65bbef286b63f4f4cca2044cf334ca63

Read REBUILD.md first. It preserves 28 widget runtime files and exactly three
shared QML changes as wiring.patch. No Rashin collector or service files.
Eleven tests plus widget CI are kept separate. The primary standalone working
project is also preserved, including uncommitted/untracked work, with generated
bytecode and Git history omitted. Both expected source variants are recorded.
All saved hashes/modes/symlinks and real archive extraction were verified.
The live widget remains untouched. The complete runtime was preserved, not
reduced to 5,000 lines. Review any later scope reduction explicitly.

## Rebuild completed

The user authorized clone, commit and push as ai-usage-dashboard. Completed at
5c9d9f11cfcbf56de27d2f5433e37b1e95e40667 in /home/methos/ryoku-arch. Read
ai-usage-dashboard-submission.md for current scope and PR restrictions. The
wait phase and earlier ai-usage branch name above are superseded.
