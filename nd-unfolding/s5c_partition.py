#!/usr/bin/env python3
"""Support and resolution of a finite hierarchy of coarse joint-5D partitions (development MC only).

Plan §5: choose the joint reporting partition J from existing physical bin edges, support and
detector resolution, using development simulations only -- never observed data or observed
generator disagreement. This reads ONLY the MC arrays of the npz (``MCgen``, ``MCreco``,
``pass_reco``, ``w_truth``, ``w_reco``); the ``measured`` array is never opened.

Hierarchy (coarse to fine; each level splits every coordinate):
  H2  = 2 x 2 x 2 x 2 x 2 (32 cells)
  H3a = 3 x 3 x 2 x 2 x 2 (72 cells)   -- muon kinematics finer
  H3b = 2 x 2 x 3 x 2 x 3 (72 cells)   -- hadronic (E_avail, W) finer
  H3  = 3 x 3 x 3 x 3 x 3 (243 cells)
Split points are the existing fine-grid edges nearest to the weighted MC-truth quantiles
(medians / tertiles) of the signal sample, so cells keep physical bin widths.

Per coordinate it reports the marginal purity and stability of each coarse bin along that
coordinate (the resolution question "does the detector permit subdividing this coordinate").
Per cell it reports the expected reco-level signal count at data POT (sum of w_reco over
reco-passing events whose reco coordinates fall in the cell), the truth count, joint purity
(fraction of reco-in-cell weight whose truth is in the same cell) and joint stability (fraction of
truth-in-cell, reco-passing weight reconstructed in the same cell).

MEASURES: development-MC support and resolution of candidate partitions. CANNOT AUTHORIZE: the
choice itself (the contract applies its frozen rule to this output) or anything about observed data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HIERARCHY = {"H2": (2, 2, 2, 2, 2), "H3a": (3, 3, 2, 2, 2), "H3b": (2, 2, 3, 2, 3), "H3": (3, 3, 3, 3, 3)}
AXES = ("pt", "pz", "eavail", "q3", "W")


def weighted_quantile(x: np.ndarray, w: np.ndarray, q: float) -> float:
    order = np.argsort(x)
    cw = np.cumsum(w[order])
    return float(x[order][np.searchsorted(cw, q * cw[-1])])


def coarse_edges(fine: np.ndarray, x: np.ndarray, w: np.ndarray, parts: int) -> np.ndarray:
    inner = []
    for k in range(1, parts):
        target = weighted_quantile(x, w, k / parts)
        candidates = fine[1:-1]
        inner.append(float(candidates[np.argmin(np.abs(candidates - target))]))
    inner = sorted(set(inner))
    return np.array([fine[0], *inner, fine[-1]])


def cell_index(coords: np.ndarray, edges: list) -> np.ndarray:
    """Flat coarse-cell index, -1 outside the grid (the fine grid's outer edges bound it)."""
    shape = [len(e) - 1 for e in edges]
    idx = []
    inside = np.ones(coords.shape[0], bool)
    for k, e in enumerate(edges):
        i = np.searchsorted(e, coords[:, k], side="right") - 1
        i = np.where(coords[:, k] == e[-1], len(e) - 2, i)  # histogramdd's closed last edge
        inside &= (i >= 0) & (i < len(e) - 1)
        idx.append(np.clip(i, 0, len(e) - 2))
    flat = np.ravel_multi_index(idx, shape)
    return np.where(inside, flat, -1)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    d = np.load(a.npz, allow_pickle=True)
    gen, reco = d["MCgen"], d["MCreco"]
    pr, wt, wr = d["pass_reco"], d["w_truth"], d["w_reco"]
    fine = [np.asarray(d[f"edges_{i}"], float) for i in range(int(d["nedges"]))]
    res = {"schema": "s5c-partition-scan/1", "inputs_read": ["MCgen", "MCreco", "pass_reco", "w_truth",
                                                           "w_reco", "edges_*"], "levels": {}}
    for name, parts in HIERARCHY.items():
        edges = [coarse_edges(fine[k], gen[:, k].astype(float), wt, parts[k]) for k in range(5)]
        n_cells = int(np.prod([len(e) - 1 for e in edges]))
        ct = cell_index(gen, edges)
        cr = np.where(pr, cell_index(reco, edges), -1)
        truth = np.bincount(ct[ct >= 0], weights=wt[ct >= 0], minlength=n_cells)
        reco_w = np.bincount(cr[cr >= 0], weights=wr[cr >= 0], minlength=n_cells)
        same = (cr >= 0) & (cr == ct)
        diag = np.bincount(cr[same], weights=wr[same], minlength=n_cells)
        truth_reco = np.bincount(ct[(ct >= 0) & pr], weights=wr[(ct >= 0) & pr], minlength=n_cells)
        with np.errstate(invalid="ignore", divide="ignore"):
            purity = np.where(reco_w > 0, diag / reco_w, 0.0)
            stability = np.where(truth_reco > 0, diag / truth_reco, 0.0)
        axis_res = {}
        for k, ax in enumerate(AXES):
            e = edges[k]
            nb = len(e) - 1
            bt = np.clip(np.searchsorted(e, gen[:, k], side="right") - 1, 0, nb - 1)
            br = np.clip(np.searchsorted(e, reco[:, k], side="right") - 1, 0, nb - 1)
            sel = pr & (ct >= 0) & (cr >= 0)
            same_ax = sel & (bt == br)
            rw = np.bincount(br[sel], weights=wr[sel], minlength=nb)
            tw = np.bincount(bt[sel], weights=wr[sel], minlength=nb)
            dw = np.bincount(br[same_ax], weights=wr[same_ax], minlength=nb)
            with np.errstate(invalid="ignore", divide="ignore"):
                axis_res[ax] = {"purity": np.where(rw > 0, dw / rw, 0.0).tolist(),
                                "stability": np.where(tw > 0, dw / tw, 0.0).tolist()}
        res["levels"][name] = {
            "axis_resolution": axis_res,
            "parts": parts,
            "edges": {ax: e.tolist() for ax, e in zip(AXES, edges)},
            "n_cells": n_cells,
            "expected_reco_signal": {"min": float(reco_w.min()), "median": float(np.median(reco_w))},
            "truth": {"min": float(truth.min())},
            "purity": {"min": float(purity.min()), "median": float(np.median(purity))},
            "stability": {"min": float(stability.min()), "median": float(np.median(stability))},
            "per_cell": {"expected_reco_signal": reco_w.tolist(), "purity": purity.tolist(),
                         "stability": stability.tolist(), "truth": truth.tolist()},
        }
    a.out.write_text(json.dumps(res))
    print(json.dumps({k: {kk: v[kk] for kk in ("n_cells", "expected_reco_signal", "purity", "stability")}
                      for k, v in res["levels"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
