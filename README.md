# AI usage - Shima Island module

A dashboard for your coding agent, built into the Ryoku **Shima** Island
Desktop page. It shows live sessions, tokens for the period you pick, your top
models and an activity heatmap. OpenCode and Codex are selectable
from the chip at the top of the card; each one is read from its own local
cache. Codex quota refresh uses its existing CLI login, and estimated spending
downloads public model prices without sending login credentials.

This repository provides the standalone installation. The built-in Ryoku
integration is proposed in [PR #757](https://github.com/Ryoku-dev/ryoku/pull/757).

Claude is hidden from the dropdown and widget settings until its collector is
validated with real usage data.

**Install time:** about 10 minutes. **Skills needed:** copy and paste.


# Widget Preview

Screenshots include earlier layouts. The current agent menu offers OpenCode
and Codex, and the Codex spending title is **Est. Spending**.

Collapsed Sections : 

<img width="562" height="327" alt="image" src="https://github.com/user-attachments/assets/cc38a1d2-f6d5-4b10-9ff4-e4620c8565d5" />
<img width="564" height="407" alt="image" src="https://github.com/user-attachments/assets/dfc7847d-b8bb-48ef-b83d-96a54705622a" />


Expanded Sections :

<img width="540" height="561" alt="image" src="https://github.com/user-attachments/assets/726ab955-8c0d-4fc4-adcd-d385c4dee80e" />
<img width="579" height="555" alt="image" src="https://github.com/user-attachments/assets/7a313875-43b5-479b-9ed3-58e4ae2db1d6" />
<img width="585" height="545" alt="image" src="https://github.com/user-attachments/assets/cff71940-eee9-427f-b301-e877856a8465" />





---

## If you only read one thing

1. `git clone https://github.com/methos28/AI_usage_widget_ryoku_shima.git`
2. Run `./install.sh` from the clone. It copies the widget, the collector and
   the systemd drop-in, then reloads the shell.
3. **Shima Settings → Island → Desktop page → Your modules** → tick **AI usage**.
4. Optional: **Shima Settings → Island → Pages → Page width** → **520** for
   more room. The default 440 px page fits the card as it is.

Done. The long version, with checks after every step, is next.

---

## Before you start

You need:

- **Ryoku Linux** with the Shima (iris) bar. Hover the clock pill at the top
  centre: it must expand into a panel with page buttons.
- **OpenCode or Codex** installed and used at least once. OpenCode normally
  stores usage at `~/.local/share/opencode/opencode.db`; Codex records local
  session rollouts. Codex plan-limit bars need an existing ChatGPT login.
- **Python 3.10 or newer** (`python3 --version`). The collector uses only the
  standard library, so there is nothing to pip install.
- **`git`** for the clone below. No GitHub account is needed; a ZIP download
  works too.

What is in this repository:

```
ai-usage/              the Shima module (QML + manifest)
collector/             the usage collector that feeds it
README.md              this guide
LICENSE                GPL-3.0
```

---

## Install, step by step

### 1. Clone the repository (1 minute)

```bash
git clone https://github.com/methos28/AI_usage_widget_ryoku_shima.git \
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

The repository collectors provide the dashboard's daily history, per-period
model totals, session activity and recorded costs or estimates. OpenCode uses
`opencode-usage-v2`; Codex uses the existing `codex-usage` script extended here.

History comes from OpenCode's per-message store, so a session that runs across
days is credited to each day it actually ran. Session totals true up the
history when a message row is missing, and the collector never attributes a
session to a database update that was only a migration touch.

```bash
mkdir -p ~/.local/bin
cp ~/Downloads/opencode-ryoku-shima/collector/opencode-usage-v2 ~/.local/bin/
cp ~/Downloads/opencode-ryoku-shima/collector/codex-usage ~/.local/bin/
chmod +x ~/.local/bin/opencode-usage-v2
chmod +x ~/.local/bin/codex-usage
```

Now tell the Ryoku timer to run it. Create this file:

```bash
mkdir -p ~/.config/systemd/user/ryoku-ai-usage.service.d
cat > ~/.config/systemd/user/ryoku-ai-usage.service.d/override.conf <<'EOF'
[Service]
ExecStart=
ExecStart=-/usr/bin/claude-usage
ExecStart=-%h/.local/bin/codex-usage
ExecStart=-%h/.local/bin/opencode-usage-v2
EOF
systemctl --user daemon-reload
systemctl --user start ryoku-ai-usage.service
```

✅ **Check:** the cache for an agent you have used should print `True True`:

```bash
python3 - <<'PY'
import json
from pathlib import Path
for tool in ("opencode", "codex"):
    path = Path.home() / ".cache" / (tool + "-usage.json")
    if path.exists():
        data = json.loads(path.read_text())
        print(tool, "_periods" in data, "_sessions" in data)
PY
```

`False` on the left means the new collector did not run. See Troubleshooting.

> An older collector may omit the history, sessions or estimated-spending
> fields. Install both repository collectors to use the current dashboard.

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

### 6. Make it wide (optional, 1 minute)

The module's card width defaults to 480 px, matched by a 520 px Island page.
The card also fits the default 440 px page untouched: the layout clamps to the
page body, and the activity heatmap needs 123 px at default density. A
wider page gives the top row more room, nothing more.

1. In Shima Settings: **Island → Pages**.
2. Optional: set **Page width** to **520**.

✅ **Check:** at the default width the card still fills the page width; at 520
the top row shows two cards side by side.

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
- **Change the period from the header:** if Trend is collapsed, the first
  click expands it. Click the period label again to open its menu.

---

## What each card shows

Every card is a pane of frosted glass: the wallpaper behind the Island, blurred
and clipped to the card, under a thin tint and hairline. Nothing else on the
page changes material.

| Card | What it tells you |
|---|---|
| **Now / Sessions** | Session titles, recorded tokens and activity, with up to two running sessions. The dot breathes while a session runs. Codex's monthly estimate sits below its sessions. |
| **Limits** | Today's local tokens and server-reported ChatGPT quota windows with reset times. Window lengths follow the response, rather than an assumed plan schedule. API-key request/token limits are not collected. |
| **Spending / Est. Spending** | OpenCode shows recorded monthly local costs. Codex shows a monthly API-equivalent estimate, with a coverage marker and tooltip. An unavailable estimate displays an em dash. |
| **Trend** | Bars for the chosen period, cache reads included. Today and Last 24 hours are hourly; other periods use fixed 7/30/45-day windows. Hover a bar to read it. |
| **Models** | The top three models of the period: cache-inclusive total, share meter, and `I… O… R… CR…` with the cache hit rate. |
| **Activity** | A full 9 × 7 heatmap of the last 63 days, plus the all-time total (cache reads included), active days and the busiest day. The flame is your current streak; hover it. |

---

## The period control

Five options, one per line in the menu:

1. **Today** - the whole day as 24 hourly slots.
2. **Last 24 hours** - rolling 24 clock hours.
3. **Last 7 days**
4. **Last 30 days**
5. **All time** - a fixed 45-day trend window, not lifetime history.

The period drives Now, Trend and Models. Spending always shows this month;
Activity always shows the last 63 days.

---

## Settings

All keys live in `~/.config/ryoku/shell.json` under
`inir.background.widgets.custom.ai-usage`. The defaults work. The period has a
menu in the card; the rest are for edge cases and you rarely touch them.

| Key | Default | What it does |
|---|---|---|
| `tool` | `opencode` | Which agent to read: `opencode` or `codex`. The chip at the top of the card writes this key. |
| `moduleWidth` | `480` | Card width in px, clamped to the page body. |
| `topModels` | `3` | Rows in the Models card. Maximum 3. |
| `period` | `30` | `today`, `24h`, `7`, `30` or `all`. The menu writes it. |

The module also writes `layoutVersion` once, to migrate old installs. Leave it.

The agent chip only offers agents that have a usage cache on this machine
(`~/.cache/<tool>-usage.json`). An agent that was never used here is hidden. If
the selected agent's cache disappears, the card falls back to the first
available agent, OpenCode first.

---

## Where the numbers come from

- `~/.cache/opencode-usage.json` - written by the collector. The module only
  reads it.
- OpenCode's collector reads its local store read-only and publishes usage
  metadata such as token counts, models, timestamps, recorded cost and titles.
- Codex reads local session rollouts for tokens, models and sessions. Its
  authenticated app-server supplies quota windows over private local stdio.
  Codex handles its saved login; the collector does not open the auth file or
  publish the account response.
- Estimated spending downloads the public OpenAI model catalog from
  `https://models.dev/api.json`. This request carries no API key, login token
  or local usage data. Codex's own quota request requires network access.
- Freshness: the cache is rewritten every minute while the page is open and
  every five minutes by the systemd timer.
- Refresh runs the collector directly for OpenCode; the Ryoku service is only a
  fallback. Claude and Codex still use the service so its install guards apply.
- The collector takes a lock, writes atomically and keeps day and hour history
  append-only, so a published total never decreases.

### Codex spending estimates and login support

Codex reads `~/.cache/codex-usage.json`, written by the installed repository
collector. It supplies account quota windows, local token history, model rows
and sessions. A ChatGPT browser or device-code login supports plan quota
windows. API-key and Bedrock accounts do not reuse historical ChatGPT limits;
Platform API request/token limits are not collected. Other credential modes
have not all been verified with real accounts.

**Est. Spending is a Standard API-equivalent token estimate, not a bill,
wallet balance or additional Plus charge.** It does not import billing history
or track top-ups. Session token categories are priced using saved daily model
rates, with duplicate events counted once.

The existing collector keeps private monthly ledgers at
`~/.local/state/ai-usage/spending-YYYY-MM.json` (or under `XDG_STATE_HOME`).
Saved rates for earlier days are retained. Days before the first saved price
snapshot remain unpriced instead of receiving today's rates retroactively.
Unknown model prices or unsupported service tiers are also excluded.

`This month*` and the tooltip identify incomplete or stale coverage. Offline
refreshes can use previously saved prices, marked stale. If no priced usage is
available, the amount displays an em dash. Hover the spending title for details.

### Deferred Claude support

Claude remains hidden from both agent selectors pending collector enrichment
and testing with real usage data. Shared cache-reading support and demo helpers
remain in the source for that follow-up. Creating a Claude cache does not add
Claude to the dropdown.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| No card on the Desktop page | The module is off. Shima Settings → Island → Desktop page → Your modules → tick AI usage. |
| `No opencode usage yet` | Open OpenCode once, then wait a minute. Or run `systemctl --user start ryoku-ai-usage.service`. |
| Models or sessions empty | Check that the selected agent has recorded usage, then verify the repository collector and `_periods` cache field from step 3. |
| Always `no session running` | Same cause: the cache has no `_sessions`. Redo step 3. |
| Numbers frozen | The page is closed, so the minute refresh is idle. Reopen it, or start the service by hand. |
| Card looks clipped | Page too narrow. Shima Settings → Island → Pages → Page width 520 (the default 440 fits; this is for extra room). |
| Period menu does not open | Click the period label at the right of the Trend header. If it stays unresponsive, reload the shell. |
| Codex spending has an asterisk or em dash | Hover the title. Some dates/models may lack saved prices, or the public price refresh may be unavailable. |
| Something broke after an update | `ryoku-shell reload`. If it persists, check the log (below) and restore the last backup. |

Log, always the first place to look:

```bash
tail -50 ~/.local/state/ryoku/surfaces/shell.log
```

---

## Uninstall

1. In Shima Settings, remove it from **Island → Desktop page → Your modules**.
2. Delete the folder: `rm -rf ~/.config/inir/widgets/ai-usage`
3. Optional, remove the repository collectors:
   `rm ~/.local/bin/opencode-usage-v2 ~/.local/bin/codex-usage` and
   `rm ~/.config/systemd/user/ryoku-ai-usage.service.d/override.conf`, then
   `systemctl --user daemon-reload`.
4. `ryoku-shell reload`.

Usage caches and persistent spending ledgers are retained after uninstall.

---

## For developers

**Repository layout**

```
ai-usage/IrisCompact.qml        the page shell, layout and menus
ai-usage/components/            one card or primitive per file
ai-usage/UsageModel.qml         cache reader, ticker, session filter
ai-usage/AiUsageTile.qml        the same numbers as a plain desktop tile
ai-usage/widget.json            manifest; iris.main is what Shima loads
collector/opencode-usage-v2     the collector that writes the cache
collector/codex-usage           Codex quotas and deduplicated rollout token history
systemd/                        the Ryoku timer drop-in
install.sh                      one-command install
test/test_collector.py          collector fixtures
test/test_codex_usage.py        Codex replay, plan-window and reset fixtures
test/test_widget.py             calendar, quota, spending and QML component checks
test/cache_contract.py          isolated cache contract check
test/lint.sh                    QML and Python static checks
```

**Test**

The test suite needs Python 3, Node.js (to execute the widget's JavaScript
parsers), and the QML lint tools supplied by Ryoku.

```bash
./test/run.sh
```

`test_collector.py` builds throwaway sqlite and file stores, runs the collector
against a temp cache and checks the v2 fields, residual true-up, append-only
history and lock. `cache_contract.py` runs the collector and asserts the live
cache contract: shell keys, `_days` order, `_hours` length, `_periods`
completeness and nesting, model rows, `_sessions` newest-first. It builds its
own SQLite fixtures rather than depending on the caller's account.

`test_codex_usage.py` checks archive moves, copied and replayed rollouts,
activity-state migration, plan changes, and server-reported quota windows.
Codex window lengths and reset times come from the account response. A Free
account that reports 43,200 minutes shows `30d`; the widget does not infer a
reset schedule from the plan name. Local token activity does not determine
the account's quota percentages. It also covers daily price snapshots, missing
historical prices, offline fallback, event deduplication, cache permissions,
RPC cleanup/redaction and account-type changes.

The standalone suite contains 44 tests: six OpenCode, 32 Codex and six widget
tests, plus the cache contract. QML compilation checks require Quickshell and
Ryoku imports. The live preview was checked on stable Ryoku; full runtime
validation on an unstable installation remains separate from these source
checks. The host-side built-in discovery changes are in the linked Ryoku PR.

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

**Licence and credit**

GPL-3.0. See `LICENSE`. The widget is built for Ryoku Shima; Shima's iNiR lineage is
by snowarch. No iNiR code is copied into this repository.
