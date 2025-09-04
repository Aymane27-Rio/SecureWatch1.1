#!/usr/bin/env python3
import boto3, json, socket, datetime

SENSITIVE_PORTS = {22, 3389}


def audit_security_groups():
    ec2 = boto3.client("ec2")
    resp = ec2.describe_security_groups()
    findings = []
    host = socket.gethostname()
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for sg in resp.get("SecurityGroups", []):
        sgid = sg.get("GroupId")
        name = sg.get("GroupName")
        for perm in sg.get("IpPermissions", []):
            fromp = perm.get("FromPort")
            top = perm.get("ToPort")
            if fromp is None or top is None:
                continue
            ports = set(range(fromp, top + 1))
            if not (ports & SENSITIVE_PORTS):
                continue
            for rng in perm.get("IpRanges", []):
                cidr = rng.get("CidrIp")
                if cidr == "0.0.0.0/0":
                    findings.append(
                        {
                            "ts": ts,
                            "host": host,
                            "category": "cloud",
                            "severity": 3,
                            "summary": f"Overly permissive SG {name} {sgid} on ports {sorted(list(ports & SENSITIVE_PORTS))}",
                            "data": {
                                "sg": sgid,
                                "name": name,
                                "cidr": cidr,
                                "ports": sorted(list(ports)),
                            },
                        }
                    )
    return findings


if __name__ == "__main__":
    try:
        print(json.dumps(audit_security_groups(), indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
