#!/usr/bin/env bash
# Static checks for the widget and the collector.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/.." && pwd)"

lint="$(command -v /usr/lib/qt6/bin/qmllint || command -v qmllint || true)"
imports="${RYOKU_QML_IMPORTS:-$HOME/.config/quickshell}"
if [ -n "$lint" ]; then
    while IFS= read -r -d '' file; do
        "$lint" -I "$imports" "$file"
    done < <(find "$root/ai-usage" -name '*.qml' -print0)
else
    echo "qmllint not found, skipping QML" >&2
fi

python3 -m py_compile "$root/collector/opencode-usage-v2"
python3 -m py_compile "$root/collector/codex-usage"
python3 -m py_compile "$root/ai-usage/bin/claude-usage"
python3 -m py_compile "$root/ai-usage/bin/model-pricing.py"
python3 -m json.tool "$root/ai-usage/bin/model-prices.json" > /dev/null
python3 -m py_compile "$root/ai-usage/bin/claude-quota.py" "$root/ai-usage/bin/claude-sessions.py" "$root/ai-usage/bin/claude-spending.py"
python3 -m py_compile "$root/ai-usage/bin/rolling-history.py"
bash -n "$root/ai-usage/bin/collect-usage" "$root/install.sh"
python3 -m py_compile "$here/test_collector.py"
python3 -m py_compile "$here/cache_contract.py"
echo "lint OK"
