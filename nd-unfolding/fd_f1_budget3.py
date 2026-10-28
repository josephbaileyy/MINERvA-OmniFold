#!/usr/bin/env python3
"""F1's third budget gate (state/measurement-paper/5d-community-20261024/FD-F1-DECLARATION-AMENDMENT-2.md section 3):
GO or STOP for F1b' in its single-wave layout, by rule, from the F1a' re-pilot's committed records. No new pilot.

F1a' (job 60425719) ran 14 gevgen processes at once and its gate, fd_f1_budget2.py, said STOP: F1b' as 128 tasks of
17,500 events in 10 waves pays a task's fixed cost (gevgen start-up and gntpc, about 165 s) 128 times. Amendment 2
keeps the events per tune (1,120,000) and runs them as 7 tasks of 160,000 per tune, all 14 at once, in one wave.

The projection, from fd_f1_budget2.summary of the 20 committed /usr/bin/time -v records (seed 60103 included):
  t        = max over the tunes of the fitted per-event time (long wall - short wall) / (17,500 - 1,000)
  L        = max over the tunes of the fitted load, short wall - 1,000 t
  task     = L + 160,000 t          (at least each tune's own L + 160,000 t)
  wall     = task + FIXED_S         (one wave; hadd, two conversions and the prep, as the earlier gates)
  memory   = 14 x the largest per-process RSS over every run
160,000 events is about 9x the largest re-pilot run, so the 160,000 t term is an extrapolation. The re-pilot measured
RSS only up to 17,500 events. F1b''s job limit (1.25 x the wall) and its per-task timeout (3 x the task) bound it.
GO iff
  * every record re-verifies against the committed f1a2-SHA256SUMS, whose own digest is pinned here,
  * memory <= MEM_FRACTION of the node's allocation,
  * 1.25 x the wall <= F1B_MAX_S (57 min, unchanged from amendment 1),
  * spent + the wall + F1c's priced 0.75 node-h <= the priced total the binding sets, and
  * the worst case (spent + F1b''s limit + F1c's 0:54) <= the ceiling the binding sets.
spent is F1's charge so far from sacct (fd/LEDGER.tsv), the re-pilot included. Anything else is a STOP for the
director.

MEASURES: a projection from committed measurements. CANNOT AUTHORIZE: anything beyond the declared stages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

_ND = Path(__file__).resolve().parent
if str(_ND) not in sys.path:
    sys.path.insert(0, str(_ND))
import fd_f1_budget2 as B2  # noqa: E402  (load_runs, summary, the re-pilot's constants)

TUNES = B2.TUNES
P = 14                      # 2 tunes x 7 tasks, all at once
N_TASKS_PER_TUNE = 7
N_EVENTS = 160_000          # per task: 7 x 160,000 = 1,120,000 per tune, F1b's 64 x 17,500
WAVES = math.ceil(len(TUNES) * N_TASKS_PER_TUNE / P)
SEED_BASE = {"G18_10a_02_11b": 60000, "AR23_20i_00_000": 61000}   # F1b's declared ranges; the first seven of each
FIXED_S = B2.FIXED_S
F1B_MAX_S = 57 * 60         # the wall rule, unchanged from amendment 1 (whose section 6 said "55-minute" in error)
WALL_MARGIN = 1.25
TIMEOUT_FACTOR = 3.0        # the per-task timeout: 3 x the projected task wall
NODE_MEM_KIB, MEM_FRACTION = B2.NODE_MEM_KIB, B2.MEM_FRACTION
F1C_NODE_H, F1C_LIMIT_H = B2.F1C_NODE_H, B2.F1C_LIMIT_H
SPENT_NODE_H = 0.408333     # sacct: F1a 0.104722 + F1b 0.202778 + F1a' 0.100833 (fd/LEDGER.tsv S4.2, S4.3, S4.5)
REPILOT_JOB_ID = "60425719"
RECORDS = (_ND.parent / "docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-f1/run/cluster"
           / "f1a2")
RECORDS_SUMS_SHA256 = "43b621681762193bca91e42ea78662053428f6097eb941516fbaf1c5de489650"   # f1a2-SHA256SUMS

assert N_TASKS_PER_TUNE * N_EVENTS == (B2.N_TASKS // len(TUNES)) * B2.N_TASK


def seeds(tune: str) -> list[int]:
    """F1b''s seeds: the first seven of F1b's declared range for the tune, in order."""
    b = SEED_BASE[tune]
    return list(range(b + 1, b + 1 + N_TASKS_PER_TUNE))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_records(root: Path, sums_sha256: str = RECORDS_SUMS_SHA256) -> dict:
    """The re-pilot's records: f1a2-SHA256SUMS is the pinned file, and every runs/ record it lists re-verifies."""
    sums = root / "f1a2-SHA256SUMS"
    if not sums.is_file() or sha256(sums) != sums_sha256:
        raise SystemExit(f"[FAIL] {sums} is not the committed f1a2-SHA256SUMS")
    listed = {}
    for line in sums.read_text().splitlines():
        h, rel = line.split("  ", 1)
        if rel.startswith("./runs/"):
            listed[rel[2:]] = h
    on_disk = sorted(str(p.relative_to(root)) for p in (root / "runs").glob("*/*.time"))
    if sorted(listed) != on_disk:
        raise SystemExit(f"[FAIL] the records under {root}/runs are not the {len(listed)} the sums list")
    for rel, h in listed.items():
        if sha256(root / rel) != h:
            raise SystemExit(f"[FAIL] {root / rel} does not match f1a2-SHA256SUMS")
    return B2.load_runs(root / "runs")


def decide(runs: dict, priced_node_h: float, ceiling_node_h: float, spent_node_h: float = SPENT_NODE_H) -> dict:
    s = B2.summary(runs)
    t = max(v["per_event_s_descriptive"] for v in s.values())
    load = max(v["load_s_descriptive"] for v in s.values())
    if not (t > 0 and load > 0):
        raise SystemExit(f"[FAIL] the fit gives per-event {t} s and load {load} s; both must be positive")
    task = load + N_EVENTS * t
    wall = WAVES * task + FIXED_S
    mem = P * max(v["max_rss_kib"] for v in s.values())
    mem_ok = mem <= MEM_FRACTION * NODE_MEM_KIB
    fits = wall * WALL_MARGIN <= F1B_MAX_S
    total = spent_node_h + wall / 3600.0 + F1C_NODE_H
    within = total <= priced_node_h
    limit_min = int(-(-(wall * WALL_MARGIN) // 60))
    h, m = divmod(limit_min, 60)
    worst = spent_node_h + limit_min / 60.0 + F1C_LIMIT_H
    capped = worst <= ceiling_node_h
    go = mem_ok and fits and within and capped
    return {"runs": s, "per_event_s_used": t, "load_s_used": load, "events_per_task": N_EVENTS,
            "events_over_largest_measured_run": N_EVENTS / B2.N_TASK,
            "concurrency": P, "tasks_per_tune": N_TASKS_PER_TUNE, "waves": WAVES,
            "f1b3_projected_task_wall_s": task, "f1b3_projected_wall_s": wall, "f1b3_fits_its_limit": fits,
            "f1b3_projected_mem_kib": mem, "node_mem_kib": NODE_MEM_KIB, "mem_fraction_limit": MEM_FRACTION,
            "mem_ok": mem_ok, "spent_node_h": spent_node_h, "f1c_node_h_priced": F1C_NODE_H,
            "f1_projected_node_h": total, "priced_node_h": priced_node_h, "within_priced": within,
            "f1b3_time_limit": f"{h:02d}:{m:02d}:00", "worst_case_node_h": worst, "ceiling_node_h": ceiling_node_h,
            "within_ceiling": capped, "f1b3_task_timeout_s": int(math.ceil(TIMEOUT_FACTOR * task)),
            "repilot_job_id": REPILOT_JOB_ID, "records_sums_sha256": RECORDS_SUMS_SHA256,
            "decision": "GO" if go else "STOP",
            "extrapolation": "160,000 events per task is about 9x the re-pilot's 17,500-event runs: the per-event term "
                             "is extrapolated, and RSS was measured only up to 17,500 events",
            "rule": "GO iff 14 x the largest per-process RSS <= 75 % of the node, 1.25 x the F1b' wall <= 57 min, "
                    "spent + F1b' + 0.75 <= the priced total, and the worst case <= the ceiling"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--records", type=Path, default=RECORDS, help="the committed f1a2 receipts directory")
    ap.add_argument("--priced-node-h", type=float, required=True, help="the priced F1 total the binding sets")
    ap.add_argument("--ceiling-node-h", type=float, required=True, help="the F1 ceiling the binding sets")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    d = decide(verify_records(a.records), a.priced_node_h, a.ceiling_node_h)
    with open(a.out, "x") as f:
        json.dump(d, f, indent=1)
    print(json.dumps({k: d[k] for k in ("f1b3_projected_task_wall_s", "f1b3_projected_wall_s", "f1b3_projected_mem_kib",
                                         "f1_projected_node_h", "worst_case_node_h", "decision")}))
    return 0 if d["decision"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
