#!/usr/bin/env python3
"""PTMC post-pilot (PTMC-DECLARATION.md section 7): from the pilot's sacct and its units, the per-replica time t_R,
the overhead o, the pilot's charge, the projection and the replicas' time limit L. Writes decision.json always, and
PROCEED plus time_limit_minutes only if every rule passes. Exit 0 = PROCEED, 6 = STOP.

  python3 ptmc_pilot_post.py --sacct SACCT.txt --units UNITS_DIR --out DIR

sacct lines: JobID|JobName|State|ExitCode|ElapsedRaw|NNodes|Start|End (TZ=UTC, -n -P), as ptmc_remote.sh writes them.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

PILOT = ["p_off_c", "p_R_c", "p_off_b1", "p_R_b1", "p_off_b2", "p_off_b3", "p_off_b4", "p_off_b5"]
CAP, STOP_AT, NODES, PER_LANE, MARGIN, FLOOR = 12.5, 11.5, 5, 10, 1.5, 1.1


def parse_sacct(text: str) -> tuple[dict, dict]:
    job, steps = None, {}
    for line in text.splitlines():
        f = line.split("|")
        if len(f) < 8:
            continue
        jid, name, state, exitc, el, nn = f[:6]
        rec = {"id": jid, "name": name, "state": state.split()[0] if state else "", "exit": exitc,
               "elapsed": int(el) if el.isdigit() else None, "nodes": int(nn) if nn.isdigit() else None}
        if "." not in jid:
            if job is not None:
                raise ValueError("two allocation lines")
            job = rec
        elif name in PILOT:
            if name in steps:
                raise ValueError(f"two steps named {name}")
            steps[name] = rec
    if job is None:
        raise ValueError("no allocation line")
    return job, steps


def decide(job: dict, steps: dict, unit_ok: dict) -> dict:
    d = {"job": job, "steps": steps, "units": unit_ok, "rules": {}}
    r = d["rules"]
    r["job_completed"] = job["state"] == "COMPLETED" and job["exit"] == "0:0" and job["nodes"] == 2 \
        and job["elapsed"] is not None
    r["every_pilot_step_completed"] = sorted(steps) == sorted(PILOT) and all(
        s["state"] == "COMPLETED" and s["exit"] == "0:0" and s["elapsed"] is not None for s in steps.values())
    r["every_pilot_unit_passes"] = all(unit_ok.get(u) is True for u in PILOT)
    if not all(r.values()):
        d["verdict"] = "STOP"
        return d
    t_r = float(steps["p_R_b1"]["elapsed"])
    o = max(0.0, float(job["elapsed"] - max(s["elapsed"] for s in steps.values())))
    pilot = job["elapsed"] * job["nodes"] / 3600.0
    runtime = PER_LANE * t_r + o
    projection = pilot + NODES * runtime / 3600.0
    cap_left = CAP - pilot
    limit_s = min(MARGIN * PER_LANE * t_r + o, cap_left / NODES * 3600.0)
    limit_min = int(math.floor(limit_s / 60.0))
    d.update(t_R_s=t_r, o_s=o, pilot_node_h=pilot, projection_node_h=projection, cap_left_node_h=cap_left,
             time_limit_minutes=limit_min, runtime_s=runtime, reservation_node_h=NODES * limit_min / 60.0)
    r["projection_within_11.5"] = projection <= STOP_AT
    r["limit_covers_1.1x_runtime"] = limit_min * 60.0 >= FLOOR * runtime
    r["reservation_within_cap_left"] = NODES * limit_min / 60.0 <= cap_left
    d["verdict"] = "PROCEED" if all(r.values()) else "STOP"
    return d


def unit_status(units: Path) -> dict:
    out = {}
    for u in PILOT:
        try:
            mk = json.loads((units / f"{u}.done").read_text())
            meta = json.loads(str(np.load(units / f"{u}.npz", allow_pickle=False)["meta"]))
            ctl = meta["controls"]
            ok = mk.get("verdict") == "PASS" and mk.get("unit") == u and all(c.get("pass") is True for c in ctl.values())
            if u.endswith("_c"):
                ok = ok and ctl.get("C-COUPLE", {}).get("pass") is True
            out[u] = bool(ok)
        except (OSError, ValueError, KeyError) as e:
            out[u] = f"unreadable: {type(e).__name__}"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--sacct", type=Path, required=True)
    ap.add_argument("--units", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if (a.out / "PROCEED").exists() or (a.out / "decision.json").exists():
        print("refusing: a decision exists", file=sys.stderr)
        return 2
    try:
        job, steps = parse_sacct(a.sacct.read_text())
        d = decide(job, steps, unit_status(a.units))
    except (OSError, ValueError) as e:
        d = {"verdict": "STOP", "why": str(e)}
    (a.out / "decision.json").write_text(json.dumps(d, indent=1, default=str) + "\n")
    if d["verdict"] != "PROCEED":
        return 6
    (a.out / "time_limit_minutes").write_text(f"{d['time_limit_minutes']}\n")
    (a.out / "PROCEED").write_text("PROCEED\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
