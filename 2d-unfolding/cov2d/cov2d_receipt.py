"""COV2D's composite-weight receipt on the real 2D bank (COV2D-DECLARATION.md section 9.2; the scoping's P2). It runs
before the price is fixed: login node, nice 19, 0 node-h. $UNI, the constraint file and F1's two ratio files are read
only through O_NOATIME descriptors, and the atime of each is checked before and after.

Over the 600 declared draws (300 per tune) and every row of each array (DECISION-20261102-joseph-1b-redesign.md,
the director's 2d (ii): an exact float64 pass over every row):

* N1. Each row's first-order composite at every draw, a_D = a_CV + sum_j (a_uj - a_CV), the numerator |a_D| for every
  (row, draw). A row whose largest numerator over the draws, divided by the smallest any draw's peak can be
  (max_b min_u |a_u|), is at most N1_BOUND x (1 - 1e-9) is certified below the bound. Every other row is evaluated
  exactly, draw by draw, by ``cov2d.compose`` in draw order and ``cov2d.peak``. A composite above N1_BOUND on any
  row and draw is STOP.
* The truth cells (the director's 2b). At each tune T, the composite truth histogram sum(w_truth_D x r_T) over
  mc_truth_denom's rows in the truth phase space, per (pT, p_par) cell, at every declared draw of T. A cell where the
  CV histogram is positive and a draw's is not is STOP.
* Descriptive: rows above the bound under the all-draws bound; rows and (row, draw) pairs with a negative composite;
  the single-universe ratios' largest |a_u / a_CV|; r_T's range.

  python cov2d_receipt.py --out receipt.json [--uni PATH] [--prep DIR] [--constraint PATH] [--chunk N]

MEASURES: the composites and histograms above. CANNOT AUTHORIZE: a run, or any coverage statement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "nd-unfolding", REPO / "nd-unfolding" / "pv-ladder", REPO / "2d-unfolding" / "re2"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import cov2d as c  # noqa: E402

UNI = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/runEventLoopOmniFold_MEFHC_universes_full.root"
PREP = "/pscratch/sd/j/josephrb/fd-f1-20261027/f1b3/prep"
TUNES = {"G18": "genie_v3_g18", "AR23": "genie_v3_ar23"}
ARRAYS = (("wr", "mc_signal_reco", "w_reco"), ("wt", "mc_truth_denom", "w_truth"), ("bkgw", "mc_background", "w_bkg"))
TRUTH_VARS = ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W")
CHUNK = 200_000
EXACT_BLOCK = 2_000
CERTIFY = c.N1_BOUND * (1 - 1e-9)


def open_noatime(path):
    return os.fdopen(os.open(path, os.O_RDONLY | os.O_NOATIME), "rb")


def read_noatime(path) -> tuple[bytes, str]:
    with open_noatime(path) as fh:
        data = fh.read()
    return data, hashlib.sha256(data).hexdigest()


def atime(path) -> int:
    return int(os.stat(path).st_atime)


def universe_columns(prefix: str) -> list[str]:
    return [c.column(prefix, b, i) for b in c.ORDER for i in range(c.BANDS[b])]


def band_slices() -> list[slice]:
    out, k = [], 0
    for b in c.ORDER:
        out.append(slice(k, k + c.BANDS[b]))
        k += c.BANDS[b]
    return out


def draw_index(draws: list) -> np.ndarray:
    """(n_draws, 38) column indices into universe_columns' order, in each draw's own order."""
    pos, k = {}, 0
    for b in c.ORDER:
        for i in range(c.BANDS[b]):
            pos[(b, i)] = k
            k += 1
    return np.array([[pos[u] for u in d.universes] for d in draws], dtype=np.int64)


def selection(idx: np.ndarray, n_univ: int) -> np.ndarray:
    S = np.zeros((n_univ, idx.shape[0]))
    for d, row in enumerate(idx):
        S[row, d] = 1.0
    return S


def n1_chunk(cv: np.ndarray, U: np.ndarray, idx: np.ndarray, S: np.ndarray, slices: list[slice]) -> dict:
    """N1 over one chunk: certified rows, exactly evaluated rows, the largest composite and the rows above."""
    A = cv[:, None] + (U - cv[:, None]) @ S
    num = np.max(np.abs(A), axis=1)
    m = np.zeros(cv.size)
    for s in slices:
        m = np.maximum(m, np.min(np.abs(U[:, s]), axis=1))
    ub = c.n1_composite(num, m)
    cand = np.flatnonzero(ub > CERTIFY)
    out = {"rows": int(cv.size), "exact_rows": int(cand.size), "above": [], "max": 0.0,
           "neg_rows": int(np.sum(np.any(A < 0, axis=1))), "neg_pairs": int(np.sum(A < 0)),
           "bound_above": int(np.sum(c.all_draws_bound(cv, [U[:, s].T for s in slices]) > c.N1_BOUND))}
    for k in range(0, cand.size, EXACT_BLOCK):
        rows = cand[k:k + EXACT_BLOCK]
        G = U[rows][:, idx]                                  # (rows, draws, 38) in draw order
        cvr = cv[rows][:, None]
        ad = G[:, :, 0].copy()
        for j in range(1, G.shape[2]):
            ad += G[:, :, j] - cvr
        comp = c.n1_composite(ad, np.max(np.abs(G), axis=2))
        worst = np.max(comp, axis=1)
        out["max"] = max(out["max"], float(worst.max()) if worst.size else 0.0)
        for r in np.flatnonzero(worst > c.N1_BOUND):
            out["above"].append({"row_in_chunk": int(rows[r]), "composite": float(worst[r]),
                                 "draw": int(np.argmax(comp[r])), "a_cv": float(cv[rows[r]])})
    return out


DRIVER = REPO / "2d-unfolding" / "re2" / "re2_driver.py"
DRIVER_NAMES = ("PT_EDGES", "PZ_EDGES", "MAX_MUON_THETA_RAD", "in_truth_phase_space")


def driver_phase_space() -> dict:
    """re2_driver.py's own PT_EDGES, PZ_EDGES, MAX_MUON_THETA_RAD and in_truth_phase_space, compiled from the driver's
    source without its module-level ``import ROOT``: the login node's uproot environment has no PyROOT, and the
    environment with PyROOT has no uproot. Nothing is retyped; a missing name refuses."""
    import ast
    tree = ast.parse(DRIVER.read_text(), str(DRIVER))
    body = [n for n in tree.body
            if (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in DRIVER_NAMES for t in n.targets))
            or (isinstance(n, ast.FunctionDef) and n.name in DRIVER_NAMES)]
    ns = {"math": math}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(DRIVER), "exec"), ns)
    missing = [k for k in DRIVER_NAMES if k not in ns]
    if missing:
        raise c.Refusal(f"re2_driver.py defines no {missing}")
    return ns


def truth_cell(pt: np.ndarray, pz: np.ndarray) -> np.ndarray:
    """Each truth row's flat (pT, p_par) cell, as the driver fills hTruth2D: rows outside the driver's own truth phase
    space (its ``in_truth_phase_space``) and rows a TH2D would put in an overflow bin get -1."""
    drv = driver_phase_space()
    pe, ze = np.asarray(drv["PT_EDGES"], float), np.asarray(drv["PZ_EDGES"], float)
    fn = drv["in_truth_phase_space"]
    ok = np.frompyfunc(lambda a, b: fn(a, b, pe[0], pe[-1], ze[0], ze[-1]), 2, 1)(pt, pz)
    ok = ok.astype(bool)
    i = np.searchsorted(pe, pt, side="right") - 1
    j = np.searchsorted(ze, pz, side="right") - 1
    ok &= (i >= 0) & (i < pe.size - 1) & (j >= 0) & (j < ze.size - 1)
    return np.where(ok, i * (ze.size - 1) + j, -1)


def cell_hists(cell: np.ndarray, weights: np.ndarray, n_cells: int) -> np.ndarray:
    """Columns of ``weights`` (rows, k) summed per cell over rows with cell >= 0: shape (k, n_cells)."""
    ok = cell >= 0
    return np.stack([np.bincount(cell[ok], weights=weights[ok, k], minlength=n_cells)
                     for k in range(weights.shape[1])])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--uni", default=UNI)
    ap.add_argument("--prep", default=PREP)
    ap.add_argument("--constraint", default=c.CONSTRAINT)
    ap.add_argument("--chunk", type=int, default=CHUNK)
    ap.add_argument("--no-pins", action="store_true", help="tests only: skip the digest pins")
    args = ap.parse_args(argv)
    import uproot
    import fd_1b_toys
    import pvl_lib
    import s5e_deform

    def c_edges(axis):
        return driver_phase_space()["PT_EDGES" if axis == "pt" else "PZ_EDGES"]

    t0 = time.time()
    rec = {"host": os.uname().nodename, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "nice": os.nice(0), "uproot": uproot.__version__, "numpy": np.__version__, "bound": c.N1_BOUND,
           "chunk": args.chunk, "stop": []}
    reads = [args.uni, args.constraint] + [str(Path(args.prep) / fd_1b_toys.TRUTHS[t]) for t in TUNES.values()]
    before = {p: atime(p) for p in reads}

    text, sha = read_noatime(args.constraint)
    if not args.no_pins and sha != c.CONSTRAINT_SHA256:
        raise c.Refusal(f"constraint file sha256 {sha}")
    w_flux = c.flux_weights(text.decode())
    ratios = {}
    for tune, name in TUNES.items():
        data, sha = read_noatime(str(Path(args.prep) / fd_1b_toys.TRUTHS[name]))
        if not args.no_pins and sha != fd_1b_toys.committed_ratio_sha256(name):
            raise c.Refusal(f"{tune} ratio sha256 {sha} is not F1's committed digest")
        ratios[tune] = json.loads(data)
        if ratios[tune].get("schema") != "s5e-shape-ratio/1":
            raise c.Refusal(f"{tune} ratio schema {ratios[tune].get('schema')}")
    draws = {t: c.declared_draws(t, w_flux) for t in TUNES}
    all_draws = draws["G18"] + draws["AR23"]
    idx_all = draw_index(all_draws)
    slices = band_slices()
    rec["n_draws"] = len(all_draws)
    rec["pins"] = {"constraint": c.CONSTRAINT_SHA256, **{t: ("unchecked" if args.no_pins else "committed F1 digest")
                                                         for t in TUNES}}

    with open_noatime(args.uni) as fh:
        f = uproot.open(fh)
        td = f["mc_truth_denom"]
        a = td.arrays(list(TRUTH_VARS) + ["w_truth"], library="np")
        gen = np.stack([np.asarray(a[k], np.float64) for k in TRUTH_VARS], axis=1)
        w_cv = np.asarray(a["w_truth"], np.float64)
        del a
        cell = truth_cell(gen[:, 0], gen[:, 1])
        n_cells = (len(c_edges("pt")) - 1) * (len(c_edges("pz")) - 1)
        edges = [pvl_lib.FINE[ax] for ax in pvl_lib.AXES5]
        r_t = {t: s5e_deform.ratio_weight(gen, edges, w_cv, ratios[t], 1.0) for t in TUNES}
        del gen
        h_t = {t: np.zeros((1 + c.N_UNIVERSES, n_cells)) for t in TUNES}
        rec["n1"] = {}
        for name, tree, prefix in ARRAYS:
            t = f[tree]
            cols = [prefix] + universe_columns(prefix)
            S = selection(idx_all, len(cols) - 1)
            agg = {"rows": 0, "exact_rows": 0, "above": [], "max": 0.0, "neg_rows": 0, "neg_pairs": 0,
                   "bound_above": 0, "single_max_ratio": 0.0, "nonfinite_zeroed": 0}
            for start in range(0, t.num_entries, args.chunk):
                stop = min(start + args.chunk, t.num_entries)
                a = t.arrays(cols, entry_start=start, entry_stop=stop, library="np")
                cv = np.asarray(a[prefix], np.float64)
                U = np.stack([np.asarray(a[k], np.float64) for k in cols[1:]], axis=1)
                agg["nonfinite_zeroed"] += int(np.sum(~np.isfinite(cv)) + np.sum(~np.isfinite(U)))
                U = np.where(np.isfinite(U), U, 0.0)
                cv = np.where(np.isfinite(cv), cv, 0.0)
                out = n1_chunk(cv, U, idx_all, S, slices)
                if name == "wt":
                    W = np.concatenate([cv[:, None], U], axis=1)
                    for tune in TUNES:
                        h_t[tune] += cell_hists(cell[start:stop], W * r_t[tune][start:stop, None], n_cells)
                for k in ("rows", "exact_rows", "neg_rows", "neg_pairs", "bound_above"):
                    agg[k] += out[k]
                agg["max"] = max(agg["max"], out["max"])
                for x in out["above"]:
                    x["row"] = start + x.pop("row_in_chunk")
                    agg["above"].append(x)
                nz = cv != 0
                if np.any(nz):
                    agg["single_max_ratio"] = max(agg["single_max_ratio"],
                                                  float(np.max(np.abs(U[nz] / cv[nz, None]))))
            agg["rows_above"] = len(agg["above"])
            agg["above"] = agg["above"][:200]
            rec["n1"][name] = agg
            if agg["rows_above"]:
                rec["stop"].append(f"N1: {agg['rows_above']} rows of {name} above {c.N1_BOUND}")
            if agg["rows"] != t.num_entries:
                rec["stop"].append(f"N1: {name} evaluated {agg['rows']} of {t.num_entries} rows")

        rec["truth_cells"] = {"n_cells": n_cells, "rows_in_phase_space": int(np.sum(cell >= 0))}
        for tune in TUNES:
            r = r_t[tune]
            h_cv, h_u = h_t[tune][0], h_t[tune][1:]
            H = np.stack([c.compose(h_cv, [h_u[k] for k in d]) for d in draw_index(draws[tune])])
            pos = h_cv > 0
            rec["truth_cells"]["cv_positive"] = int(pos.sum())
            bad = np.argwhere(H[:, pos] <= 0)
            rec["truth_cells"][tune] = {"r_min": float(r.min()), "r_max": float(r.max()),
                                        "cv_total": float(h_cv.sum()),
                                        "draws_with_nonpositive_cell": int(np.unique(bad[:, 0]).size),
                                        "min_cell_ratio_to_cv": float(np.min(H[:, pos] / h_cv[pos]))}
            if bad.size:
                rec["stop"].append(f"truth cells: {tune} has {np.unique(bad[:, 0]).size} draws with a "
                                   f"non-positive cell where the CV is positive")

    after = {p: atime(p) for p in reads}
    rec["atime_moved"] = [p for p in reads if after[p] != before[p]]
    if rec["atime_moved"]:
        rec["stop"].append(f"atime moved on {rec['atime_moved']}")
    rec["verdict"] = "STOP" if rec["stop"] else "PASS"
    rec["seconds"] = round(time.time() - t0, 1)
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True))
    print(f"COV2D-RECEIPT {rec['verdict']} stops={len(rec['stop'])}")
    for s in rec["stop"]:
        print(f"STOP {s}")
    return 0 if rec["verdict"] == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
