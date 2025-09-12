#!/usr/bin/env python3
import argparse, json, os, re, datetime, socket

AUTH_LOGS = ["/var/log/auth.log", "/var/log/secure"]  # debian/ubuntu, rhel-like


def find_auth_log():
    for p in AUTH_LOGS:
        if os.path.exists(p):
            return p
    return None


def parse_failed_ssh(log_path, threshold):
    ip_counts = {}
    pat = re.compile(r"Failed password .* from ([0-9]{1,3}(?:\.[0-9]{1,3}){3})")
    with open(log_path, "r", errors="ignore") as f:
        for line in f:
            m = pat.search(line)
            if m:
                ip = m.group(1)
                ip_counts[ip] = ip_counts.get(ip, 0) + 1
    events = []
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    host = socket.gethostname()
    for ip, count in ip_counts.items():
        if count >= threshold:
            events.append(
                {
                    "ts": ts,
                    "host": host,
                    "category": "auth",
                    "severity": 2,
                    "summary": f"SSH failed logins from {ip}: {count}",
                    "data": {"ip": ip, "count": count},
                }
            )
    return events


def parse_sudo_anomalies(log_path):
    events = []
    pat = re.compile(r"sudo: .*authentication failure")
    with open(log_path, "r", errors="ignore") as f:
        count = sum(1 for line in f if pat.search(line))
    if count:
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        host = socket.gethostname()
        events.append(
            {
                "ts": ts,
                "host": host,
                "category": "auth",
                "severity": 2 if count >= 3 else 1,
                "summary": f"Sudo authentication failures: {count}",
                "data": {"count": count},
            }
        )
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--threshold", type=int, default=5, help="SSH failed login threshold"
    )
    ap.add_argument("--out", required=True, help="Output NDJSON path")
    args = ap.parse_args()

    log_path = find_auth_log()
    if not log_path:
        return

    events = []
    events += parse_failed_ssh(log_path, args.threshold)
    events += parse_sudo_anomalies(log_path)

    if events:
        with open(args.out, "w") as f:
            for e in events:
                f.write(json.dumps(e) + "\n")


if __name__ == "__main__":
    main()
