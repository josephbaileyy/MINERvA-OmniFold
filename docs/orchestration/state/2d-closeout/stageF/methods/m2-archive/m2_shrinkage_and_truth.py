#!/usr/bin/env python3
"""Follow-up to m2_archive_checks.py (read-only on CFS).

(a) Why tr(W^-1 C_prod) ~ 47 and not 109: rebuild the Ledoit-Wolf metric of s5p_joint.ledoit_wolf from the 194 pilot
    products at a scan of shrinkage intensities lambda (lambda = 0.01549 reproduces the frozen V) and evaluate
    tr(V_lambda^-1 S_pilot) (in-sample) and tr(W_lambda^-1 C_R) (the MnvTune production residual); plus the pilot's
    standardized correlation spectrum.
(b) The fine-cell mechanism of the x_true spread at the MnvTune null (r = 1): per fine cell, across products, how
    often xtrue_flat is 0, and whether the non-zero values are identical across seeds.

Usage: python -I m2_shrinkage_and_truth.py CODE_DIR OUT_DIR
"""
import hashlib
import io
import json
import sys
from pathlib import Path

CODE, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(CODE))
import numpy as np  # noqa: E402

import s5p_joint as sj  # noqa: E402

ARCH = Path("/global/cfs/cdirs/m3246/josephrb/s5p-archive-20261006")
NS = "/pscratch/sd/j/josephrb/s5p-20260926/"
MAN = {}
for line in (ARCH / "SHA256SUMS").read_text().splitlines():
    h, p = line.split(None, 1)
    MAN[p.strip()] = h
READ = []


def load(path):
    b = Path(path).read_bytes()
    h = hashlib.sha256(b).hexdigest()
    s = str(path)
    rel = s[len(str(ARCH)) + 1:] if s.startswith(str(ARCH)) else None
    READ.append((s, h, len(b), "not-in-archive" if rel is None else ("match" if MAN.get(rel) == h else "MISMATCH")))
    return np.load(io.BytesIO(b), allow_pickle=False)


def lw_at(X, lam):
    """s5p_joint.ledoit_wolf with the intensity fixed at lam (same standardization and ddof rescaling)."""
    X = np.asarray(X, float)
    n, p = X.shape
    Xc = X - X.mean(0)
    sd = np.sqrt((Xc ** 2).mean(0))
    Z = Xc / np.where(sd > 0, sd, 1.0)
    S = Z.T @ Z / n
    off = ~np.eye(p, dtype=bool)
    R = np.where(off, (1 - lam) * S, S)
    return R * np.outer(sd, sd) * n / (n - 1), S


def main() -> int:
    design = json.loads((CODE / "design.json").read_text())
    supported = json.loads((CODE / "s5c_contract.json").read_text())["measurement"]["partition_J"]["supported_cells"]
    U, names, pz_index = sj.j_matrix({}, supported)
    model = sj.Model(design, U)
    V = np.asarray(np.load(ARCH / "stage3/V/V-s3v.npz", allow_pickle=False)["V"], float)
    spec = design["nulls"]["MnvTune_v1"]
    mu, var = sj.prediction(ARCH / spec["prediction"][len(NS):], U)
    pf = sj.product_files(design["v_ensemble_glob"])
    Fp = []
    for p in pf:
        z = load(p)
        m = json.loads(str(z["meta"]))
        Fp.append(model.apply(U @ np.asarray(z["xsec_flat"], float), m, int(m["pseudo_seed"])))
    Fp = np.array(Fp)
    files = sj.product_files(str(ARCH / spec["calibration_glob"][len(NS):]))
    cmap, nJ = sj.s1.coarse_map(sj.s1.J_EDGES, supported)
    inJ = cmap >= 0
    F, seeds, XTfine = [], [], []
    for p in files:
        z = load(p)
        m = json.loads(str(z["meta"]))
        F.append(model.apply(U @ np.asarray(z["xsec_flat"], float), m, int(m["pseudo_seed"])))
        seeds.append(int(m["pseudo_seed"]))
        XTfine.append(np.asarray(z["xtrue_flat"], float)[inJ])
    F, seeds, XTfine = np.array(F), np.array(seeds), np.array(XTfine)
    eps = np.array([np.random.default_rng([int(spec["surrogate_seed0"]), int(s), 0x4A02]).normal(size=mu.size)
                    * np.sqrt(var) for s in seeds])
    R = F - (mu + eps)
    CR, CF = np.cov(R.T), np.cov(F.T)
    Sp = np.cov(Fp.T)
    out = {"lambda_frozen": 0.015494889917521543, "scan": {}}
    _, Scorr = lw_at(Fp, 0.0)
    ev = np.sort(np.linalg.eigvalsh(Scorr))[::-1]
    out["pilot_corr_eigs"] = {"n": int(ev.size), "top5": [float(v) for v in ev[:5]],
                              "n_below_lambda_frozen": int((ev < 0.0155).sum()),
                              "n_below_1e-3": int((ev < 1e-3).sum()), "min": float(ev.min()),
                              "sum_top10_over_p": float(ev[:10].sum() / ev.size)}
    # production standardized-correlation spectrum, same estimator
    _, Scq = lw_at(F, 0.0)
    evq = np.sort(np.linalg.eigvalsh(Scq))[::-1]
    out["prod_corr_eigs"] = {"top5": [float(v) for v in evq[:5]], "n_below_lambda_frozen": int((evq < 0.0155).sum()),
                             "n_below_1e-3": int((evq < 1e-3).sum()), "min": float(evq.min())}
    for lam in (0.0, 0.001, 0.003, 0.0155, 0.03, 0.1, 0.3, 1.0):
        Vl, _ = lw_at(Fp, lam)
        Wl = Vl + np.diag(var)
        row = {"tr_Vinv_S_pilot": float(np.trace(np.linalg.solve(Vl, Sp))),
               "tr_Vinv_C_F_prod": float(np.trace(np.linalg.solve(Vl, CF))),
               "tr_Winv_C_R_prod": float(np.trace(np.linalg.solve(Wl, CR))),
               "cond_W": float(np.linalg.cond(Wl))}
        if lam == 0.0155:
            row["max_abs_rel_diff_to_frozen_V_at_exact_lambda"] = float(
                np.max(np.abs(lw_at(Fp, 0.015494889917521543)[0] - V)) / np.max(np.abs(V)))
        out["scan"][str(lam)] = row
    # oracle: the metric equal to the production covariance itself
    out["oracle_tr_Cprod^-1_C_R"] = float(np.trace(np.linalg.solve(CR, CR)))
    # (b) fine-cell mechanism of x_true at r = 1
    nz = XTfine > 0
    frac0 = 1 - nz.mean(0)
    some = (frac0 > 0) & (frac0 < 1)
    ref = np.where(nz, XTfine, np.nan)
    spread = np.nanmax(ref, 0) - np.nanmin(ref, 0)
    scale = np.nanmax(np.abs(ref), 0)
    ok = np.isfinite(spread) & (scale > 0)
    out["xtrue_fine_MnvTune"] = {
        "n_products": int(len(files)), "n_fine": int(inJ.size),
        "n_fine_in_reported_J": int(inJ.sum()),
        "n_fine_in_J_zero_in_some_but_not_all_products": int(some.sum()),
        "n_fine_in_J_always_zero": int((frac0 == 1).sum()),
        "max_rel_spread_of_nonzero_values_in_J": float(np.max(spread[ok] / scale[ok])),
        "n_fine_in_J_nonzero_values_not_identical": int((spread[ok] > 0).sum()),
        "median_frac_products_zero_among_intermittent_cells": float(np.median(frac0[some])) if some.any() else None,
    }
    # does setting the intermittently-empty fine cells back to their non-zero value restore x_true = constant per J?
    fill = np.where(nz, XTfine, np.nanmax(ref, 0)[None, :])
    fill = np.nan_to_num(fill)
    UJ = U[:, inJ]
    XJ = XTfine @ UJ.T
    XJf = fill @ UJ.T
    out["xtrue_fine_MnvTune"]["J_rel_sd_raw"] = {k: float(np.percentile(XJ.std(0, ddof=1) / XJ.mean(0), k)) for k in (50, 90, 100)}
    out["xtrue_fine_MnvTune"]["J_rel_sd_after_refilling_empty_fine_cells"] = {k: float(np.percentile(XJf.std(0, ddof=1) / XJf.mean(0), k)) for k in (50, 90, 100)}
    out["xtrue_fine_MnvTune"]["J_mean_rel_vs_G_after_refill"] = {"max_abs": float(np.max(np.abs(XJf.mean(0) / mu - 1))),
                                                                 "median": float(np.median(XJf.mean(0) / mu - 1))}
    (OUT / "m2_shrinkage_and_truth.json").write_text(json.dumps(out, indent=1))
    with open(OUT / "inputs_sha256_followup.tsv", "w") as fh:
        fh.write("path\tsha256\tbytes\tarchive_SHA256SUMS\n")
        for r in READ:
            fh.write("\t".join(map(str, r)) + "\n")
    v = {}
    for r in READ:
        v[r[3]] = v.get(r[3], 0) + 1
    print(json.dumps({"inputs": len(READ), "verdicts": v}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
