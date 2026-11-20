Latest publication: user approved commit and push on 2026-11-10 03:11 IST. Published
b650d0c474553931ef551332051e46fe3d651d62 to methos28/ryoku:ai-usage. Remote head and
clean fork working tree verified. Previous staged-only statements below are
historical; consult the newest project log for current CI status.

# AI Usage bug audit

The full module audit completed on 2026-11-10. See the primary BUG_AUDIT_2026-11-10.md and newest PROJECT_LOG.md entries before future edits. All 172 primary and 172 fork regression tests and required gates pass; tested repairs are live, with fork changes staged but uncommitted/unpushed.

Repairs cover cache-inclusive/large totals, cache shape and freshness, private atomic publication and lock handling, native SQLite paths/schema variants, active-session priority, full model counts, DST/calendar boundaries, malformed pricing/ledger data and storage failures, Claude streamed metadata/zero-usage records, and safe standalone install rollback. The obsolete runtime shared-cache diagnostic was removed; demo generation now requires an explicit destination and refuses existing caches.

Rashin, distro docs, original collector CI and the desktop widget manager remain unchanged from the original upstream review base. Keep that boundary. Real Codex request identities and token components matched across 1,151 requests; earlier daily prices remain frozen. CLI PID observations inside the agent sandbox cannot validate host processes because namespaces differ. Real host idle/PID and quota RPC checks pass; a new paid Claude active-to-idle turn was not launched during the audit.
