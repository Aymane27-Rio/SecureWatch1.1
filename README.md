# SecureWatch — Automated Linux Security & Cloud Monitoring Suite

SecureWatch is a modular toolkit to automate baseline security checks on Linux (Ubuntu/Kali), detect suspicious activity, and generate structured logs + human-readable reports. It also ships with a Prometheus exporter and a cloud (AWS) monitoring stub.

> ⚠️ Run scripts that require privileged ops with `sudo`.

## Features
- Modular **Bash** checks: users, ports, firewall, updates, AIDE/rkhunter hooks, file integrity.
- **Log parsing** (SSH brute force, sudo anomalies) → JSON events.
- **HTML reports** + NDJSON/JSON logs saved under `data/`.
- Optional **Prometheus exporter** for Grafana dashboards.
- Optional **AWS security group audit** (overly permissive ingress).

## Quickstart

New update: You can now run SecureWatch in two ways:

### Native (Ubuntu/Kali)

```bash
# 0) Unzip and enter
unzip securewatch-skeleton.zip && cd securewatch

# 1) Install OS dependencies
make install-deps

# 2) Create Python venv + deps (for reporting/exporter/cloud)
make venv

# 3) Run a one-off security sweep (writes logs + report under data/)
make run

# 4) Start Prometheus exporter (port :9109) in foreground
make exporter

# (Optional) Install systemd timer for hourly scans
sudo make enable-systemd   # edits may be required to point to your absolute path
```

---

## Web App Setup (Linux)

This section explains how to run the SecureWatch Web API (FastAPI) and the Vite/React Web Dashboard locally on a Linux host.

### Prerequisites

- Python 3.11+
- Node.js 18+
- SQLite3 (CLI) optional for inspecting DB
- Docker Desktop/Engine (optional, for containerized runs)

### 1) Prepare data directories

```bash
mkdir -p data/logs data/reports data/state
```

### 2) Start the Web API (FastAPI + Uvicorn)

```bash
cd webapi
python -m venv .venv && source .venv/bin/activate   # or use your preferred env manager
pip install -r requirements.txt

# Optional: set API key and paths (defaults shown)
export WEBAPI_DB_PATH="$(pwd)/../data/state/securewatch.db"
export WEBAPI_LOGS_DIR="$(pwd)/../data/logs"
# export WEBAPI_API_KEY="replace_with_a_strong_key"
# export WEBAPI_ALLOW_SCAN=0
# export WEBAPI_INGEST_INTERVAL=60

uvicorn webapi.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify API is up:

```bash
curl http://localhost:8000/hello
curl http://localhost:8000/reports
```

### 3) Generate sample data (so the Web App has something to show)

Run SecureWatch once to write logs/reports under `data/`.

```bash
# From repo root
sudo make run           # or run your scripts/securewatch.sh directly

# Confirm artifacts exist
ls -l data/logs/
ls -l data/reports/
```

Optionally trigger ingestion via API (if you set an API key, pass it via header):

```bash
curl -X POST -H "X-API-Key: ${WEBAPI_API_KEY:-}" http://localhost:8000/ingest
```

### 4) Start the Web Dashboard (Vite/React)

```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

Notes:

- The dev server proxies `/api` to `http://localhost:8000` (configured in `vite.config.js`).
- If the backend is not running, the browser console/terminal will show proxy ECONNREFUSED.

Production preview:

```bash
npm run build
npm run preview   # http://localhost:3000
```

### 5) Dockerized Web Dashboard

Build and run the frontend image (served by Nginx):

```bash
cd frontend
docker build -t securewatch-frontend .
docker run --rm -p 8080:80 securewatch-frontend   # app at http://localhost:8080
```

The container proxies `/api` to `http://host.docker.internal:8000` by default (see `frontend/nginx.conf`). Ensure the Web API is running on the host at port 8000.

### 6) Dockerized Web API

```bash
docker build -f webapi/Dockerfile -t securewatch-webapi .
docker run --rm -p 8000:8000 \
  -e WEBAPI_DB_PATH=/app/data/state/securewatch.db \
  -e WEBAPI_LOGS_DIR=/app/data/logs \
  -e WEBAPI_API_KEY=replace_with_a_strong_key \
  -v $(pwd)/data:/app/data \
  securewatch-webapi
```

Now the frontend container at `http://localhost:8080` can reach the API via `/api`.

### 7) Optional: Docker Compose

There is a `docker-compose.yml` in the repo. Ensure the ports for the `frontend` service map to the container port exposed by its Dockerfile (80). For example:

```yaml
  frontend:
    build: ./frontend
    ports:
      - "3000:80"   # host:container
```

Then run:

```bash
docker compose up --build -d
```

### Verification Checklist

- Web API
  - `curl http://localhost:8000/hello` returns JSON.
  - `curl http://localhost:8000/reports` returns a list (possibly empty initially).
  - After running `make run` (or your script), `curl http://localhost:8000/reports` shows new items.

- Web App
  - Open the UI (dev: `http://localhost:5173`, preview: `http://localhost:3000`, Docker: `http://localhost:8080`).
  - Dashboard shows metrics (last run, totals) and reports list.
  - Clicking “view raw JSON” on a report opens `/api/reports/{id}`.

### Troubleshooting

- Proxy ECONNREFUSED in `npm run dev`
  - Ensure the Web API is running at `http://localhost:8000`.
  - The Vite dev proxy forwards `/api` → backend; if backend is down, calls fail.

- 502/404 from frontend in Docker
  - Verify Web API is reachable on the host `:8000`.
  - Confirm `host.docker.internal` resolves (Docker Desktop). If using Linux Engine without this alias, update `frontend/nginx.conf` to point to the correct host/IP.

- Empty dashboard
  - Run a SecureWatch scan to generate data under `data/`.
  - Trigger `/ingest` or wait for periodic ingest (default every 60s).

### Or Dockerized (more recommended for portability)

```bash
# 0) Build the image
docker build -t securewatch .

# 1) Run a one-off security sweep
docker run --rm -v $(pwd)/data:/app/data securewatch

# Reports will be available under ./data/reports/

# (Optional) Run with docker-compose
docker compose up

```

## Layout
- `scripts/securewatch.sh` — Orchestrator (runs modules, aggregates JSON, renders report, alerts).
- `modules/*` — Individual checks.
- `python/log_parser.py` — Parses system logs for anomalies.
- `python/report_generator.py` — Renders HTML report.
- `python/exporters/securewatch_exporter.py` — Prometheus metrics exporter.
- `python/cloud_monitor/aws_monitor.py` — AWS security group audit (stub).
- `config/securewatch.conf` — Tuning (thresholds, paths, email/slack settings).
- `data/` — Logs, reports, state.
- `systemd/*.service|*.timer` — Units for scheduled runs.
- `dashboards/grafana/*.json` — Starter dashboard.

## Security & Privacy
- Designed for local ops; **does not exfiltrate** data unless you enable alerts/webhooks.
- Logs may contain IPs/usernames. Handle and share responsibly.
- Use at your own risk; review code and tailor thresholds to your environment.

## Cloud Notes
- AWS checks require credentials via environment or `~/.aws/credentials`.
- Minimal sample detects `0.0.0.0/0` on sensitive ports (22/3389); extend as needed.

## UPDATE 1: Local Web Dashboard (FastAPI backend + Vite frontend)

Run the full stack:

docker compose up --build -d

- frontend -> http://localhost:3000
- backend  -> http://localhost:8000
- prometheus -> http://localhost:9090
- grafana -> http://localhost:3001


## UPDATE 2: 

from the project root, run:

```bash
# 1) Build images and start services
docker compose up --build -d

# 2) Force a run of SecureWatch to produce events (if needed):
# If the exporter is a one-shot, run it manually so it writes ./data/logs/events_*.json
# If your exporter is triggered differently, follow your existing method:
sudo make run    # (if this writes into ./data on the host)

# 3) Check that the JSON file exists
ls -l data/logs/events_*.json
ls -l data/reports/*.html

# 4) Trigger ingestion (either via API or let background task run)
# If you set WEBAPI_API_KEY in docker-compose.yml to 'replace_with_a_strong_key'
curl -X POST -H "X-API-Key: replace_with_a_strong_key" http://localhost:8000/ingest

# 5) Query the WebAPI
curl http://localhost:8000/hello
curl http://localhost:8000/reports
curl http://localhost:8000/events?limit=50

# 6) Inspect the SQLite DB
sqlite3 data/state/securewatch.db "SELECT count(*) FROM events;"
sqlite3 data/state/securewatch.db "SELECT * FROM reports ORDER BY created_at DESC LIMIT 5;"

```
