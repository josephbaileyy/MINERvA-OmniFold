#!/usr/bin/env python3
"""Phase 3: corrected GPU-nondeterminism floor diagnostic.

Compare the corrected NOMINAL 5D xsec to a same-config, same-seed REPEAT (the
floor run). With estimator/subsample seeds held fixed and no bootstrap, the only
source of difference is GPU nondeterminism (cuDNN/atomics). This single pair is
a DIAGNOSTIC FLOOR, not a covariance estimate; it is recorded before C_stat and
C_ml spreads are interpreted (they must exceed this floor to be meaningful).

Pure numpy (loads write_xsec_replica npzs: xsec_flat, shape, total_xsec) -- runs
on the login node.

  python3 pet/floor_diagnostic_bkgsub.py \
    --nominal products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz \
    --floor   products/pet/bkgsub/pet_floor_bkgsub_5d_xsec.npz \
    --out     products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json
"""
import argparse
import json
import os

import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--nominal", default="products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz")
    ap.add_argument("--floor", default="products/pet/bkgsub/pet_floor_bkgsub_5d_xsec.npz")
    ap.add_argument("--out", default="products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json")
    args = ap.parse_args()

    nz = np.load(args.nominal); fz = np.load(args.floor)
    nom = np.asarray(nz["xsec_flat"], float)
    flr = np.asarray(fz["xsec_flat"], float)
    if nom.shape != flr.shape:
        raise SystemExit(f"[FAIL] shape mismatch nominal{nom.shape} floor{flr.shape}")
    tot_nom = float(nz["total_xsec"]); tot_flr = float(fz["total_xsec"])

    rep = nom > 0                          # reported-bin mask = corrected nominal CV>0
    diff = flr - nom
    reld = np.abs(diff[rep]) / nom[rep]    # per-reported-bin relative floor
    pct = lambda a, q: float(np.percentile(a, q)) if a.size else 0.0

    out = {
        "campaign": "PET bkgsub 5D corrected GPU-nondeterminism floor (Phase 3)",
        "nominal": os.path.abspath(args.nominal), "floor": os.path.abspath(args.floor),
        "note": "single same-seed pair: a diagnostic floor, NOT a covariance estimate",
        "n_bins": int(nom.size), "n_reported_bins": int(rep.sum()),
        "total_sigma_nominal": tot_nom, "total_sigma_floor": tot_flr,
        "total_abs_diff": abs(tot_flr - tot_nom),
        "total_rel_diff": abs(tot_flr - tot_nom) / tot_nom if tot_nom else None,
        "per_bin_rel_floor": {
            "median": float(np.median(reld)) if reld.size else 0.0,
            "mean": float(np.mean(reld)) if reld.size else 0.0,
            "p90": pct(reld, 90), "p99": pct(reld, 99),
            "max": float(reld.max()) if reld.size else 0.0,
        },
        "l2_norm_diff_over_nominal": float(np.linalg.norm(diff[rep]) / np.linalg.norm(nom[rep]))
        if rep.any() else None,
        "sqrt_sum_sq_abs_diff": float(np.sqrt(np.sum(diff[rep] ** 2))) if rep.any() else 0.0,
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    pb = out["per_bin_rel_floor"]
    print(f"[floor] reported_bins={out['n_reported_bins']} "
          f"total_rel_diff={out['total_rel_diff']:.3e} "
          f"per-bin rel floor: median={pb['median']:.3e} p90={pb['p90']:.3e} "
          f"p99={pb['p99']:.3e} max={pb['max']:.3e}")
    print(f"[floor] wrote {os.path.abspath(args.out)}")


if __name__ == "__main__":
    main()
