#!/usr/bin/env python3
import argparse, json, os, datetime, html


def load_events(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def severity_tag(sev):
    return (
        ["info", "low", "medium", "high", "critical"][sev] if 0 <= sev < 5 else str(sev)
    )


def render_html(events, out_path):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for e in events:
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td><pre style='white-space:pre-wrap'>{}</pre></td></tr>".format(
                html.escape(e.get("ts", "")),
                html.escape(e.get("host", "")),
                html.escape(e.get("category", "")),
                html.escape(severity_tag(int(e.get("severity", 0)))),
                html.escape(e.get("summary", "")),
                html.escape(json.dumps(e.get("data", {}), indent=2)),
            )
        )
    table = "\n".join(rows)
    content = """<!doctype html>
<html><head><meta charset="utf-8"><title>SecureWatch Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{{font-family:system-ui, -apple-system, Segoe UI, Roboto, Arial; margin:20px;}}
h1{{margin:0 0 10px}}
small{{color:#555}}
table{{width:100%; border-collapse:collapse; margin-top:16px}}
th,td{{border:1px solid #ddd; padding:8px; vertical-align:top}}
th{{background:#f5f5f5; text-align:left}}
.tag{{display:inline-block; padding:2px 8px; border-radius:999px; background:#eee; font-size:12px}}
</style></head>
<body>
<h1>SecureWatch Report</h1>
<small>Generated at {now}</small>
<table>
<thead><tr><th>Timestamp</th><th>Host</th><th>Category</th><th>Severity</th><th>Summary</th><th>Data</th></tr></thead>
<tbody>
{table}
</tbody>
</table>
</body></html>""".format(
        now=now, table=table
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    events = load_events(args.input)
    out = args.out or "data/reports/report.html"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    render_html(events, out)
    print(f"Wrote HTML report to {out}")


if __name__ == "__main__":
    main()
