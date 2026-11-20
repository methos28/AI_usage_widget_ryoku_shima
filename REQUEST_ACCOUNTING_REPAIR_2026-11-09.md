# Codex request accounting repair

Implemented and deployed on 2026-11-09. No commit or push was made.

## Fixed behavior

The existing bundled Codex collector now reads native request records by session and response identity. It reconciles cumulative mirrors in either order, including delayed mirrors and records split across files. It includes request-only compaction calls, respects inherited subagent boundaries, and uses continuation-aware cumulative fallback for older logs. Archived copies and temporarily truncated logs retain already recorded requests without adding them again.

Codex and OpenCode now use matching token components: O excludes reasoning, R contains reasoning, and cache reads/writes are separate. Pricing includes reasoning once within total output and uses the complete request input when choosing a context tier. The actual nested thread-settings event is parsed. Unknown prices and unsupported tiers remain unpriced rather than being assigned a fabricated cost.

Activity state is schema 5. The display cache keeps its existing schema 3 contract and adds accounting version 2. Both activity and history use the same request ledger. Reconstructed dates replace inflated old buckets; unavailable historical dates are preserved. Spending migration replaces reconstructed old cumulative identities, retains unavailable historical records, and keeps every saved daily price snapshot. Before migration, a private monthly `spending-YYYY-MM.before-request-accounting.json` backup is saved automatically.

No new login, key, dependency, collector script, billing permission, or manual cache deletion is needed. Quota percentages remain provider-reported and are independent of token totals.

## Exact validation

The frozen audit snapshot contains 653 unique requests. Two consecutive isolated refreshes produced the audited Sol values exactly:

| Category | Reconstructed value |
| --- | ---: |
| Input excluding cache reads | 1,753,628 |
| Cache reads | 133,322,880 |
| Output excluding reasoning | 248,400 |
| Reasoning | 270,089 |
| Output including reasoning | 518,489 |
| Total including cache reads | 135,594,997 |

Using the same saved prices and coverage, the covered Codex spending subtotal changes from $52.926383 to $33.327711. November 6 remains unpriced. These are Standard API-equivalent estimates, not verified account charges. The live amount continues to increase as further work is recorded.

A later live snapshot contained 718 requests. Every cached request matched independently parsed raw input, cached input, output and reasoning components. Daily totals matched the request sum, and independent ledger pricing matched the cache amount of $36.917120. The subsequent visible refresh showed about $37.10 as work continued. Saved daily price dictionaries were unchanged across the live migration. Usage/activity/ledger files remained mode 0600.

## Tests and delivery

- Primary: 6 OpenCode, 43 Codex, and 10 widget tests, totaling 59, plus cache contracts.
- Fork: 42 Codex, 10 widget, and 9 shared compatibility/delivery tests, totaling 61, plus the Codex shell fixture and cache contract.
- QML lint, QML bindings, delivery, window-manager isolation and whitespace checks pass. Existing raw-lint warnings remain visible; the fatal-QML check passes.
- Eleven new collector tests cover native mirror orders, copied/split/delayed records, request-only compaction, legacy continuations, inherited snapshots, incremental format upgrades, frozen-price migration, native tier settings, inherited subagent prefixes and malformed native counts. Three representative tests fail against the old backed-up collector.
- Primary source, fork source, live bundled collector, protected service collector and earlier home-bin collector all have identical SHA-256 `56009a8696fb6d8c25e5fcff668bcf711fdaf7826a28f0462ba73e23c3b5721e`.

The user-owned legacy collector copies were updated because they share the spending ledger. Existing service/drop-in settings were preserved. A restricted refresh could not initialize app-server; the approved normal refresh succeeded with the existing ChatGPT login and published rpc/Plus quota data. The shell reload succeeded and the actual desktop card was inspected. The recent runtime log contains no AI usage component errors. Unrelated pre-existing shell warnings remain outside this repair.

Live backup: `~/.local/share/ryoku/ai-usage-backup/request-repair-live-20261109-144515/`. It contains previous collector copies, caches, ledger, a price snapshot comparison and the inspected preview. Earlier source backups are in `request-repair-20261109-135529/` beside it. The automatic ledger migration backup is retained separately in the spending state directory.

All edits remain uncommitted in the primary project and the user's existing `ai-usage` review branch. No branch switch, remote push, upstream write, package upgrade, account change or new credential was made.

## CodexBar expenditure comparison

Reviewed CodexBar commit `7447bc77c2497323d9c41e40164ce705533493c8`.

| CodexBar source | Meaning | Relation to this widget |
| --- | --- | --- |
| Local Codex usage / Estimated spend | Token usage priced at model API rates | Same concept as Est. Spending; it is API-equivalent value, not an extra subscription charge |
| OpenAI organization cost provider | Reported organization costs from `/v1/organization/costs`, with separate completion usage | A distinct billing integration using an Admin API key; not added here |
| Provider-reported plan metering | An additional provider-supplied value where available | Separate from locally priced token activity |

The current dashboard explicitly labels the first category Estimated spend and separately displays Plan metered where present: [summary view](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/Sources/CodexBar/SpendDashboard/SpendDashboardSummary.swift#L16). The API integration is documented in [OpenAI provider](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/openai.md).

CodexBar combines models.dev metadata, bundled rates, overrides, context/tier rules and known dated repricing. Its current-catalog repricing paths differ from this widget's intentionally frozen daily snapshots. This repair preserves the user's daily-price policy and Est. Spending label. See [model pricing](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/model-pricing.md).

CodexBar's Swift tests were not run because no Swift compiler is installed. The spending distinction is based on reviewed source, not account billing probes.
