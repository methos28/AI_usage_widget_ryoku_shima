Adds theme-aware transitions to AI Usage and prevents previous-agent data from flashing during dropdown switches.

- Ease quota fills over 360 ms, token/API Value numbers over 380 ms, and state fades over 180 ms using Shima's gentle curve.
- Load first values and agent changes directly, retarget updates smoothly, and respect hidden surfaces and reduced motion.
- Retain quota delegates during normal refreshes while clearing their presentation state on agent switches.
- Show a neutral loading state until the selected snapshot is ready. Tag asynchronous reads and discard old generations or superseded cache versions.
- Apply matching snapshot guards to the desktop tile as well as the Island cards.

Both primary and fork-targeted suites pass 233 cases without skips, including native Qt checks for all six switch directions, rapid round trips, missing caches, latest-snapshot selection and motion behavior. Merged-source QML and focused switch/motion checks pass after syncing with latest unstable-dev. Normal commit and push hooks pass. A representative hardware-rendered card probe showed unchanged frame pacing for the smoother motion.

The branch is synced with unstable-dev at 3f4f6ee. The diff contains nine widget QML files, the focused usage guide and the existing changelog entry. Collector/accounting code is unchanged. PR #881's prior fixes are already in the base.
