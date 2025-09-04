#!/usr/bin/env bash
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)

# Use ss if available, else netstat
if command -v ss >/dev/null 2>&1; then
  CMD="ss -tuln"
elif command -v netstat >/dev/null 2>&1; then
  CMD="netstat -tuln"
else
  exit 0
fi

$CMD | awk 'NR>1 {print $1, $5}' | while read proto addr; do
  port=$(echo "$addr" | awk -F: '{print $NF}')
  if [[ "$port" =~ ^[0-9]+$ ]]; then
    sev=1
    if [ "$port" -lt 1024 ]; then sev=2; fi
    echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"network\",\"severity\":$sev,\"summary\":\"Listening port\",\"data\":{\"proto\":\"$proto\",\"port\":$port}}"
  fi
done
