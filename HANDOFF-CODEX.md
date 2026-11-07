# Handoff prompt for Codex

Copy everything below the line into Codex, run in
`/home/methos/Documents/opencode_widget_ryoku_shima`.

---

You are continuing an existing project, not starting fresh. Work only in
`/home/methos/Documents/opencode_widget_ryoku_shima` unless a record names
another path.

Before doing anything, read these files completely, in this order:

1. `AGENTS.md` — project-only rules. They override habits from other projects.
2. `PROJECT_LOG.md` — full history: what changed, what broke, diagnoses,
   requirement changes, current commit and live state.
3. `PLAN.md` — current phase and open work.

Then confirm the current state yourself, do not trust memory:

```bash
git status -sb
git log --oneline -5
diff -rq ai-usage ~/.config/inir/widgets/ai-usage
python3 - <<'EOF'
import json, os, datetime
for t in ("opencode","codex","claude"):
    p=f"/home/methos/.cache/{t}-usage.json"
    if os.path.exists(p):
        d=json.load(open(p)); st=os.stat(p)
        print(t, datetime.datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M"),
              d.get("_source"), "days", len(d.get("_days", [])),
              "sessions", len(d.get("_sessions", [])))
EOF
```

HARD RULES:

- Do not commit locally. Do not push anywhere. The user must explicitly say
  "push to local" or "push to remote"; they mean commit-only and push-only
  respectively.
- Do not optimise, refactor, or clean up beyond the requested fix.
- Record every change, requirement change, and diagnosis in `PROJECT_LOG.md` as
  you go. Append; never rewrite history.
- Edit the repository copy first, run the gates, then copy to
  `~/.config/inir/widgets/ai-usage` and reload `ryoku-shell`. Never leave the
  live widget ahead of the repository.
- Claude is deliberately absent from the shipped widget menu until its collector
  is enriched. Do not "restore" it.

Gates before any live copy:

```bash
cd /home/methos/Documents/opencode_widget_ryoku_shima
./test/run.sh
cd /home/methos/Projects/ryoku-unstable
RYOKU_QML_IMPORTS="$PWD/ryoku/shell/quickshell" \
  bin/ryoku-dev-lint-qml /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage
bin/ryoku-dev-verify-qml-bindings --quiet \
  /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage/*.qml \
  /home/methos/Documents/opencode_widget_ryoku_shima/ai-usage/components/*.qml
bash tests/codex-usage.sh
python3 tests/ai-usage-cache.py
```

Current state at handoff (verify, do not assume):

- Widget repo `main` is `bf0cfca`. Working tree has uncommitted changes in
  `ai-usage/IrisCompact.qml`, `ai-usage/UsageModel.qml`,
  `ai-usage/components/AiUsageTrendCard.qml`,
  `ai-usage/components/AiUsageSpendBody.qml`, plus project docs and
  `opencode.json`. The live widget matches the working tree.
- Ryoku checkout branch `ai-usage-builtin` is `6cff48603` with an uncommitted
  change to `ryoku/rashin/usage/codex-usage` (milliseconds hours plus migration
  of old second-based rows).
- Codex cache is `_source: rpc`, plan `plus`, two recorded days, three sessions.
  OpenCode cache is `storage+v2` with 48 days. Claude is a demo/stale cache and
  is not installed.
- Recent accepted behaviour: fixed calendar slots for trends (7/30, All-time
  fixed at 45 days), bars fill card width, 13-week heatmap with dim zero days,
  Codex Spending shows `$0.00`, running state from turn lifecycle, local-hour
  milliseconds for Codex.

Open work, in order:

1. Get the user's visual sign-off on the live dashboard (Codex and OpenCode
   cards, trends, heatmap, spend, row height).
2. Add the missing fixtures listed in `PLAN.md` phase 2, one at a time, and
   record results.
3. Only after approval, prepare commits and wait for the phrase "push to local".
4. Port accepted fixes into the Ryoku branch and run its gates.
5. Claude enrichment is a separate follow-up; do not start it unless asked.

Click-input findings still need a live reproduction before code changes: read the
click backlog in `PLAN.md` and do not rewrite hit-testing on a hunch.

When you finish reading, reply with: current state, any discrepancy between the
records and reality, and the single next action you propose. Do not make changes
before that reply.
