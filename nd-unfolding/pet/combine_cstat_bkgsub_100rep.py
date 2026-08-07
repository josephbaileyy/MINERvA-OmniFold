#!/usr/bin/env python3
"""P1 / #15: build the 100-replica corrected PET C_stat candidate + full gates.

REVIEW STATUS: reviewed and tracked 2026-08-07 (claude-opus-5). Previously untracked, so it had
never been read by anything but its author. Review found the module structurally sound -- strict
manifest, per-replica coherent-draw revalidation, mean-centered covariance, refuses to overwrite the
frozen 20-replica reference -- and TWO VACUOUS GATES, both fixed in the same commit that tracked it:

  * SYMMETRY was `sym_err > 1e-30`, an ABSOLUTE threshold. Measured on the real products,
    `max|C| = 8.13e-79` and the diagonal median is 3.87e-86, so 1e-30 sits ~49 orders of magnitude
    above the scale of the quantity. Not merely loose: a COMPLETELY WRONG matrix would pass, because
    every entry of any plausible wrong matrix is also << 1e-30. The gate could not fail.
  * PSD was `min_eig >= -1e-9 * max(max_eig, 1.0)`. With `max_eig = 2.72e-77` the `max(..., 1.0)`
    pins the tolerance at the absolute -1e-9, so any negative eigenvalue this problem can produce
    passes. Same defect, same cause.

Both are now RELATIVE to the matrix's own scale. Measured against the two existing products the
fixed gates still pass with margin -- symmetry `max|C-C^T| = 0.0` exactly, and
`min_eig/max_eig = -8.4e-16` against a -1e-9 relative tolerance -- so this TIGHTENS a gate that
could not fire rather than loosening one that could. Same family as the `atol=1e-8` default measured
against cross sections of ~1e-38 caught under CLM-011 on 2026-08-06: an absolute tolerance inherited
into a problem whose natural scale is ~1e-80.

NOT YET RUN: no 100-replica product exists (`products/pet/bkgsub/` holds the 20-replica
`pet_cstat_bkgsub_5d.npz` and an interim 42-replica file) and the 1-100 replica inventory this script
globs is not on disk, so the gate battery has never executed on real input. That is BEN-040's blind
spot, which is why this review is recorded rather than assumed.

Also fixed: `_ND` was hardcoded to an absolute /pscratch path, so the module could not be
imported in any other checkout and its gates could not be unit-tested at all. It is now
resolved from `__file__`.

Strict extension of `combine_cstat_bkgsub.py` to the full 1-100 statistical
inventory. In one pass it:

  * loads the exact 5D replica manifest (rejects missing / duplicate /
    wrong-shape / non-finite / wrong-id via `load_replica_manifest`);
  * re-validates EVERY replica's coherent data/MC Poisson contract from its
    weight file (`validate_full_replica_weights`: bootstrap seed matches the
    filename, `mc_indices` are the ordered full-sample range, and the stored
    `mc_bootstrap_factor` equals the canonical seed draw) -- can be skipped with
    --no-weight-check for a fast covariance-only rebuild once weights are
    already proven;
  * masks on the CORRECTED PET nominal CV>0 reported bins (the common mask/order
    shared by C_ml, C_syst, C_retrain, C_lateral) and asserts it is identical to
    the frozen 20-replica product's mask;
  * builds the replica-MEAN-centered covariance C = Z^T Z / (n-1);
  * runs the covariance gate battery: exact symmetry, PSD (eigvalsh), finite
    diagonal, and the GPU-floor comparison;
  * writes a NEW product (default pet_cstat_bkgsub_5d_100rep.npz) and a rich
    summary. It NEVER overwrites the 20-replica product.

The estimator/subsample seeds are held fixed across replicas by the launcher
(PET_ESTIMATOR_SEED=42, --seed 0); C_stat therefore varies only the Poisson
replica id. That invariance is a launcher constant, recorded in the summary.

  python3 pet/combine_cstat_bkgsub_100rep.py \
    --glob 'products/pet/bkgsub/bootstrap_replicas/5d/pet_bootstrap_5d_*.npz' \
    --weights-dir products/pet/bkgsub/bootstrap_replicas/weights \
    --cv products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz \
    --floor products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json \
    --ref20 products/pet/bkgsub/pet_cstat_bkgsub_5d.npz \
    --expected-ids 1-100 \
    --out products/pet/bkgsub/pet_cstat_bkgsub_5d_100rep.npz
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

# Resolved from THIS file rather than hardcoded to /pscratch/... -- the absolute scratch path
# made the module unimportable in any other checkout, which is why its gate battery had never
# been exercised by a test. Scratch is also purgeable (CLAUDE.md), so a tracked module must not
# depend on a scratch-absolute path to find its own siblings.
_ND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ND not in sys.path:
    sys.path.insert(0, _ND)
from replica_manifest import load_replica_manifest       # noqa: E402
from pet_bootstrap import validate_full_replica_weights  # noqa: E402


def compute_cstat(X, cv):
    """Replica-mean-centered C_stat on the CV>0 reported bins + gate battery.

    X: (n_rep, n_bins) replica cross sections (full grid).
    cv: (n_bins,) corrected nominal cross section (defines the CV>0 mask/order).
    Returns (C, rep_mask, sigma, rel, stats, gates). C is on the reported
    sub-space (n_reported x n_reported). C = Z^T Z / (n-1) is a Gram matrix, so
    its nonzero spectrum equals that of the small n_rep x n_rep Gram G = Z Z^T /
    (n-1); PSD is verified from G (full-space min eig = 0 by construction).
    """
    X = np.asarray(X, float); cv = np.asarray(cv, float)
    if X.ndim != 2 or cv.ndim != 1 or X.shape[1] != cv.shape[0]:
        raise ValueError(f"shape mismatch: X{X.shape} vs cv{cv.shape}")
    n = X.shape[0]
    if n < 2:
        raise ValueError("need >=2 replicas for a covariance")
    rep = cv > 0
    Xr = X[:, rep]; cvr = cv[rep]
    Z = Xr - Xr.mean(0)
    C = (Z.T @ Z) / (n - 1)
    sig = np.sqrt(np.clip(np.diag(C), 0, None))
    rel = sig / cvr
    sym_err = float(np.max(np.abs(C - C.T)))
    diag_finite = bool(np.all(np.isfinite(np.diag(C))))
    G = (Z @ Z.T) / (n - 1)
    gvals = np.linalg.eigvalsh(0.5 * (G + G.T))
    min_eig = float(gvals.min()); max_eig = float(gvals.max())
    # RELATIVE to the matrix's own scale, not absolute -- see REVIEW STATUS. The previous
    # `-1e-9 * max(max_eig, 1.0)` pinned the tolerance at -1e-9 absolute because max_eig is ~1e-77
    # here, so no negative eigenvalue this problem can produce could ever have failed it.
    c_scale = float(np.abs(C).max())
    sym_tol = 1e-12 * c_scale
    sym_ok = bool(sym_err <= sym_tol)
    psd_ok = bool(min_eig >= -1e-9 * max_eig) if max_eig > 0 else bool(min_eig >= 0.0)
    stats = {
        "sqrt_trace": float(np.sqrt(max(C.trace(), 0.0))),
        "per_bin_rel_median": float(np.median(rel)),
        "per_bin_rel_p90": float(np.percentile(rel, 90)),
        "per_bin_rel_max": float(rel.max()),
        "n_reported_bins": int(rep.sum()),
    }
    gates = {
        "symmetry_max_abs": sym_err,
        "symmetry_tolerance_relative": sym_tol,
        "symmetry_ok": sym_ok,
        "covariance_scale_max_abs": c_scale,
        "gram_min_eigenvalue": min_eig, "gram_max_eigenvalue": max_eig,
        "eigen_note": "Gram (nonzero) spectrum of C=Z^T Z/(n-1); full-space min eig=0 by construction",
        "psd": psd_ok, "finite_diagonal": diag_finite,
    }
    return C, rep, sig, rel, stats, gates


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", required=True)
    ap.add_argument("--weights-dir",
                    default="products/pet/bkgsub/bootstrap_replicas/weights")
    ap.add_argument("--cv", default="products/pet/bkgsub/pet_nominal_bkgsub_5d_xsec.npz")
    ap.add_argument("--floor", default="products/pet/bkgsub/pet_floor_bkgsub_5d_diagnostic.json")
    ap.add_argument("--ref20", default="products/pet/bkgsub/pet_cstat_bkgsub_5d.npz",
                    help="frozen 20-replica product; mask + sigma cross-check (not overwritten)")
    ap.add_argument("--expected-ids", required=True, help="inclusive LO-HI, e.g. 1-100")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-weight-check", action="store_true",
                    help="skip the per-replica coherent-draw revalidation (weights already proven)")
    a = ap.parse_args()

    lo, hi = (int(v) for v in a.expected_ids.split("-", 1))
    if hi < lo:
        ap.error("--expected-ids must be LO-HI with HI>=LO")
    if os.path.abspath(a.out) == os.path.abspath(a.ref20):
        ap.error("refuse to overwrite the frozen reference product with --out")

    paths = sorted(glob.glob(a.glob))
    X, ids = load_replica_manifest(paths, set(range(lo, hi + 1)))   # strict 1-100
    print(f"[manifest] PASS: {len(ids)} replicas, ids {ids.min()}-{ids.max()}, "
          f"nbins={X.shape[1]}, finite={bool(np.all(np.isfinite(X)))}")

    # coherent data/MC Poisson draw + ordered MC indices, per replica
    if not a.no_weight_check:
        for rid in ids.tolist():
            wf = os.path.join(a.weights_dir, f"pet_bootstrap_weights_{rid}.npz")
            with np.load(wf, allow_pickle=False) as w:
                n_events = int(w["w_push"].shape[0])
                validate_full_replica_weights(w, n_events, rid)
        print(f"[coherent-draw] PASS: all {len(ids)} weight files validate "
              f"(ordered full mc_indices + canonical mc_bootstrap_factor, n={n_events})")
    else:
        print("[coherent-draw] SKIPPED (--no-weight-check)")

    cv = np.asarray(np.load(a.cv)["xsec_flat"], float)
    if X.shape[1] != cv.shape[0]:
        raise SystemExit(f"[FAIL] replica nbins {X.shape[1]} != cv {cv.shape[0]}")

    C, rep, sig, rel, stats, gates = compute_cstat(X, cv)
    cvr = cv[rep]
    sqrt_tr = stats["sqrt_trace"]; relmed = stats["per_bin_rel_median"]
    sym_err = gates["symmetry_max_abs"]
    min_eig = gates["gram_min_eigenvalue"]; max_eig = gates["gram_max_eigenvalue"]
    diag_finite = gates["finite_diagonal"]; psd_ok = gates["psd"]
    print(f"[cov-gate] symmetry max|C-C^T|={sym_err:.3e} (tol "
          f"{gates['symmetry_tolerance_relative']:.3e}, rel. to max|C|="
          f"{gates['covariance_scale_max_abs']:.3e})  Gram min_eig={min_eig:.3e}  "
          f"max_eig={max_eig:.3e}  PSD={'PASS' if psd_ok else 'FAIL'} "
          f"(full-space min eig=0 by Gram construction)  finite_diag={diag_finite}")

    # common mask/order + convergence vs the frozen 20-replica product
    mask_match = None; relmed20 = None
    if a.ref20 and os.path.exists(a.ref20):
        with np.load(a.ref20) as r20:
            mask20 = np.asarray(r20["reported_mask"])
            mask_match = bool(np.array_equal(mask20, rep))
            if "sigma" in r20.files:                       # sigma20 lives in cv>0 space
                sig20 = np.asarray(r20["sigma"], float)
                relmed20 = float(np.median(sig20 / cvr))
        print(f"[mask] identical to 20-replica product: {mask_match}  "
              f"(20-rep per-bin rel median={100*relmed20:.3f}%)"
              if relmed20 is not None else
              f"[mask] identical to 20-replica product: {mask_match}")

    floor_med = None
    if os.path.exists(a.floor):
        floor_med = json.load(open(a.floor)).get("per_bin_rel_floor", {}).get("median")

    # C = Z^T Z / (n-1) is symmetric to machine precision and PSD by construction, so any failure
    # here is a numerical or logic regression and must refuse to write. Thresholds are RELATIVE (see
    # REVIEW STATUS): the previous absolute `sym_err > 1e-30` could not fail on a matrix whose
    # largest entry is ~1e-79, so it would have blessed an arbitrarily wrong matrix.
    sym_ok = gates["symmetry_ok"]
    if not (psd_ok and diag_finite and sym_ok):
        raise SystemExit(f"[FAIL] covariance gate: sym={sym_err:.3e} > tol "
                         f"{gates['symmetry_tolerance_relative']:.3e} (relative to max|C|="
                         f"{gates['covariance_scale_max_abs']:.3e})  psd={psd_ok} "
                         f"finite_diag={diag_finite}")

    np.savez_compressed(a.out, C_stat=C, reported_mask=rep, replica_ids=ids,
                        cv=cv, sigma=sig)
    gates["mask_identical_to_20rep"] = mask_match
    summary = {
        "campaign": "PET bkgsub 5D corrected C_stat -- 100-replica candidate (#15)",
        "n_replicas": int(X.shape[0]), "replica_ids": ids.tolist(),
        "expected_ids": f"{lo}-{hi}",
        "n_reported_bins": stats["n_reported_bins"],
        "sqrt_trace": sqrt_tr,
        "per_bin_rel_median": relmed,
        "per_bin_rel_p90": stats["per_bin_rel_p90"],
        "per_bin_rel_max": stats["per_bin_rel_max"],
        "floor_per_bin_rel_median": floor_med,
        "cstat_over_floor_ratio": (relmed / floor_med) if floor_med else None,
        "coherent_draw_checked": (not a.no_weight_check),
        "estimator_seed_fixed": 42, "subsample_seed_fixed": 0,
        "gates": gates,
        "reference_20rep": os.path.abspath(a.ref20) if a.ref20 else None,
        "per_bin_rel_median_20rep": relmed20,
        "out": os.path.abspath(a.out),
    }
    spath = os.path.splitext(a.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)
    print(f"[cstat-100] {X.shape[0]} replicas, {stats['n_reported_bins']} bins, "
          f"sqrt-trace={sqrt_tr:.4e}, per-bin rel median={100*relmed:.3f}% "
          f"p90={100*stats['per_bin_rel_p90']:.3f}%")
    if floor_med:
        print(f"[cstat-100] rel median {relmed:.3e} vs floor {floor_med:.3e} "
              f"(ratio {relmed/floor_med:.0f}x)")
    print(f"[cstat-100] wrote {a.out} + {spath}")


if __name__ == "__main__":
    main()
