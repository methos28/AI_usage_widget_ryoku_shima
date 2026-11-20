Latest publication: user approved commit and push on 2026-11-10 03:11 IST. Published
b650d0c474553931ef551332051e46fe3d651d62 to methos28/ryoku:ai-usage. Remote head and
clean fork working tree verified. Previous staged-only statements below are
historical; consult the newest project log for current CI status.

# AI usage model pricing

The user requires multi-model API Value for Codex and Claude. The old Sonnet-only implementation was superseded on 2026-11-09. Widget-owned bin/model-pricing.py and model-prices.json provide 65 OpenAI and 35 Claude model IDs, native legacy and published snapshot IDs, public metadata refresh without credentials, private last-good caches and bundled offline rates. OpenCode retains recorded local costs.

Published context and service tiers are supported. Haiku 5.5 uses total prompt length including cache reads/writes for its 100,000-token boundary. Claude TTL splits distinguish five-minute and one-hour cache writes; output includes thinking once. Codex Fast/Priority, Flex, Batch and Ultrafast use explicit published rates where available. Unknown/private prices and incomplete pricing metadata remain marked, not silently zero.

Today can gain missing model/tier entries. Verified saved rates remain frozen; today's stale provisional fallback may refresh. Earlier daily snapshots are not repriced with current rates. The observed Codex November 6 history predates the first saved snapshot and remains explicitly unpriced under that policy.

All runtime files belong to the widget. Keep Rashin collectors, distro docs and original collector CI unchanged; only required module wiring, focused tests/widget CI and root CHANGELOG.md may differ outside the widget. Live installation is current; fork corrections and pricing changes are staged but not committed or pushed. See the latest primary PROJECT_LOG.md before changing publication status.
