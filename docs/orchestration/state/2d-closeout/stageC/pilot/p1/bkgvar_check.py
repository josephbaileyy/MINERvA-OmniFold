#!/usr/bin/env python3
"""P1 declared check: the background stream's reco-level variance equals sum w^2 of B (login node, no unfold).

  python bkgvar_check.py --d2 D2 --omnifile OMNI --out RESULT.json [--n 2000]

D2 holds driver_p1.py and uq/reported_cells.py. The script imports driver_p1's own background loader
(fill_bkg_reco_2d with return_fill_rows=True, called as main() calls it), its factor draw
(p1_draw_bkg_factors) and its refill (p1_refill_bkg_2d).

Procedure. Draw N = 2000 independent factor vectors b_bkg with bootstrap seeds s = 1..N through
p1_draw_bkg_factors (default_rng(s + 20,000,000).poisson(1, n), n = mc_background entries). For each,
refill B*_c = sum_i b_bkg[entry_i] * w_i * pot per reco cell c of the 14 x 16 analysis grid
(reported_cells.PT_EDGES / PZ_EDGES; rows outside the grid, the overflow rows, are excluded from the cells).
The refill over 2000 draws is vectorized (np.bincount on the cell of each fill row, found once with the
TH2D's own FindFixBin); for s = 1, 2, 3 it is compared with driver_p1.p1_refill_bkg_2d, and a relative
difference above 1e-12 in any cell makes the result INCONCLUSIVE.

DECLARED CHECK (frozen before the first run). Per cell c with sum w^2_c > 0:
    s^2_c   = sample variance of B*_c over the N draws (ddof = 1)
    kappa_c = sum w^4_c / (sum w^2_c)^2          (the Poisson(1) fourth-cumulant term)
    SE_c    = sum w^2_c * sqrt((2 + kappa_c) / N)
    z_c     = (s^2_c - sum w^2_c) / SE_c
    pooled z = sum_c z_c / sqrt(n_cells)
PASS iff max_c |z_c| <= 5 and |pooled z| <= 3; otherwise FAIL.
Cells are independent (each fill row lies in one cell and each tree entry fills at most one row), so the
z_c are independent under the null. What this check cannot see: an entry-to-row mapping error that still
gives iid Poisson(1) factors per row has the same variance law; test_noop.py C3/C4 test the mapping.
The mean of B*_c against B_c is reported for information only.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time

import numpy as np

N_DEFAULT = 2000
Z_CELL_MAX = 5.0
Z_POOLED_MAX = 3.0
REFILL_TOL = 1e-12


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d2", required=True)
    ap.add_argument("--omnifile", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=N_DEFAULT)
    a = ap.parse_args()
    import ROOT
    ROOT.gROOT.SetBatch(True)
    sys.path.insert(0, os.path.join(a.d2, "uq"))
    from reported_cells import PT_EDGES, PZ_EDGES, GRID_SHAPE
    drv_path = os.path.join(a.d2, "driver_p1.py")
    drv = load("driver_p1", drv_path)
    t0 = time.time()
    rep = {"schema": "p1-bkgvar/1", "omnifile": a.omnifile, "omnifile_bytes": os.path.getsize(a.omnifile),
           "driver_p1": drv_path, "driver_p1_sha256": sha_file(drv_path),
           "bkgvar_check_sha256": sha_file(os.path.abspath(__file__)), "N": a.n, "seeds": [1, a.n],
           "bkg_seed_offset": drv.P1_BKG_SEED_OFFSET, "host": os.uname().nodename,
           "criterion": {"z_cell_max": Z_CELL_MAX, "z_pooled_max": Z_POOLED_MAX,
                         "SE": "sum_w2 * sqrt((2 + kappa) / N), kappa = sum_w4 / sum_w2^2",
                         "refill_tol": REFILL_TOL}}
    if not (np.array_equal(np.asarray(drv.PT_EDGES), PT_EDGES) and np.array_equal(np.asarray(drv.PZ_EDGES), PZ_EDGES)):
        raise SystemExit("[FAIL] driver_p1 edges differ from reported_cells edges")

    f = ROOT.TFile.Open(a.omnifile)
    _, _, pot = drv.get_pot_scales(f)
    t_bkg = f.Get("mc_background")
    n_ent = int(t_bkg.GetEntries())
    h = drv.make_th2d("hBkgCheck", "B", drv.PT_EDGES, drv.PZ_EDGES)
    _, _, _, rows = drv.fill_bkg_reco_2d(t_bkg, h, pot, pt_lo=drv.PT_EDGES[0], pt_hi=drv.PT_EDGES[-1],
                                         pz_lo=drv.PZ_EDGES[0], pz_hi=drv.PZ_EDGES[-1], return_fill_rows=True)
    ax, ay = h.GetXaxis(), h.GetYaxis()
    ix = np.fromiter((ax.FindFixBin(float(x)) for x in rows["pt"]), dtype=np.int64, count=rows["pt"].size)
    iy = np.fromiter((ay.FindFixBin(float(y)) for y in rows["pz"]), dtype=np.int64, count=rows["pz"].size)
    nx, ny = GRID_SHAPE
    in_grid = (ix >= 1) & (ix <= nx) & (iy >= 1) & (iy <= ny)
    cell = (ix[in_grid] - 1) * ny + (iy[in_grid] - 1)          # C order (pT, p_par), the paper GlobalID
    ent = rows["entry"][in_grid]
    wp = rows["w_pot"][in_grid]
    ncell = nx * ny
    n_rows_c = np.bincount(cell, minlength=ncell)
    sw = np.bincount(cell, weights=wp, minlength=ncell)
    sw2 = np.bincount(cell, weights=wp ** 2, minlength=ncell)
    sw4 = np.bincount(cell, weights=wp ** 4, minlength=ncell)
    hB = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)]).ravel()
    rep.update(pot_scale=pot, n_entries=n_ent, n_fill_rows=int(rows["entry"].size),
               n_fill_rows_in_grid=int(in_grid.sum()), n_fill_rows_outside_grid=int((~in_grid).sum()),
               entries_unique=bool(np.unique(rows["entry"]).size == rows["entry"].size),
               B_from_rows_vs_hist_max_rel=float(np.max(np.abs(sw - hB)[hB != 0] / np.abs(hB[hB != 0]))))

    # The vectorized refill must agree with the driver's own TH2D refill.
    refill = {}
    for s in (1, 2, 3):
        b = drv.p1_draw_bkg_factors(s, n_ent)
        hs = drv.p1_refill_bkg_2d(f"hStar{s}", "B*", rows, b, drv.PT_EDGES, drv.PZ_EDGES)
        hv = np.array([[hs.GetBinContent(i + 1, j + 1) for j in range(ny)] for i in range(nx)]).ravel()
        vv = np.bincount(cell, weights=b[ent] * wp, minlength=ncell)
        nz = hv != 0
        refill[str(s)] = {"max_rel": float(np.max(np.abs(vv - hv)[nz] / np.abs(hv[nz]), initial=0.0)),
                          "zero_cells_agree": bool(np.array_equal(vv == 0, hv == 0))}
    rep["refill_crosscheck"] = refill
    refill_ok = all(r["max_rel"] <= REFILL_TOL and r["zero_cells_agree"] for r in refill.values())
    f.Close()

    X = np.empty((a.n, ncell))
    for k, s in enumerate(range(1, a.n + 1)):
        b = drv.p1_draw_bkg_factors(s, n_ent)
        X[k] = np.bincount(cell, weights=b[ent] * wp, minlength=ncell)
    s2 = X.var(axis=0, ddof=1)
    mean = X.mean(axis=0)
    use = sw2 > 0
    kappa = np.where(use, sw4 / np.where(use, sw2, 1.0) ** 2, np.nan)
    se = np.where(use, sw2 * np.sqrt((2.0 + kappa) / a.n), np.nan)
    z = np.where(use, (s2 - sw2) / se, np.nan)
    zu = z[use]
    pooled = float(zu.sum() / np.sqrt(use.sum()))
    imax = int(np.nanargmax(np.abs(z)))
    zm = np.where(use, (mean - sw) / np.sqrt(np.where(use, sw2, 1.0) / a.n), np.nan)
    rep.update(n_cells_used=int(use.sum()), max_abs_z=float(np.abs(zu).max()), argmax_globalid=imax,
               argmax_cell={"n_rows": int(n_rows_c[imax]), "sum_w2": float(sw2[imax]), "s2": float(s2[imax]),
                            "kappa": float(kappa[imax]), "z": float(z[imax])},
               pooled_z=pooled, mean_z=float(zu.mean()), sd_z=float(zu.std(ddof=1)),
               n_cells_abs_z_gt_3=int(np.sum(np.abs(zu) > 3)),
               ratio_s2_over_sumw2={"median": float(np.median(s2[use] / sw2[use])),
                                    "min": float(np.min(s2[use] / sw2[use])),
                                    "max": float(np.max(s2[use] / sw2[use]))},
               kappa_max=float(np.nanmax(kappa)), min_rows_in_used_cell=int(n_rows_c[use].min()),
               info_mean_check={"max_abs_z_mean": float(np.nanmax(np.abs(zm))),
                                "pooled_z_mean": float(np.nansum(zm) / np.sqrt(use.sum()))})
    rep["cells"] = [{"globalid": int(c), "n_rows": int(n_rows_c[c]), "sum_w": float(sw[c]),
                     "sum_w2": float(sw2[c]), "kappa": float(kappa[c]), "s2": float(s2[c]),
                     "z": float(z[c]), "mean": float(mean[c])} for c in np.flatnonzero(use)]
    if not refill_ok:
        rep["verdict"] = "INCONCLUSIVE"
        rep["why"] = "the vectorized refill disagrees with driver_p1.p1_refill_bkg_2d"
    else:
        rep["verdict"] = "PASS" if (rep["max_abs_z"] <= Z_CELL_MAX and abs(pooled) <= Z_POOLED_MAX) else "FAIL"
    rep["seconds"] = round(time.time() - t0, 1)
    with open(a.out, "w") as fh:
        json.dump(rep, fh, indent=1, sort_keys=True)
    print(json.dumps({k: rep[k] for k in ("verdict", "n_cells_used", "max_abs_z", "argmax_globalid", "pooled_z",
                                          "ratio_s2_over_sumw2", "refill_crosscheck", "seconds")}, indent=1))
    return 0 if rep["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
