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
    job, steps, ids = None, {}, set()
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
        if jid in ids:
            raise ValueError(f"a repeated step id {jid}")
        ids.add(jid)
        if tail and tail not in HOUSEKEEPING and not (tail.isdigit() and tail == str(int(tail))):
            raise ValueError(f"a step id that is neither canonical numeric nor housekeeping: {jid}")
        if not tail and jid != jobid:  # the allocation line is exactly the job id ("4242.", B4)
            raise ValueError(f"a malformed allocation id {jid!r}")
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


def support_table_ok(sup) -> bool:
    """C-SUPPORT's table is complete: 200 seeds, every listed seed in 1..200 with a non-empty, duplicate-free list
    of cell indices in 0..223, and the cell count equal to the listed cells."""
    if not (isinstance(sup, dict) and sup.get("pass") is True and sup.get("n_seeds") == 200):
        return False
    fails, n = sup.get("failures"), sup.get("n_seed_cells")
    if not isinstance(fails, dict) or not isinstance(n, int) or isinstance(n, bool):
        return False
    total = 0
    for k, cells in fails.items():
        if not (isinstance(k, str) and k.isdigit() and k == str(int(k)) and 1 <= int(k) <= 200
                and isinstance(cells, list) and cells):
            return False
        if not all(isinstance(c, int) and not isinstance(c, bool) and 0 <= c < 224 for c in cells):
            return False
        if len(set(cells)) != len(cells):
            return False
        total += len(cells)
    return total == n


RUNNER_PIN_KEYS = {"driver", "runner", "ptmc_run", "ptmc_lib", "rows", "join_record", "config", "inputs", "roounfold_lib"}


def pilot_files_ok(units: Path, jobid: str, rows: Path, lib_sha: str) -> dict:
    """The pilot's units directory holds exactly the 8 units' products and their pins receipts, each receipt passing
    and naming its unit and products' digests, and every unit's meta names this pilot job."""
    import hashlib
    want = {f"{u}{x}" for u in PILOT for x in (".npz", ".root", ".done")} | {f"pins_{u}.json" for u in PILOT}
    have = {p.name for p in units.iterdir()}
    out = {"files_exactly_the_pilot's": have == want}
    # the pins post-pilot can verify itself (confirm-3 B3): rows, the tool's runner and library, the bound RooUnfold.
    # It cannot see the deploy tree's driver, runner or config, nor the staged inputs: the scorer's C-PINS checks those
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()  # noqa: E731
    own = {"rows": sha(rows), "ptmc_run": sha(HERE.parent / "ptmc_run.py"), "ptmc_lib": sha(HERE.parent / "ptmc_lib.py"),
           "roounfold_lib": lib_sha}
    ok = out["files_exactly_the_pilot's"]
    for u in PILOT if ok else ():
        rec = json.loads((units / f"pins_{u}.json").read_text())
        digests = {n: hashlib.sha256((units / n).read_bytes()).hexdigest() for n in (f"{u}.done", f"{u}.npz", f"{u}.root")}
        meta = json.loads(str(np.load(units / f"{u}.npz", allow_pickle=False)["meta"]))
        ok = ok and rec.get("pass") is True and rec.get("units") == [u] and rec.get("outputs") == {u: digests}
        ok = ok and isinstance(rec.get("before"), dict) and set(rec["before"]) == RUNNER_PIN_KEYS \
            and rec.get("before") == rec.get("after") and all(rec["before"][k] == v for k, v in own.items())
        ok = ok and str(meta.get("slurm_job")) == jobid
        ok = ok and meta.get("unfolder") == lib_sha  # the bound RooUnfold, as ptmc_remote.sh pins it (confirm-3 B11)
    out["pins_receipts_and_job"] = bool(ok)
    return out


def pilot_cross_unit(units: Path, rows: Path) -> dict:
    """C-NORM, C-FIX and C-MOVE's seed-1 fill record, on the pilot's units (the scorer's own checks)."""
    import re
    import ptmc_score as S
    out = {}
    metas = {u: json.loads(str(np.load(units / f"{u}.npz", allow_pickle=False)["meta"])) for u in PILOT}
    norm = {metas[u].get("extract_args_sha256") for u in PILOT}
    one = next(iter(norm))
    out["C-NORM"] = len(norm) == 1 and isinstance(one, str) and bool(re.fullmatch(r"[0-9a-f]{64}", one))
    ro, rr = S.root_objects(units / "p_off_c.root"), S.root_objects(units / "p_R_c.root")
    out["C-FIX"] = all(S.fix_equal(ro, rr).values())
    entries = np.asarray(np.load(rows)["entry"], np.int64)
    out["C-MOVE-seed1"] = S.replica_moves(units, "p_R_b1", S.move_reference(units, entries))
    sup = metas["p_R_c"].get("support")
    out["C-SUPPORT-table"] = support_table_ok(sup)
    out["support"] = sup
    out["seconds"] = {u: metas[u].get("seconds") for u in PILOT}
    return out


def decide(job: dict, steps: dict, units: Path, rows: Path, lib_sha: str) -> dict:
    d = {"job": job, "steps": steps, "rules": {}}
    r = d["rules"]
    r["job_completed"] = (job["name"] == "ptmc_pilot" and job["state"] == "COMPLETED" and job["exit"] == "0:0"
                          and job["nodes"] == PILOT_NODES and job["elapsed"] > 0)
    r["every_pilot_step_completed"] = (sorted(steps) == sorted(PILOT) and all(
        s["state"] == "COMPLETED" and s["exit"] == "0:0" and s["nodes"] == 1 and 0 < s["elapsed"] <= job["elapsed"]
        for s in steps.values()))
    receipts = {u: P.unit_receipt(units, u) for u in PILOT}
    files = pilot_files_ok(units, job["id"], rows, lib_sha)
    d["files"] = files
    r["pilot_files_and_pins_receipts"] = all(files.values())
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
    ap.add_argument("--lib-sha", required=True, help="the bound libRooUnfold.so digest (ptmc_remote.sh's LIB_SHA)")
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
        d = decide(job, steps, a.units, a.rows, a.lib_sha)
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
    try:  # the decision, the C-SUPPORT table with it, is printed before PROCEED exists (B12)
        print(json.dumps({"decision": d}, indent=1, default=str), flush=True)
    except (OSError, ValueError) as e:
        sys.stderr.write(f"STOP: printing the decision failed: {e}\n")
        return 6
    (a.out / "time_limit_minutes").write_text(f"{d['time_limit_minutes']}\n")
    (a.out / "PROCEED").write_text("PROCEED\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
