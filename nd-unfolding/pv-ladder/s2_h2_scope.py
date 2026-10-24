#!/usr/bin/env python3
"""S2 scoping (state/measurement-scoping/pv-ladder/S2-H2-CMODEL-SCOPE.md): how L-5D-PV's reweights and closures land on
s5p's H2 partition (2 x 2 x 2 x 2 x 2, s5p_stage1_inspect.H2_EDGES), from simulation only (numpy only).

Per H2 cell, with the reported flag and the response figures of s5p's Stage-1 receipt:
  the prior's truth weight p (ratios.json, exact on the fine grid) and the fine cells it covers;
  per vertex, the truth-level departure d_k = sum(p r_k) / sum(p) - 1, exact because r_k is constant on each fine cell,
      and the shares of p on the gate's tiers (own ratio, J-coarse pooled, r = 1), GiBUU's r = 1 split into the
      p_parallel >= 10 GeV/c cut and the rest;
  the share of p in fine cells beside a step in r > 0.1 drawn by the gate or a cut (pvl_lib.classify_cells, union over
      the vertices: the step-adjacent tail caveat);
  the NuWro closure bias (L-5D-PV_e_closure_nuwro against its truth) and the closure floor (_closure_tune_v1), and how
      many reported cells have |bias| > 1 %: the positive control's power on H2;
  and an aggregation check: the closure truth on H2 by pvl_lib's integration and by s5p_stage1_inspect's coarse_map with
      its fine volumes, which must agree.

It never opens a data product: the nominal and vertex unfolds are configuration (e)'s data result, and DECISION-20261024
(-5d-community-standard-route) item 2 requires cells to be declared before any such result is read.

MEASURES: arithmetic on the frozen reweights, two closure products and a committed receipt. CANNOT AUTHORIZE: any
claim, the H2 cells, or C_model,5D.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))
import pvl_lib as L  # noqa: E402
import s5p_stage1_inspect as s1  # noqa: E402

RUNG = "L-5D-PV"
VERTICES = ("genie_mec", "nuwro", "gibuu")
CLOSURES = ("L-5D-PV_e_closure_nuwro", "L-5D-PV_e_closure_tune_v1")
MIN_BIAS = 0.01  # the positive control's |bias| threshold (pv2d_lib.positive_control)
MIN_CELLS = 20


def check(path, want, what):
    got = L.sha256_path(path)
    if got != want:
        raise SystemExit(f"[FAIL] {what}: sha256 {got} != {want}")
    return got


def h2_of_fine():
    """The H2 cell of every fine cell (by centre), with s5p's own map."""
    if tuple(s1.AXES) != L.AXES5 or any(tuple(s1.FINE[a]) != tuple(L.FINE[a]) for a in L.AXES5):
        raise SystemExit("[FAIL] s5p_stage1_inspect's fine grid is not pvl_lib's")
    return s1.coarse_map(s1.H2_EDGES)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ratios", type=Path, required=True, help="the frozen prep/ratios/L-5D-PV directory")
    ap.add_argument("--products", type=Path, required=True, help="a directory holding the two closure products")
    ap.add_argument("--stage1", type=Path, default=_HERE.parents[1] / "docs/orchestration/state/s5p/stage1/stage1_inspect.json")
    ap.add_argument("--prep-sums", type=Path, default=_HERE / "prep-SHA256SUMS")
    ap.add_argument("--receipts", type=Path, default=_HERE.parents[1] /
                    "docs/orchestration/state/measurement-scoping/pv-ladder/receipts/SHA256SUMS")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"[FAIL] refusing to overwrite {a.out}")
    prep = dict(ln.split()[::-1] for ln in a.prep_sums.read_text().splitlines() if ln.strip())
    rec = dict(ln.split()[::-1] for ln in a.receipts.read_text().splitlines() if ln.strip())
    inputs = {}
    for f in ["ratios.json"] + [f"{v}.json" for v in VERTICES]:
        inputs[f"ratios/{RUNG}/{f}"] = check(a.ratios / f, prep[f"./ratios/{RUNG}/{f}"], f)
    for c in CLOSURES:
        inputs[f"products/{c}.npz"] = check(a.products / f"{c}.npz", rec[f"products/{c}.npz"], c)
    inputs["stage1_inspect.json"] = L.sha256_path(a.stage1)

    R = L.load_json(a.ratios / "ratios.json")
    if R["rung"] != RUNG or tuple(R["axes"]) != L.AXES5:
        raise SystemExit("[FAIL] ratios.json is not L-5D-PV's 5D reweight")
    shape = tuple(len(L.FINE[x]) - 1 for x in L.AXES5)
    cell, n = h2_of_fine()
    S1 = L.load_json(a.stage1)["mc"]["H2"]
    reported = np.asarray(S1["reported"], bool)
    if n != 32 or reported.size != 32 or int(reported.sum()) != 27:
        raise SystemExit("[FAIL] H2 is not 32 cells with 27 reported")

    def agg(v):
        return np.bincount(cell, weights=np.asarray(v, float), minlength=n)

    p = np.asarray(R["prior_truth_weight"], float)
    P = agg(p)
    pz_hi = np.asarray(L.FINE["pz"][1:])[np.unravel_index(np.arange(p.size), shape)[1]]
    out = {"schema": "s2-h2-scope/1", "post_hoc": False, "simulation_only": True, "h2_edges": s1.H2_EDGES,
           "inputs": inputs, "code": {"s2_h2_scope.py": L.sha256_path(__file__), "pvl_lib.py": L.sha256_path(L.__file__),
                                      "s5p_stage1_inspect.py": L.sha256_path(Path(s1.__file__))},
           "cells": {"reported": reported.tolist(), "n_fine": np.bincount(cell, minlength=n).tolist(),
                     "n_fine_prior_positive": np.bincount(cell[p > 0], minlength=n).tolist(),
                     "prior_truth_weight": P.tolist(),
                     **{k: S1[k] for k in ("mc_neff_truth", "purity", "stability", "background_fraction")}},
           "vertices": {}}
    near = np.zeros(p.size, bool)
    for v in VERTICES:
        rv = R["vertices"][v]
        r = np.asarray(L.load_json(a.ratios / rv["ratio_file"])["r"], float)
        lab = np.asarray(rv["label"], dtype=object)
        cls = L.classify_cells(r, lab, shape)
        near |= np.isin(cls, ("gate", "cut"))
        with np.errstate(invalid="ignore", divide="ignore"):
            d = agg(p * r) / P - 1.0
            shares = {"own ratio": agg(p * (lab == "fine")) / P, "coarse cell": agg(p * (lab == "coarse")) / P,
                      "r = 1": agg(p * np.isin(lab, ("noisy", "off"))) / P}
            if v == "gibuu":
                shares["r = 1, p_parallel >= 10"] = agg(p * (np.isin(lab, ("noisy", "off")) & (pz_hi > 10.0))) / P
            step = {"gate": agg(p * (cls == "gate")) / P, "cut": agg(p * (cls == "cut")) / P}
        dr = d[reported]
        top = np.sort(dr ** 2)[::-1]
        out["vertices"][v] = {"departure": d.tolist(), "tier_shares": {k: x.tolist() for k, x in shares.items()},
                              "step_adjacent_shares": {k: x.tolist() for k, x in step.items()},
                              "departure_on_reported": {"median_abs": float(np.median(np.abs(dr))),
                                                        "max_abs": float(np.max(np.abs(dr))),
                                                        "n_abs_gt_0.01": int((np.abs(dr) > 0.01).sum()),
                                                        "top3_share_of_sum_sq": float(top[:3].sum() / top.sum())}}
    with np.errstate(invalid="ignore", divide="ignore"):
        out["step_adjacent_share_union"] = (agg(p * near) / P).tolist()

    def on_h2(x):
        return agg(L.integrated(x, L.AXES5))

    cl = {}
    for c in CLOSURES:
        z = np.load(a.products / f"{c}.npz", allow_pickle=True)
        meta = json.loads(str(z["meta"]))
        if meta["rung"] != RUNG or meta["arm"] != "e" or not meta["closure"]:
            raise SystemExit(f"[FAIL] {c} is not an L-5D-PV (e) closure")
        x, xt = on_h2(z["xsec_flat"]), on_h2(z["xtrue_flat"])
        alt = s1.sums(np.arange(p.size), p.size, np.arange(p.size), np.asarray(z["xtrue_flat"], float) *
                      s1.fine_volume(), np.ones(p.size, bool))
        alt = np.bincount(cell, weights=alt, minlength=n)
        b = x / xt - 1.0
        cl[c] = {"bias": b.tolist(), "aggregation_check_max_rel": float(np.max(np.abs(alt[reported] / xt[reported] - 1.0))),
                 "on_reported": {"median_abs": float(np.median(np.abs(b[reported]))),
                                 "max_abs": float(np.max(np.abs(b[reported]))),
                                 "n_abs_gt_0.01": int((np.abs(b[reported]) > MIN_BIAS).sum())}}
    out["closures"] = cl
    nb = cl["L-5D-PV_e_closure_nuwro"]["on_reported"]["n_abs_gt_0.01"]
    out["pc_power_on_h2"] = {"n_cells_abs_bias_gt_0.01": nb, "min_cells": MIN_CELLS, "powered": nb >= MIN_CELLS}
    a.out.write_text(json.dumps(out, indent=1) + "\n")

    print("cell rep   neffT  purity  stab  P-share | d GENIE+MEC  NuWro  GiBUU | GiBUU r=1 (pz>=10) | step-adj | NuWro bias  floor")
    for i in range(n):
        print(f"{i:4d} {'Y' if reported[i] else '-'} {S1['mc_neff_truth'][i]:9.0f} {S1['purity'][i]:6.3f} "
              f"{S1['stability'][i]:5.3f} {P[i] / P.sum():7.4f} | "
              + " ".join(f"{out['vertices'][v]['departure'][i]:+7.3f}" for v in VERTICES)
              + f" | {out['vertices']['gibuu']['tier_shares']['r = 1'][i]:5.2f} "
                f"({out['vertices']['gibuu']['tier_shares']['r = 1, p_parallel >= 10'][i]:4.2f}) | "
                f"{out['step_adjacent_share_union'][i]:5.2f} | "
                f"{cl[CLOSURES[0]]['bias'][i]:+7.4f} {cl[CLOSURES[1]]['bias'][i]:+8.5f}")
    for v in VERTICES:
        print(f"[s2] {v}: {out['vertices'][v]['departure_on_reported']}")
    for c in CLOSURES:
        print(f"[s2] {c}: {cl[c]['on_reported']}, aggregation check {cl[c]['aggregation_check_max_rel']:.2e}")
    print(f"[s2] PC power on H2: {out['pc_power_on_h2']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
