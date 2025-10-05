import os
import threading
import time
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
import sqlite3
from .db import get_conn, init_db
from .ingest import ingest_reports_from_dir

app = FastAPI(title="SecureWatch WebAPI (M2)")

# config via .env
DB_PATH = os.environ.get("WEBAPI_DB_PATH", "/app/data/state/securewatch.db")
LOGS_DIR = os.environ.get("WEBAPI_LOGS_DIR", "/app/data/logs")
API_KEY = os.environ.get("WEBAPI_API_KEY", "")  # set a non-empty value in production
ALLOW_SCAN = os.environ.get("WEBAPI_ALLOW_SCAN", "0") == "1"
INGEST_INTERVAL = int(os.environ.get("WEBAPI_INGEST_INTERVAL", "60"))  # seconds

# ensure DB exists
conn = get_conn(DB_PATH)
init_db(conn)
conn.close()

def check_api_key(token: str):
    if not API_KEY:
        # if no API key configured we treat as open (for development)
        return True
    return token == API_KEY

@app.get("/hello")
def hello():
    return {"message": "SecureWatch WebAPI (M2) running"}

@app.get("/reports")
def list_reports():
    conn = get_conn(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT report_id, filename, ts, total, created_at FROM reports ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"reports": rows}

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    conn = get_conn(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT report_id, filename, ts, total, created_at FROM reports WHERE report_id=? LIMIT 1", (report_id,))
    r = cur.fetchone()
    if not r:
        conn.close()
        raise HTTPException(status_code=404, detail="report not found")
    cur.execute("SELECT id, ts, host, category, severity, summary, data FROM events WHERE report_id=? ORDER BY id ASC", (report_id,))
    events = [dict(row) for row in cur.fetchall()]
    conn.close()
    return {"report": dict(r), "events": events}

@app.get("/events")
def query_events(severity: int = None, category: str = None, limit: int = 100, offset: int = 0):
    conn = get_conn(DB_PATH)
    cur = conn.cursor()
    q = "SELECT id, report_id, ts, host, category, severity, summary, data FROM events"
    clauses = []
    params = []
    if severity is not None:
        clauses.append("severity = ?")
        params.append(severity)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if clauses:
        q += " WHERE " + " AND ".join(clauses)
    q += " ORDER BY ts DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cur.execute(q, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"count": len(rows), "events": rows}

@app.get("/events/{eid}")
def get_event(eid: int):
    conn = get_conn(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, report_id, ts, host, category, severity, summary, data FROM events WHERE id=? LIMIT 1", (eid,))
    r = cur.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="event not found")
    return dict(r)

@app.post("/ingest")
def manual_ingest(x_api_key: str = Header(None), background: BackgroundTasks = None):
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
    # run ingestion in background to avoid blocking
    background.add_task(ingest_reports_from_dir, LOGS_DIR, DB_PATH)
    return JSONResponse({"status": "ingest started"})

@app.post("/scan")
def trigger_scan(x_api_key: str = Header(None)):
    if not check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="invalid api key")
    if not ALLOW_SCAN:
        raise HTTPException(status_code=403, detail="scan triggering is disabled")
    # Attempt to run the securewatch script - ensure scripts were copied into the image
    script = Path("/app/scripts/securewatch.sh")
    if not script.exists():
        raise HTTPException(status_code=500, detail="securewatch script not available in container")
    # run synchronously but in a thread so request returns quickly
    def _run():
        import subprocess
        try:
            subprocess.run(["/bin/bash", str(script)], check=True)
            # optional: auto-ingest after run
            ingest_reports_from_dir(LOGS_DIR, DB_PATH)
        except Exception as e:
            print("scan failed:", e)
    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    return {"status": "scan triggered"}

# background ingestion thread
def periodic_ingest():
    while True:
        try:
            ingest_reports_from_dir(LOGS_DIR, DB_PATH)
        except Exception as e:
            print("periodic ingest error:", e)
        time.sleep(INGEST_INTERVAL)

@app.on_event("startup")
def startup_event():
    # start background ingestion thread
    t = threading.Thread(target=periodic_ingest, daemon=True)
    t.start()
