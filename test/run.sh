#!/usr/bin/env bash
# Repository test entry point.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
"$here/lint.sh"
python3 "$here/test_collector.py"
python3 "$here/test_codex_usage.py"
