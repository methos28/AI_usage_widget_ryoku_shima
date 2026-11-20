# AI Usage restoration after user-managed Ryoku 1.1.0 update

Prepared 2026-11-18 15:09 IST. The user is about to update Ryoku and explicitly wants the approved transitions reinstalled afterward. Current installed release is stable 1.0.9 (08ff328), update target 1.1.0. Wait for their confirmation that the update is finished; do not initiate the update.

Independent verified restore bundle: /home/methos/Documents/ai-usage-update-backup/20261118-150955. It contains the exact 32-file primary and live widget, installer, SHA-256 manifest and restore instructions. Source commit 24b6db3; feature publication f039733d7. Current live code matches that approved source, with gentle 360-ms bars/380-ms numbers/180-ms fades and agent-switch snapshot isolation.

After completion: read upgraded status/map/ownership, check live user widget and Shima motion/API compatibility, validate against upgraded imports, reinstall atomically via the supported user-owned widget installer and reload, then verify all-agent switching, motion, bytes and logs. Do not overwrite usage caches, ledgers, credentials or shell settings. Do not edit shipped Quickshell files. The user copy may already be intact.

Follow the standing post-upgrade bootloader verification runbook, starting from newest baseline 2026-11-12; preserve GRUB, existing entries and user-owned GRUB config. Preparation made no package, runtime, auth, settings or boot change. No new commit/push is requested.
