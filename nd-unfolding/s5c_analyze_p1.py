#!/usr/bin/env python3
"""Summarize pilot P1 (single-unfold seed channel, reproducibility, cost) from its products.

Reads the ``s5c_unfold.py`` products of ``state/s5c/p1-tasks.tsv`` and reports, on the 43 M1
functionals (the 42 (E_avail,W) destination rows of ``project_cov_nd.build_projection`` over the
full 65,856-cell grid, whose cells outside the support contribute zero, plus the all-ones row) and
on the bins with a positive central value:

* F1 (production) seed spread over seeds 42..51: relative standard deviation per functional and
  per bin (median, p90, max), and the total cross section's;
* the seed channel: |x(seed 42) - x(seed 43)| for production, full-binning and deterministic;
* repeat-run reproducibility (same seed twice) for production and deterministic;
* row-order permutation sensitivity of the deterministic configuration;
* wall time per configuration.

MEASURES: single-unfold central-value behaviour only. CANNOT AUTHORIZE: any covariance-stability,
coverage or adoption statement (a covariance's seed stability needs complete constructions).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

import project_cov_nd as pc

AXES = ["pt", "pz", "eavail", "q3", "W"]


def functionals() -> np.ndarray:
    shape = tuple(len(pc.AXIS_EDGES[a]) - 1 for a in AXES)
    n = int(np.prod(shape))
    all_cells = np.arange(n)
    dst_shape = (shape[2], shape[4])
    idx = np.unravel_index(all_cells, shape)
    hit = np.unique(np.ravel_multi_index((idx[2], idx[4]), dst_shape))
    dst_index_of = -np.ones(int(np.prod(dst_shape)), dtype=int)
    dst_index_of[hit] = np.arange(hit.size)
    M, dropped = pc.build_projection(AXES, ["eavail", "W"], all_cells, shape, dst_shape, dst_index_of)
    assert dropped == 0 and M.shape == (42, n)
    return M


def load(directory: Path) -> dict:
    out = {}
    for f in sorted(directory.glob("*.npz")):
        z = np.load(f, allow_pickle=False)
        out[f.stem] = {"x": z["xsec_flat"], "meta": json.loads(str(z["meta"]))}
    return out


def rel(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> dict:
    d = np.abs(a[mask] - b[mask]) / np.abs(b[mask])
    return {"bitwise_equal": bool(np.array_equal(a, b)), "max": float(d.max()),
            "median": float(np.median(d)), "p90": float(np.quantile(d, 0.9))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--products", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    P = load(a.products)
    M = functionals()
    ones = np.ones((1, M.shape[1]))
    U = np.vstack([M, ones])
    res = {"schema": "s5c-p1-summary/1", "products": sorted(P), "n_functionals": int(U.shape[0])}
    base = P["f1_s42"]["x"]
    mask = base > 0
    res["n_bins_positive"] = int(mask.sum())

    seeds = [k for k in P if k.startswith("f1_s") and not k.endswith("_rep")]
    X = np.array([P[k]["x"] for k in seeds])
    F = X @ U.T
    fmean, fstd = F.mean(0), F.std(0, ddof=1)
    frel = fstd / np.abs(fmean)
    bm = X[:, mask]
    brel = bm.std(0, ddof=1) / np.abs(bm.mean(0))
    tot = np.array([P[k]["meta"]["total_xsec"] for k in seeds])
    res["f1_seed_spread"] = {
        "seeds": seeds,
        "functional_rel_std": {"max": float(frel.max()), "median": float(np.median(frel)),
                               "argmax": int(frel.argmax()), "all_ones_row": float(frel[-1])},
        "bin_rel_std": {"median": float(np.median(brel)), "p90": float(np.quantile(brel, 0.9)),
                        "max": float(brel.max())},
        "total_xsec_rel_std": float(tot.std(ddof=1) / tot.mean()),
    }
    pairs = {
        "production_s42_vs_s43": ("f1_s42", "f1_s43"),
        "full_binning_s42_vs_s43": ("fb_s42", "fb_s43"),
        "deterministic_s42_vs_s43": ("f2_s42", "f2_s43"),
        "production_repeat_s42": ("f1_s42", "f1_s42_rep"),
        "deterministic_repeat_s42": ("f2_s42", "f2_s42_rep"),
        "deterministic_perm1": ("f2_s42", "f2_s42_perm1"),
        "deterministic_perm2": ("f2_s42", "f2_s42_perm2"),
        "full_binning_vs_production_s42": ("fb_s42", "f1_s42"),
        "deterministic_vs_production_s42": ("f2_s42", "f1_s42"),
    }
    res["pairs"] = {}
    for name, (i, j) in pairs.items():
        if i in P and j in P:
            fi, fj = U @ P[i]["x"], U @ P[j]["x"]
            res["pairs"][name] = {"bins": rel(P[i]["x"], P[j]["x"], mask),
                                  "functionals_max_rel": float(np.max(np.abs(fi - fj) / np.abs(fj)))}
    res["seconds_unfold"] = {k: P[k]["meta"]["seconds_unfold"] for k in P}
    res["threads"] = {k: P[k]["meta"]["threads"] for k in P}
    a.out.write_text(json.dumps(res, indent=1))
    print(json.dumps({"f1_seed_spread": res["f1_seed_spread"]["functional_rel_std"],
                      "pairs": {k: (v["bins"]["bitwise_equal"], v["bins"]["max"], v["functionals_max_rel"])
                                for k, v in res["pairs"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
