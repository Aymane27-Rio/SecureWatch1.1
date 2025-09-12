#!/usr/bin/env bash
# Lightweight watcher sample: emits a single info entry; for continuous watch, run separately.
set -euo pipefail
HOST=$(hostname)
TS=$(date -Iseconds)
echo "{\"ts\":\"$TS\",\"host\":\"$HOST\",\"category\":\"integrity\",\"severity\":0,\"summary\":\"inotify-tools available: $(command -v inotifywait >/dev/null 2>&1 && echo yes || echo no)\",\"data\":{}}"
