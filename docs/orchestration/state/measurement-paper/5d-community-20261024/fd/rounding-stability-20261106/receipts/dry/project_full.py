#!/usr/bin/env python3
"""RS1's full-run projection from the dry run's own records (RS1-DECLARATION.md §7 item 2).

Reads the dry run's queue.tsv and dry.tsv, the nine log-dry/<id>.start/.end records and the dry job's sacct line;
writes nothing. Per-unfold time per arm = that arm's dry task wall (a one-unfold task, so it includes one input
load: conservative for tasks of 4). An arm the dry run did not measure takes the largest measured time of its family
(S_omni: the S arms; P2: P1) or, failing that, the largest measured time overall (the F axis arms). The remaining
tasks are packed in queue order onto 8 lanes, each task going to the lane that frees first (xargs -P 8), plus 120 s
of job setup.

    python3 project_full.py <receipt dir with queue.tsv, dry.tsv, log-dry/, sacct-60970044.txt>
"""
import json
import sys
from pathlib import Path

LANES, SETUP_S, CAP, LIMIT_H = 8, 120.0, 8.0, 7.25

d = Path(sys.argv[1])
tasks = [l.split("\t") for l in (d / "queue.tsv").read_text().splitlines() if l and not l.startswith("#")]
dry = {l.split("\t")[0] for l in (d / "dry.tsv").read_text().splitlines() if l and not l.startswith("#")}
wall = {i: float((d / "log-dry" / f"{i}.end").read_text()) - float((d / "log-dry" / f"{i}.start").read_text())
        for i in dry}
arm_of = lambda tid: tid[len("rs1_"):].rsplit("_", 1)[0]  # noqa: E731
per = {}
for i, w in wall.items():
    per[arm_of(i)] = max(per.get(arm_of(i), 0.0), w)
family = {"S_omni": ("S_ref", "S_all"), "P2": ("P1",)}
overall = max(per.values())
used = {}
for t in tasks:
    a = arm_of(t[0])
    if a in per:
        used[a] = (per[a], "measured")
    elif a in family and any(f in per for f in family[a]):
        used[a] = (max(per[f] for f in family[a] if f in per), "family max " + "/".join(family[a]))
    else:
        used[a] = (overall, "overall max")
rest = [(t[0], int(t[1]), arm_of(t[0])) for t in tasks if t[0] not in dry]
lanes = [0.0] * LANES
for tid, n, a in rest:
    k = lanes.index(min(lanes))
    lanes[k] += n * used[a][0]
wall_h = (max(lanes) + SETUP_S) / 3600
row = (d / "sacct-60970044.txt").read_text().splitlines()[0].split("|")
charge = int(row[5]) * int(row[6]) / 3600
limit = min(LIMIT_H, 0.9 * (CAP - charge))
print(json.dumps({"dry_tasks": len(dry), "dry_task_wall_s": {k: round(v, 1) for k, v in sorted(wall.items())},
                  "per_unfold_s_used": {a: [round(v, 1), why] for a, (v, why) in sorted(used.items())},
                  "remaining_tasks": len(rest), "remaining_unfolds": sum(n for _, n, _ in rest),
                  "lane_loads_h": [round(x / 3600, 3) for x in lanes], "projected_full_wall_h": round(wall_h, 3),
                  "dry_charge_node_h": round(charge, 4), "limit_h": round(limit, 3),
                  "full_run_may_start": wall_h <= limit}, indent=1))
