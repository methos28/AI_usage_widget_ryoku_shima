# Claude model-count audit — 2026-11-09

The user resumed the saved Sonnet/Haiku review at 19:09 IST. The observed token
collector is correct for both models. No token-parser change is needed.
One numeric regression was added; application code and the live cache were not
changed. The separate API Value limitation remains explicit: only Sonnet has
verified saved prices, so Haiku contributes tokens but is currently unpriced.

## Independent reconstruction

Read both native project transcripts without printing or copying prompts.
There are 51 assistant records representing 25 distinct response identities.
All repeated counters within each response are identical, so streaming snapshot
selection does not explain this report. Independent final-response counts match
every current dashboard period/model total. Source hashes stayed stable during
the reconstruction.

| Model | Responses | Uncached input | Output including thinking | Thinking subset | Non-thinking output | Cache reads | Cache writes | Inclusive total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Sonnet 5.5 | 15 | 32 | 7,522 | 1,705 | 5,817 | 831,602 | 141,517 | 980,673 |
| Haiku 5.5 | 10 | 20 | 7,667 | 3,877 | 3,790 | 653,589 | 78,354 | 739,630 |

Combined total is **1,720,303**, matching today's private cache. Input, cache
reads and cache writes are separate native classes. Thinking is a subset of
native output and must not be added to that inclusive output again.

## Sonnet output: a display split, not a missing count

The reported 7.5K is native inclusive output: exactly 7,522. The widget shows
`O 5.8K` for 5,817 non-thinking tokens and `R 1.7K` for 1,705 thinking tokens.
Together they equal 7,522. Model totals and API pricing include both once.

This matches Anthropic's documented semantics: `output_tokens` includes thinking;
`output_tokens_details.thinking_tokens` is its observability breakdown.
[Official thinking documentation](https://platform.claude.com/docs/en/build-with-claude/thinking-steering-and-cost).

The input total likewise includes each of uncached input, cache reads and cache
creation. [Official cache accounting](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

## Haiku: two different response checkpoints

The quoted 356.6K dashboard value exactly matches the first five Haiku responses.
The quoted 430.5K recount exactly matches six responses:

| Native response timestamp, UTC | Haiku responses so far | Inclusive total |
|---|---:|---:|
| 2026-11-09 10:40:46.131 | 5 | 356,575 |
| 2026-11-09 10:51:49.944 | 6 | 430,498 |
| 2026-11-09 10:53:33.431 | 10 | 739,630 |

The sixth response contains input **2**, output including thinking **672**,
cache reads **72,544** and cache writes **705**. Its total is **73,923**, exactly
`430,498 - 356,575`. This accounts for the apparent gap without dropping cache
writes. At the five-response checkpoint, cache writes already total **72,544**;
at six responses, they total **73,249**.

The expanded historical model screenshot was not supplied, so its exact capture
time cannot be proved from the two collapsed screenshots. However, both quoted
rounded numbers are exactly reproduced by consecutive native response prefixes.
That supports the user's timing caveat. All Haiku responses belong to the same
continuing session, so an older-session exclusion is not needed to explain this
Haiku difference.

## Same-session model switching and period scope

The continuing session contains 11 Sonnet responses and all 10 Haiku responses.
The older session contributes four more Sonnet responses totaling 266,294.
The collector attributes each response using `message.model`, rather than the
session's latest selected model, so switching from Sonnet medium to Haiku high
does not reassign earlier tokens. Sonnet's combined total includes both local
sessions; Haiku has one. All observed responses fall within the selected local
Today and Last 24 hours windows, which currently therefore match.

## API Value coverage is separate

The current `$0.72*` is the partial Sonnet-only API-equivalent value:
**$0.7245122** before publication rounding. Its saved priced-token coverage is
980,673; Haiku's 739,630 tokens are recorded as unpriced. The current verified
price dictionary supports exact `claude-sonnet-5-5`, not `claude-haiku-5-5`.
The asterisk correctly marks this incomplete coverage. Haiku's unknown price
does not remove its tokens from Models, Trend or today's total.

Adding Haiku pricing is separate from the token recount. This audit does not
guess a Sonnet rate for Haiku or modify frozen daily price dictionaries.

## Regression and evidence

Added `test_observed_model_switch_keeps_writes_thinking_and_snapshot_boundaries`
to `test/test_claude_usage.py`. Its sanitized numeric fixture repeats response
blocks, includes both session scopes, switches the continuing session's model,
and reproduces all three Haiku checkpoints plus Sonnet's O/R split. It uses no
native request identities, prompts, credentials or network calls.

Private evidence directory:
`~/.local/share/ryoku/ai-usage-backup/claude-recount-audit-20261109-191418`.
It contains a sanitized numeric audit, source hashes and the frozen dashboard
cache. The raw prompt transcripts were not copied. Final suite results are
recorded in `PROJECT_LOG.md`.

No model prompt, authentication change, production collector refresh, shell
reload, ledger edit, fork edit, commit or push was performed for this audit.
The previously pending fresh active-to-idle Desktop observation remains pending;
this historical token recount does not establish that separate live transition.
