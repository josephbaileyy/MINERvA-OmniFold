#!/usr/bin/env python3
"""F1's second budget gate (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md section 3):
from the F1a' re-pilot, run at F1b''s own concurrency, decide GO or STOP before F1b', by rule.

F1b ran 128 gevgen processes at once and ran out of memory (job 60417614): the first gate (fd_f1_budget.py) had a
two-process pilot, a declared contention factor and no per-process memory. The re-pilot measures both at the
production concurrency P:
  per tune, N_LONG processes generate N2 events, and N_SHORT processes generate N1 events twice in a row, so all P run
  together for the whole pilot; each run is timed by /usr/bin/time -v (elapsed wall and maximum resident set size).
  per-event time  t    = (max long wall - max short wall) / (N2 - N1)         (the contended time, measured)
  load            L    = max short wall - N1 t                                (spline load and set-up, measured)
  task wall            = L + N_TASK t                                         (one F1b' task, N_TASK events)
  F1b' wall            = WAVES x max over tunes of the task wall + FIXED_S    (hadd, conversion, prep)
  RSS per process      = max long RSS + max(0, slope) x (N_TASK - N2),  slope = (max long RSS - max short RSS) / (N2 - N1)
  F1b' memory          = P x max over tunes of the RSS per process
GO iff
  * t > 0 and L >= 0 (a pilot that cannot be fitted is a STOP),
  * F1b' memory <= MEM_FRACTION of the node's allocation,
  * 1.25 x the F1b' wall <= F1B_MAX_S, and
  * spent + re-pilot + F1b' wall + F1c's priced 0.75 node-h <= the priced total the binding sets, and
  * worst_case_node_h (below) <= the ceiling the binding sets (Joseph's 2.5 node-h in total).
On GO it writes F1b''s time limit (1.25 x the projected wall, rounded up to a minute) and worst_case_node_h (spent +
re-pilot + F1b''s limit + F1c's 0:54), the most F1 can be charged. Anything else is a STOP for the director.

MEASURES: a projection from measured runs. CANNOT AUTHORIZE: anything beyond the declared stages.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

TUNES = ("G18_10a_02_11b", "AR23_20i_00_000")
P = 64                      # F1b''s concurrency, and the re-pilot's
N_LONG, N_SHORT = 16, 16    # per tune: long processes, and short processes that each run twice
N1, N2 = 1_500, 3_000       # events per short run and per long run
N_TASK = 17_500             # events per F1b' task (unchanged)
N_TASKS = 128               # F1b' tasks (unchanged)
WAVES = math.ceil(N_TASKS / P)
FIXED_S = 900.0             # hadd, two conversions and the prep (as the first gate)
F1B_MAX_S = 45 * 60
WALL_MARGIN = 1.25
NODE_MEM_KIB = 487_802 * 1024   # the exclusive CPU node's allocation (sacct AllocTRES mem=487802M)
MEM_FRACTION = 0.75
F1C_NODE_H = 0.75
F1C_LIMIT_H = 54 / 60
SEED_BASE = {"G18_10a_02_11b": 60100, "AR23_20i_00_000": 61100}   # re-pilot seeds base+1 .. base+48 per tune

_ELAPSED = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\S+)")
_RSS = re.compile(r"Maximum resident set size \(kbytes\): (\d+)")
_EXIT = re.compile(r"Exit status: (\d+)")


def wall_seconds(text: str) -> float:
    parts = [float(x) for x in text.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(f"unparseable elapsed time {text!r}")


def parse_time_v(text: str) -> dict:
    """GNU time -v's elapsed wall (s), maximum RSS (KiB) and exit status."""
    e, r, x = _ELAPSED.search(text), _RSS.search(text), _EXIT.search(text)
    if not (e and r and x):
        raise ValueError("not a complete /usr/bin/time -v record")
    return {"elapsed_s": wall_seconds(e.group(1)), "maxrss_kib": int(r.group(1)), "exit": int(x.group(1))}


def seeds(tune: str) -> dict[str, list[int]]:
    """The declared re-pilot seeds: long runs first, then the two runs of each short process."""
    b = SEED_BASE[tune]
    longs = list(range(b + 1, b + 1 + N_LONG))
    shorts = list(range(b + 1 + N_LONG, b + 1 + N_LONG + 2 * N_SHORT))
    return {"long": longs, "short": shorts}


def load_runs(root: Path) -> dict:
    """<root>/<tune>/{long,short}_s<seed>.time, exactly the declared seeds, every run exit 0."""
    out = {}
    for tune in TUNES:
        out[tune] = {}
        for role, want in seeds(tune).items():
            recs = []
            for s in want:
                p = root / tune / f"{role}_s{s}.time"
                if not p.is_file():
                    raise SystemExit(f"[FAIL] missing {p}")
                r = parse_time_v(p.read_text())
                if r["exit"] != 0:
                    raise SystemExit(f"[FAIL] {p}: exit {r['exit']}")
                recs.append(r)
            out[tune][role] = recs
        extra = sorted(str(p) for p in (root / tune).glob("*.time")
                       if p.name not in {f"{r}_s{s}.time" for r, w in seeds(tune).items() for s in w})
        if extra:
            raise SystemExit(f"[FAIL] undeclared runs {extra[:3]}")
    return out


def fit(runs: dict) -> dict:
    """Per tune: the contended per-event time, the load, the task wall and the per-process RSS at N_TASK events."""
    out = {}
    for tune, r in runs.items():
        long_w = max(x["elapsed_s"] for x in r["long"])
        short_w = max(x["elapsed_s"] for x in r["short"])
        long_m = max(x["maxrss_kib"] for x in r["long"])
        short_m = max(x["maxrss_kib"] for x in r["short"])
        t = (long_w - short_w) / (N2 - N1)
        load = short_w - N1 * t
        slope = (long_m - short_m) / (N2 - N1)
        out[tune] = {"long_wall_s": long_w, "short_wall_s": short_w, "per_event_s": t, "load_s": load,
                     "task_wall_s": load + N_TASK * t, "long_rss_kib": long_m, "short_rss_kib": short_m,
                     "rss_slope_kib_per_event": slope, "rss_at_task_kib": long_m + max(0.0, slope) * (N_TASK - N2),
                     "fit_ok": bool(t > 0 and load >= 0)}
    return out


def decide(runs: dict, spent_node_h: float, pilot_node_h: float, priced_node_h: float,
           ceiling_node_h: float = float("inf")) -> dict:
    f = fit(runs)
    fit_ok = all(v["fit_ok"] for v in f.values())
    wall = WAVES * max(v["task_wall_s"] for v in f.values()) + FIXED_S
    mem = P * max(v["rss_at_task_kib"] for v in f.values())
    mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB
    fits = wall * WALL_MARGIN <= F1B_MAX_S
    total = spent_node_h + pilot_node_h + wall / 3600.0 + F1C_NODE_H
    within = total <= priced_node_h
    limit_min = int(-(-(wall * WALL_MARGIN) // 60))
    h, m = divmod(limit_min, 60)
    worst = spent_node_h + pilot_node_h + limit_min / 60.0 + F1C_LIMIT_H
    capped = worst <= ceiling_node_h
    go = fit_ok and mem_ok and fits and within and capped
    return {"fit": f, "concurrency": P, "waves": WAVES, "f1b2_projected_wall_s": wall, "f1b2_fits_its_limit": fits,
            "f1b2_projected_mem_kib": mem, "node_mem_kib": NODE_MEM_KIB, "mem_fraction_limit": MEM_FRACTION,
            "mem_ok": mem_ok, "fit_ok": fit_ok, "spent_node_h": spent_node_h, "repilot_node_h": pilot_node_h,
            "f1c_node_h_priced": F1C_NODE_H, "f1_projected_node_h": total, "priced_node_h": priced_node_h,
            "within_priced": within, "f1b2_time_limit": f"{h:02d}:{m:02d}:00",
            "worst_case_node_h": worst, "ceiling_node_h": ceiling_node_h, "within_ceiling": capped,
            "decision": "GO" if go else "STOP",
            "rule": "GO iff the fit is physical, P x the per-process RSS at 17,500 events <= 75 % of the node, 1.25 x "
                    "the F1b' wall <= 45 min, spent + re-pilot + F1b' + 0.75 <= the priced total, and the worst case <= the "
                    "ceiling"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True, help="the re-pilot's time records")
    ap.add_argument("--spent-node-h", type=float, required=True, help="F1 charged before the re-pilot (the ledger)")
    ap.add_argument("--repilot-node-h", type=float, required=True)
    ap.add_argument("--priced-node-h", type=float, required=True, help="the priced F1 total the binding sets")
    ap.add_argument("--ceiling-node-h", type=float, required=True, help="the F1 ceiling the binding sets")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    d = decide(load_runs(a.runs), a.spent_node_h, a.repilot_node_h, a.priced_node_h, a.ceiling_node_h)
    with open(a.out, "x") as f:
        json.dump(d, f, indent=1)
    print(json.dumps({k: d[k] for k in ("f1b2_projected_wall_s", "f1b2_projected_mem_kib", "f1_projected_node_h",
                                         "decision")}))
    return 0 if d["decision"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
