#!/usr/bin/env python3
"""s5p truths built from the 5D generator predictions (docs/orchestration/state/s5p/gen5d/).

Two ratio kinds, each written as a JSON file the pseudo-experiment tools read through ``--eavail-ratio``:

``cond`` (schema ``s5p-cond-ratio/1``): a CONDITIONAL shape ratio. From two 5D predictions (numerator N,
denominator D) it forms, per fine (E_avail, W) cell, the distribution of q3 (summed over pT, p_parallel and
weighted by the cell volumes), normalizes it within the cell and writes rho(E_avail, W, q3) = N(q3 | E_avail, W)
/ D(q3 | E_avail, W). A (E_avail, W, q3) cell where either prediction is empty gets rho = 1; rho is clipped to
[0.25, 4]; both rules and their counts are recorded. The truth ``cond_ratio`` reweights MC truth rows by
r = 1 + a (rho - 1) and then RESCALES WITHIN EACH fine (E_avail, W) truth cell so that the cell's
w_truth-weighted sum is unchanged: the (E_avail, W) marginal of the truth is preserved exactly and only the
q3 dependence at fixed (E_avail, W) changes (the anchored form of the s5c q3_given_eavail_w stress).

``coarse`` (schema ``s5p-coarse-ratio/1``): a joint-5D ratio on a coarse partition (the J or H2 edges):
rho_c = N_c / D_c of cell-integrated cross sections, 1 where either is empty. The truth ``coarse_ratio``
reweights rows by rho of their coarse cell; with ``--preserve-total`` in the ratio file the in-grid total is
rescaled to be unchanged (a shape departure), otherwise the rate is kept (a generator null: the truth's
coarse-cell integrals then equal N's when D is the MC truth itself).

Rows outside the 5D grid (including the -9999 truth sentinels) keep r = 1 in both.

MEASURES: ratios between fixed predictions and truth reweights built from them. CANNOT AUTHORIZE: any
statement about which prediction describes nature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

AXES = ("pt", "pz", "eavail", "q3", "W")
CLIP = (0.25, 4.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_pred(path: Path) -> tuple[np.ndarray, list]:
    z = np.load(path, allow_pickle=True)
    if "edges_0" in z.files:
        edges = [np.asarray(z[f"edges_{i}"], float) for i in range(5)]
    else:  # the gen5d converter's naming
        edges = [np.asarray(z[f"edges_{a}"], float) for a in AXES]
    shape = tuple(len(e) - 1 for e in edges)
    return np.asarray(z["xsec_flat"], float).reshape(shape), edges


def volumes(edges: list) -> np.ndarray:
    w = [np.diff(e) for e in edges]
    return np.einsum("a,b,c,d,e->abcde", *w)


def cond_ratio(num: np.ndarray, den: np.ndarray, edges: list) -> tuple[np.ndarray, dict]:
    """rho[e, w, q] over the fine (E_avail, W, q3) cells."""
    vol = volumes(edges)
    n3 = (num * vol).sum(axis=(0, 1)).transpose(0, 2, 1)  # (eavail, W, q3)
    d3 = (den * vol).sum(axis=(0, 1)).transpose(0, 2, 1)
    ns, ds = n3.sum(axis=2, keepdims=True), d3.sum(axis=2, keepdims=True)
    ok = (n3 > 0) & (d3 > 0) & (ns > 0) & (ds > 0)
    rho = np.ones_like(n3)
    rho[ok] = (n3 / np.where(ns > 0, ns, 1))[ok] / (d3 / np.where(ds > 0, ds, 1))[ok]
    clipped = (rho < CLIP[0]) | (rho > CLIP[1])
    rho = np.clip(rho, *CLIP)
    return rho, {"cells": int(rho.size), "cells_without_shape_information": int((~ok).sum()),
                 "cells_clipped": int(clipped.sum()), "rho_min": float(rho.min()), "rho_max": float(rho.max())}


def cell_of(coords: np.ndarray, edges: list) -> tuple[np.ndarray, list]:
    ok = np.ones(coords.shape[0], bool)
    for k, e in enumerate(edges):
        ok &= (coords[:, k] >= e[0]) & (coords[:, k] <= e[-1])
    idx = [np.clip(np.searchsorted(np.asarray(e, float), coords[ok, k], side="right") - 1, 0, len(e) - 2)
           for k, e in enumerate(edges)]
    return ok, idx


def cond_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict, amplitude: float) -> np.ndarray:
    e_e, e_w, e_q = (np.asarray(x, float) for x in ratio["edges"])
    for got, want in ((e_e, edges[2]), (e_w, edges[4]), (e_q, edges[3])):
        if not np.allclose(got, np.asarray(want, float)):
            raise ValueError("the ratio's edges differ from the grid's")
    rho = np.asarray(ratio["rho"], float).reshape(len(e_e) - 1, len(e_w) - 1, len(e_q) - 1)
    ok, idx = cell_of(gen, edges)
    ie, iq, iw = idx[2], idx[3], idx[4]
    raw = 1.0 + amplitude * (rho[ie, iw, iq] - 1.0)
    if np.any(raw <= 0):
        raise ValueError("amplitude makes the reweight non-positive")
    w = np.asarray(w_truth, float)[ok]
    ew = ie * (len(e_w) - 1) + iw
    n = (len(e_e) - 1) * (len(e_w) - 1)
    s0 = np.bincount(ew, weights=w, minlength=n)
    s1 = np.bincount(ew, weights=w * raw, minlength=n)
    raw = raw * np.where(s1 > 0, s0 / np.where(s1 > 0, s1, 1), 1.0)[ew]
    r = np.ones(gen.shape[0])
    r[ok] = raw
    return r


def coarse_cells(gen: np.ndarray, edges: list, cedges: list) -> tuple[np.ndarray, np.ndarray]:
    """Coarse-cell index of every in-grid row, assigning each FINE cell by its centre (the J rows' rule)."""
    ok, idx = cell_of(gen, edges)
    cidx = []
    for k in range(5):
        f = np.asarray(edges[k], float)
        centre = 0.5 * (f[:-1] + f[1:])[idx[k]]
        c = np.asarray(cedges[k], float)
        cidx.append(np.clip(np.searchsorted(c, centre, side="right") - 1, 0, len(c) - 2))
    return ok, np.ravel_multi_index(cidx, [len(c) - 1 for c in cedges])


def coarse_integrals(x: np.ndarray, edges: list, cedges: list) -> np.ndarray:
    vol = volumes(edges)
    shape = x.shape
    grids = np.meshgrid(*[0.5 * (np.asarray(e)[:-1] + np.asarray(e)[1:]) for e in edges], indexing="ij")
    cidx = [np.clip(np.searchsorted(np.asarray(c, float), g, side="right") - 1, 0, len(c) - 2) for g, c in zip(grids, cedges)]
    cell = np.ravel_multi_index(cidx, [len(c) - 1 for c in cedges])
    return np.bincount(cell.ravel(), weights=(x * vol).ravel(), minlength=int(np.prod([len(c) - 1 for c in cedges])))


def coarse_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict, amplitude: float) -> np.ndarray:
    cedges = [np.asarray(c, float) for c in ratio["coarse_edges"]]
    rho = np.asarray(ratio["rho"], float)
    ok, cell = coarse_cells(gen, edges, cedges)
    raw = 1.0 + amplitude * (rho[cell] - 1.0)
    if np.any(raw <= 0):
        raise ValueError("amplitude makes the reweight non-positive")
    if ratio.get("preserve_total"):
        w = np.asarray(w_truth, float)[ok]
        raw *= w.sum() / (w * raw).sum()
    r = np.ones(gen.shape[0])
    r[ok] = raw
    return r


def install(s5n_pseudo) -> None:
    """Add truths ``cond_ratio`` and ``coarse_ratio`` to s5n_pseudo.truth_weight (resolved at call time)."""
    original = s5n_pseudo.truth_weight
    if getattr(original, "_s5p_truths", False):
        return

    def dispatch(name, inputs, amplitude, r):
        if name == "cond_ratio":
            if r is None or r.get("schema") != "s5p-cond-ratio/1":
                raise ValueError("cond_ratio needs an s5p-cond-ratio/1 file via --eavail-ratio")
            return cond_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], r, amplitude)
        if name == "coarse_ratio":
            if r is None or r.get("schema") != "s5p-coarse-ratio/1":
                raise ValueError("coarse_ratio needs an s5p-coarse-ratio/1 file via --eavail-ratio")
            return coarse_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], r, amplitude)
        return original(name, inputs, amplitude, r)

    dispatch._s5p_truths = True
    s5n_pseudo.truth_weight = dispatch
    for t in ("cond_ratio", "coarse_ratio"):
        if t not in s5n_pseudo.TRUTHS:
            s5n_pseudo.TRUTHS = tuple(s5n_pseudo.TRUTHS) + (t,)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--kind", choices=("cond", "coarse"), required=True)
    ap.add_argument("--numerator", type=Path, required=True, help="5D prediction npz (gen5d)")
    ap.add_argument("--denominator", type=Path, required=True, help="5D prediction npz (gen5d) or an MC-truth npz of the same form")
    ap.add_argument("--coarse-edges", default=None, help="JSON list of five edge lists (kind coarse)")
    ap.add_argument("--preserve-total", action="store_true")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.out.exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    num, edges = load_pred(a.numerator)
    den, edges_d = load_pred(a.denominator)
    for x, y in zip(edges, edges_d):
        if not np.allclose(x, y):
            raise SystemExit("the two predictions are on different grids")
    out = {"label": a.label, "numerator": {"path": str(a.numerator), "sha256": sha256(a.numerator)},
           "denominator": {"path": str(a.denominator), "sha256": sha256(a.denominator)},
           "code_sha256": sha256(Path(__file__).resolve())}
    if a.kind == "cond":
        rho, stats = cond_ratio(num, den, edges)
        out.update({"schema": "s5p-cond-ratio/1", "axes": ["eavail", "W", "q3"],
                    "edges": [edges[2].tolist(), edges[4].tolist(), edges[3].tolist()],
                    "definition": "rho = N(q3 | E_avail, W) / D(q3 | E_avail, W) per fine cell (C order eavail, W, q3), volumes included; 1 where either is empty; clipped to [0.25, 4]; the truth reweight is renormalized within each fine (E_avail, W) cell",
                    "rho": rho.ravel(order="C").tolist(), "stats": stats})
    else:
        cedges = [np.asarray(c, float) for c in json.loads(a.coarse_edges)]
        n_c, d_c = coarse_integrals(num, edges, cedges), coarse_integrals(den, edges, cedges)
        ok = (n_c > 0) & (d_c > 0)
        rho = np.ones_like(n_c)
        rho[ok] = n_c[ok] / d_c[ok]
        out.update({"schema": "s5p-coarse-ratio/1", "coarse_edges": [c.tolist() for c in cedges],
                    "preserve_total": bool(a.preserve_total), "rho": rho.tolist(),
                    "numerator_cell_integrals": n_c.tolist(), "denominator_cell_integrals": d_c.tolist(),
                    "definition": "rho_c = N_c / D_c of coarse-cell integrated cross sections (fine cells assigned by centre); 1 where either is empty",
                    "stats": {"cells": int(rho.size), "cells_without_information": int((~ok).sum()),
                              "rho_min": float(rho[ok].min()) if ok.any() else None, "rho_max": float(rho[ok].max()) if ok.any() else None}})
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"label": a.label, "kind": a.kind, **out["stats"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
