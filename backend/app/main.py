from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import glob, json, os

app = FastAPI(title="SecureWatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change for production
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

LOG_DIR = os.environ.get("SECUREWATCH_LOG_DIR", "/app/data/logs")

def latest_reports():
    files = sorted(glob.glob(os.path.join(LOG_DIR, "events_*.json")))
    return files

@app.get("/api/metrics")
def metrics():
    files = latest_reports()
    if not files:
        return {"total_events": 0, "by_severity": {}, "by_category": {}, "last_run": None}
    path = files[-1]
    try:
        with open(path, "r", encoding="utf-8") as f:
            events = json.load(f)
    except Exception:
        events = []
    total = len(events)
    by_sev = {}
    by_cat = {}
    for e in events:
        sev = str(e.get("severity", 0))
        cat = e.get("category", "unknown")
        by_sev[sev] = by_sev.get(sev, 0) + 1
        by_cat[cat] = by_cat.get(cat, 0) + 1
    ts = os.path.basename(path).replace("events_", "").replace(".json", "")
    return {"total_events": total, "by_severity": by_sev, "by_category": by_cat, "last_run": ts}

@app.get("/api/reports")
def list_reports():
    files = latest_reports()
    out = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                events = json.load(f)
        except Exception:
            events = []
        ts = os.path.basename(p).replace("events_", "").replace(".json", "")
        by_sev = {}
        for e in events:
            sev = str(e.get("severity", 0))
            by_sev[sev] = by_sev.get(sev, 0) + 1
        out.append({"id": ts, "file": os.path.basename(p), "summary": {"total": len(events), "by_severity": by_sev}})
    return out

@app.get("/api/reports/{report_id}")
def get_report(report_id: str):
    path = os.path.join(LOG_DIR, f"events_{report_id}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data