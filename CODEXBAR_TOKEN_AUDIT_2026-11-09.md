# CodexBar comparison and local token collector audit

Date: 2026-11-09. This is an audit, not a deployed fix.

## Verdict

The local Codex collector is not correct for the currently recorded history. It overcounts inherited cumulative usage at four continuation-file boundaries, misses a request-only compaction, and suppresses the reasoning breakdown. The output comparison with OpenCode also mixes two different definitions of output.

The pricing multiplication is correct for the records supplied to it. Those records are wrong, so estimated spending is wrong too. No source code, live collector, cache, spending ledger, setting, or remote branch was modified by this audit. This report and append-only project/vault notes are the durable changes.

## Scope and reproducibility

- CodexBar was cloned read-only into `/tmp/codexbar-audit-20261109` at commit `7447bc77c2497323d9c41e40164ce705533493c8`.
- The primary widget and live widget were compared with `diff -rq`; they match. The primary and fork working trees already contain the recorded, uncommitted bundled-collector migration. Those edits were preserved.
- Audited the private widget cache with `updated_at: 13:24:17`, and each rollout only through the byte offset recorded in the corresponding activity snapshot. Eleven physical files represent seven session IDs. The two widget cache files stayed unchanged during the audit reads.
- There are 659 cumulative token events, 652 positive cumulative deltas, and 653 unique native request records. Every cumulative total satisfies `input_tokens + output_tokens == total_tokens`. No negative counters, counter decreases, invalid cache subsets, or repeated response IDs were found within this snapshot.
- Temporary read-only reconstruction: `/tmp/codexbar-audit-20261109/audit_local.py`; numeric evidence: `local-audit.json` beside it. No prompts, response text, authentication files, credentials, RPC, or billing endpoints were needed. The temporary audit code is not a new product collector.

Cache SHA-256 values are retained in `local-audit.json`. Native request records were deduplicated by their response identity, then assigned the model from the surrounding turn context. The model grouping contains 198 Sol requests at high effort and 380 at xhigh; the widget merges those efforts into one model row.

## Exact comparison for the saved cache cutoff

The DeepSeek column is `deepseek/deepseek-v4.1-flash (commandcode)` from OpenCode. It includes the existing collector's session-aggregate residual adjustment. These are the user's recorded workloads, not a controlled model benchmark.

| Token category | Sol: current collector | Sol: unique native requests | DeepSeek: OpenCode collector |
| --- | ---: | ---: | ---: |
| Input excluding cache reads | 2,761,528 | 1,753,628 | 4,048,762 |
| Cache reads | 191,386,752 | 133,322,880 | 228,237,952 |
| Output including reasoning | 780,579 | 518,489 | 918,318 |
| Reasoning within output | Shown as 0 | 270,089 | 593,042 |
| Output excluding reasoning | Not shown separately | 248,400 | 325,276 |
| Total including cache reads | 194,928,859 | 135,594,997 | 233,205,032 |

The visible `O` comparison was 780,579 against 325,276. The first number includes reasoning and continuation overcount; the second excludes reasoning. After normalization, Sol has 248,400 non-reasoning output tokens against DeepSeek's 325,276. Including reasoning, the comparable counts are 518,489 and 918,318.

The widget's `I` also means input excluding cache reads. The raw API input total for Sol is 135,076,508, of which 133,322,880 are cache reads. Neither the reported 2.8M nor the corrected 1.75M represents all prompt processing. Input volume alone does not predict output volume.

OpenAI documents reasoning as a subset of billed output: [Reasoning models](https://developers.openai.com/api/docs/guides/reasoning). Non-reasoning output should not be equated exactly with words shown in chat; output can also contain tool calls and structural tokens: [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting).

## Confirmed local defects

### 1. Continuation files restart the collector baseline at zero

Affected source: `ai-usage/bin/codex-usage`, `scan_activity()` around lines 650–710 and `history_records()` around lines 810–916.

Each physical file starts with zero `last_total`, `last_cached`, and `last_output`. The next event is treated as new usage even when the file's `session_meta.history_base` declares earlier history. Event hashing uses session ID, timestamp, and cumulative usage. It prevents exact replays but cannot remove an inherited baseline combined with a genuinely new request at a new timestamp.

Four live continuation pages reproduce this. For example, a continuation opens with a cumulative total of 18,234,947 and `last_token_usage.total_tokens` of 312,020. The collector adds 18,234,947 as new activity. The inherited 17,922,927 must not be added again.

The current Sol inclusive total exceeds the unique-request total by 59,333,862 tokens. Its output total is overstated by 262,090 tokens. This is an observed bug in current data, not only a hypothetical archive-copy risk.

### 2. A request-only compaction is missing

Affected source: the same two readers inspect `token_count`, not native `token_usage_record` usage.

One native request has 448,026 input tokens, 447,744 cached input tokens, 5,327 output tokens, and 453,353 total tokens. Its response ID matches the following `compacted.payload.compaction_response_id`. No cumulative token event accounts for this request. Summing only `last_token_usage` would miss it too.

This omission partly offsets the larger overcount. It must be restored separately; subtracting inherited baselines alone is insufficient.

### 3. Reasoning is discarded as a breakdown

Affected source: `history_records()` around lines 897–916 sets `reasoning: 0` and copies all output into `output`. OpenCode's message rows have separate `output` and `reasoning` fields. The same `O`/`R` labels therefore have different meanings across agents.

Correct total-output accounting must retain reasoning once. A consistent display can show either total output with an explicit reasoning subset, or non-reasoning output plus a separate reasoning category. It must not add a subset twice.

### Additional limitations found

The Codex reader checks for `thread_settings_applied` as a top-level event. The actual native shape is `event_msg` with `payload.type == thread_settings_applied`. All 106 inspected settings events report the default tier, so no Fast-mode pricing error was measured here. This remains a real parsing gap for other tiers. The history display also hardcodes cache-write counts to zero; inspected requests have zero cache writes, so that does not change this snapshot's totals.

The daily/hourly cache merge retains the maximum old value, and the spending ledger retains previously observed events. Both will preserve old inflated data after a parser-only fix. A repair needs a coordinated migration; a normal refresh is insufficient.

## Spending impact

Using the existing saved daily prices, exactly the same cache cutoff, and the same coverage:

| Local date | Current calculation | Unique-request reconstruction |
| --- | ---: | ---: |
| 2026-11-07 | $26.5507934 | $21.6299082 |
| 2026-11-08 | $4.1424250 | $4.1424250 |
| 2026-11-09 | $22.2331642 | $7.5553778 |
| Covered subtotal | **$52.926383** | **$33.327711** |

The measured excess is $19.598672. Both amounts exclude November 6 because there is no saved price snapshot for that day. This is a partial Standard API-equivalent token estimate across the recorded Codex models, not a Plus charge, an invoice, or a remaining balance. Background collection continued to update the shared ledger after this cutoff; later ledger totals were not substituted into this comparison.

The retained Sol price snapshots match the fetched [official model card](https://developers.openai.com/api/docs/models/gpt-6.1-sol): per million tokens, $2 input, $0.10 cache reads, $2.50 cache writes, and $10 output. Above 272,000 input tokens per request, the saved tier uses $4/$0.20/$5/$15 respectively. The estimator applies those saved rates correctly to its supplied counters. A false inherited baseline can also select the long-context tier incorrectly, so the cost impact is not merely the duplicated token count times one flat rate.

## What CodexBar does

The relevant implementation is more careful than the current local collector. This is a source review of the named paths, not a guarantee for every provider or a claim that CodexBar was run on the user's accounts.

1. **Account quota:** its Codex provider obtains plan limits through PAT/OAuth or CLI RPC. OAuth calls `https://chatgpt.com/backend-api/wham/usage`; CLI fallback uses `codex app-server`. These percentages are independent of local token arithmetic. See [Codex provider](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/codex.md).
2. **Local request accounting:** the scanner parses native `token_usage_record`, validates numeric components, keeps response identities, and reconciles mirrored cumulative events instead of adding both representations. It resolves continuation/fork baselines and keeps checkpoints and rows in SQLite. See [request parser and ledger](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/Sources/CodexBarCore/Vendored/CostUsage/CostUsageScanner.swift#L3787) and [cross-file request identity](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/Sources/CodexBarCore/Vendored/CostUsage/CostUsageScanner%2BRequestIdentity.swift).
3. **Local cost estimates:** it resolves provider/model pricing from a 24-hour models.dev cache, bundled fallback rates, and explicit overrides. It splits inclusive OpenAI input into uncached input, cache reads, and available cache writes; output already includes reasoning. It applies context and supported Fast/priority rules. It also has dated handling for known historical repricing. This differs from the local widget's policy of freezing each day's observed price snapshot. See [pricing pipeline](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/model-pricing.md) and [cost formula](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/Sources/CodexBarCore/Vendored/CostUsage/CostUsagePricing.swift#L698).
4. **Reported API spending:** the separate OpenAI provider calls organization `/costs` and `/usage/completions` endpoints using an Admin API key. It follows pagination and supports project filters. It does not infer billed organization costs from a ChatGPT login. The implementation has a separate legacy balance fallback. See [OpenAI provider](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/openai.md) and `Sources/CodexBarCore/Resources/Plugins/openai.js`.
5. **OpenCode and Command Code:** local SQLite history and provider account quota are distinct sources. Command Code has a dedicated billing/quota integration, while OpenCode history readers use recorded local costs with migration deduplication. They should not be treated as one universal token-to-quota formula. See [OpenCode](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/opencode.md) and [Command Code](https://github.com/steipete/CodexBar/blob/7447bc77c2497323d9c41e40164ce705533493c8/docs/command-code.md).

The underlying OpenAI estimate is:

```text
uncached_input = input_tokens - cached_input_tokens - cache_write_input_tokens
cost = uncached_input * input_rate
     + cached_input_tokens * cache_read_rate
     + cache_write_input_tokens * cache_write_rate
     + output_tokens * output_rate
```

Rates must be per token, with the correct request-level context/tier. Reasoning is not a fifth amount added to output cost.

## OpenCode verification and limits

Installed OpenCode reports `v2.2.6`. Its read-only database has 5,909 assistant messages and 10 compaction messages. The target DeepSeek model has 1,264 stored message records. Raw totals are 4,024,980 input, 324,415 output, 587,927 reasoning, and 227,676,672 cache-read tokens. The collector adds session-aggregate residuals of 23,782 input, 861 output, 5,115 reasoning, and 561,280 cache reads. This reproduces the displayed row exactly.

No comparable continuation inflation was demonstrated in that OpenCode row. Its residuals cannot establish the original timestamp or model of missing requests, and recorded local dollar costs are not verified Command Code invoices. The collector's fallback-store precedence also does not prove coverage of every possible mixed legacy/v2 database. The conclusion is limited to the inspected store and target model, not universal correctness.

## Tests

Existing tests pass: `python3 test/test_collector.py` (6) and `python3 test/test_codex_usage.py` (32). These use disposable homes and stores, with live RPC and price fetching disabled where applicable.

Three isolated correct-behavior tests in `/tmp/codexbar-audit-20261109/reproduce.py` fail against the unchanged collector:

```text
Continuation: expected 4,000 total tokens; got 7,000.
Request-only compaction: expected 1,234 total tokens; got 0.
Reasoning breakdown: expected 400; got 0.
```

CodexBar's Swift tests were not run: no Swift compiler is installed. Its parser, pricing, continuation handling, and request-identity tests were inspected in source. No account probes, GUI launch, or dependency installation was performed.

## Recommended repair scope

Use native request usage as the primary accounting source, with session/response deduplication and mirrored-event reconciliation. Keep a continuation-aware legacy fallback. Retain distinct token components and normalize display labels across agents. Parse native tier settings in their actual envelope.

Before deployment, add the three failing cases and continued/copied/reordered/incremental request cases to the existing collector suite. Verify exact parity against the 653-request snapshot. Preserve the existing daily price snapshots, then rebuild affected usage/activity buckets and spending-event counters together, removing superseded inflated entries. Do not delete or silently reprice historical snapshots. Keep all existing bundled-delivery and UI contracts.

Implementation, migration, live deployment, commits, and pushes remain outstanding; the user's current request was to investigate and report.
