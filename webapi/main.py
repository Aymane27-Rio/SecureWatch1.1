from fastapi import FastAPI
from pathlib import Path
import json

app = FastAPI(title="SecureWatch Web API")

DATA_DIR = Path("/app/data")

@app.get("/hello")
def hello():
    return {"message": "SecureWatch WebAPI is alive!"}

@app.get("/reports")
def list_reports():
    """List generated HTML reports."""
    reports = [f.name for f in (DATA_DIR / "reports").glob("*.html")]
    return {"reports": reports}

@app.get("/reports/{filename}")
def get_report(filename: str):
    """Return the content of a specific report as text."""
    report_path = DATA_DIR / "reports" / filename
    if not report_path.exists():
        return {"error": "Report not found"}
    return {"content": report_path.read_text(encoding="utf-8")}