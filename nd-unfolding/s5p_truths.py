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

``fine`` (schema ``s5p-fine-ratio/1``; review round 1 F2): a generator null at the FINE resolution, so that the
null truth's within-J-cell shapes are the generator's own and not MnvTune's. Per fine cell f of a supported coarse
cell c, rho_f = N_f / D_f where both predictions have >= ``n_min`` events in f and the ratio lies in the clip range
(a "resolved" fine cell, clip [0.1, 10]); the other fine cells of c with D_f > 0 share rho_fb,c = (N_c - sum_resolved
N_f) / (sum D_f), so the coarse integral of the reweighted truth is N_c EXACTLY; if rho_fb,c exceeds 10, or
no unresolved cell with D_f > 0 exists while a remainder does, the whole coarse cell takes the coarse rho_c. Cells
outside ``only_cells`` keep rho = 1. rho (65,856 values) is written to an npz whose sha256 the JSON records and the
reader verifies. The truth ``fine_ratio`` reweights rows by rho of their fine cell (rate kept).

Rows outside the 5D grid (including the -9999 truth sentinels) keep r = 1 in every kind.

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


FINE_CLIP = (0.1, 10.0)  # a resolved fine cell's ratio
FINE_FALLBACK_CLIP = (0.0, 10.0)  # the shared remainder ratio (a generator empty there legitimately empties it)
FINE_N_MIN = 20


def load_counts(path: Path) -> np.ndarray:
    return np.asarray(np.load(path, allow_pickle=True)["nevt_flat"], float)


def fine_cell_of_fine_grid(edges: list, cedges: list) -> np.ndarray:
    """The coarse cell of every fine cell (by centre, the J rows' rule), C order."""
    grids = np.meshgrid(*[0.5 * (np.asarray(e)[:-1] + np.asarray(e)[1:]) for e in edges], indexing="ij")
    cidx = [np.clip(np.searchsorted(np.asarray(c, float), g, side="right") - 1, 0, len(c) - 2) for g, c in zip(grids, cedges)]
    return np.ravel_multi_index(cidx, [len(c) - 1 for c in cedges]).ravel()


def fine_ratio(num: np.ndarray, den: np.ndarray, n_num: np.ndarray, n_den: np.ndarray, edges: list, cedges: list,
               only: np.ndarray, n_min: int = FINE_N_MIN, clip: tuple = FINE_CLIP,
               fallback_clip: tuple = FINE_FALLBACK_CLIP) -> tuple[np.ndarray, dict]:
    """rho over the fine grid (flat, C order) and the construction's accounting."""
    vol = volumes(edges).ravel()
    N, D = num.ravel() * vol, den.ravel() * vol
    cell = fine_cell_of_fine_grid(edges, cedges)
    ncell = int(np.prod([len(c) - 1 for c in cedges]))
    r = np.where(D > 0, N / np.where(D > 0, D, 1.0), 0.0)
    resolved = (n_num.ravel() >= n_min) & (n_den.ravel() >= n_min) & (N > 0) & (D > 0) & (r >= clip[0]) & (r <= clip[1])
    rho = np.ones(N.size)
    acc = {"coarse_cells_carrying": 0, "coarse_cells_reverted_to_coarse": 0, "fine_cells_resolved": 0,
           "fine_cells_fallback": 0, "N_in_carrying_cells": 0.0, "N_in_resolved_fine_cells": 0.0,
           "max_abs_coarse_integral_error_rel": 0.0}
    for c in np.flatnonzero(only):
        inc = cell == c
        Nc, Dc = N[inc].sum(), D[inc].sum()
        if not (Nc > 0 and Dc > 0):
            continue
        acc["coarse_cells_carrying"] += 1
        acc["N_in_carrying_cells"] += float(Nc)
        ok = inc & resolved
        fb = inc & ~resolved & (D > 0)
        rem = Nc - N[ok].sum()
        dfb = D[fb].sum()
        rfb = rem / dfb if dfb > 0 else None
        if (rfb is None and abs(rem) > 1e-12 * Nc) or (rfb is not None and not (fallback_clip[0] <= rfb <= fallback_clip[1])):
            rho[inc] = Nc / Dc
            acc["coarse_cells_reverted_to_coarse"] += 1
        else:
            rho[ok] = r[ok]
            if rfb is not None:
                rho[fb] = rfb
            acc["fine_cells_resolved"] += int(ok.sum())
            acc["fine_cells_fallback"] += int(fb.sum())
            acc["N_in_resolved_fine_cells"] += float(N[ok].sum())
        err = abs((rho[inc] * D[inc]).sum() / Nc - 1.0)
        acc["max_abs_coarse_integral_error_rel"] = max(acc["max_abs_coarse_integral_error_rel"], float(err))
    acc["fraction_of_N_in_resolved_fine_cells"] = acc["N_in_resolved_fine_cells"] / acc["N_in_carrying_cells"] if acc["N_in_carrying_cells"] else None
    acc.update({"n_min": n_min, "clip": list(clip), "fallback_clip": list(fallback_clip), "rho_min": float(rho.min()), "rho_max": float(rho.max())})
    return rho, acc


def load_fine_rho(ratio: dict) -> np.ndarray:
    path = Path(ratio["rho_npz"]["path"])
    if sha256(path) != ratio["rho_npz"]["sha256"]:
        raise ValueError(f"{path}: digest differs from the fine-ratio file's")
    return np.asarray(np.load(path, allow_pickle=False)["rho"], float)


def fine_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict, amplitude: float = 1.0) -> np.ndarray:
    fe = [np.asarray(e, float) for e in ratio["fine_edges"]]
    for got, want in zip(fe, edges):
        if not np.allclose(got, np.asarray(want, float)):
            raise ValueError("the ratio's fine edges differ from the grid's")
    rho = load_fine_rho(ratio)
    ok, idx = cell_of(gen, edges)
    raw = 1.0 + amplitude * (rho[np.ravel_multi_index(idx, [len(e) - 1 for e in fe])] - 1.0)
    if np.any(raw <= 0):
        raise ValueError("amplitude makes the reweight non-positive")
    r = np.ones(gen.shape[0])
    r[ok] = raw
    return r


def hypothesis_weight(gen: np.ndarray, edges: list, w_truth: np.ndarray, ratio: dict, amplitude: float = 1.0) -> np.ndarray:
    """The null-truth reweight of a hypothesis file of either generator-null kind."""
    if ratio.get("schema") == "s5p-fine-ratio/1":
        return fine_weight(gen, edges, w_truth, ratio, amplitude)
    if ratio.get("schema") == "s5p-coarse-ratio/1":
        return coarse_weight(gen, edges, w_truth, ratio, amplitude)
    raise ValueError(f"not a generator-null ratio file: {ratio.get('schema')}")


def install(s5n_pseudo) -> None:
    """Add truths ``cond_ratio``, ``coarse_ratio`` and ``fine_ratio`` to s5n_pseudo.truth_weight (resolved at call time)."""
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
        if name == "fine_ratio":
            if r is None or r.get("schema") != "s5p-fine-ratio/1":
                raise ValueError("fine_ratio needs an s5p-fine-ratio/1 file via --eavail-ratio")
            return fine_weight(inputs["MCgen"], inputs["edges"], inputs["w_truth"], r, amplitude)
        return original(name, inputs, amplitude, r)

    dispatch._s5p_truths = True
    s5n_pseudo.truth_weight = dispatch
    for t in ("cond_ratio", "coarse_ratio", "fine_ratio"):
        if t not in s5n_pseudo.TRUTHS:
            s5n_pseudo.TRUTHS = tuple(s5n_pseudo.TRUTHS) + (t,)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--kind", choices=("cond", "coarse", "fine"), required=True)
    ap.add_argument("--numerator", type=Path, required=True, help="5D prediction npz (gen5d)")
    ap.add_argument("--denominator", type=Path, required=True, help="5D prediction npz (gen5d) or an MC-truth npz of the same form")
    ap.add_argument("--coarse-edges", default=None, help="JSON list of five edge lists (kinds coarse and fine)")
    ap.add_argument("--rho-out", type=Path, default=None, help="kind fine: the npz that receives rho")
    ap.add_argument("--preserve-total", action="store_true")
    ap.add_argument("--only-cells", default=None,
                    help="JSON list of coarse cell indices that carry the ratio; every other cell keeps rho = 1 (kind coarse)")
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
    elif a.kind == "fine":
        if a.rho_out is None or a.only_cells is None or a.rho_out.exists():
            raise SystemExit("kind fine needs --only-cells and a new --rho-out")
        cedges = [np.asarray(c, float) for c in json.loads(a.coarse_edges)]
        only = np.zeros(int(np.prod([len(c) - 1 for c in cedges])), bool)
        only[np.asarray(json.loads(a.only_cells), int)] = True
        rho, stats = fine_ratio(num, den, load_counts(a.numerator), load_counts(a.denominator), edges, cedges, only)
        np.savez_compressed(a.rho_out, rho=rho)
        out.update({"schema": "s5p-fine-ratio/1", "fine_edges": [e.tolist() for e in edges],
                    "coarse_edges": [c.tolist() for c in cedges], "only_cells": json.loads(a.only_cells),
                    "rho_npz": {"path": str(a.rho_out), "sha256": sha256(a.rho_out)},
                    "definition": "rho_f = N_f / D_f on resolved fine cells (>= n_min events in both, ratio in clip); the other fine cells of the coarse cell share the remainder so the coarse integral is N_c exactly; a coarse cell whose remainder ratio leaves fallback_clip takes rho_c; rho = 1 outside only_cells; rate kept",
                    "numerator_cell_integrals": coarse_integrals(num, edges, cedges).tolist(),
                    "denominator_cell_integrals": coarse_integrals(den, edges, cedges).tolist(), "stats": stats})
    else:
        cedges = [np.asarray(c, float) for c in json.loads(a.coarse_edges)]
        n_c, d_c = coarse_integrals(num, edges, cedges), coarse_integrals(den, edges, cedges)
        ok = (n_c > 0) & (d_c > 0)
        if a.only_cells is not None:
            only = np.zeros(ok.size, bool)
            only[np.asarray(json.loads(a.only_cells), int)] = True
            ok &= only
        rho = np.ones_like(n_c)
        rho[ok] = n_c[ok] / d_c[ok]
        out.update({"schema": "s5p-coarse-ratio/1", "coarse_edges": [c.tolist() for c in cedges],
                    "preserve_total": bool(a.preserve_total), "only_cells": None if a.only_cells is None else json.loads(a.only_cells),
                    "rho": rho.tolist(),
                    "numerator_cell_integrals": n_c.tolist(), "denominator_cell_integrals": d_c.tolist(),
                    "definition": "rho_c = N_c / D_c of coarse-cell integrated cross sections (fine cells assigned by centre); 1 where either is empty",
                    "stats": {"cells": int(rho.size), "cells_without_information": int((~ok).sum()),
                              "rho_min": float(rho[ok].min()) if ok.any() else None, "rho_max": float(rho[ok].max()) if ok.any() else None}})
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"label": a.label, "kind": a.kind, **out["stats"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
