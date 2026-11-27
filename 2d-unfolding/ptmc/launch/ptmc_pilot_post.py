#!/usr/bin/env python3
"""PTMC post-pilot (PTMC-DECLARATION.md section 7), with the director's binding rulings:
- The pilot's accounting, bound to its job ID, gives t_R (p_R_b1's step), the overhead o, the pilot's charge, the
  projection and the replicas' time limit L.
- Every pilot unit must pass the strict receipt check shared with the scorer.
- Before PROCEED, the pilot-computable cross-unit controls run: C-NORM, C-FIX, and C-MOVE's seed-1 fill record. The
  C-SUPPORT table must be complete and printed.

All arithmetic is in integer seconds and node-seconds (codex r1 #5).
- Projection: pilot_ns + 5 x (10 t_R + o) <= 11.5 x 3600 node-seconds.
- L (minutes) = min(floor((1.5 x 10 t_R + o) / 60), (12.5 x 3600 - pilot_ns) // (5 x 60)).
- The floor: 60 L >= 1.1 x (10 t_R + o), checked as 600 L >= 11 (10 t_R + o).

Writes decision.json always, and PROCEED plus time_limit_minutes only if every rule passes. Exit 0 = PROCEED,
6 = STOP, 2 = refused.

  python3 ptmc_pilot_post.py --sacct SACCT.txt --jobid N --units UNITS_DIR --rows ROWS.npz --out DIR
          [--recheck DECISION.json]   (the replicas' submit: recompute and require the same L)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import ptmc_lib as P  # noqa: E402

PILOT = ["p_off_c", "p_R_c", "p_off_b1", "p_R_b1", "p_off_b2", "p_off_b3", "p_off_b4", "p_off_b5"]
CAP_S, STOP_S = 45000, 41400  # 12.5 and 11.5 node-h, in node-seconds
NODES, PER_LANE, PILOT_NODES = 5, 10, 2
HOUSEKEEPING = ("batch", "extern")


def parse_sacct(text: str, jobid: str) -> tuple[dict, dict]:
    """The allocation line and the eight named unit steps of job `jobid`; anything else is refused."""
    job, steps = None, {}
    for line in text.splitlines():
        if not line.strip():
            continue
        f = line.split("|")
        if len(f) != 8:
            raise ValueError(f"a malformed sacct row: {line!r}")
        jid, name, state, exitc, el, nn = f[:6]
        head, _, tail = jid.partition(".")
        if head != jobid:
            raise ValueError(f"a row of another job: {jid}")
        if not (el.isdigit() and nn.isdigit()):
            raise ValueError(f"non-numeric elapsed or nodes: {line!r}")
        rec = {"id": jid, "name": name, "state": state.split()[0] if state else "", "exit": exitc,
               "elapsed": int(el), "nodes": int(nn)}
        if not tail:
            if job is not None:
                raise ValueError("two allocation lines")
            job = rec
        elif tail in HOUSEKEEPING:
            continue
        else:
            if name not in PILOT or name in steps:
                raise ValueError(f"an unexpected or repeated step {name!r}")
            steps[name] = rec
    if job is None:
        raise ValueError("no allocation line")
    return job, steps


def pilot_cross_unit(units: Path, rows: Path) -> dict:
    """C-NORM, C-FIX and C-MOVE's seed-1 fill record, on the pilot's units (the scorer's own checks)."""
    import ptmc_score as S
    out = {}
    metas = {u: json.loads(str(np.load(units / f"{u}.npz", allow_pickle=False)["meta"])) for u in PILOT}
    norm = {metas[u].get("extract_args_sha256") for u in PILOT}
    out["C-NORM"] = len(norm) == 1 and isinstance(next(iter(norm)), str)
    ro, rr = S.root_objects(units / "p_off_c.root"), S.root_objects(units / "p_R_c.root")
    out["C-FIX"] = all(S.fix_equal(ro, rr).values())
    entries = np.asarray(np.load(rows)["entry"], np.int64)
    keys = ("fill_entry", "fill_pt", "fill_pz", "fill_w")
    ref = np.load(units / "p_off_b1.npz", allow_pickle=False)
    r1 = np.load(units / "p_R_b1.npz", allow_pickle=False)
    keep = ~np.isin(np.asarray(ref["fill_entry"], np.int64), entries)
    e = np.asarray(ref["fill_entry"])
    out["C-MOVE-seed1"] = bool(e.size > 0 and np.unique(e).size == e.size
                               and all(np.array_equal(np.asarray(r1[k]), np.asarray(ref[k])[keep]) for k in keys))
    sup = metas["p_R_c"].get("support")
    out["C-SUPPORT-table"] = bool(isinstance(sup, dict) and sup.get("n_seeds") == 200 and "failures" in sup)
    out["support"] = sup
    out["seconds"] = {u: metas[u].get("seconds") for u in PILOT}
    return out


def decide(job: dict, steps: dict, units: Path, rows: Path) -> dict:
    d = {"job": job, "steps": steps, "rules": {}}
    r = d["rules"]
    r["job_completed"] = (job["name"] == "ptmc_pilot" and job["state"] == "COMPLETED" and job["exit"] == "0:0"
                          and job["nodes"] == PILOT_NODES and job["elapsed"] > 0)
    r["every_pilot_step_completed"] = (sorted(steps) == sorted(PILOT) and all(
        s["state"] == "COMPLETED" and s["exit"] == "0:0" and s["nodes"] == 1 and 0 < s["elapsed"] <= job["elapsed"]
        for s in steps.values()))
    receipts = {u: P.unit_receipt(units, u) for u in PILOT}
    d["units"] = {u: (True if v["ok"] else v["why"]) for u, v in receipts.items()}
    r["every_pilot_unit_passes"] = all(v["ok"] for v in receipts.values())
    if not all(r.values()):
        d["verdict"] = "STOP"
        return d
    cross = pilot_cross_unit(units, rows)
    d["cross_unit"] = {k: v for k, v in cross.items() if k not in ("support",)}
    d["C-SUPPORT"] = cross["support"]
    for k in ("C-NORM", "C-FIX", "C-MOVE-seed1", "C-SUPPORT-table"):
        r[k] = bool(cross[k])
    t_r = steps["p_R_b1"]["elapsed"]
    o = job["elapsed"] - max(s["elapsed"] for s in steps.values())
    pilot_ns = job["elapsed"] * job["nodes"]
    runtime = PER_LANE * t_r + o
    projection_ns = pilot_ns + NODES * runtime
    limit_min = min((15 * t_r + o) // 60, (CAP_S - pilot_ns) // (NODES * 60))
    d.update(t_R_s=t_r, o_s=o, pilot_node_s=pilot_ns, pilot_node_h=pilot_ns / 3600, runtime_s=runtime,
             projection_node_s=projection_ns, projection_node_h=projection_ns / 3600,
             cap_left_node_s=CAP_S - pilot_ns, time_limit_minutes=int(limit_min),
             reservation_node_s=NODES * 60 * int(limit_min))
    r["o_nonnegative"] = o >= 0
    r["projection_within_11.5"] = projection_ns <= STOP_S
    r["limit_positive"] = limit_min >= 1
    r["limit_covers_1.1x_runtime"] = 600 * limit_min >= 11 * runtime
    r["reservation_within_cap_left"] = NODES * 60 * limit_min <= CAP_S - pilot_ns
    d["verdict"] = "PROCEED" if all(r.values()) else "STOP"
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--sacct", type=Path, required=True)
    ap.add_argument("--jobid", required=True)
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--recheck", type=Path, default=None)
    a = ap.parse_args(argv)
    if not a.jobid.isdigit():
        print("refusing: the job id is not numeric", file=sys.stderr)
        return 2
    if a.recheck is None and ((a.out / "PROCEED").exists() or (a.out / "decision.json").exists()):
        print("refusing: a decision exists", file=sys.stderr)
        return 2
    try:
        job, steps = parse_sacct(a.sacct.read_text(), a.jobid)
        d = decide(job, steps, a.units, a.rows)
    except Exception as e:  # a STOP, never a pass
        d = {"verdict": "STOP", "why": f"{type(e).__name__}: {e}"}
    if a.recheck is not None:  # the replicas' submit: the same PROCEED and the same L, or nothing is submitted
        prev = json.loads(a.recheck.read_text())
        same = (d.get("verdict") == "PROCEED" and prev.get("verdict") == "PROCEED"
                and d.get("time_limit_minutes") == prev.get("time_limit_minutes"))
        print(json.dumps({"recheck": "SAME" if same else "DIFFERS", "time_limit_minutes": d.get("time_limit_minutes")}))
        return 0 if same else 6
    (a.out / "decision.json").write_text(json.dumps(d, indent=1, default=str) + "\n")
    if d["verdict"] != "PROCEED":
        return 6
    (a.out / "time_limit_minutes").write_text(f"{d['time_limit_minutes']}\n")
    (a.out / "PROCEED").write_text("PROCEED\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
