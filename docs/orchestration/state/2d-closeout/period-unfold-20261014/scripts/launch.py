#!/usr/bin/env python3
"""Submit one batch of period-unfold jobs from jobs.tsv, behind a charge gate. Dry run unless --submit.

    python3 launch.py B0 [--submit]     # pu_CTRL_s42, pu_PA_s42, pu_PB_s42, pu_PC_s42
    python3 launch.py B1 [--submit]     # the 3 seed-43 runs and the 30 bootstrap replicas; needs control PASS

GATE (refusal = stop and report to the director):
  charge of every terminal pu_* job since 2026-10-14 from sacct (ElapsedRaw x billing / 256)
  + the FULL cap of every pu_* job still PENDING or RUNNING (billing x TimeLimit / 256)
  + the batch's caps (jobs.tsv enforced_nh)
  <= CEILING charged node-h. An unreadable sacct is a refusal, never zero.
Also refuses a job name that already has a sacct row or is in squeue (no double submission), and B1 unless
$NS/results/control.json says PASS (analyze_periods.py control). Needs Python >= 3.7.
"""
import csv
import json
import os
import subprocess
import sys

NS = "/pscratch/sd/j/josephrb/2d-closeout-period-unfold-20261014"
HERE = os.path.dirname(os.path.abspath(__file__))
TSV = os.path.join(HERE, "jobs.tsv")
SBATCH = os.path.join(HERE, "sbatch_period_unfold.sh")
CEILING = 6.0
SINCE = "2026-10-14"
BATCH = {"B0": lambda n: n in ("pu_CTRL_s42", "pu_PA_s42", "pu_PB_s42", "pu_PC_s42"),
         "B1": lambda n: n.endswith("_s43") or "_b" in n}


def hms(s):
    d, _, t = s.rpartition("-")
    h, m, x = (int(v) for v in t.split(":"))
    return (int(d) if d else 0) * 86400 + h * 3600 + m * 60 + x


def sacct_rows():
    r = subprocess.run(["sacct", "-X", "-n", "-P", "-u", os.environ.get("USER", "josephrb"), "-S", SINCE,
                        "-o", "JobID,JobName%60,State,ElapsedRaw,AllocTRES%120,TimelimitRaw"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"REFUSE: sacct failed rc={r.returncode}: {r.stderr.strip()}")
    rows = []
    for ln in r.stdout.splitlines():
        p = ln.split("|")
        if len(p) == 6 and p[1].startswith("pu_"):
            rows.append(dict(zip(("id", "name", "state", "elapsed", "tres", "limit_min"), p)))
    return rows


def billing(tres, fallback):
    for kv in tres.split(","):
        if kv.startswith("billing="):
            return int(kv.split("=")[1])
    return fallback


def main():
    batch, submit = sys.argv[1], "--submit" in sys.argv[2:]
    rows = list(csv.DictReader(open(TSV), delimiter="\t"))
    todo = [r for r in rows if BATCH[batch](r["name"])]
    if batch == "B1":
        cj = os.path.join(NS, "results", "control.json")
        if not os.path.isfile(cj) or json.load(open(cj)).get("verdict") != "PASS":
            sys.exit(f"REFUSE: {cj} is not PASS")
    acct = sacct_rows()
    q = subprocess.run(["squeue", "-h", "-u", os.environ.get("USER", "josephrb"), "-o", "%j"],
                       capture_output=True, text=True)
    if q.returncode != 0:
        sys.exit("REFUSE: squeue failed")
    queued = set(q.stdout.split())
    seen = {a["name"] for a in acct} | queued
    dup = [r["name"] for r in todo if r["name"] in seen]
    if dup:
        sys.exit(f"REFUSE: already submitted: {dup}")
    tsv_bill = {r["name"]: int(r["billing"]) for r in rows}
    charged = in_flight = 0.0
    for a in acct:
        b = billing(a["tres"], tsv_bill.get(a["name"], 256))
        if a["state"] in ("PENDING", "RUNNING", "REQUEUED", "SUSPENDED", "CONFIGURING", "COMPLETING"):
            in_flight += b * int(a["limit_min"]) * 60 / 256 / 3600
        else:
            charged += b * int(a["elapsed"] or 0) / 256 / 3600
    want = sum(float(r["enforced_nh"]) for r in todo)
    total = charged + in_flight + want
    print(f"[gate] charged {charged:.4f} + in-flight caps {in_flight:.4f} + batch {batch} caps {want:.4f} "
          f"= {total:.4f} node-h (ceiling {CEILING})")
    if total > CEILING:
        sys.exit("REFUSE: the gate exceeds the ceiling; stop and report to the director")
    for d in ("logs", "out", "results", "retries", "tmp"):
        os.makedirs(os.path.join(NS, d), exist_ok=True)
    for r in todo:
        cmd = ["sbatch", "--parsable", f"--job-name={r['name']}", f"--qos={r['qos']}",
               f"--cpus-per-task={r['cpus']}", f"--mem={r['mem']}", f"--time={r['time']}", SBATCH]
        if submit:
            s = subprocess.run(cmd, capture_output=True, text=True)
            print(r["name"], s.returncode, s.stdout.strip(), s.stderr.strip())
            if s.returncode != 0:
                sys.exit("STOP: sbatch failed")
        else:
            print("[dry-run]", " ".join(cmd))


if __name__ == "__main__":
    main()
