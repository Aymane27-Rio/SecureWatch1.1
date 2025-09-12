#!/usr/bin/env bash
set -euo pipefail
JSON_PATH="${1:-}"
COUNT="${2:-0}"

SUBJECT="[SecureWatch] Critical findings: ${COUNT}"
BODY="SecureWatch detected ${COUNT} critical finding(s).\nSee JSON: ${JSON_PATH}"

# Try local mail if available
if command -v mail >/dev/null 2>&1; then
  echo -e "$BODY" | mail -s "$SUBJECT" root@localhost || true
fi

# Slack webhook (optional)
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
  payload=$(jq -n --arg t "$SUBJECT" --arg b "$BODY" '{text: ($t + "\n" + $b)}')
  curl -s -X POST -H 'Content-type: application/json' --data "$payload" "$SLACK_WEBHOOK_URL" >/dev/null || true
fi
