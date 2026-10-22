#!/usr/bin/env python3
"""RE-1 movement table for the higher-dimensional central values: configuration (e) against the purity ones.

    re1_nd_movement.py --dim {3,4,5} --e E.npz --c C.npz --current CUR.root \
        --expect-e-sha256 S --expect-c-sha256 S --expect-current-sha256 S \
        [--trunk z-cv.npz --expect-trunk-sha256 S] --out movement.json [--tsv cells.tsv]

Three central values per dimension, on the same fine grid:

* (e): ``s5e_candidate.py --candidate R -- ... --bkg-mode negweight-refined --data`` (deterministic
  LightGBM, refinement 400 trees / 31 leaves), the RE-1 product;
* (c): ``s5n_pseudo.py --bkg-mode purity --data`` on the same npz: the same deterministic estimator with
  purity subtraction, so (e) - (c) is the background treatment alone;
* (a): the deliverables' current central value (3D: the 3D driver's ``hXSec3D``; 4D and 5D: the ND
  driver's ``hXSecND_flat``), so (e) - (a) is what the deliverables would see.

The cells are those where (a), (c) and (e) are all positive. The movement is relative, per cell and
integrated over the grid's bin volumes. Only for 5D does a quotable total uncertainty exist: the
adopted trunk ``3d7465f6...`` (``hCov_combined5d_total_uthrow`` on its 10,694-cell support, rows mapped by
``hRowIndex5D``), whose four travelling measurements (adoption record section 4) apply to anything
quoted in its units. No 3D or 4D covariance is quotable (AGENTS.md), so those rows are relative only.

MEASURES: the declared movement. CANNOT AUTHORIZE: an adoption, a claim, or a judgement on whether the
background-treatment obligation is met (the director takes the table to Joseph).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SHAPES = {3: (14, 16, 7), 4: (14, 16, 7, 7), 5: (14, 16, 7, 7, 6)}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def load_product(path: Path, shape: tuple, want: dict) -> tuple[np.ndarray, dict]:
    d = np.load(path, allow_pickle=False)
    meta = json.loads(str(d["meta"]))
    if tuple(int(s) for s in d["shape"]) != shape:
        raise RuntimeError(f"{path}: shape {tuple(d['shape'])} != {shape}")
    for key, value in want.items():
        if meta.get(key) != value:
            raise RuntimeError(f"{path}: meta {key}={meta.get(key)!r}, wanted {value!r}")
    return np.asarray(d["xsec_flat"], float), meta


def load_current(path: Path, dim: int, shape: tuple) -> np.ndarray:
    import ROOT
    f = ROOT.TFile.Open(str(path), "READ")
    if dim == 3:
        h = f.Get("hXSec3D")
        arr = np.array([[[h.GetBinContent(i, j, k) for k in range(1, shape[2] + 1)]
                         for j in range(1, shape[1] + 1)] for i in range(1, shape[0] + 1)])
        flat = arr.ravel(order="C")
    else:
        h = f.Get("hXSecND_flat")
        flat = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
    f.Close()
    if flat.size != int(np.prod(shape)):
        raise RuntimeError(f"{path}: {flat.size} cells, wanted {int(np.prod(shape))}")
    return flat


def volumes(edges: list) -> np.ndarray:
    v = np.ones(1)
    for e in edges:
        v = np.multiply.outer(v, np.diff(np.asarray(e, float)))
    return v.ravel(order="C")


def dist(x: np.ndarray) -> dict:
    a = np.abs(x)
    return {"median_abs": float(np.median(a)), "p84_abs": float(np.percentile(a, 84)),
            "p98_abs": float(np.percentile(a, 98)), "max_abs": float(a.max()), "mean_signed": float(x.mean()),
            "n_over_1": int((a > 1).sum()), "n_over_2": int((a > 2).sum())}


def pair(top: np.ndarray, base: np.ndarray, cells: np.ndarray, vol: np.ndarray, sigma: np.ndarray | None) -> dict:
    d = top[cells] - base[cells]
    rel = 100.0 * d / base[cells]
    out = {"relative_percent": dist(rel),
           "integral_change_percent": float(100.0 * ((vol[cells] @ top[cells]) / (vol[cells] @ base[cells]) - 1.0))}
    if sigma is not None:
        out["in_trunk_total_sigma"] = dist(d / sigma)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--dim", type=int, choices=sorted(SHAPES), required=True)
    for k in ("e", "c"):
        ap.add_argument(f"--{k}", type=Path, required=True)
        ap.add_argument(f"--expect-{k}-sha256", required=True)
    ap.add_argument("--current", type=Path, required=True)
    ap.add_argument("--expect-current-sha256", required=True)
    ap.add_argument("--edges-npz", type=Path, required=True, help="the of_inputs npz the products were unfolded from")
    ap.add_argument("--trunk", type=Path)
    ap.add_argument("--expect-trunk-sha256")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tsv", type=Path)
    a = ap.parse_args(argv)
    shape = SHAPES[a.dim]
    files = {"e": a.e, "c": a.c, "current": a.current}
    want = {"e": a.expect_e_sha256, "c": a.expect_c_sha256, "current": a.expect_current_sha256}
    if a.trunk:
        if a.dim != 5:
            print("the trunk is 5D", file=sys.stderr)
            return 2
        files["trunk"], want["trunk"] = a.trunk, a.expect_trunk_sha256
    got = {k: sha256_path(p) for k, p in files.items()}
    if got != want:
        print(f"input digests {got} differ from {want}", file=sys.stderr)
        return 4
    xe, me = load_product(a.e, shape, {"bkg_mode": "negweight-refined", "config": "deterministic", "data": True})
    xc, mc = load_product(a.c, shape, {"bkg_mode": "purity", "config": "deterministic", "data": True})
    cp = me["refinement"]["classifier_params"]
    if (cp.get("n_estimators"), cp.get("num_leaves")) != (400, 31) or me["code_sha256"].get("candidate") != "R":
        raise RuntimeError(f"(e) is not candidate R at 400/31: {cp}")
    if me["input_npz_sha256"] != mc["input_npz_sha256"] or me["estimator_seed"] != mc["estimator_seed"]:
        raise RuntimeError("(e) and (c) were unfolded from different inputs or seeds")
    xa = load_current(a.current, a.dim, shape)
    e = np.load(a.edges_npz, allow_pickle=True)
    if sha256_path(a.edges_npz) != me["input_npz_sha256"]:
        raise RuntimeError("--edges-npz is not the npz the products were unfolded from")
    edges = [np.asarray(e[f"edges_{i}"], float) for i in range(int(e["nedges"]))]
    vol = volumes(edges)
    cells = np.flatnonzero((xa > 0) & (xc > 0) & (xe > 0))
    sigma = None
    out = {"schema": "re1-nd-movement/1", "dim": a.dim, "inputs_sha256": got, "n_grid": int(np.prod(shape)),
           "n_cells_all_positive": int(cells.size), "estimator_seed": me["estimator_seed"],
           "refinement_e": {k: me["refinement"].get(k) for k in ("clipped_fraction", "refined_over_signed")},
           "code_sha256": sha256_path(Path(__file__).resolve())}
    if a.trunk:
        z = np.load(a.trunk, allow_pickle=False)
        rows = np.asarray(z["hRowIndex5D"], int)
        sig_flat = np.full(int(np.prod(shape)), np.nan)
        sig_flat[rows] = np.sqrt(np.diag(z["hCov_combined5d_total_uthrow"]))
        keep = np.isin(cells, rows)
        out["n_cells_on_trunk_support"] = int(keep.sum())
        out["trunk_central_equals_current"] = bool(np.array_equal(np.asarray(z["hXSecND_flat"], float), xa))
        cells_t = cells[keep]
        sigma = sig_flat[cells_t]
        out["e_minus_c_on_trunk_support"] = pair(xe, xc, cells_t, vol, sigma)
        out["e_minus_a_on_trunk_support"] = pair(xe, xa, cells_t, vol, sigma)
    out["e_minus_c"] = pair(xe, xc, cells, vol, None)
    out["e_minus_a"] = pair(xe, xa, cells, vol, None)
    out["c_minus_a"] = pair(xc, xa, cells, vol, None)
    a.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    if a.tsv:
        idx = np.unravel_index(cells, shape)
        with open(a.tsv, "w") as fh:
            fh.write("flat\t" + "\t".join(f"i{k}" for k in range(a.dim)) + "\ta\tc\te\trel_e_c_pct\trel_e_a_pct\n")
            for n, f in enumerate(cells):
                fh.write(f"{f}\t" + "\t".join(str(int(i[n])) for i in idx)
                         + f"\t{xa[f]:.10e}\t{xc[f]:.10e}\t{xe[f]:.10e}\t{100 * (xe[f] / xc[f] - 1):.6f}"
                         f"\t{100 * (xe[f] / xa[f] - 1):.6f}\n")
    print(json.dumps({"dim": a.dim, "cells": int(cells.size),
                      "e_minus_c_median_abs_pct": out["e_minus_c"]["relative_percent"]["median_abs"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
