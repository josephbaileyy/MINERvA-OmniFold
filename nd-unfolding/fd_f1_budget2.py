#!/usr/bin/env python3
"""F1's second budget gate (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-1.md section 3):
from the F1a' re-pilot, run at F1b''s own concurrency with full-size tasks, decide GO or STOP before F1b', by rule.

F1b ran 128 gevgen processes at once and ran out of memory in gevgen's start-up (job 60417614), before any of the
killed processes had built its flux driver. F1a's batch step had recorded MaxRSS 45,610,936 K for two concurrent GENIE
processes, about 22 GiB each, and nothing read it. The re-pilot therefore runs at the production concurrency P and
measures, per process, with /usr/bin/time -v:
  per tune, N_LONG processes run one full F1b' task (N_TASK events) and N_SHORT processes run N1 events twice in a
  row, so all P run together for about the length of one task.
  F1b' wall      = WAVES x (max long wall over both tunes) + FIXED_S     (the long runs ARE F1b' tasks at P-way load)
  F1b' memory    = P x (max RSS over every run)                          (the start-up peak and the full-task peak)
  per-event time and load (descriptive only): t = (long wall - short wall) / (N_TASK - N1), L = short wall - N1 t
GO iff
  * every run exited 0,
  * F1b' memory <= MEM_FRACTION of the node's allocation,
  * 1.25 x the F1b' wall <= F1B_MAX_S,
  * spent + re-pilot + F1b' wall + F1c's priced 0.75 node-h <= the priced total the binding sets, and
  * worst_case_node_h (spent + re-pilot + F1b''s limit + F1c's 0:54) <= the ceiling the binding sets.
On GO it writes F1b''s time limit (1.25 x the projected wall, rounded up to a minute). Anything else is a STOP for
the director. submit_fd_f1.sh f1b2 also refuses unless sacct's MaxRSS for the re-pilot's batch step, the node-level
peak, is within MEM_FRACTION of the node.

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
P = 16                      # F1b''s concurrency, and the re-pilot's: 16 x ~22 GiB start-up peak (F1a) is ~74 % of the node
N_LONG, N_SHORT = 4, 4      # per tune: full-task processes, and short processes that each run twice
N1 = 1_000                  # events per short run
N_TASK = 17_500             # events per F1b' task (unchanged), and per long re-pilot run
N_TASKS = 128               # F1b' tasks (unchanged)
WAVES = math.ceil(N_TASKS / P)
FIXED_S = 900.0             # hadd, two conversions and the prep (as the first gate)
F1B_MAX_S = 55 * 60         # F1b''s largest allowed limit: 0.3075 + 0.33 + 0.917 + 0.9 = 2.45 <= Joseph's 2.5
WALL_MARGIN = 1.25
NODE_MEM_KIB = 487_802 * 1024   # the exclusive CPU node's allocation (sacct AllocTRES mem=487802M)
MEM_FRACTION = 0.75
F1C_NODE_H = 0.75
F1C_LIMIT_H = 54 / 60
SEED_BASE = {"G18_10a_02_11b": 60100, "AR23_20i_00_000": 61100}   # re-pilot seeds base+1 .. base+12 per tune

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
    """GNU time -v's elapsed wall (s), maximum RSS (KiB: the largest single process of the waited tree) and exit."""
    e, r, x = _ELAPSED.search(text), _RSS.search(text), _EXIT.search(text)
    if not (e and r and x):
        raise ValueError("not a complete /usr/bin/time -v record")
    return {"elapsed_s": wall_seconds(e.group(1)), "maxrss_kib": int(r.group(1)), "exit": int(x.group(1))}


def seeds(tune: str) -> dict[str, list[int]]:
    """The declared re-pilot seeds: the long runs first, then the two runs of each short process."""
    b = SEED_BASE[tune]
    return {"long": list(range(b + 1, b + 1 + N_LONG)),
            "short": list(range(b + 1 + N_LONG, b + 1 + N_LONG + 2 * N_SHORT))}


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
        declared = {f"{r}_s{s}.time" for r, w in seeds(tune).items() for s in w}
        extra = sorted(str(p) for p in (root / tune).glob("*.time") if p.name not in declared)
        if extra:
            raise SystemExit(f"[FAIL] undeclared runs {extra[:3]}")
    return out


def summary(runs: dict) -> dict:
    out = {}
    for tune, r in runs.items():
        lw = max(x["elapsed_s"] for x in r["long"])
        sw = max(x["elapsed_s"] for x in r["short"])
        t = (lw - sw) / (N_TASK - N1)
        out[tune] = {"long_wall_s": lw, "short_wall_s": sw,
                     "max_rss_kib": max(x["maxrss_kib"] for x in r["long"] + r["short"]),
                     "long_rss_kib": max(x["maxrss_kib"] for x in r["long"]),
                     "short_rss_kib": max(x["maxrss_kib"] for x in r["short"]),
                     "per_event_s_descriptive": t, "load_s_descriptive": sw - N1 * t}
    return out


def decide(runs: dict, spent_node_h: float, pilot_node_h: float, priced_node_h: float, ceiling_node_h: float) -> dict:
    s = summary(runs)
    wall = WAVES * max(v["long_wall_s"] for v in s.values()) + FIXED_S
    mem = P * max(v["max_rss_kib"] for v in s.values())
    mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB
    fits = wall * WALL_MARGIN <= F1B_MAX_S
    total = spent_node_h + pilot_node_h + wall / 3600.0 + F1C_NODE_H
    within = total <= priced_node_h
    limit_min = int(-(-(wall * WALL_MARGIN) // 60))
    h, m = divmod(limit_min, 60)
    worst = spent_node_h + pilot_node_h + limit_min / 60.0 + F1C_LIMIT_H
    capped = worst <= ceiling_node_h
    go = mem_ok and fits and within and capped
    return {"runs": s, "concurrency": P, "waves": WAVES, "f1b2_projected_wall_s": wall, "f1b2_fits_its_limit": fits,
            "f1b2_projected_mem_kib": mem, "node_mem_kib": NODE_MEM_KIB, "mem_fraction_limit": MEM_FRACTION,
            "mem_ok": mem_ok, "spent_node_h": spent_node_h, "repilot_node_h": pilot_node_h,
            "f1c_node_h_priced": F1C_NODE_H, "f1_projected_node_h": total, "priced_node_h": priced_node_h,
            "within_priced": within, "f1b2_time_limit": f"{h:02d}:{m:02d}:00", "worst_case_node_h": worst,
            "ceiling_node_h": ceiling_node_h, "within_ceiling": capped, "decision": "GO" if go else "STOP",
            "rule": "GO iff 16 x the largest per-process RSS <= 75 % of the node, 1.25 x the F1b' wall <= 55 min, "
                    "spent + re-pilot + F1b' + 0.75 <= the priced total, and the worst case <= the ceiling"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--runs", type=Path, required=True, help="the re-pilot's time records")
    ap.add_argument("--spent-node-h", type=float, required=True, help="F1 charged before the re-pilot (the ledger)")
    ap.add_argument("--repilot-node-h", type=float, required=True)
    ap.add_argument("--priced-node-h", type=float, required=True, help="the priced F1 total the binding sets")
    ap.add_argument("--ceiling-node-h", type=float, required=True, help="the F1 ceiling the binding sets")
    ap.add_argument("--job-id", required=True, help="the re-pilot's Slurm job, for submit_fd_f1.sh's sacct check")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    d = decide(load_runs(a.runs), a.spent_node_h, a.repilot_node_h, a.priced_node_h, a.ceiling_node_h)
    d["repilot_job_id"] = a.job_id
    with open(a.out, "x") as f:
        json.dump(d, f, indent=1)
    print(json.dumps({k: d[k] for k in ("f1b2_projected_wall_s", "f1b2_projected_mem_kib", "f1_projected_node_h",
                                         "decision")}))
    return 0 if d["decision"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
