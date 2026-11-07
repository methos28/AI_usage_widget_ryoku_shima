#!/usr/bin/env bash
# Install the widget, collector and service drop-in on this machine.
set -euo pipefail

root="$(cd "$(dirname "$0")" && pwd)"
widgets="$HOME/.config/inir/widgets"
bin="$HOME/.local/bin"
dropin="$HOME/.config/systemd/user/ryoku-ai-usage.service.d"

install -d "$widgets" "$bin" "$dropin"
rm -rf "$widgets/ai-usage"
cp -a "$root/ai-usage" "$widgets/ai-usage"
install -m 755 "$root/collector/opencode-usage-v2" "$bin/opencode-usage-v2"
install -m 755 "$root/collector/codex-usage" "$bin/codex-usage"
install -m 644 "$root/systemd/ryoku-ai-usage.service.d/override.conf" \
    "$dropin/override.conf"

systemctl --user daemon-reload
systemctl --user start ryoku-ai-usage.service || true
ryoku-shell reload

printf 'installed: %s\n' "$widgets/ai-usage"
printf 'collector: %s\n' "$bin/opencode-usage-v2"
printf 'collector: %s\n' "$bin/codex-usage"
printf 'service:   %s\n' "$dropin/override.conf"
