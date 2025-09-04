#!/usr/bin/env bash
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)
while IFS=: read -r user _ uid gid _ home shell; do
  if [ "$uid" -eq 0 ]; then
    echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"accounts\",\"severity\":2,\"summary\":\"UID 0 account detected\",\"data\":{\"user\":\"$user\",\"shell\":\"$shell\"}}"
  fi
done < /etc/passwd
