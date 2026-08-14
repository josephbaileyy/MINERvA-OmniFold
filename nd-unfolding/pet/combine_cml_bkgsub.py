#!/usr/bin/env python3
"""Phase 5: build the PET-specific C_ml from the corrected crossed-seed ensemble.

The C_ml members are the 12 unbootstrapped trainings over
subsample-seed x estimator-seed (`cml/pet_s{S}_e{E}_bkgsub_5d_xsec.npz`). They
are keyed by their (S,E) filename (all carry the nominal-extractor seed=0, so
combine_cov_nd's seed-manifest cannot distinguish them). C_ml is centered on the
JOINT training-ensemble mean on the corrected-nominal CV>0 reported-bin mask
(same mask/order as C_stat via combine_cov_nd), and a two-way (balanced-grid)
variance decomposition reports the estimator-seed, subsample-seed, and
interaction contributions.

Pure numpy -- runs on the login node.

  python3 pet/combine_cml_bkgsub.py \
    --glob 'products/pet/bkgsub/cml/pet_s*_e*_bkgsub_5d_xsec.npz' \
    --cv products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz \
    --floor products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json \
    --out products/pet/bkgsub/pet_cml_bkgsub_5d.npz \
    --expect 12
"""
import argparse
import glob
import json
import os
import re

import numpy as np

_RE = re.compile(r"pet_s(\d+)_e(\d+)_bkgsub_5d_xsec\.npz$")


def load_members(paths):
    S, E, X = [], [], []
    for p in sorted(paths):
        m = _RE.search(os.path.basename(p))
        if not m:
            raise SystemExit(f"[FAIL] cannot parse (sub,est) seeds from {p}")
        S.append(int(m.group(1))); E.append(int(m.group(2)))
        X.append(np.asarray(np.load(p)["xsec_flat"], float))
    return np.array(S), np.array(E), np.vstack(X)


def two_way_decomposition(Xr, S, E):
    """Balanced crossed-grid SS decomposition per reported bin, averaged over bins.
    Returns mean fractional contributions (sub, est, interaction+residual)."""
    subs = sorted(set(S.tolist())); ests = sorted(set(E.tolist()))
    ns, ne = len(subs), len(ests)
    if Xr.shape[0] != ns * ne:
        return {"balanced": False, "note": f"{Xr.shape[0]} members != {ns}x{ne} grid"}
    # index members into a (ns, ne, nbins) grid
    grid = np.full((ns, ne, Xr.shape[1]), np.nan)
    for k in range(Xr.shape[0]):
        grid[subs.index(S[k]), ests.index(E[k])] = Xr[k]
    if np.isnan(grid).any():
        return {"balanced": False, "note": "grid has missing/duplicate cells"}
    grand = grid.mean(axis=(0, 1))
    mean_sub = grid.mean(axis=1)                    # (ns, nbins)
    mean_est = grid.mean(axis=0)                    # (ne, nbins)
    ss_sub = ne * ((mean_sub - grand) ** 2).sum(axis=0)
    ss_est = ns * ((mean_est - grand) ** 2).sum(axis=0)
    ss_tot = ((grid - grand) ** 2).sum(axis=(0, 1))
    ss_int = np.clip(ss_tot - ss_sub - ss_est, 0, None)
    good = ss_tot > 0
    frac = lambda ss: float(np.median((ss[good] / ss_tot[good]))) if good.any() else 0.0
    return {"balanced": True, "grid": [ns, ne],
            "median_frac_subsample": frac(ss_sub),
            "median_frac_estimator": frac(ss_est),
            "median_frac_interaction": frac(ss_int)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", default="products/pet/bkgsub/cml/pet_s*_e*_bkgsub_5d_xsec.npz")
    ap.add_argument("--cv", default="products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz")
    ap.add_argument("--floor", default="products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json")
    ap.add_argument("--out", default="products/pet/bkgsub/pet_cml_bkgsub_5d.npz")
    ap.add_argument("--expect", type=int, default=12)
    ap.add_argument("--allow-incomplete-family", action="store_true",
                    help="Build from an INCOMPLETE family anyway, for a diagnostic or an "
                         "intermediate. The product is written to a NONQUOTABLE-DIAGNOSTIC.-prefixed "
                         "path and its summary carries quotable=false. Never use for publication.")
    args = ap.parse_args()

    cv = np.asarray(np.load(args.cv)["xsec_flat"], float)
    rep = cv > 0
    paths = glob.glob(args.glob)
    # FAIL CLOSED ON AN INCOMPLETE FAMILY (BEN-244, 2026-08-14). This was a `print` warning that
    # built from whatever it found. With Gate 6 at `passing_members [1]` of five, that made
    # `do_not_select_passing_subset` a rule on people only: the builder would have produced C_ML
    # from the one passing member, exit 0, into a log this filesystem block-buffers for hours
    # (BEN-028). Measured before the fix, at 1 member of 12: exit 0, BOTH files written, and
    # `n-1 = 0` so the covariance was ENTIRELY NaN while the two-way decomposition printed
    # `subsample=0.000 estimator=0.000 interaction=0.000` -- a NaN matrix at the publication path
    # under a summary that reads clean. Regression: tests/test_cml_family_completeness_fails_closed.py
    family_complete = len(paths) == args.expect
    if not family_complete:
        detail = (f"found {len(paths)} members, expected {args.expect}. An incomplete C_ML family is "
                  f"a SUBSET, and building the covariance from a subset is what "
                  f"do_not_select_passing_subset forbids. Pass --allow-incomplete-family to build a "
                  f"NON-QUOTABLE diagnostic instead.")
        if not args.allow_incomplete_family:
            raise SystemExit(f"[cml][FAIL] {detail}")
        print(f"[cml][WARN] {detail}")
        print("[cml][WARN] --allow-incomplete-family given: this product is NON-QUOTABLE.")
        args.out = os.path.join(os.path.dirname(os.path.abspath(args.out)),
                                "NONQUOTABLE-DIAGNOSTIC." + os.path.basename(args.out))
    S, E, X = load_members(paths)
    if X.shape[1] != cv.shape[0]:
        raise SystemExit(f"[FAIL] member nbins {X.shape[1]} != cv {cv.shape[0]}")
    Xr = X[:, rep]; cvr = cv[rep]
    Z = Xr - Xr.mean(0)
    C = (Z.T @ Z) / (Xr.shape[0] - 1)          # ensemble-mean-centered
    sig = np.sqrt(np.clip(np.diag(C), 0, None))
    relmed = float(np.median(sig / cvr))
    sqrt_tr = float(np.sqrt(max(C.trace(), 0.0)))
    decomp = two_way_decomposition(Xr, S, E)

    floor_med = None
    if os.path.exists(args.floor):
        fl = json.load(open(args.floor))
        floor_med = fl.get("per_bin_rel_floor", {}).get("median")

    np.savez_compressed(args.out, C_ml=C, reported_mask=rep,
                        sub_seeds=S, est_seeds=E, xsec_members=X,
                        cv=cv, sigma=sig)
    summary = {
        "campaign": "PET bkgsub 5D corrected C_ml (Phase 5)",
        # DECLARED, not inferred: a consumer must be able to gate on completeness without
        # recomputing it, and `quotable` must be false on the page it is false on.
        "family_complete": bool(family_complete),
        "quotable": bool(family_complete),
        "allow_incomplete_family": bool(args.allow_incomplete_family),
        "n_members": int(X.shape[0]), "expected": args.expect,
        "sub_seeds": S.tolist(), "est_seeds": E.tolist(),
        "n_reported_bins": int(rep.sum()),
        "sqrt_trace": sqrt_tr, "per_bin_rel_median": relmed,
        "variance_decomposition": decomp,
        "floor_per_bin_rel_median": floor_med,
        "cml_over_floor_ratio": (relmed / floor_med) if floor_med else None,
        "out": os.path.abspath(args.out),
    }
    spath = os.path.splitext(args.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)
    print(f"[cml] {X.shape[0]} members, reported {int(rep.sum())} bins, "
          f"sqrt-trace={sqrt_tr:.3e}, per-bin rel median={100*relmed:.3f}%")
    if floor_med:
        print(f"[cml] per-bin rel median {relmed:.3e} vs floor {floor_med:.3e} "
              f"(ratio {relmed/floor_med:.1f}x)")
    if decomp.get("balanced"):
        print(f"[cml] variance decomposition (median frac): "
              f"subsample={decomp['median_frac_subsample']:.3f} "
              f"estimator={decomp['median_frac_estimator']:.3f} "
              f"interaction={decomp['median_frac_interaction']:.3f}")
    print(f"[cml] wrote {args.out} + {spath}")


if __name__ == "__main__":
    main()
