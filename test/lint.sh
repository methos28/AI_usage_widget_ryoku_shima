#!/usr/bin/env bash
# Static checks for the widget and the collector.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/.." && pwd)"

lint="$(command -v /usr/lib/qt6/bin/qmllint || command -v qmllint || true)"
if [ -n "$lint" ]; then
    while IFS= read -r -d '' file; do
        "$lint" -I "$HOME/.config/quickshell" "$file"
    done < <(find "$root/ai-usage" -name '*.qml' -print0)
else
    echo "qmllint not found, skipping QML" >&2
fi

python3 -m py_compile "$root/collector/opencode-usage-v2"
python3 -m py_compile "$here/test_collector.py"
python3 -m py_compile "$here/cache_contract.py"
echo "lint OK"
