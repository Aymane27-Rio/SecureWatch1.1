import sqlite3
import os
from pathlib import Path

DEFAULT_DB = "/app/data/state/securewatch.db"

def get_conn(db_path=None):
    db_path = db_path or os.environ.get("WEBAPI_DB_PATH", DEFAULT_DB)
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn):
    cur = conn.cursor()
    # Reports table (one row per events_*.json file)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT UNIQUE,
        filename TEXT,
        ts TEXT,
        total INTEGER,
        created_at TEXT
    );
    """)
    # Events table (one row per NDJSON event)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT,
        ts TEXT,
        host TEXT,
        category TEXT,
        severity INTEGER,
        summary TEXT,
        data TEXT,
        FOREIGN KEY(report_id) REFERENCES reports(report_id)
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON events(severity);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_reports_reportid ON reports(report_id);")
    conn.commit()
