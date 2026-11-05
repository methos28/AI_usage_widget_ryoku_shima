# AI usage — Shima Island module

A dashboard for your coding agent, built into the Ryoku **Shima** Island
Desktop page. It shows live OpenCode sessions, tokens for the period you pick,
your top models and an activity heatmap. OpenCode data is read from this
machine; no account and no network call. Claude Code and Codex are also
selectable and are read from their own local caches.

**Install time:** about 10 minutes. **Skills needed:** copy and paste.


# Widget Preview
Collapsed Sections : 

<img width="608" height="645" alt="image" src="https://github.com/user-attachments/assets/1ae61688-438d-4215-8cc0-19f1b2544985" />

Expanded Sections :

<img width="578" height="901" alt="image" src="https://github.com/user-attachments/assets/6263e9c7-7b1c-4258-a6be-5c8bfc8ab406" />


---

## If you only read one thing

1. `git clone https://github.com/methos28/opencode_ryoku_shima_module.git`
2. Copy `ai-usage/` into `~/.config/inir/widgets/`.
3. Copy `collector/opencode-usage-v2` into `~/.local/bin/`, make it executable,
   add the systemd drop-in below, start the service.
4. Run `ryoku-shell reload`.
5. **Shima Settings → Island → Desktop page → Your modules** → tick **AI usage**.
6. **Shima Settings → Island → Pages → Page width** → **520**.

Done. The long version, with checks after every step, is next.

---

## Before you start

You need:

- **Ryoku Linux** with the Shima (iris) bar. Hover the clock pill at the top
  centre: it must expand into a panel with page buttons.
- **OpenCode** installed and used at least once, so its database exists at
  `~/.local/share/opencode/opencode.db`.
- **Python 3.10 or newer** (`python3 --version`). The collector uses only the
  standard library, so there is nothing to pip install.
- **`git`** for the clone below. No GitHub account is needed; a ZIP download
  works too.

What is in this repository:

```
ai-usage/              the Shima module (QML + manifest)
collector/             the usage collector that feeds it
README.md              this guide
LICENSE                MIT
```

---

## Install, step by step

### 1. Clone the repository (1 minute)

```bash
git clone https://github.com/methos28/opencode_ryoku_shima_module.git \
  ~/Downloads/opencode-ryoku-shima
```

✅ **Check:** `ls ~/Downloads/opencode-ryoku-shima` shows `ai-usage`,
`collector`, `README.md`, `LICENSE`.

### 2. Copy the widget (1 minute)

The folder **must** be named `ai-usage`; the shell uses that name as the module
id.

```bash
mkdir -p ~/.config/inir/widgets
cp -r ~/Downloads/opencode-ryoku-shima/ai-usage ~/.config/inir/widgets/
```

✅ **Check:** `ls ~/.config/inir/widgets/ai-usage/widget.json` prints the path.

This folder is yours. `ryoku update` does not touch it, so the module survives
updates.

### 3. Copy the collector (2 minutes)

The stock Ryoku collector keeps seven days of OpenCode history. This module's
Trend, Models and Now cards want more: daily history, per-period model totals,
live sessions and recorded cost. That is what `opencode-usage-v2` adds.

History comes from OpenCode's per-message store, so a session that runs across
days is credited to each day it actually ran. Session totals true up the
history when a message row is missing, and the collector never attributes a
session to a database update that was only a migration touch.

```bash
mkdir -p ~/.local/bin
cp ~/Downloads/opencode-ryoku-shima/collector/opencode-usage-v2 ~/.local/bin/
chmod +x ~/.local/bin/opencode-usage-v2
```

Now tell the Ryoku timer to run it. Create this file:

```bash
mkdir -p ~/.config/systemd/user/ryoku-ai-usage.service.d
cat > ~/.config/systemd/user/ryoku-ai-usage.service.d/override.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/usr/bin/claude-usage
ExecStart=-/usr/bin/codex-usage
ExecStart=-%h/.local/bin/opencode-usage-v2
EOF
systemctl --user daemon-reload
systemctl --user start ryoku-ai-usage.service
```

✅ **Check:** this prints `True True`:

```bash
python3 - <<'PY'
import json, os
d = json.load(open(os.path.expanduser("~/.cache/opencode-usage.json")))
print("_periods" in d, "_sessions" in d)
PY
```

`False` on the left means the new collector did not run. See Troubleshooting.

> Skipped this step? The module still loads, but Models, Spending and the
> session list stay empty and the Trend only covers the last seven days.

> The `ryoku-ai-usage.timer` unit ships with the optional `ryoku-rashin`
> package. If `systemctl --user status ryoku-ai-usage.timer` says it does not
> exist, install that package first; the drop-in above has no base unit without
> it.

### 4. Reload the shell (30 seconds)

```bash
ryoku-shell reload
```

✅ **Check:** reload finishes and the log stays quiet:

```bash
grep -i "ai-usage\|IrisCompact" ~/.local/state/ryoku/surfaces/shell.log
```

No output is good.

### 5. Turn the module on (1 minute)

1. Hover the clock pill to open the Island.
2. Click the **gear** at the right end of the page buttons. **Shima Settings**
   opens.
3. In Shima Settings: **Island → Desktop page**.
4. Find **Your modules** and tick **AI usage**.

✅ **Check:** open the Island on its **Desktop** page (the middle page button).
The card is under the date and agenda.

### 6. Make it wide (1 minute)

The module is designed for a 480 px card, which needs a 520 px Island page.

1. In Shima Settings: **Island → Pages**.
2. Set **Page width** to **520**.

✅ **Check:** the card fills the page width and the top row shows two cards
side by side.

### 7. Pick a period (10 seconds)

1. Click the **Trend** row to open it.
2. Click the period text on its right (`Last 30 days`).
3. Pick from the menu.

---

## How to use it

- **Open the module:** hover the clock, click the **Desktop** page button.
- **Open or close a section:** click its row (Trend, Models, Activity). They
  start closed.
- **Change the period:** open Trend, click the period text, pick one.
- **Refresh:** nothing to do. The collector runs again every minute while the
  page is open.
- **Collapsed rows are read-only:** the period text only works when Trend is
  open. Clicking a closed row opens it.

---

## What each card shows

Every card is a pane of frosted glass: the wallpaper behind the Island, blurred
and clipped to the card, under a thin tint and hairline. Nothing else on the
page changes material.

| Card | What it tells you |
|---|---|
| **Now** | The agent, when it last wrote, and up to two running sessions: title, how long it has run, its tokens. The dot is green and breathes while a session runs. |
| **Limits** | Only appears when the cache reports a real provider plan: today's tokens plus the 5h/7d windows with meters. |
| **Spending** | Only appears when the period recorded a cost. Amount, API value, tokens and cache share. |
| **Trend** | Bars for the chosen period, cache reads included. Today and Last 24 hours are hourly; the rest are daily (weekly above 100 buckets). Hover a bar to read it. |
| **Models** | The top three models of the period: cache-inclusive total, share meter, and `I… O… R… CR…` with the cache hit rate. |
| **Activity** | A heatmap of every recorded day, plus the all-time total (cache reads included), active days and the busiest day. The flame is your current streak; hover it. |

---

## The period control

Five options, one per line in the menu:

1. **Today** — the whole day as 24 hourly slots.
2. **Last 24 hours** — rolling 24 clock hours.
3. **Last 7 days**
4. **Last 30 days**
5. **All time**

The period drives Now, Spending, Trend and Models. Activity always shows the
whole history.

---

## Settings

All keys live in `~/.config/ryoku/shell.json` under
`inir.background.widgets.custom.ai-usage`. The defaults work. The period has a
menu in the card; the rest are for edge cases and you rarely touch them.

| Key | Default | What it does |
|---|---|---|
| `tool` | `opencode` | Which agent to read: `opencode`, `claude` or `codex`. |
| `moduleWidth` | `480` | Card width in px, clamped to the page body. |
| `topModels` | `3` | Rows in the Models card. Maximum 3. |
| `period` | `30` | `today`, `24h`, `7`, `30` or `all`. The menu writes it. |

The module also writes `layoutVersion` once, to migrate old installs. Leave it.

---

## Where the numbers come from

- `~/.cache/opencode-usage.json` — written by the collector. The module only
  reads it.
- The collector reads OpenCode's own local database
  (`~/.local/share/opencode/opencode.db`) read-only. It never reads prompts or
  replies, only token counts, models, times, cost and session titles.
- No network. No sign-in. Nothing leaves the machine.
- Freshness: the cache is rewritten every minute while the page is open and
  every five minutes by the systemd timer.

### Other agents

`tool: claude` reads `~/.cache/claude-usage.json`. `tool: codex` reads
`~/.cache/codex-usage.json`. Both are written by the stock Ryoku collectors.

Those collectors are lighter than the OpenCode one: they write the 5h/7d quota,
today's tokens and a seven-day `_recent_days` list, but no long history, model
rows or session list. So on Claude and Codex the Now, Models and Spending cards
stay empty, and Trend and Activity cover seven days. The quota windows and
today's total are accurate.

`claude-usage` asks Anthropic's usage endpoint with the OAuth login Claude Code
already stored; it sends no prompts. It cannot write a cache until Claude Code
has been used and `~/.claude/.credentials.json` exists. Codex likewise needs
`~/.codex` from a Codex run.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| No card on the Desktop page | The module is off. Shima Settings → Island → Desktop page → Your modules → tick AI usage. |
| `No opencode usage yet` | Open OpenCode once, then wait a minute. Or run `systemctl --user start ryoku-ai-usage.service`. |
| Models / Spending empty | The old collector is running. Redo step 3 and check `_periods` prints `True`. |
| Always `no session running` | Same cause: the cache has no `_sessions`. Redo step 3. |
| Numbers frozen | The page is closed, so the minute refresh is idle. Reopen it, or start the service by hand. |
| Card looks clipped | Page too narrow. Shima Settings → Island → Pages → Page width 520. |
| Period menu does not open | Trend is closed. Click the row first; the period text works only when open. |
| Something broke after an update | `ryoku-shell reload`. If it persists, check the log (below) and restore the last backup. |

Log, always the first place to look:

```bash
tail -50 ~/.local/state/ryoku/surfaces/shell.log
```

---

## Uninstall

1. In Shima Settings, remove it from **Island → Desktop page → Your modules**.
2. Delete the folder: `rm -rf ~/.config/inir/widgets/ai-usage`
3. Optional, remove the collector:
   `rm ~/.local/bin/opencode-usage-v2` and
   `rm -r ~/.config/systemd/user/ryoku-ai-usage.service.d`, then
   `systemctl --user daemon-reload`.
4. `ryoku-shell reload`.

Your usage cache is untouched. Delete `~/.cache/opencode-usage.json` if you
want it gone too.

---

## For developers

**Repository layout**

```
ai-usage/IrisCompact.qml       the Island card grid (the whole UI)
ai-usage/UsageModel.qml        cache reader, ticker, session filter
ai-usage/AiUsageTile.qml       the same numbers as a plain desktop tile
ai-usage/widget.json           manifest; iris.main is what Shima loads
ai-usage/test/cache_contract.py  end-to-end cache check
collector/opencode-usage-v2    the collector that writes the cache
```

**Test**

```bash
python3 ~/.config/inir/widgets/ai-usage/test/cache_contract.py
```

It runs the collector and asserts the contract: shell keys, `_days` order,
`_hours` length, `_periods` completeness and nesting, model rows ranked by cache-inclusive
totals, `_sessions` newest-first with a boolean `running`.

**Rules**

- Never edit shipped QML under `/usr/share/ryoku` or `~/.config/quickshell`.
  This module is user-owned; keep it that way.
- Style with Shima tokens only: `IrisStyle`, `IrisText`, `IrisSurface`,
  `IrisChip`, `MaterialSymbol`. No hard-coded colours.
- Reload after every edit: `ryoku-shell reload`. Edits are live through the
  `widget-loads` symlink, but Qt needs the reload to recompile.
- Do not hand-edit `~/.config/ryoku/shell.json` while the shell runs; a reload
  can write its in-memory copy back over your change.
- Do not pass a generation argument to `scripts/scan-widgets.sh`; it prunes the
  live staging directory.

**Licence**

MIT. See `LICENSE`.
