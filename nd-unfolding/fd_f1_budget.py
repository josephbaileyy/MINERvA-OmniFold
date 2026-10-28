#!/usr/bin/env python3
"""F1's budget gate (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION.md section 6): from the F1a
pilot's measured generation walls, project F1 and decide GO or STOP before F1b, by rule.

The pilot generates N_PILOT events per tune in one process on an otherwise idle node, spline load included. F1b runs
128 processes on the node's 128 cores, so its per-event time is taken CONTENTION times the pilot's (memory bandwidth
and clock, not measured by a two-process pilot). Charging the whole pilot wall to its events and once more per task
as the load:
  F1b wall  = CONTENTION x max over tunes of (wall x N_TASK / N_PILOT + wall)  +  FIXED_S   (hadd, conversion, prep)
  F1 total  = F1a node-h so far + F1b wall / 3600 (one node) + F1C_NODE_H
GO iff the F1b wall x 1.25 fits F1B_MAX_S and the F1 total is at most the priced 1.25 node-h; anything else is a
STOP for the director, never an overrun (the director's ruling, 2026-10-27).

The scheduler enforces the rest: F1b is submitted with --time = 1.25 x the projected wall rounded up to a minute
(f1b_time_limit), F1c with F1C_LIMIT; worst_case_node_h is F1a so far plus both limits, the most F1 can be charged.

MEASURES: a projection. CANNOT AUTHORIZE: anything beyond the declared stages.
"""
from __future__ import annotations

import argparse
import json
import sys

N_PILOT, N_TASK = 10_000, 17_500
CONTENTION = 1.25         # F1b's per-event time against the pilot's (declared, not measured)
FIXED_S = 900.0            # hadd, two conversions and the prep: the pv-ladder prep took 318 s (job 60201984)
F1B_MAX_S = 45 * 60        # F1b's largest allowed time limit
WALL_MARGIN = 1.25         # the stop rule's margin on a job's projected wall
F1C_NODE_H = 0.75          # F1c's priced upper end (FD-PLAN.md section 5.2, F1c 0.68-0.75)
F1C_LIMIT = "00:54:00"     # 1.25 x F1c's projected 2,550 s, rounded up to a minute
PRICED_NODE_H = 1.25       # the F1 total as priced (FD-PLAN.md section 5.2; the director's ruling)


def decide(walls: dict[str, float], f1a_node_h: float) -> dict:
    if not walls or any(w <= 0 for w in walls.values()):
        raise SystemExit("[FAIL] every tune needs a positive pilot wall")
    per_task = {k: CONTENTION * (w * N_TASK / N_PILOT + w) for k, w in walls.items()}
    f1b_s = max(per_task.values()) + FIXED_S
    total = f1a_node_h + f1b_s / 3600.0 + F1C_NODE_H
    fits = f1b_s * WALL_MARGIN <= F1B_MAX_S
    within = total <= PRICED_NODE_H
    limit_min = int(-(-(f1b_s * WALL_MARGIN) // 60))
    h, m = divmod(limit_min, 60)
    worst = f1a_node_h + limit_min / 60.0 + int(F1C_LIMIT[:2]) + int(F1C_LIMIT[3:5]) / 60.0
    return {"pilot_walls_s": walls, "per_event_upper_bound_s": {k: w / N_PILOT for k, w in walls.items()},
            "f1b_task_wall_s": per_task, "f1b_projected_wall_s": f1b_s, "f1b_fits_its_limit": fits,
            "contention": CONTENTION, "f1b_time_limit": f"{h:02d}:{m:02d}:00", "f1c_time_limit": F1C_LIMIT,
            "worst_case_node_h": worst,
            "f1a_node_h": f1a_node_h, "f1c_node_h_priced": F1C_NODE_H, "f1_projected_node_h": total,
            "within_priced": within, "decision": "GO" if fits and within else "STOP",
            "rule": "GO iff 1.25 x the projected F1b wall fits 45 min and F1a + F1b + F1c <= 1.25 node-h; F1b is "
                    "submitted with --time f1b_time_limit"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--wall", action="append", required=True, metavar="TUNE=SECONDS")
    ap.add_argument("--f1a-node-h", type=float, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    walls = {k: float(v) for k, v in (x.split("=", 1) for x in a.wall)}
    d = decide(walls, a.f1a_node_h)
    with open(a.out, "x") as f:
        json.dump(d, f, indent=1)
    print(json.dumps({k: d[k] for k in ("f1b_projected_wall_s", "f1_projected_node_h", "decision")}))
    return 0 if d["decision"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
