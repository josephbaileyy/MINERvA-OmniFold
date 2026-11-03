#!/usr/bin/env python3
"""1B A2.1, the director's items 3 and 4 on (e2): the 16 denominator rows that change cell between cv.npz's float32
td_* and the source's float64 coordinates (fd_1b_cvdenom's PASS record), carried to the level 1B grades, U x_T, in
units of S1's reported sigma_c. Descriptive; login node, single-threaded numpy.

* Item 3: each moved row's two fine cells through the H2 map (one reporting cell or a boundary), and its effect on
  U x_T at each truth's nominal x_T when the CV's weight moves with it; also all 16 together, the difference between
  the nominal denominator (float64 binning) and (e2)'s d_CV (float32 binning), which the stat role's and the central
  values' nominal natures carry against the toys' composites.
* Item 4: per declared draw, the composite denominator's offsets, exactly, by two identities (tested):
  amendment 2 as bound minus (e2) = ((k - 1) - n_det) Delta_CV, n_det the detector universes after the first; and
  (e2) minus a float64-binned composite = sum over moved rows of tdw_D,row (e_cell32 - e_cell64), tdw_D,row the
  row's first-order composite over the draw's bank universes (a detector universe brings the CV's row). Their effect
  on U x_T at each truth's nominal x_T (A and B fixed, D shifted), over sigma_c; S1's single-universe level too.
The bank universes' tdw are read at the 16 rows only, by seek, through O_NOATIME, pinned by size and mtime against
the pins file (toys.check_pins' convention for the bound bank; weaker than a sha256 of the bytes).

MEASURES: offsets in sigma_c, descriptive. CANNOT AUTHORIZE: a verdict, a change to S1, a remedy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

import fd_1b_c2 as c2
import fd_1b_inv as inv
import fd_1b_mc as mc
import fd_1b_score as fs
import fd_1b_toys as toys
import s1_assemble as sa

SCHEMA = "fd-1b-binning/1"
FLAG_SIGMA = 0.05                   # the director's: a reporting cell above this under amendment 2 comes first


def delta_cv(moved: list, n: int) -> np.ndarray:
    """Delta_CV per fine cell, hist_f32(tdw_CV) - hist_f64(tdw_CV), attributed exactly to the moved rows."""
    d = np.zeros(n)
    for _, c64, c32, w in moved:
        d[c32] += w
        d[c64] -= w
    return d


def bound_minus_e2(tags: list[str], dcv: np.ndarray) -> np.ndarray:
    """Amendment 2 as bound minus (e2), one draw: bound subtracts d64 for each term j >= 2 where (e2) subtracts d32,
    and a detector term brings d64 under bound and d32 under (e2): ((k - 1) - n_det after the first) Delta_CV."""
    n_det = sum(t.rpartition("_")[0] in sa.DETECTOR_BANDS for t in tags[1:])
    if tags[0].rpartition("_")[0] in sa.DETECTOR_BANDS:
        raise c2.Refusal("a draw's first universe is a detector universe: the identity is stated for a bank first")
    return ((len(tags) - 1) - n_det) * dcv


def e2_minus_f64(tags: list[str], moved: list, rows_u: dict, n: int) -> np.ndarray:
    """(e2) minus a float64-binned composite, one draw: each moved row's first-order composite weight over the draw
    (a detector universe brings the CV's row, a zero term), moved from its float64 cell to its float32 cell."""
    d = np.zeros(n)
    for j, (_, c64, c32, w_cv) in enumerate(moved):
        vals = [rows_u[t][j] if t in rows_u else w_cv for t in tags]
        w_d = vals[0] + sum(v - w_cv for v in vals[1:])
        d[c32] += w_d
        d[c64] -= w_d
    return d


def effect(dD: np.ndarray, A: np.ndarray, B: np.ndarray, D: np.ndarray, flux: np.ndarray, const: dict,
           U: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """U x_T(D + dD) - U x_T(D), over sigma_c, at fixed A and B (1B's graded truth, c2.xt_flat)."""
    x0 = c2.xt_flat(A[None], B[None], D[None], flux[None], **const)[0]
    x1 = c2.xt_flat(A[None], B[None], (D + dD)[None], flux[None], **const)[0]
    return (U @ (x1 - x0)) / sigma


def rows_at(path: Path, rows: list[int], pin: dict) -> np.ndarray:
    """A universe's tdw at ``rows``, by seek, through O_NOATIME; size and mtime must be the pins file's; non-finite
    values zeroed as fd_1b_inv.universe_weights(..., "zero") gives them."""
    st = path.stat()
    if (st.st_size, st.st_mtime_ns) != (pin["size"], pin["mtime_ns"]):
        raise c2.Refusal(f"{path} changed after it was pinned")
    with inv.open_noatime(path) as fh:
        version = np.lib.format.read_magic(fh)
        read = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
        shape, fortran, dtype = read(fh)
        if len(shape) != 1 or fortran:
            raise c2.Refusal(f"{path}: not a 1-D array")
        start, size = fh.tell(), dtype.itemsize
        out = []
        for r in rows:
            fh.seek(start + int(r) * size)
            out.append(np.frombuffer(fh.read(size), dtype=dtype)[0])
    return np.nan_to_num(np.asarray(out, np.float64), nan=0.0, posinf=0.0, neginf=0.0)


def summarize(E: np.ndarray) -> dict:
    """E: draws x cells, in sigma_c: per cell the max |.| and median |.| over draws, and the largest cell."""
    a = np.abs(E)
    return {"per_cell_max": a.max(axis=0).tolist(), "per_cell_median": np.median(a, axis=0).tolist(),
            "largest": float(a.max()), "largest_cell": int(a.max(axis=0).argmax())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    for k in ("npz", "bank", "detector-dir", "pins", "flux-constraint", "definition", "staged", "prep", "cvdenom",
              "out"):
        ap.add_argument(f"--{k}", type=Path, required=True)
    for k in ("pins", "cvdenom"):
        ap.add_argument(f"--expect-{k}-sha256", required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    inv.OPENED.clear()
    if inv.sha256_noatime(a.npz) != sa.INPUT_NPZ_SHA256:
        raise c2.Refusal("the input npz is not the declared one")
    if inv.sha256_noatime(a.pins) != a.expect_pins_sha256:
        raise c2.Refusal("pins file digest differs")
    with inv.open_noatime(a.pins) as fh:
        pins = json.loads(fh.read().decode())
    if inv.sha256_noatime(a.cvdenom) != a.expect_cvdenom_sha256:
        raise c2.Refusal("the CV denominator read's record digest differs")
    with inv.open_noatime(a.cvdenom) as fh:
        cvd = json.loads(fh.read().decode())
    if cvd.get("verdict") != "PASS" or not cvd["checks"]["B_tolerance"]["passes"]:
        raise c2.Refusal("the CV denominator read did not PASS")
    moved = [tuple(r) for r in cvd["checks"]["B_tolerance"]["rows"]]
    inputs = inv.load_inputs(a.npz)
    edges = inputs["edges"]
    shape = tuple(np.asarray(e).size - 1 for e in edges)
    n = int(np.prod(shape))
    fm = np.asarray(sa.fine_map(a.definition))
    U = sa.functional_matrix(fm)
    s1 = mc.via_noatime(fs.load_s1, a.staged / "s1" / "s1_assembly.npz")
    if not np.allclose(U, s1["U"], rtol=0, atol=1e-6):
        raise c2.Refusal("the definition's functional is not S1's")
    sigma = np.sqrt(np.diag(fs.reported_matrix(s1)))
    const = {"n_nucleons": float(inputs["n_nucleons"]), "data_pot": float(inputs["data_pot"]), "shape": shape,
             "edges": edges}
    D64 = np.asarray(inputs["denom_nd"], float).ravel()
    dcv = delta_cv(moved, n)
    flux = np.asarray(inputs["flux"], float)
    ptru = np.asarray(inputs["pass_truth"], bool)
    cells = np.where(ptru, mc.flat_cells(np.asarray(inputs["MCgen"], float), edges), -1)
    wt = np.asarray(inputs["w_truth"], float)
    hist = lambda w: np.bincount(cells[cells >= 0], weights=w[cells >= 0], minlength=n)  # noqa: E731
    truths = {"nominal": np.ones(wt.size)}
    for t in ("g18", "ar23"):
        ratio, _ = mc.truth_ratio(t, a.prep)
        truths[t] = mc.truth_weight(t, inputs, ratio, None)
    AB = {t: (hist(wt * r), hist(wt)) for t, r in truths.items()}
    # item 3
    item3 = []
    for row, c64, c32, w in moved:
        e = np.zeros(n)
        e[c32], e[c64] = w, -w
        rec = {"row": int(row), "cell64": int(c64), "cell32": int(c32), "weight": float(w),
               "R64": int(fm[c64]), "R32": int(fm[c32]), "same_reporting_cell": bool(fm[c64] == fm[c32])}
        for t, (A, B) in AB.items():
            z = effect(e, A, B, D64, flux, const, U, sigma)
            rec[t] = {"max_abs_sigma": float(np.max(np.abs(z))), "cells": {int(c): float(z[c])
                                                                              for c in np.flatnonzero(z != 0)}}
        item3.append(rec)
    basis = {t: effect(dcv, A, B, D64, flux, const, U, sigma).tolist() for t, (A, B) in AB.items()}
    # item 4
    tags = toys.s1_universes()
    bank_tags = [t for t in tags if t.rpartition("_")[0] not in sa.DETECTOR_BANDS]
    rows_u = {}
    for t in bank_tags:
        p = mc.universe_dir(t, a.bank, a.detector_dir) / f"{t}_tdw.npy"
        rows_u[t] = rows_at(p, [m[0] for m in moved], pins["files"][str(p)])
    s1_level = {}
    for t, (A, B) in AB.items():
        worst = 0.0
        for u in bank_tags:
            single = np.zeros(n)
            for j, (_, c64, c32, _w) in enumerate(moved):
                single[c32] += rows_u[u][j]
                single[c64] -= rows_u[u][j]
            worst = max(worst, float(np.max(np.abs(effect(single, A, B, D64, flux, const, U, sigma)))))
        s1_level[t] = worst
    flux_p = mc.via_noatime(toys.flux_probabilities, a.flux_constraint)
    groups = toys.interaction_groups(a.bank)
    item4, flags = {}, []
    for truth in ("g18", "ar23"):
        A, B = AB[truth]
        Eb, Ee = [], []
        for sd in mc.TOY_SEEDS[truth]:
            d = mc.draw_universes(toys.draw_for_seed(sd, flux_p, groups))
            e2 = e2_minus_f64(d, moved, rows_u, n)
            Ee.append(effect(e2, A, B, D64, flux, const, U, sigma))
            Eb.append(effect(e2 + bound_minus_e2(d, dcv), A, B, D64, flux, const, U, sigma))
        item4[truth] = {"amendment_2_as_bound_vs_float64": summarize(np.array(Eb)),
                        "e2_vs_float64": summarize(np.array(Ee)), "draws": len(Eb)}
        if item4[truth]["amendment_2_as_bound_vs_float64"]["largest"] > FLAG_SIGMA:
            flags.append(truth)
    digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (
        Path(__file__).resolve(), Path(c2.__file__).resolve(), Path(mc.__file__).resolve())}
    rec = {"schema": SCHEMA, "step": "binning-items-3-4", "moved_rows": len(moved),
           "same_reporting_cell": int(sum(r["same_reporting_cell"] for r in item3)), "item3": item3,
           "nominal_basis_f32_minus_f64_sigma": basis, "s1_single_universe_level_max_sigma": s1_level,
           "item4": item4, "flag_above_0_05_sigma_under_amendment_2": flags,
           "note": ("effects at each truth's nominal A and B with D shifted (descriptive); sigma_c is S1's reported "
                    "(C_total_plus_C_resp); the plug-in waits for the capture"),
           "bank_tdw_pin": "size and mtime against the pins file (toys.check_pins' convention), not sha256",
           "threads": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
           "code_sha256": digests, "cvdenom_sha256": a.expect_cvdenom_sha256, "seconds": round(time.time() - t0, 1),
           "atime": inv.atime_check()}
    a.out.write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"FD-1B-BINNING moved={len(moved)} same_R={rec['same_reporting_cell']} flags={flags} "
          f"largest_bound={ {t: v['amendment_2_as_bound_vs_float64']['largest'] for t, v in item4.items()} } "
          f"largest_e2={ {t: v['e2_vs_float64']['largest'] for t, v in item4.items()} } s1={s1_level}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
