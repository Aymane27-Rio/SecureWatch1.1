#!/usr/bin/env bash
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)
if command -v aide >/dev/null 2>&1; then
  sudo aide --check >/tmp/aide.out 2>/dev/null || true
  if grep -q "AIDE found differences" /tmp/aide.out 2>/dev/null; then
    echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"integrity\",\"severity\":3,\"summary\":\"AIDE found differences\",\"data\":{}}"
  else
    echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"integrity\",\"severity\":0,\"summary\":\"AIDE no differences\",\"data\":{}}"
  fi
fi
