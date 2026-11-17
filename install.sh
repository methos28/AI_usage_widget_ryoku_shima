#!/usr/bin/env bash
# Install the self-contained widget and its bundled collectors on this machine.
set -euo pipefail
umask 077

root="$(cd "$(dirname "$0")" && pwd)"
widgets="$HOME/.config/inir/widgets"
target="$widgets/ai-usage"
[[ -f "$root/ai-usage/widget.json" ]] || { echo "widget source is incomplete" >&2; exit 1; }
install -d "$widgets"
exec {install_lock_fd}>>"$widgets/.ai-usage-install.lock"
flock "$install_lock_fd"
staging="$(mktemp -d "$widgets/.ai-usage-stage.XXXXXX")"
backup=""
published=0

cleanup() {
    local status=$?
    trap - EXIT
    trap '' INT TERM
    if (( status != 0 )); then
        if [[ -n "$backup" && ( -e "$backup" || -L "$backup" ) ]]; then
            rm -rf -- "$target"
            mv -T -- "$backup" "$target"
        elif (( published )); then
            rm -rf -- "$target"
        fi
    fi
    rm -rf -- "$staging"
    if (( status == 0 )) && [[ -n "$backup" ]]; then rm -rf -- "$backup"; fi
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

cp -a "$root/ai-usage/." "$staging/"
if [[ -e "$target" || -L "$target" ]]; then
    backup="$(mktemp -d "$widgets/.ai-usage-before.XXXXXX")"
    rmdir -- "$backup"
    mv -T -- "$target" "$backup"
fi
mv -T -- "$staging" "$target"
published=1
ryoku-shell reload {install_lock_fd}>&-

printf 'installed: %s\n' "$target"
printf 'collectors: %s\n' "$target/bin"
