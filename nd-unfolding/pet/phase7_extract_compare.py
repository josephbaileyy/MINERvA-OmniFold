#!/usr/bin/env python3
"""Phase 7: frozen-map vs retrained-map universe estimate + materiality test.

For one systematic universe u, using ONE common corrected nominal cloud/mask:
    CV        = PETxsec5D(nominal_pc, NOMINAL_weights).xsec(None)      # nominal
    x_frozen  = PETxsec5D(nominal_pc, NOMINAL_weights).xsec(r_u)       # frozen map
    x_retrain = PETxsec5D(nominal_pc, RETRAINED_weights).xsec(r_u)     # retrained map
    s_u       = x_frozen - CV        (frozen one-sided systematic shift)
    Delta_u   = x_retrain - x_frozen (retraining response)
on the reported mask (CV>0, the corrected-nominal 10,550-bin mask).

PREDECLARED materiality criterion (see PET_UQ_PRODUCTION_STATUS.md Phase 7 --
fixed BEFORE any retraining result is inspected):
    overall_ratio = ||Delta_u|| / ||s_u||                 (L2 on reported mask)
    frac_bins     = mean( |Delta_u| > 0.25 * |s_u| )      (reported bins)
    MATERIAL(u)  := overall_ratio > 0.25  OR  frac_bins > 0.05
If MATERIAL for any targeted band the FINAL C_total gains a retraining-response
inflation C_retrain = sum_u outer(Delta_u, Delta_u) over material bands (rank-1
per band), added to C_syst-final. If immaterial for all, the response is
DOCUMENTED as negligible and omitted (never silently dropped).

nominal_pc keeps bit-identical w_truth (PETxsec5D's W-source gate); only the
push weights (w_push) differ between frozen and retrained. Both apply the SAME
r_u, so Delta_u isolates the map-retraining response. PyROOT (root_6_28).

STATUS of the ratio source: PRELIMINARY when --bank is the pre-fix
`bank_uthrow_5d` (KNOWN_ISSUES #13/#16). FINAL uses the background-aware bank.
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_ND = f"{_REPO}/nd-unfolding"
if _ND not in sys.path:
    sys.path.insert(0, _ND)


def _ensure_pyroot():
    try:
        import ROOT  # noqa: F401
        return
    except Exception:
        prefix = os.environ.get("ROOT628_PREFIX", "/global/homes/j/josephrb/.conda/envs/root_6_28")
        rootpy = f"{prefix}/bin/python3"
        if os.environ.get("_PET_P7_REEXEC") == "1" or not os.path.exists(rootpy):
            raise SystemExit("[FAIL] PyROOT unavailable after re-exec; source setup_salloc_env.sh")
        os.environ["_PET_P7_REEXEC"] = "1"
        setup = f"{_REPO}/setup_salloc_env.sh"
        os.execvp("bash", ["bash", "-lc",
                            f"source {setup} >/dev/null 2>&1; exec {rootpy} "
                            + " ".join(f"'{x}'" for x in [os.path.abspath(__file__), *sys.argv[1:]])])


def universe_file(key):
    """Pure key -> (bank filename, human label). ROOT-free (unit-testable).
    key = 'MaRES:1' (band:endpoint 0|1) or 'flux:37' (flux universe u)."""
    name, idx = key.split(":")
    idx = int(idx)
    if name == "flux":
        return f"sig_flux_t_{idx}.npy", f"Flux:{idx}"
    if idx not in (0, 1):
        raise ValueError(f"knob endpoint must be 0 or 1, got {idx} in {key!r}")
    return f"sig_{name}_t_{idx}.npy", f"{name}:{'+1' if idx else '-1'}"


def _universe_ratio(bank, key, invalid_policy):
    from pet_systematics_5d import _opt, RHO_CLIP
    from uq_math import guarded_ratio
    fname, label = universe_file(key)
    r = guarded_ratio(_opt(bank, fname), label, invalid_policy=invalid_policy, clip=RHO_CLIP)
    return np.asarray(r, dtype=np.float64), label


THRESH_OVERALL = 0.25   # ||Delta||/||s|| material threshold
THRESH_BIN = 0.25       # per-bin |Delta| > THRESH_BIN*|s|
THRESH_FRAC = 0.05      # material if that holds in > THRESH_FRAC of reported bins


def materiality(delta, s):
    """delta, s on the reported mask. Returns the predeclared metrics + verdict."""
    n_s = float(np.linalg.norm(s))
    n_d = float(np.linalg.norm(delta))
    overall = n_d / n_s if n_s > 0 else float("inf")
    with np.errstate(divide="ignore", invalid="ignore"):
        bin_hit = np.abs(delta) > THRESH_BIN * np.abs(s)
    frac = float(np.mean(bin_hit))
    material = bool(overall > THRESH_OVERALL or frac > THRESH_FRAC)
    return {"norm_delta": n_d, "norm_s": n_s, "overall_ratio": overall,
            "frac_bins_over": frac, "material": material,
            "thresholds": {"overall": THRESH_OVERALL, "bin": THRESH_BIN, "frac": THRESH_FRAC}}


def main():
    _ensure_pyroot()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--universe", required=True)
    ap.add_argument("--pc", default=f"{_ND}/of_inputs_pc_fullcloud_bkgsub_5d.npz")
    ap.add_argument("--w-source", default=f"{_ND}/of_inputs_5d.npz")
    ap.add_argument("--nominal-weights",
                    default=f"{_ND}/products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz")
    ap.add_argument("--retrained-weights", required=True)
    ap.add_argument("--bank", default=f"{_ND}/bank_uthrow_5d")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="neutral")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=f"{_ND}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", required=True, help="npz for CV/x_frozen/x_retrain/delta + metrics")
    a = ap.parse_args()

    from pet_systematics_5d import PETxsec5D
    from xsec_nd import total_xsec

    is_null = a.universe in ("null", "identity")
    if is_null:
        # NULL CONTROL: r=identity, so x_frozen == CV and Delta_null = x_null - CV
        # is the pure training-noise floor (see driver). No bank read.
        r_u, label = None, "null"
    else:
        r_u, label = _universe_ratio(a.bank, a.universe, a.invalid_ratio)

    pet_nom = PETxsec5D(a.pc, a.nominal_weights, a.mcfile, a.flux_hist, a.w_source, a.comp_ref)
    x_cv = pet_nom.xsec(None)
    rep = x_cv > 0
    x_frozen = pet_nom.xsec(r_u)

    pet_re = PETxsec5D(a.pc, a.retrained_weights, a.mcfile, a.flux_hist, a.w_source, a.comp_ref)
    # CV consistency guard: the retrained push must bin the SAME reported support
    x_cv_re = pet_re.xsec(None)
    if not np.array_equal(x_cv_re > 0, rep):
        # retrained CV support can differ where push->0; intersect and warn (do NOT crash)
        print(f"[p7cmp] WARN retrained CV support differs on {int((rep!=(x_cv_re>0)).sum())} bins; "
              "using the nominal reported mask (common central).", flush=True)
    x_retrain = pet_re.xsec(r_u)

    cv, xf, xr = x_cv[rep], x_frozen[rep], x_retrain[rep]
    s_u = xf - cv
    delta = xr - xf
    if is_null:
        # noise floor: s_u == 0 by construction, so report ||Delta_null|| directly
        # and its scale relative to CV. NOT a material/immaterial verdict.
        nd, ncv = float(np.linalg.norm(delta)), float(np.linalg.norm(cv))
        m = {"null_control": True, "norm_delta": nd, "norm_cv": ncv,
             "noise_floor_over_cv": (nd / ncv if ncv > 0 else float("inf")),
             "frac_bins_over_1pct_cv": float(np.mean(np.abs(delta) > 0.01 * np.abs(cv))),
             "material": None}
    else:
        m = materiality(delta, s_u)

    tot = lambda v: float(total_xsec(v.reshape(pet_nom.shape, order="C"), pet_nom.edges))
    # BANK-INVARIANT (verified 2026-07-14): the retraining-response consumes only
    # sig_<band>_t truth ratios, which are bit-identical between bank_uthrow_5d and
    # the background-aware bank_uthrow_5d_bkgaware (all 30 consumed files verified;
    # unified_throw.py --dump is signal-only, so the KNOWN_ISSUES #13 background-aware
    # fix leaves these inputs unchanged). Results are FINAL for the retraining-
    # response, NOT stale/pre-fix. See PET_UQ_PRODUCTION_STATUS.md receipts.
    summary = {
        "campaign": "PET bkgsub Phase 7 retraining-response (bank-invariant; verified vs bkgaware)"
                    if os.path.basename(a.bank) in ("bank_uthrow_5d", "bank_uthrow_5d_bkgaware")
                    else "PET bkgsub Phase 7 retraining-response",
        "universe": a.universe, "label": label,
        "bank": os.path.abspath(a.bank), "invalid_ratio": a.invalid_ratio,
        "status": "bank-invariant (verified 2026-07-14): consumes only sig_<band>_t truth ratios, "
                  "bit-identical bank_uthrow_5d vs bank_uthrow_5d_bkgaware (unified_throw.py --dump "
                  "is signal-only; KNOWN_ISSUES #13 touches only per-universe background). FINAL for "
                  "the retraining-response; C_syst-final and lateral still run on the bkgaware bank."
                  if os.path.basename(a.bank) in ("bank_uthrow_5d", "bank_uthrow_5d_bkgaware")
                  else "final-bank",
        "n_reported_bins": int(rep.sum()),
        "total_xsec": {"cv": tot(x_cv), "frozen": tot(x_frozen), "retrain": tot(x_retrain)},
        "materiality": m,
        "retrained_weights": os.path.abspath(a.retrained_weights),
        "nominal_weights": os.path.abspath(a.nominal_weights),
        "out": os.path.abspath(a.out),
    }
    np.savez_compressed(a.out, cv=x_cv, x_frozen=x_frozen, x_retrain=x_retrain,
                        reported_mask=rep, delta_reported=delta, s_reported=s_u,
                        ratio=(np.ones(1) if r_u is None else r_u), universe=a.universe)
    spath = os.path.splitext(a.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)
    if is_null:
        print(f"[p7cmp] NULL CONTROL: ||Delta_null||={m['norm_delta']:.3e} "
              f"(noise floor = {m['noise_floor_over_cv']*100:.2f}% of ||CV||; "
              f"frac bins >1%CV = {m['frac_bins_over_1pct_cv']:.3f})")
    else:
        print(f"[p7cmp] {label}: ||Delta||={m['norm_delta']:.3e} ||s||={m['norm_s']:.3e} "
              f"overall={m['overall_ratio']:.3f} frac_bins>({THRESH_BIN}|s|)={m['frac_bins_over']:.3f} "
              f"-> MATERIAL={m['material']}")
    print(f"[p7cmp] totals cv={summary['total_xsec']['cv']:.4e} "
          f"frozen={summary['total_xsec']['frozen']:.4e} retrain={summary['total_xsec']['retrain']:.4e}")
    print(f"[p7cmp] wrote {a.out} + {spath}")


if __name__ == "__main__":
    main()
