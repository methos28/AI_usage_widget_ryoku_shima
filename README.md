# AI usage - Shima Island module

A dashboard for your coding agent, built into the Ryoku **Shima** Island
Desktop page. It shows live sessions, tokens for the period you pick, your top
models and an activity heatmap. OpenCode, Codex and Claude are selectable
from the chip at the top of the card; each one is read from its own local
cache. Codex quota refresh uses its existing CLI login, and estimated spending
downloads public model prices without sending login credentials.

This repository provides the standalone installation. The built-in Ryoku
integration is proposed in [PR #757](https://github.com/Ryoku-dev/ryoku/pull/757).

Claude's standalone preview reads native Claude Code Desktop/CLI history,
account limits and local API-equivalent spending. The downstream Ryoku fork
still holds Claude out pending live lifecycle acceptance.

**Install time:** about 10 minutes. **Skills needed:** copy and paste.


# Widget Preview

Screenshots include earlier layouts. The standalone agent menu offers OpenCode,
Codex and Claude. All agents use the **API Value** label.

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
2. Run `./install.sh` from the clone. It copies the widget and its bundled
   collectors, then reloads the shell. No systemd drop-in is required.
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
- **Bash and `flock`** for the bundled launcher (`command -v bash flock`).
- **`git`** for the clone below. No GitHub account is needed; a ZIP download
  works too.

What is in this repository:

```
ai-usage/              the self-contained Shima module (QML, manifest and bin/)
collector/             compatibility links to the bundled collector sources
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

### 3. Check the bundled collectors (30 seconds)

Both executable collectors ship inside the widget folder:

```text
ai-usage/bin/collect-usage     launcher for both supported tools
ai-usage/bin/opencode-usage    OpenCode history and recorded costs
ai-usage/bin/codex-usage       Codex history, plan limits and spending estimates
```

The widget resolves these paths relative to its own QML, including custom
folders with spaces. It collects whenever the page opens and every 15 seconds
while the dashboard or tile is visible. Its singleton worker stops polling and
retrying when no card is visible.
The launcher checks for each CLI or its local data before collecting it.
The widget does not require the optional `ryoku-rashin` package or its timer.

To run a collection manually:

```bash
~/.config/inir/widgets/ai-usage/bin/collect-usage
```

The widget owns `~/.cache/ai-usage/`. Older system collectors still write their
separate shared caches, so they cannot overwrite this module's data.

Check the private cache for an agent you have used:

```bash
python3 - <<'PY'
import json
from pathlib import Path
for tool in ("opencode", "codex"):
    path = Path.home() / ".cache" / "ai-usage" / (tool + "-usage.json")
    if path.exists():
        data = json.loads(path.read_text())
        print(tool, "_periods" in data, "_sessions" in data)
PY
```

Each used agent should print `True True` after collection. Existing service
customizations from older installations are left untouched for other shell
panels; this widget no longer uses them.

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
- **Refresh:** all agents collect every 15 seconds while a card is visible.
  Opening it requests an immediate refresh. Hidden cards do not poll.
- **Change the period from the header:** if Trend is collapsed, the first
  click expands it. Click the period label again to open its menu.

---

## What each card shows

Every card is a pane of frosted glass: the wallpaper behind the Island, blurred
and clipped to the card, under a thin tint and hairline. Nothing else on the
page changes material.

| Card | What it tells you |
|---|---|
| **Now / Sessions** | Session titles, recorded tokens and activity, with up to two running sessions. The dot breathes while a session runs. Codex and Claude show their monthly estimate below sessions. |
| **Limits** | Today's local tokens and observed account quotas with local reset dates/times and timezone. Claude captures show their age; missing reset times are explicitly unavailable. API-key request/token limits are not collected. |
| **API Value** | OpenCode shows recorded monthly local costs. Codex and Claude show monthly API-equivalent estimates, with coverage markers and tooltips. An unavailable estimate displays an em dash. |
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
| `tool` | `opencode` | Which agent to read: `opencode`, `codex` or `claude` (preview). The chip writes this key. |
| `moduleWidth` | `480` | Card width in px, clamped to the page body. |
| `topModels` | `3` | Rows in the Models card. Maximum 3. |
| `period` | `30` | `today`, `24h`, `7`, `30` or `all`. The menu writes it. |

The module also writes `layoutVersion` once, to migrate old installs. Leave it.

The agent chip only offers agents that have a usage cache on this machine
(`~/.cache/ai-usage/<tool>-usage.json`). An agent that was never used here is hidden. If
the selected agent's cache disappears, the card falls back to the first
available agent, OpenCode first.

---

## Where the numbers come from

- `~/.cache/ai-usage/opencode-usage.json` - written by the bundled collector. The module only
  reads it.
- OpenCode's collector reads its local store read-only and publishes usage
  metadata such as token counts, models, timestamps, recorded cost and titles.
- Codex reads local session rollouts for tokens, models and sessions. Its
  authenticated app-server supplies quota windows over private local stdio.
  Codex handles its saved login; the collector does not open the auth file or
  publish the account response.
  Session names use Codex's saved `session_index.jsonl` titles, including later
  renames. Missing names fall back to the first prompt or working directory.
- Estimated spending downloads the public OpenAI model catalog from
  `https://models.dev/api.json`. This request carries no API key, login token
  or local usage data. Codex's own quota request requires network access.
- Claude reads native local Code history, session registry and observed account
  limits into `~/.cache/ai-usage/claude-usage.json`; its exact pricing snapshot
  is described below.
- Freshness: one widget-owned worker collects all agents every 15 seconds
  while the dashboard or tile is visible. Hidden cards do not poll.
  Opening the page requests an immediate collection; overlapping requests share
  the active run. OAuth quota probes retain their separate cooldown.
- Refresh invokes the bundled launcher by its own path for all supported
  agents. `RYOKU_AI_USAGE_COLLECTOR` can override the OpenCode executable; that
  executable must accept `--cache <path>`. Bundled collectors default to private
  widget caches and use their own locks; Rashin executables are not required.
- Collectors take locks and publish atomically. Codex retains token history;
  Claude token history follows available local transcripts. Both estimate
  ledgers retain previously collected request values.

### Token accounting and automatic history repair

Codex counts native requests once across copied and continued logs, including
compaction calls. Older logs use a continuation-aware cumulative fallback.
For all agents, `O` excludes reasoning, `R` shows reasoning, and cache reads
and writes have separate counts. Tool results sent to the model remain input.
Plan-limit percentages come from the provider, independently of local totals.

The first refresh repairs affected usage and spending records automatically.
It preserves saved daily price snapshots and retains a private pre-migration
ledger backup. No new login, API key, or manual cache deletion is required.
Unknown model prices and unsupported processing tiers remain unpriced.

### Codex spending estimates and login support

The module reads `~/.cache/ai-usage/codex-usage.json`, written by its bundled
Codex collector. It supplies account quota windows, local token history, model rows
and sessions. A ChatGPT browser or device-code login supports plan quota
windows. API-key and Bedrock accounts do not reuse historical ChatGPT limits;
Platform API request/token limits are not collected. Other credential modes
have not all been verified with real accounts.

**API Value is an API-equivalent token estimate, not a bill,
wallet balance or additional Plus charge.** It does not import billing history
or track top-ups. Session token categories are priced using saved daily model
rates, with duplicate events counted once. Published Fast/Priority, Flex, Batch
and Ultrafast rates and per-request context tiers are supported where available.

The existing collector keeps private monthly ledgers at
`~/.local/state/ai-usage/spending-YYYY-MM.json` (or under `XDG_STATE_HOME`).
Saved rates for earlier days are retained. Days before the first saved price
snapshot remain unpriced instead of receiving today's rates retroactively.
Unknown model prices or unsupported service tiers are also excluded.

`This month*` and the tooltip identify incomplete or stale coverage. Offline
refreshes can use previously saved prices, marked stale. If no priced usage is
available, the amount displays an em dash. Hover the spending title for details.

### Claude Desktop / CLI

The bundled `bin/claude-usage` reads `CLAUDE_CONFIG_DIR/projects/**/*.jsonl`
(default `~/.claude/projects`) into the private Claude widget cache. Desktop
Code sessions and CLI sessions using that store share the same collector.
Cloud-only Desktop sessions, ordinary chat and other devices are outside the
local token history. Responses are deduplicated by message/request identity;
thinking is included once in output pricing. Cache reads and cache writes stay
separate from uncached input. Explicit incomplete response placeholders are
excluded and mark the estimate partial.

Claude Desktop's native `~/.config/Claude/plan-usage-history.json` stores actual
5-hour/7-day account percentages. The collector checks matching account and
organization metadata before displaying them. These account limits include
shared-account use outside this machine; local tokens and spending do not.
Captures older than 20 minutes, or whose recorded reset has passed, are labelled
last-known. Missing data is unavailable, never zero. Desktop's compact history
does not contain reset times, but its complete cached account-usage response
does. The collector reads only the bound usage endpoint's hashed Chromium cache
entries, validates keys/checksums/HTTP dates, and extracts the real five-hour and
weekly deadlines. Reset dates/times appear beneath both bars, as for Codex,
in the machine's local timezone (for example `10 Nov, 12:19 AM IST`).
Passed deadlines are not rolled into invented new windows. A missing deadline
shows `reset time unavailable`. Current Zstandard-compressed Desktop responses
use Python 3.14's standard decompressor; unsupported cache formats fail safely
back to observed percentages without guessed reset times.
Existing readable Claude Code subscription OAuth credentials can supply live
quotas and reset times without Desktop. On Linux these are the CLI's saved
`.credentials.json` under `~/.claude` or `CLAUDE_CONFIG_DIR`. API-key/cloud-provider
logins do not supply these subscription quota windows. Requests and failures are
throttled for five minutes. The collector does not
decrypt Desktop cookies, sign in, refresh credentials or launch Claude.

Running sessions require a verified native PID/start time plus native status or
an unfinished turn. New completion/idle events end running state even if the
app stays open. All agents share the 15-second cadence while a card is visible.
Claude account measurements still depend on a fresh Desktop capture or saved
CLI subscription credentials. An inaccessible process produces unknown activity
rather than a fabricated live session.

Claude **API Value** uses a separate private
`~/.local/state/ai-usage/claude-spending-YYYY-MM.json` ledger and frozen daily
prices. The shared widget-owned price catalog covers current and legacy Claude
models, including Sonnet, Haiku, Opus, Fable and Mythos. Published snapshot IDs
and provider prefixes resolve explicitly. Haiku 5.5's higher tier applies per
request above 100,000 prompt tokens, including cache reads and writes. Opus
Fast and Batch use their published rates; thinking counts as output once.
Native TTL splits distinguish five-minute and one-hour cache writes.

Both Codex and Claude refresh public price metadata automatically from the
provider pricing docs and the models.dev catalog. The bundle includes offline
rates and retains a private last-good catalog. Unknown new model IDs trigger
a throttled refresh. No extra login, API key or package is required. Catalogs
refresh daily; failures retry after 15 minutes while saved rates remain usable.
All price requests contain public URLs only, without prompts, usage or credentials.

Today's saved snapshots gain missing models and service tiers without changing
known verified rates. A successful refresh can replace today's stale fallback
rates. Earlier daily snapshots stay frozen; days without a price snapshot
remain unpriced. Unpublished models, unsupported tiers, missing token metadata
and additional server-tool fees are disclosed through partial coverage. This
is local API value, not a subscription charge.

This follows [CodexBar's Claude local-cost strategy](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/claude.md):
deduplicate native responses, price input/output/cache classes independently,
and keep account quotas separate. The widget preserves its existing policy of
not repricing earlier days with current rates.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| No card on the Desktop page | The module is off. Shima Settings → Island → Desktop page → Your modules → tick AI usage. |
| `No opencode usage yet` | Use OpenCode once, then refresh the widget or run `~/.config/inir/widgets/ai-usage/bin/collect-usage`. |
| Models or sessions empty | Check that the selected agent has recorded usage, then verify the repository collector and `_periods` cache field from step 3. |
| Always `no session running` | Verify the selected agent is executing a turn. For Claude, native idle/completion ends activity; inaccessible PID metadata shows `session status unavailable`. |
| Numbers frozen | Reopen the page to resume collection, or run the bundled launcher by hand. Check its output for errors. |
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
3. `ryoku-shell reload`.

Private usage caches and persistent spending ledgers are retained after uninstall.
Older installations may have separate global collector copies or service
overrides. Those are not created by the current installer and are left alone;
review their other consumers before removing them.

---

## For developers

**Repository layout**

```
ai-usage/IrisCompact.qml        the page shell, layout and menus
ai-usage/components/            one card or primitive per file
ai-usage/UsageModel.qml         cache reader, ticker, session filter
ai-usage/AiUsageTile.qml        the same numbers as a plain desktop tile
ai-usage/widget.json            manifest; iris.main is what Shima loads
ai-usage/bin/                  canonical collector scripts and local launcher
collector/                     compatibility symlinks to ai-usage/bin/
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

The standalone suite contains 126 tests: six OpenCode, 43 Codex, eight Claude
integration, 24 Claude quota, 20 Claude lifecycle, 13 Claude spending and 12 widget
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

### Claude Desktop preview

Claude reads local desktop transcript history without a CLI. Real
tokens, account limits, Sonnet 5.5 API value and idle state are verified. Native
active lifecycle fixtures pass; one fresh user-run Desktop turn remains the
final live check. The shipped fork remains held out until acceptance. No
authentication settings are changed. See the Claude data-source section above.
