"""Resource ledger of the PET final-design study from `sacct` (run on a Perlmutter login node).

Every job whose name starts with `pfd-` submitted since the study began is listed with its QOS,
state, elapsed time, allocated GPUs and billing, and the charged hours derived from them:
GPU-hours = elapsed x allocated GPUs (A100); for CPU jobs, node-hours = elapsed x billing / 256
(a whole Perlmutter CPU node reports billing=256 in AllocTRES, measured on this study's debug jobs;
cross-checked against `iris` charged hours in the ledger record). Writes a TSV and a JSON summary. Steps are excluded
(`-X`); a job's own row is its allocation.

    ssh saul.nersc.gov python3.11 ledger_from_sacct.py --start 2026-09-25T21:00:00 --out ledger.tsv
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta

FIELDS = "JobID,JobName%40,QOS,Partition,State,Submit,Start,End,ElapsedRaw,AllocTRES%120,Account"


def windows(start: datetime, end: datetime, days: int = 10):
    t = start
    while t < end:
        u = min(t + timedelta(days=days), end)
        yield t, u
        t = u


def parse_tres(s: str) -> dict[str, float]:
    out = {}
    for part in s.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            m = re.match(r"([0-9.]+)([KMGT]?)", v)
            if m:
                out[k] = float(m.group(1))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", default=None)
    ap.add_argument("--prefix", default="pfd-")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    start = datetime.fromisoformat(a.start)
    end = datetime.fromisoformat(a.end) if a.end else datetime.now()
    rows = {}
    for s, e in windows(start, end):
        cmd = ["sacct", "-X", "-n", "-P", "-u", "josephrb", "-S", s.isoformat(timespec="seconds"),
               "-E", e.isoformat(timespec="seconds"), "-o", FIELDS]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise SystemExit(f"sacct failed ({res.returncode}): {res.stderr.strip()}")
        for line in res.stdout.splitlines():
            f = line.split("|")
            if len(f) < 11 or not f[1].startswith(a.prefix):
                continue
            rows[f[0]] = f
    out_rows = []
    tot = {"gpu_hours": 0.0, "cpu_node_hours": 0.0, "jobs": 0}
    for jid, f in sorted(rows.items()):
        tres = parse_tres(f[9])
        el = float(f[8] or 0) / 3600.0
        gpus = tres.get("gres/gpu", 0.0)
        billing = tres.get("billing", 0.0)
        gpu_h = el * gpus
        cpu_nh = el * billing / 256.0 if gpus == 0 else 0.0
        tot["gpu_hours"] += gpu_h
        tot["cpu_node_hours"] += cpu_nh
        tot["jobs"] += 1
        out_rows.append({"job": jid, "name": f[1], "qos": f[2], "partition": f[3], "state": f[4],
                         "submit": f[5], "start": f[6], "end": f[7], "elapsed_h": round(el, 4),
                         "gpus": gpus, "billing": billing, "gpu_hours": round(gpu_h, 4),
                         "cpu_node_hours": round(cpu_nh, 4), "account": f[10]})
    with open(a.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()) if out_rows else ["job"],
                           delimiter="\t")
        w.writeheader()
        w.writerows(out_rows)
    summary = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in tot.items()}
    summary.update({"start": a.start, "end": end.isoformat(timespec="seconds"),
                    "prefix": a.prefix})
    with open(a.out.rsplit(".", 1)[0] + ".summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
