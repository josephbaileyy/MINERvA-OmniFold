#!/usr/bin/env python3
"""s5e withheld physical deformations W2 and W3: multi-dimensional generator shape ratios.

Contract ``stage_A_assessment.withheld_physical_deformations``: W2 is GENIE MEC over GENIE CV in
(E_avail, W) (``hXSec_eavailW``); W3 is NuWro over GENIE v2 in (pT, p_parallel, E_avail)
(``hXSec3D``). W1 (NuWro/GENIE E_avail) is the committed 1D ratio used through
``s5n_pseudo.eavail_ratio_weight``.

``build``: reads the two predictions on the analysis binning (the edges must equal the grid's), converts
each to per-cell cross-section fractions (content x cell volume, normalized over the cells) and writes
``shape_ratio = frac_num / frac_den`` per cell. A cell where either prediction is non-positive gets
ratio 1 (it carries no shape information); every ratio is then clipped to [0.25, 4] as a positivity
guard; both rules and the counts they touch are recorded. No unfold output is read.

``ratio_weight``: r = 1 + a (rho_cell - 1) on truth rows inside the 5D grid (cell from the ratio's
axes), then one constant rescales the in-grid rows so the w_truth-weighted in-grid total is unchanged
(a pure shape departure); rows outside the grid keep r = 1 -- the same convention as the E_avail ratio.

MEASURES: a shape ratio between two fixed predictions and its truth reweight. CANNOT AUTHORIZE: any
statement about which generator describes nature; W2/W3 are known-truth departures only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

AXIS_NAMES = ("pt", "pz", "eavail", "q3", "W")
KINDS = {"eavailW": ("hXSec_eavailW", (2, 4)), "pt_pz_eavail": ("hXSec3D", (0, 1, 2))}
CLIP = (0.25, 4.0)


def ratio_from_contents(num: np.ndarray, den: np.ndarray, vol: np.ndarray) -> tuple[np.ndarray, dict]:
    num, den, vol = (np.asarray(x, float) for x in (num, den, vol))
    ok = (num > 0) & (den > 0)
    fn = np.where(ok, num * vol, 0.0)
    fd = np.where(ok, den * vol, 0.0)
    fn, fd = fn / fn.sum(), fd / fd.sum()
    rho = np.ones_like(num)
    rho[ok] = fn[ok] / fd[ok]
    clipped = (rho < CLIP[0]) | (rho > CLIP[1])
    rho = np.clip(rho, *CLIP)
    return rho, {"cells": int(rho.size), "cells_without_shape_information": int((~ok).sum()),
                 "cells_clipped": int(clipped.sum()), "rho_min": float(rho.min()), "rho_max": float(rho.max())}


def ratio_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict, amplitude: float) -> np.ndarray:
    axes = [int(a) for a in ratio["axes"]]
    for a, e in zip(axes, ratio["edges"]):
        if not np.allclose(np.asarray(e, float), np.asarray(edges[a], float)):
            raise ValueError(f"the ratio's {AXIS_NAMES[a]} edges differ from the grid's")
    rho = np.asarray(ratio["shape_ratio"], float).reshape([len(edges[a]) - 1 for a in axes])
    if np.any(rho <= 0):
        raise ValueError("shape_ratio must be positive")
    ok = np.ones(gen.shape[0], bool)
    for k in range(gen.shape[1]):
        ek = np.asarray(edges[k], float)
        ok &= (gen[:, k] >= ek[0]) & (gen[:, k] <= ek[-1])
    idx = tuple(np.clip(np.searchsorted(np.asarray(edges[a], float), gen[ok, a], side="right") - 1, 0, len(edges[a]) - 2)
                for a in axes)
    raw = 1.0 + amplitude * (rho[idx] - 1.0)
    if np.any(raw <= 0):
        raise ValueError("amplitude makes the reweight non-positive")
    w = np.asarray(w_truth, float)[ok]
    raw *= w.sum() / (w * raw).sum()
    r = np.ones(gen.shape[0])
    r[ok] = raw
    return r


def install_ratio_truth(s5n_pseudo) -> None:
    """Add truth ``ratio_nd`` to ``s5n_pseudo``: ``truth_weight`` (resolved at call time by
    ``build_pseudo``) dispatches it to ``ratio_weight`` with the ratio loaded from ``--eavail-ratio``;
    every other truth name is handled by the original function unchanged."""
    original = s5n_pseudo.truth_weight
    if getattr(original, "_s5e_ratio_nd", False):
        return

    def dispatch(name, inputs, amplitude, r):
        if name == "ratio_nd":
            if r is None or r.get("schema") != "s5e-shape-ratio/1":
                raise ValueError("ratio_nd needs an s5e-shape-ratio/1 file via --eavail-ratio")
            return ratio_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], r, amplitude)
        return original(name, inputs, amplitude, r)

    dispatch._s5e_ratio_nd = True
    s5n_pseudo.truth_weight = dispatch
    if "ratio_nd" not in s5n_pseudo.TRUTHS:
        s5n_pseudo.TRUTHS = tuple(s5n_pseudo.TRUTHS) + ("ratio_nd",)


def read_hist(path: Path, name: str):
    import ROOT

    f = ROOT.TFile.Open(str(path), "READ")
    h = f.Get(name)
    if not h:
        raise SystemExit(f"{path}: no {name}")
    axes = [h.GetXaxis(), h.GetYaxis()] + ([h.GetZaxis()] if h.InheritsFrom("TH3") else [])
    edges = [[a.GetBinLowEdge(i + 1) for i in range(a.GetNbins())] + [a.GetBinUpEdge(a.GetNbins())] for a in axes]
    shape = [len(e) - 1 for e in edges]
    c = np.zeros(shape)
    for ijk in np.ndindex(*shape):
        c[ijk] = h.GetBinContent(h.GetBin(*[i + 1 for i in ijk]))
    f.Close()
    return edges, c


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--kind", choices=sorted(KINDS), required=True)
    ap.add_argument("--numerator", type=Path, required=True)
    ap.add_argument("--denominator", type=Path, required=True)
    ap.add_argument("--grid-npz", type=Path, required=True, help="the analysis inputs (edges only)")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    hname, axes = KINDS[a.kind]
    en, cn = read_hist(a.numerator, hname)
    ed, cd = read_hist(a.denominator, hname)
    z = np.load(a.grid_npz, allow_pickle=True)
    grid = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    for x, y, ax in zip(en, ed, axes):
        if not (np.allclose(x, y) and np.allclose(x, grid[ax])):
            raise SystemExit(f"{AXIS_NAMES[ax]} binning differs between the predictions or from the grid")
    vol = np.ones(cn.shape)
    for d, ax in enumerate(axes):
        w = np.diff(grid[ax])
        vol = vol * w.reshape([-1 if i == d else 1 for i in range(len(axes))])
    rho, stats = ratio_from_contents(cn, cd, vol)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    out = {"schema": "s5e-shape-ratio/1", "label": a.label, "kind": a.kind, "histogram": hname,
           "axes": list(axes), "edges": [grid[ax].tolist() for ax in axes],
           "definition": "shape_ratio = frac_num / frac_den per cell (C order), frac = content x cell volume normalized over cells with both predictions positive; ratio 1 where either is non-positive; clipped to [0.25, 4]",
           "shape_ratio": rho.ravel(order="C").tolist(), "stats": stats,
           "numerator": {"path": str(a.numerator), "sha256": digest(a.numerator)},
           "denominator": {"path": str(a.denominator), "sha256": digest(a.denominator)},
           "code_sha256": digest(Path(__file__).resolve())}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"label": a.label, **stats}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
