#!/usr/bin/env python3
"""Per-job resource rows for every confirmatory-stage (`pv1-*`) job that ran, from `sacct`.

`resources-V1.tsv` was written by hand and stops at the infrastructure jobs of 2026-09-23; the
PILOT/FINAL/STRESS jobs were never added. This rebuilds them from the scheduler's own record:

    ssh perlmutter.nersc.gov 'sacct -u josephrb -S 2026-09-23T00:00 -X -n -P \
        -o JobID,JobName,Account,Partition,QOS,NNodes,AllocTRES,ElapsedRaw,State,Start' \
        | python3 ledger_from_sacct.py > resources-V1-sacct.tsv

Charges: gpu_hours = ElapsedRaw x gres/gpu / 3600; cpu_core_hours = ElapsedRaw x cpu / 3600
(the convention of `resources-V1.tsv`). Only jobs in a terminal state with ElapsedRaw > 0 are
written (a job cancelled while pending charged nothing; a running job's charge is not final).
Job ids already recorded in another `resources-*.tsv` are skipped, so `aggregate_resources.py`
never sees one job twice. `-S` in `sacct` is Perlmutter local time (America/Los_Angeles); `Start`
is converted to UTC here.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
COLUMNS = ["date_utc", "phase", "slurm_job", "account", "partition_qos", "nodes", "gpus",
           "elapsed_s", "gpu_hours", "cpu_core_hours", "state", "purpose"]
PURPOSE = {
    "pv1-chain": "confirmatory run chain (PILOT/FINAL/STRESS; stage per job in <stage>/submissions.txt)",
    "pv1-single": "confirmatory single-run copy (gpu_shared race copy of a chain row)",
    "pv1-inputs": "confirmatory inputs check",
    "pv1-targets": "population targets + tests",
    "pv1-locktest": "flock run-lock test",
    "pv1-pytest": "confirmatory tests",
    "pv1-cpucheck": "CPU check of the confirmatory input path",
}
TERMINAL = ("COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY", "NODE_FAIL", "PREEMPTED")
LOCAL = ZoneInfo("America/Los_Angeles")


def recorded_elsewhere() -> set[str]:
    out: set[str] = set()
    for path in CAMPAIGN.rglob("resources-*.tsv"):
        if path.name == "resources-V1-sacct.tsv":
            continue
        with path.open(newline="") as fh:
            out |= {row["slurm_job"] for row in csv.DictReader(fh, delimiter="\t")}
    return out


def tres(field: str) -> dict[str, str]:
    return dict(kv.split("=", 1) for kv in field.split(",") if "=" in kv)


def main() -> None:
    skip = recorded_elsewhere()
    rows = []
    for line in sys.stdin:
        parts = line.rstrip("\n").split("|")
        if len(parts) != 10:
            continue
        jid, name, account, partition, qos, nodes, alloc, elapsed, state, start = parts
        if not name.startswith("pv1-") or jid in skip:
            continue
        if not state.startswith(TERMINAL) or int(elapsed or 0) <= 0:
            continue
        t = tres(alloc)
        gpus, cpus, sec = int(t.get("gres/gpu", 0)), int(t.get("cpu", 0)), int(elapsed)
        when = datetime.fromisoformat(start).replace(tzinfo=LOCAL).astimezone(ZoneInfo("UTC"))
        rows.append({"date_utc": when.strftime("%Y-%m-%dT%H:%M:%SZ"), "phase": "V1", "slurm_job": jid,
                     "account": account, "partition_qos": f"{partition}/{qos}", "nodes": nodes,
                     "gpus": str(gpus), "elapsed_s": str(sec), "gpu_hours": f"{sec * gpus / 3600:.3f}",
                     "cpu_core_hours": f"{sec * cpus / 3600:.3f}", "state": state.split()[0],
                     "purpose": PURPOSE.get(name, name)})
    rows.sort(key=lambda r: (r["date_utc"], r["slurm_job"]))
    w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, delimiter="\t", lineterminator="\n")
    w.writeheader()
    w.writerows(rows)


if __name__ == "__main__":
    main()
