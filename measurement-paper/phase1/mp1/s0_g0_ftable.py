#!/usr/bin/env python3
"""MP1-A S0, gate G0 (BINDING-PHASE1-ADDENDUM-2 R1): tabulate the calorimetric map q0 = F(pc) for one playlist and
test it on held-out events.

pc = sum over the ten allNonMuonClusters species of (_id + _od), negative defaults as 0; q0 = MasterAnaDev_recoil_E.
F is built from the TRAIN file's selected-like events (the six reco pre-cuts, as in s0_inspect_q0_g2.py) as a
monotone piecewise-linear interpolant:
  1. sort the (pc, q0) pairs by pc;
  2. split them greedily into maximal runs that lie on one straight line (each point within 1e-9 relative of the
     line through the run's first point and its first distinct successor);
  3. fit each run's line by least squares; the knots are the intersections of consecutive lines when they fall
     between the two runs, and otherwise (near-parallel lines) the gap's midpoint on the mean of the two lines;
     single-point runs are refused (no line can be determined).
The table is the knot list (x, F(x)), from pc = 0 to the largest training pc, and F is extended beyond both ends with
the end segments' slopes. G0: max |F(pc) - q0| / q0 <= 1e-4 over the HELD-OUT file's selected-like events with
q0 > 0 (a different MC file of the same playlist). Descriptive: the same on all held-out events with pc, q0 > 0.

    python -I s0_g0_ftable.py <train.root> <heldout.root> --table <out.txt> [--json <out.json>]
Exit 0 = G0 PASS, 1 = G0 FAIL, 2 = could not evaluate (e.g. a single-point run).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys

import numpy as np
import uproot

SPECIES = ("proton", "meson", "em", "other", "low_neutron", "mid_neutron", "high_neutron", "xtalk", "muon", "none")
LINE_TOL = 1e-9
G0_TOL = 1e-4
BRANCHES = ["MasterAnaDev_recoil_E", "isMinosMatchTrack", "MasterAnaDev_minos_trk_is_ok", "MasterAnaDev_minos_trk_qp",
            "phys_n_dead_discr_pair_upstream_prim_track_proj", "MasterAnaDev_muon_theta", "vtx"]
BRANCHES += [f"part_response_recoil_allNonMuonClusters_{s}_{x}" for s in SPECIES for x in ("id", "od")]


def load(path: str) -> dict:
    """Read pc, q0 and the selected-like mask from one MC AnaTuple."""
    a = uproot.open(path)["MasterAnaDev"].arrays(BRANCHES, library="np")
    q0 = a["MasterAnaDev_recoil_E"].astype(float)
    pc = sum(np.clip(a[f"part_response_recoil_allNonMuonClusters_{s}_{x}"].astype(float), 0.0, None)
             for s in SPECIES for x in ("id", "od"))
    v = np.stack(a["vtx"]).astype(float)
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    hexa = (np.abs(y) < -np.abs(x) / np.sqrt(3.0) + 2.0 * 850.0 / np.sqrt(3.0)) & (np.abs(x) < 850.0)
    sel = ((z >= 5980) & (z <= 8422) & hexa & (a["MasterAnaDev_muon_theta"] < 20.0 * np.pi / 180.0)
           & (a["isMinosMatchTrack"] == 1) & (a["MasterAnaDev_minos_trk_is_ok"] == 1)
           & (a["phys_n_dead_discr_pair_upstream_prim_track_proj"] < 1) & (a["MasterAnaDev_minos_trk_qp"] < 0))
    return {"pc": pc, "q0": q0, "sel": sel, "n": len(q0)}


def segments(P: np.ndarray, Q: np.ndarray) -> list[tuple[int, int]]:
    """Maximal runs [i, j) of the sorted pairs that lie on one line, to LINE_TOL relative."""
    runs, i, n = [], 0, len(P)
    while i < n:
        j = i + 1
        while j < n and P[j] == P[i]:
            j += 1
        if j >= n:
            runs.append((i, n))
            break
        slope = (Q[j] - Q[i]) / (P[j] - P[i])
        k = j + 1
        while k < n and abs(Q[i] + slope * (P[k] - P[i]) - Q[k]) <= LINE_TOL * abs(Q[k]) + LINE_TOL:
            k += 1
        runs.append((i, k))
        i = k
    return runs


def build_table(P: np.ndarray, Q: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[dict]]:
    o = np.argsort(P, kind="stable")
    P, Q = P[o], Q[o]
    lines, info = [], []
    for i, j in segments(P, Q):
        if j - i < 2 or P[j - 1] == P[i]:
            raise ValueError(f"a single-point run at pc = {P[i]:.6g}: no line can be determined")
        m, b = np.polyfit(P[i:j], Q[i:j], 1)
        resid = np.max(np.abs(m * P[i:j] + b - Q[i:j]) / np.abs(Q[i:j]))
        lines.append((m, b, P[i], P[j - 1]))
        info.append({"n": int(j - i), "pc_first": float(P[i]), "pc_last": float(P[j - 1]), "slope": float(m),
                     "intercept": float(b), "max_rel_resid": float(resid)})
    xs, ys = [0.0], [lines[0][1]]
    for (m1, b1, _, last1), (m2, b2, first2, _) in zip(lines[:-1], lines[1:]):
        if m1 == m2:
            raise ValueError(f"consecutive runs with equal slope near pc = {last1:.6g}")
        xk = (b2 - b1) / (m1 - m2)
        if last1 - 1e-9 * last1 <= xk <= first2 + 1e-9 * first2:
            yk = m1 * xk + b1
        else:
            # Near-parallel neighbours (e.g. slopes 1.530447 / 1.530537): the intersection is ill-conditioned and
            # falls outside the gap between the runs. Place the knot at the gap's midpoint, on the mean of the two
            # lines; both runs then stay within |m1 - m2| * gap of their own lines (G0 measures the effect).
            xk = 0.5 * (last1 + first2)
            yk = 0.5 * ((m1 * xk + b1) + (m2 * xk + b2))
            info[len(xs) - 1]["knot_after_is_gap_midpoint"] = True
        xs.append(xk)
        ys.append(yk)
    xs.append(lines[-1][3])
    ys.append(lines[-1][0] * lines[-1][3] + lines[-1][1])
    xs, ys = np.array(xs), np.array(ys)
    if np.any(np.diff(xs) <= 0) or np.any(np.diff(ys) < 0):
        raise ValueError("the tabulated F is not monotone")
    return xs, ys, info


def evaluate(xs: np.ndarray, ys: np.ndarray, pc: np.ndarray) -> np.ndarray:
    """F(pc): linear between knots, extended with the end slopes (the universe's rule)."""
    out = np.interp(pc, xs, ys)
    lo, hi = pc < xs[0], pc > xs[-1]
    s0 = (ys[1] - ys[0]) / (xs[1] - xs[0])
    s1 = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
    out[lo] = ys[0] + s0 * (pc[lo] - xs[0])
    out[hi] = ys[-1] + s1 * (pc[hi] - xs[-1])
    return out


def rel_stats(F: np.ndarray, q0: np.ndarray) -> dict:
    r = np.abs(F - q0) / np.abs(q0)
    return {"n": int(r.size), "max": float(r.max()), "p99": float(np.percentile(r, 99)),
            "p50": float(np.median(r)), "n_over_1e-4": int(np.sum(r > G0_TOL))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("train")
    ap.add_argument("heldout")
    ap.add_argument("--table", required=True)
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if a.train == a.heldout:
        print("refusing: the held-out file must differ from the training file", file=sys.stderr)
        return 2
    tr, ho = load(a.train), load(a.heldout)
    mt = tr["sel"] & (tr["pc"] > 0) & (tr["q0"] > 0)
    try:
        xs, ys, info = build_table(tr["pc"][mt], tr["q0"][mt])
    except ValueError as exc:
        print(json.dumps({"G0": "COULD_NOT_EVALUATE", "error": str(exc)}))
        return 2
    with open(a.table, "w") as fh:
        fh.write(f"# MP1-A S0 calorimetric map F: q0 = F(pc), playlist 1A, from {a.train}\n")
        fh.write(f"# {len(xs)} knots; linear between knots, end slopes beyond; built "
                 f"{datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
        for x, y in zip(xs, ys):
            fh.write(f"{x:.17g} {y:.17g}\n")
    with open(a.table, "rb") as fh:
        table_sha = hashlib.sha256(fh.read()).hexdigest()
    mh = ho["sel"] & (ho["pc"] > 0) & (ho["q0"] > 0)
    ma = (ho["pc"] > 0) & (ho["q0"] > 0)
    res = {
        "train": a.train, "heldout": a.heldout, "table": a.table, "table_sha256": table_sha,
        "train_entries": tr["n"], "train_selected_used": int(mt.sum()), "heldout_entries": ho["n"],
        "segments": info, "knots": [[float(x), float(y)] for x, y in zip(xs, ys)],
        "train_selected": rel_stats(evaluate(xs, ys, tr["pc"][mt]), tr["q0"][mt]),
        "heldout_selected": rel_stats(evaluate(xs, ys, ho["pc"][mh]), ho["q0"][mh]),
        "heldout_selected_beyond_training_range": int(np.sum(ho["pc"][mh] > xs[-1])),
        "heldout_all_pc_q0_positive_descriptive": rel_stats(evaluate(xs, ys, ho["pc"][ma]), ho["q0"][ma]),
        "tolerance": G0_TOL,
    }
    res["G0"] = "PASS" if res["heldout_selected"]["max"] <= G0_TOL else "FAIL"
    text = json.dumps(res, indent=1)
    print(text)
    if a.json:
        with open(a.json, "w") as fh:
            fh.write(text + "\n")
    return 0 if res["G0"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
