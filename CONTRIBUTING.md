# Contributing

This repository is a user-owned Shima module, not a Ryoku core checkout. The
rules below are the ones that keep it maintainable and compatible with a future
upstream contribution.

- One QML component per file. Shared primitives live in `ai-usage/components/`.
- Keep the collector backwards compatible: the shell's own AI panel reads the
  same cache. Add fields, do not rename existing ones.
- The day and hour history is append-only. Never make a published total shrink.
- Test on the live desktop, not only that a file parses.
- Write commits in the imperative mood, one logical change per commit.
- Do not add AI or bot attribution trailers.
- No em-dashes in user-facing text.
- Run `./test/run.sh` before a commit.

## Commit subjects

Short imperative subject, 72 characters or fewer, no trailing period:

```
ai usage: split the island page into components
collector: keep published history append-only
```

## Licence

The repository is licensed under GPL-3.0 and
the `LICENSE` file carries the licence text.
