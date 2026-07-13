#!/usr/bin/env python3
"""Phase 6 (preliminary vertical): corrected PET C_syst on the bkgsub nominal.

Reproduces pet_systematics_5d.py's VALIDATED, convention-corrected C_syst block
verbatim (per-knob mean-centered +/-1sigma `mat_covariance`, + 100-flux
mean-centered, MAT biased 1/N, `guarded_ratio` invalid-policy) on the CORRECTED
nominal push weights and the corrected-nominal CV>0 reported-bin mask -- but
builds ONLY the vertical C_syst. It deliberately does NOT build C_ml (that is
the crossed-seed ensemble, combine_cml_bkgsub.py -- pet_systematics_5d's built-in
C_ml is the FORBIDDEN nominal-vs-alt rank-1 outer product) nor C_stat (strict
combiner).

STATUS: PRELIMINARY / support-limited. Uses the pre-fix `bank_uthrow_5d`
(KNOWN_ISSUES #13/#16: CV-support-limited laterals, background frozen at CV).
The frozen-reweighter vertical calculation consumes TRUTH ratios only, so this
is a legitimate preliminary vertical block; the FINAL C_syst must consume the
GBDT session's background-aware / selection-complete rebank when it lands.

Run under root_6_28 on a compute node (124 x 32.8M 5D re-binnings).
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

from pet_systematics_5d import PETxsec5D, KNOB_BANDS, _opt, RHO_CLIP  # noqa: E402
from uq_math import guarded_ratio, mat_covariance, require_truth_ratio_bank  # noqa: E402
from xsec_nd import total_xsec  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc", default=f"{_ND}/of_inputs_pc_fullcloud_bkgsub_5d.npz")
    ap.add_argument("--w-source", default=f"{_ND}/of_inputs_5d.npz")
    ap.add_argument("--weights", default=f"{_ND}/products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz")
    ap.add_argument("--bank", default=f"{_ND}/bank_uthrow_5d")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=f"{_ND}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="neutral",
                    help="matches the locked GBDT decision: hold ~5e-5 GENIE "
                         "negative-weight artifacts at CV for the affected knob")
    ap.add_argument("--out", default=f"{_ND}/products/pet/bkgsub/pet_csyst_prelim_bkgsub_5d.npz")
    a = ap.parse_args()

    pet = PETxsec5D(a.pc, a.weights, a.mcfile, a.flux_hist, a.w_source, a.comp_ref)
    x_cv = pet.xsec(None)
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    print(f"[csyst] CV total={total_xsec(x_cv.reshape(pet.shape, order='C'), pet.edges):.4e} "
          f"reported={nrep}", flush=True)

    flux_ids = require_truth_ratio_bank(a.bank, KNOB_BANDS, expected_flux=100)
    ratio = lambda v, l: guarded_ratio(v, l, invalid_policy=a.invalid_ratio, clip=RHO_CLIP)

    C = np.zeros((nrep, nrep))
    perband = {}
    for b in KNOB_BANDS:
        x_m = pet.xsec(ratio(_opt(a.bank, f"sig_{b}_t_0.npy"), f"{b}:-1"))[rep]
        x_p = pet.xsec(ratio(_opt(a.bank, f"sig_{b}_t_1.npy"), f"{b}:+1"))[rep]
        cb = mat_covariance(np.stack([x_m, x_p]))
        C += cb
        perband[b] = float(np.sqrt(np.trace(cb)))
        print(f"[csyst] {b}: sqrt-tr={perband[b]:.3e} (mean-centered +/-)", flush=True)
    fX = [pet.xsec(ratio(_opt(a.bank, f"sig_flux_t_{u}.npy"), f"Flux:{u}"))[rep]
          for u in flux_ids]
    Cf = mat_covariance(np.asarray(fX))
    C += Cf
    perband["flux"] = float(np.sqrt(np.trace(Cf)))
    print(f"[csyst] flux ({len(flux_ids)}): sqrt-tr={perband['flux']:.3e}", flush=True)

    sig = np.sqrt(np.clip(np.diag(C), 0, None))
    rel = sig / base
    np.savez_compressed(a.out, C_syst=C, reported_mask=rep, cv=x_cv, sigma=sig)
    summary = {
        "campaign": "PET bkgsub 5D corrected C_syst VERTICAL (Phase 6 PRELIMINARY)",
        "status": "PRELIMINARY / support-limited: pre-fix bank_uthrow_5d "
                  "(KNOWN_ISSUES #13/#16); FINAL needs GBDT background-aware/"
                  "selection-complete rebank (uq_5d, in flight).",
        "n_reported_bins": nrep,
        "invalid_ratio": a.invalid_ratio,
        "sqrt_trace": float(np.sqrt(max(C.trace(), 0.0))),
        "per_bin_rel_median": float(np.median(rel)),
        "per_bin_rel_p90": float(np.percentile(rel, 90)),
        "per_band_sqrt_trace": perband,
        "bank": a.bank, "weights": a.weights, "out": os.path.abspath(a.out),
    }
    spath = os.path.splitext(a.out)[0] + ".summary.json"
    json.dump(summary, open(spath, "w"), indent=2)
    print(f"[csyst] sqrt-trace={summary['sqrt_trace']:.3e} "
          f"per-bin rel median={100*summary['per_bin_rel_median']:.2f}% "
          f"p90={100*summary['per_bin_rel_p90']:.2f}%")
    print(f"[csyst] wrote {a.out} + {spath}")
    print("[csyst] PRELIMINARY vertical C_syst done (support-limited; not final).")


if __name__ == "__main__":
    main()
