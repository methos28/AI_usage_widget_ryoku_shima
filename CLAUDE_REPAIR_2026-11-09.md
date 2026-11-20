# Claude Desktop collector repair — 2026-11-09

The standalone/live widget now displays observed Claude account limits, local
Sonnet 5.5 API value and native session lifecycle. Three user-requested agents
worked on isolated helpers; the parent reviewed their implementations, requested
ordering repairs, integrated the collector/UI, ran the gates and deployed.
Everything remains uncommitted. The downstream Ryoku fork is unchanged.

## Account limits

The installed Desktop application writes successful account usage responses to
`~/.config/Claude/plan-usage-history.json`. Version 2 maps five-hour utilization
to `fh`, seven-day utilization to `sd`, and records epoch milliseconds plus an
organization identity. The helper checks the Desktop account against local
profile metadata and selects only matching organization samples.

The first observed values were 18% and 50%. A later Desktop capture reported
39% and 52% while local tokens stayed unchanged. These are account-wide limits,
including use outside this machine. They are not reconstructed from token sums.
Desktop history does not store reset times, so none are invented.

Capture age is visible. Values older than 20 minutes move out of current quota
fields and appear only as labelled last-known data. Missing or mismatched data
is unavailable. Zero is shown only for an actual numeric zero measurement.
An optional existing scoped OAuth token supports read-only quota fallback.
Requests and failures are throttled for five minutes and retained results are
bound to a token fingerprint. Redirects cannot forward credentials. No login,
credential refresh, cookie decryption or model invocation was added.

## API value and CodexBar comparison

Reviewed CodexBar at commit
`7447bc77c2497323d9c41e40164ce705533493c8`, including
`CostUsageScanner+Claude.swift`, `CostUsagePricing.swift` and `docs/claude.md`.
Its local cost scanner prices native uncached input, output, cache reads and
cache creation. One-hour creation costs twice base input; remaining five-minute
creation uses its own rate. Native output already includes thinking. Account
quotas and optional organization billing are separate data sources.

The widget follows those token classes and response identity rules. It accepts
`requestId`/`request_id`, falls back to session/message identity, merges repeated
cumulative snapshots, and excludes explicit null-stop initialization placeholders.
Thinking is separated for display but added to output only once for pricing.
Unlike a default five-minute assumption, missing cache TTL splits stay unpriced.

Verified exact `claude-sonnet-5-5` prices on 2026-11-09 against
[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing):

| Class | USD per million tokens |
|---|---:|
| Uncached input | 2.00 |
| Output including thinking | 10.00 |
| Cache reads | 0.10 |
| Five-minute cache writes | 2.50 |
| One-hour cache writes | 4.00 |

Claude uses separate private `claude-spending-YYYY-MM.json` ledgers under
`~/.local/state/ai-usage`. Daily prices freeze on first capture. Older days with
no saved rates stay unpriced. Unknown models/tiers/speed/TTL splits do not become
zero-cost events. Later dates mark the verified snapshot stale. Extra server-tool
fees mark the token subtotal partial. There is no runtime Claude price download.
The UI says **Est. Spending**, shows coverage, and explains that the value is
local API-equivalent usage rather than a subscription charge or wallet balance.

Independent reconstruction of the existing real logs:

| Counter | Tokens |
|---|---:|
| Distinct responses | 11 |
| Uncached input | 22 |
| Output including thinking | 6,114 |
| Thinking subset | 1,663 |
| Cache reads | 562,928 |
| Cache writes, all one-hour | 138,395 |
| Cache-inclusive total | 707,459 |

Exact API value is **$0.6710568**, published as `$0.671057` and displayed as
`$0.67`. Independent final-response parsing matches the collector's daily/model
totals. Repeated collection leaves token counts and value unchanged. These
numbers cover local transcripts, not the friend's other account activity.

## Sessions

The helper reads `~/.claude/sessions/*.json`, verifies PID/start ticks and
available machine/namespace/boot evidence, and reconciles native status clocks
with transcript lifecycle. A session can appear before its first usage record.
Newer completion/interruption overrides stale working status; a newer prompt can
override stale idle only with a verified live process. Merely keeping Desktop
open or writing a recent file does not establish running. Inaccessible processes
produce unknown status, not a fabricated live session.

The parent identified stale status ordering during review. Four additional
fixtures reproduced seven failures before the agent repaired the helper.
The parent also corrected null TTL fields for zero-cache-write responses.
The visible Claude page refreshes only Claude every five seconds, without
starting Codex RPC or OpenCode. The actual completed Desktop process is verified
alive and correctly remains idle. A new real active turn is still pending;
the optional three-minute live watch observed no new prompt.

## Validation and delivery

All 117 primary tests pass: 6 OpenCode, 43 Codex, 7 Claude integration, 16 Claude
quota, 20 Claude lifecycle, 13 Claude spending and 12 widget tests. Cache
contracts, fatal QML lint, QML binding checks and whitespace checks pass.
Existing nonfatal QML/resource warnings remain. The actual desktop card was
inspected with real quotas and `$0.67`; no AI-widget runtime errors appeared.

Backup, numeric evidence, gate logs and idle preview:
`~/.local/share/ryoku/ai-usage-backup/claude-complete-20261109-154352`.
Source and live code hashes match. The private cache/ledger use mode `0600`.
No authentication settings, Codex collector, Codex ledger, service settings,
upstream files, fork files, commits or remote branches were changed.
