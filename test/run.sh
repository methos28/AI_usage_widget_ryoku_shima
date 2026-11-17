#!/usr/bin/env bash
# Repository test entry point.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
"$here/lint.sh"
python3 "$here/test_collector.py"
python3 "$here/test_claude_usage.py"
python3 "$here/test_claude_quota.py"
python3 "$here/test_claude_sessions.py"
python3 "$here/test_claude_spending.py"
python3 "$here/test_model_pricing.py"
python3 "$here/test_codex_usage.py"
python3 "$here/test_rolling_history.py"
python3 "$here/test_widget.py"
python3 "$here/test_refresh.py"
python3 "$here/test_ryoku_integration.py"
python3 "$here/test_install.py"
python3 "$here/cache_contract.py"
