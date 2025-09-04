#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import time, os, glob, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(BASE)  # project root
LOG_DIR = os.path.join(ROOT, "data", "logs")

g_total = Gauge("securewatch_events_total", "Total events in last report")
g_by_sev = Gauge(
    "securewatch_events_severity", "Events by severity in last report", ["severity"]
)
g_by_cat = Gauge(
    "securewatch_events_category", "Events by category in last report", ["category"]
)


def latest_json():
    files = sorted(glob.glob(os.path.join(LOG_DIR, "events_*.json")))
    return files[-1] if files else None


def tick():
    path = latest_json()
    if not path:
        g_total.set(0)
        return
    with open(path, "r") as f:
        events = json.load(f)
    g_total.set(len(events))
    sev_counts = {}
    cat_counts = {}
    for e in events:
        sev = str(e.get("severity", 0))
        cat = e.get("category", "unknown")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for sev, c in sev_counts.items():
        g_by_sev.labels(severity=sev).set(c)
    for cat, c in cat_counts.items():
        g_by_cat.labels(category=cat).set(c)


if __name__ == "__main__":
    start_http_server(9109)
    while True:
        tick()
        time.sleep(15)
