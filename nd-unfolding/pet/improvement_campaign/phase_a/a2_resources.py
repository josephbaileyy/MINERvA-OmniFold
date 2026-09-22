#!/usr/bin/env python3
"""Phase A2, Part 4: parse the raw resource captures into `receipts/resources.json`.

The raw captures are made on a Perlmutter login node by the commands recorded at the top of each
file (`iris`, `iris project m3246`, `myquota`, `showquota`, `cfsquota m3246`, `sshare`, `sacctmgr`,
`squeue`, `sacct`). This script only parses them; it queries nothing. Light enough for a laptop.

Historical GPU-hours are DEVICE hours, sum over allocations of (gres/gpu count x ElapsedRaw), from
`sacct -X` over user josephrb 2026-09-15 .. 2026-09-22, attributed by job name and working
directory. They are cross-checked against the per-run receipts' own `seconds`.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

# Attribution of pet-* jobs in the window. The comparison's own launchers named these directories.
CAMPAIGN_ARRAYS = {"58627088": "tuning", "58692542": "pilot", "58692544": "final"}
COMPARISON_PREP_NAMES = {
    "pet-campaign-smoke", "pet-diagnose-theirs", "pet-batch-variance", "pet-matched-timing",
    "pet-cost-calibration", "pet-port-profile", "pet-port-80g", "pet-validate-80g",
    "pet-40g-confirm", "pet-prod-validate", "pet-tf32off-timing", "pet-fp32-timing",
    "pet-region-census", "pet-eavail-characterization", "pet-knn-census",
    "pet-tail-validation", "pet-four-arm-probe", "pet-width-gate", "pet-source-characterization",
    "pet-inference-benchmark"}
CAMPAIGN_CPU_NAMES = {"pet-build-inputs", "pet-r4-extract", "pet-join-launch",
                      "pet-prematerialize", "pet-select-lr", "pet-report-deck"}
EARLIER_PET_LANE_NAMES = {"pet-routing-matrix", "pet-matrix-closeout", "pet-amended-calibration"}


def gpus(tres: str) -> int:
    m = re.search(r"gres/gpu=(\d+)", tres)
    return int(m.group(1)) if m else 0


def parse_table(text: str, first_col: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if parts and parts[0] == first_col:
            rows.append(parts)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt-hours", type=json.loads, default=None,
                    help='per-stage sum of receipt "seconds"/3600, e.g. {"tuning": 12.464}')
    args = ap.parse_args()
    raw = args.raw
    out: dict[str, Any] = {"scope": "Phase A2 Part 4: resources", "raw_dir": str(raw)}

    # ---- allocations
    iris = (raw / "iris_project_m3246.txt").read_text()
    alloc = {}
    for name in ("m3246_g", "m3246"):
        row = next(r for r in parse_table(iris, name))
        charged, allocated = float(row[1]), float(row[2])
        alloc[name] = {"charged": charged, "allocated": allocated,
                       "remaining": allocated - charged,
                       "fraction_used": charged / allocated}
    user = (raw / "iris_user.txt").read_text()
    for name in ("m3246_g", "m3246"):
        row = next(r for r in parse_table(user, name))
        alloc[name]["user_josephrb_charged"] = float(row[1])
        alloc[name]["user_josephrb_allocated"] = float(row[2])
    out["allocation"] = {
        "command": "iris project m3246 ; iris (user view)",
        "captured": re.search(r"date_utc: (\S+)", iris).group(1),
        "units": ("NERSC allocation hours as iris reports them (GPU node-hours for m3246_g, CPU "
                  "node-hours for m3246) -- the unit label is INFERRED from NERSC's charging "
                  "policy, iris prints no unit"),
        "projects": alloc}

    # ---- storage
    my = (raw / "myquota.txt").read_text()
    storage = {}
    for fs in ("home", "pscratch"):
        row = next(r for r in parse_table(my, fs))
        storage[fs] = {"used": row[1], "quota": row[2], "percent": row[3],
                       "inodes_used": row[4], "inode_quota": row[5]}
    cfs = (raw / "cfsquota_m3246.txt").read_text()
    row = next(r for r in parse_table(cfs, "m3246"))
    storage["cfs_m3246"] = {"used_gb": float(row[1]), "quota_gb": float(row[2]),
                            "percent": float(row[3]), "inodes_used": int(row[4]),
                            "inode_quota": int(row[5]),
                            "remaining_gb": float(row[2]) - float(row[1])}
    out["storage"] = {"commands": ["myquota", "showquota", "cfsquota m3246", "prjquota m3246"],
                      "filesystems": storage}

    # ---- queue
    q = (raw / "queue_depth.txt").read_text()
    depth = {}
    for m in re.finditer(r"^(\S+) (PENDING|RUNNING) jobs=(\d+)$", q, re.M):
        depth.setdefault(m.group(1), {})[m.group(2)] = int(m.group(3))
    out["queue_depth"] = {"command": "squeue -h -q <qos> -t <state> | wc -l",
                          "captured": re.search(r"date_utc: (\S+)", q).group(1),
                          "by_qos": depth,
                          "gpu_shared_pending_reasons_raw": q.split("pending by reason")[1]
                          .split("#")[0].strip().splitlines()}

    # ---- start latency (own gpu_shared jobs; first task of each array)
    fmt = "%Y-%m-%dT%H:%M:%S"
    lat_all, lat_first = [], defaultdict(list)
    for line in (raw / "start_latency_gpu_shared_josephrb.psv").read_text().splitlines():
        jid, name, qos, sub, start, state = line.split("|")
        try:
            d = (datetime.strptime(start, fmt) - datetime.strptime(sub, fmt)).total_seconds() / 3600
        except ValueError:
            continue
        lat_all.append(d)
        lat_first[jid.split("_")[0]].append(d)
    firsts = [min(v) for v in lat_first.values()]

    def summ(v: list[float]) -> dict[str, float]:
        v = sorted(v)
        return {"n": len(v), "median_h": statistics.median(v),
                "p90_h": v[int(0.9 * (len(v) - 1))], "max_h": v[-1]}
    out["start_latency_gpu_shared"] = {
        "source": ("sacct -u josephrb -X -S 2026-09-15 (states CD,F,TO,CA,R), QOS gpu_shared, "
                   "Start - Submit"),
        "first_task_per_job_or_array": summ(firsts),
        "every_task": summ(lat_all),
        "caveat": ("array tasks share one submit time and start as earlier tasks finish, so "
                   "'every_task' measures array throughput as much as queue wait; the first task "
                   "is the queue-wait measure, but for a job submitted with --dependency it also "
                   "includes the time waiting on the dependency, so it is an upper bound. Own jobs "
                   "only: other users' submit times are not visible to this account")}

    # ---- historical GPU-hours
    rows = list(csv.DictReader((raw / "sacct_josephrb_20260915_20260922.psv").open(),
                               delimiter="|"))
    groups: dict[str, dict[str, Any]] = defaultdict(lambda: {"allocations": 0, "gpu_hours": 0.0,
                                                             "cpu_core_hours": 0.0, "jobs": set(),
                                                             "states": defaultdict(int)})
    per_stage = defaultdict(float)
    for r in rows:
        name = r["JobName"]
        if not name.startswith("pet-"):
            continue
        array = r["JobID"].split("_")[0]
        if name == "pet-campaign" and array in CAMPAIGN_ARRAYS:
            g = "campaign_gpu_arrays_executed"
        elif name == "pet-campaign":
            g = "campaign_gpu_superseded_submissions"
        elif name in COMPARISON_PREP_NAMES:
            g = "comparison_prep_and_validation"
        elif name in CAMPAIGN_CPU_NAMES:
            g = "campaign_cpu_helpers_and_extraction"
        elif name in EARLIER_PET_LANE_NAMES:
            g = "earlier_pet_lane_2026-09-15_16_not_comparison"
        else:
            g = "unattributed_pet"
        e = int(r["ElapsedRaw"] or 0)
        gh = gpus(r["AllocTRES"]) * e / 3600
        ch = int(r["NCPUS"] or 0) * e / 3600
        G = groups[g]
        G["allocations"] += 1
        G["gpu_hours"] += gh
        G["cpu_core_hours"] += ch
        G["jobs"].add(array)
        G["states"][r["State"].split()[0]] += 1
        if g == "campaign_gpu_arrays_executed":
            per_stage[CAMPAIGN_ARRAYS[array]] += gh
    hist = {k: {**v, "jobs": sorted(v["jobs"]), "states": dict(v["states"])}
            for k, v in groups.items()}
    comparison_total = sum(hist[k]["gpu_hours"] for k in hist
                           if k in ("campaign_gpu_arrays_executed",
                                    "campaign_gpu_superseded_submissions",
                                    "comparison_prep_and_validation"))
    out["historical_comparison_gpu_hours"] = {
        "method": ("sacct -u josephrb -X -S 2026-09-15T00:00:00 -E 2026-09-22T23:59:59 "
                   "--format=...ElapsedRaw,AllocTRES,WorkDir; GPU-h = gres/gpu x ElapsedRaw; "
                   "attribution by job name / array id / working directory"),
        "groups": hist,
        "campaign_arrays_by_stage_gpu_hours": dict(per_stage),
        "campaign_arrays_total_gpu_hours": sum(per_stage.values()),
        "comparison_total_gpu_hours_including_prep": comparison_total,
        "receipt_cross_check_hours": args.receipt_hours,
        "projections_in_the_comparison_docs_were_not_consumption": {
            "HANDOFF-20260920-complete-comparison.md": "540 GPU-h (projection, superseded)",
            "CAMPAIGN_COST_STEP_SCOPED-20260920.json": "365.8 GPU-h (projection, superseded)",
            "CAMPAIGN_RUNNING-20260920.md": "58.5 GPU-h, 73.1 with retries (projection)"},
        "nersc_charge_note": ("a gpu_shared allocation of 1 GPU is charged as a quarter GPU node; "
                              "device hours / 4 approximates GPU node-hours charged (INFERRED "
                              "from NERSC policy, not read from iris per job)"),
    }
    args.output.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("allocation",)}, indent=1))
    print(json.dumps(out["historical_comparison_gpu_hours"]["campaign_arrays_by_stage_gpu_hours"]))
    print(out["historical_comparison_gpu_hours"]["comparison_total_gpu_hours_including_prep"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
