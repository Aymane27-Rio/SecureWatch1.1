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

