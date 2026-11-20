# Claude CLI quota refresh

On 2026-11-10, live subscription OAuth usage was verified with the installed widget helper. A real account GET succeeded using saved CLI credentials while Desktop captures were excluded, PATH contained no CLI executables and process launches were blocked. A repeat within five seconds used the existing cooldown. No CLI or Desktop process invocation is required by the quota reader; the user's running prompt was not closed during testing.

Usable saved subscription OAuth credentials are required. Installing the CLI without signing in is insufficient. The widget reads existing credentials and does not renew an expired login. Collection runs at module load and while visible. The current implementation prioritizes a fresh Desktop capture for up to 20 minutes, then uses CLI OAuth for stale/missing captures. OAuth refresh is throttled to five minutes, with reset-boundary refresh handling.

This confirms quota access only. The new live CLI session's process verification remained unknown in the same observation; do not claim its active-session indicator was verified.
