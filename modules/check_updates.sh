#!/usr/bin/env bash
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)

if command -v apt >/dev/null 2>&1; then
  updates=$(apt list --upgradable 2>/dev/null | grep -v "Listing..." | wc -l | tr -d ' ')
  sev=0
  if [ "$updates" -gt 0 ]; then sev=1; fi
  echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"packages\",\"severity\":$sev,\"summary\":\"Upgradable packages: $updates\",\"data\":{\"count\":$updates}}"
fi
