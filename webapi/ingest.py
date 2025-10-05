import json
from pathlib import Path
from .db import get_conn, init_db
import datetime

def ingest_reports_from_dir(logs_dir="/app/data/logs", db_path=None, dry_run=False):
    logs_dir = Path(logs_dir)
    conn = get_conn(db_path)
    init_db(conn)
    cur = conn.cursor()

    inserted_reports = 0
    inserted_events = 0

    for path in sorted(logs_dir.glob("events_*.json")):
        report_id = path.name.replace("events_", "").replace(".json", "")
        # skip if report already ingested
        cur.execute("SELECT 1 FROM reports WHERE report_id=? LIMIT 1", (report_id,))
        if cur.fetchone():
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                events = json.load(f)
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            continue

        total = len(events)
        now = datetime.datetime.utcnow().isoformat()
        if not dry_run:
            cur.execute(
                "INSERT INTO reports (report_id, filename, ts, total, created_at) VALUES (?, ?, ?, ?, ?)",
                (report_id, path.name, report_id, total, now),
            )
            for e in events:
                cur.execute(
                    "INSERT INTO events (report_id, ts, host, category, severity, summary, data) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        report_id,
                        e.get("ts"),
                        e.get("host"),
                        e.get("category"),
                        int(e.get("severity", 0)),
                        e.get("summary"),
                        json.dumps(e.get("data", {})),
                    ),
                )
            conn.commit()
        inserted_reports += 1
        inserted_events += total

    conn.close()
    return {"reports": inserted_reports, "events": inserted_events}
