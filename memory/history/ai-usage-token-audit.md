# AI usage token audit: observed continuation overcount

Audited on 2026-11-09. The bundled collector architecture remains as documented in ai-usage-bundled-collectors.md. This note records the audit and subsequent repair, not an architecture change. The fixes were deployed on 2026-11-09; see the repair checkpoint below.

Current Codex history is inflated at four continuation-file boundaries. Both scan_activity() and history_records() initialize counters at zero for each physical file and ignore session_meta.history_base. A new page can start with inherited cumulative usage, counted again at a new timestamp. Event hashing prevents exact copies but does not fix this boundary. The live primary widget matched source during the audit.

The saved private cache at 13:24:17 was reconstructed through activity-state offsets: 11 files, seven sessions, 653 unique native token_usage_record requests. Sol output was 780,579 in the collector versus 518,489 from unique requests. The latter includes 270,089 reasoning and 248,400 non-reasoning output. Uncached input was 2,761,528 versus 1,753,628. Model aggregation mixes high and xhigh. A request-only compaction of 453,353 tokens is also omitted by token_count-only reading.

The display uses incompatible O/R meanings: Codex includes reasoning in output and sets reasoning to zero; OpenCode stores output and reasoning separately. Target DeepSeek Command Code counts are 325,276 output and 593,042 reasoning after session residual adjustments. Do not compare its O alone to Codex's inclusive output.

At the same cutoff and using the same saved daily prices, the partial Codex estimate reconstructs from $52.926383 to $33.327711. November 6 remains unpriced. Daily snapshots must be preserved in any repair. Cache bucket max-merging and retained bad ledger events mean a parser-only refresh will not remove inflated history. A coordinated usage/activity/ledger migration is needed.

Existing six OpenCode and 32 Codex tests pass but miss these cases. Three isolated tests fail for continuation accounting, request-only compaction, and reasoning display. CodexBar commit 7447bc77c2497323d9c41e40164ce705533493c8 supplies reference request-ledger, mirror reconciliation, continuation baselines and provider-scoped pricing logic. Its Swift tests were not run; no compiler is installed.

Full durable report: /home/methos/Documents/opencode_widget_ryoku_shima/CODEXBAR_TOKEN_AUDIT_2026-11-09.md. Temporary clone/evidence/reproductions: /tmp/codexbar-audit-20261109. No collector code, live state, pricing ledger or settings were changed. The user requested an audit; implementation remains outstanding.

## Repair checkpoint — 2026-11-09

The user authorised implementation. Native request identity, mirror reconciliation, continuation-aware legacy fallback, compaction, reasoning/cache-write components and real settings envelopes are fixed. Activity schema 5 retains the canonical request ledger. Reconstructed cache dates and old spending identities migrate automatically while daily prices and unavailable historical records survive. A private monthly before-request-accounting backup is saved.

All 59 primary and 61 fork tests plus delivery/QML/cache gates pass. The frozen 653-request audit reproduces $33.327711 exactly. A later 718-request live snapshot independently matches every raw token component, day totals and the $36.917120 estimate. Existing prices stayed unchanged. The normal quota refresh succeeds as rpc/Plus with the existing login; shell reload and live card inspection succeeded.

The primary, fork, bundled live, protected libexec and home-bin collectors now match. Legacy user-owned copies were updated because they share the same spending ledger; no service configuration was changed. Live backup: ~/.local/share/ryoku/ai-usage-backup/request-repair-live-20261109-144515/. Full report: /home/methos/Documents/opencode_widget_ryoku_shima/REQUEST_ACCOUNTING_REPAIR_2026-11-09.md. Changes remain uncommitted and unpushed. Earlier paragraphs are the historical pre-fix audit, not current behavior.
