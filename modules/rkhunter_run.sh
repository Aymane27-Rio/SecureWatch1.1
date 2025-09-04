#!/usr/bin/env bash
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)
if command -v rkhunter >/dev/null 2>&1; then
  out=$(sudo rkhunter --check --sk --nocolors --quiet || true)
  warnings=$(echo "$out" | grep -c "Warning:" || true)
  sev=0; [ "$warnings" -gt 0 ] && sev=2
  echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"malware\",\"severity\":$sev,\"summary\":\"rkhunter warnings: $warnings\",\"data\":{\"warnings\":$warnings}}"
fi
