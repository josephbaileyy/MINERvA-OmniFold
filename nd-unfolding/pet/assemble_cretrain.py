#!/usr/bin/env python3
"""Assemble the Phase-7 retraining-response covariance C_retrain.

Per the predeclared consequence rule (PET_UQ_PRODUCTION_STATUS.md Phase 7):
    C_retrain = sum_u outer(Delta_u, Delta_u)   over MATERIAL bands (rank-1 per band)
where Delta_u = x_retrain - x_frozen on the corrected-nominal reported mask
(CV>0, 10,550 bins). Immaterial bands are documented and omitted (never silently
dropped). C_retrain is PSD by construction (sum of rank-1 outer products) and is
added to C_syst-final downstream.

Inputs are the per-universe response.npz + summary.json produced by
phase7_extract_compare.py. BANK-INVARIANT/FINAL: these consume only signal
truth ratios, bit-identical between bank_uthrow_5d and bank_uthrow_5d_bkgaware
(see PET_UQ receipts). ROOT-free; login-runnable pure numpy.
"""
import argparse
import json
import os

import numpy as np

_ND = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding"
# predeclared set: model knobs (+1sigma) + dominant flux universe
DEFAULT_TAGS = ["MaRES_1", "2p2h_1", "MaCCQE_1", "LowQ2_1", "CCQEPauliSupViaKF_1", "flux_55"]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--p7dir", default=f"{_ND}/products/pet/bkgsub/p7")
    ap.add_argument("--tags", default=",".join(DEFAULT_TAGS),
                    help="comma-separated universe tags (response file stems)")
    ap.add_argument("--out", default=f"{_ND}/products/pet/bkgsub/pet_cretrain_bkgsub_5d.npz")
    ap.add_argument("--require-all", action="store_true",
                    help="fail if any tag's response/summary is missing (default: skip+warn)")
    a = ap.parse_args()
    tags = [t for t in a.tags.split(",") if t]

    mask_ref = None
    contribs, skipped, immaterial = [], [], []
    C = None
    for tag in tags:
        rp = os.path.join(a.p7dir, f"pet_p7_{tag}_response.npz")
        sp = os.path.join(a.p7dir, f"pet_p7_{tag}_response.summary.json")
        if not (os.path.exists(rp) and os.path.exists(sp)):
            msg = f"missing response/summary for {tag}"
            if a.require_all:
                raise SystemExit(f"[FAIL] {msg}")
            print(f"[cretrain] SKIP {tag}: {msg}", flush=True); skipped.append(tag); continue
        z = np.load(rp)
        rep = z["reported_mask"]
        delta = np.asarray(z["delta_reported"], dtype=np.float64)
        if mask_ref is None:
            mask_ref = rep; n = int(rep.sum()); C = np.zeros((n, n), dtype=np.float64)
        elif not np.array_equal(rep, mask_ref):
            raise SystemExit(f"[FAIL] {tag} reported_mask differs from reference "
                             "(all universes must share the corrected-nominal CV>0 mask)")
        if delta.shape[0] != mask_ref.sum():
            raise SystemExit(f"[FAIL] {tag} delta len {delta.shape[0]} != {int(mask_ref.sum())}")
        m = json.load(open(sp)).get("materiality", {})
        material = bool(m.get("material"))
        info = {"tag": tag, "material": material,
                "overall_ratio": m.get("overall_ratio"),
                "frac_bins_over": m.get("frac_bins_over"),
                "norm_delta": float(np.linalg.norm(delta))}
        if material:
            C += np.outer(delta, delta)  # rank-1, PSD
            contribs.append(info)
            print(f"[cretrain] + {tag}: MATERIAL (overall={info['overall_ratio']}, "
                  f"||Delta||={info['norm_delta']:.3e}) -> rank-1 added", flush=True)
        else:
            immaterial.append(info)
            print(f"[cretrain] . {tag}: immaterial (overall={info['overall_ratio']}) -> omitted",
                  flush=True)

    if C is None:
        raise SystemExit("[FAIL] no universes loaded")
    # PSD sanity (sum of outer products => >= 0 up to fp noise)
    evmin = float(np.linalg.eigvalsh(C)[0]) if C.shape[0] <= 12000 else None
    diag = np.diag(C)
    sqrt_tr = float(np.sqrt(np.trace(C)))
    summary = {
        "campaign": "PET bkgsub Phase 7 C_retrain (retraining-response covariance)",
        "status": "bank-invariant / FINAL for the retraining-response (see KNOWN_ISSUES receipts)",
        "consequence_rule": "C_retrain = sum_u outer(Delta_u, Delta_u) over MATERIAL bands (rank-1 each)",
        "n_reported_bins": int(mask_ref.sum()),
        "rank": len(contribs),
        "contributing_material_bands": contribs,
        "immaterial_documented_omitted": immaterial,
        "skipped_missing": skipped,
        "sqrt_trace": sqrt_tr,
        "min_eig": evmin,
        "per_bin_sigma_median_frac_note": "sigma=sqrt(diag(C_retrain)); combine with C_syst-final downstream",
    }
    np.savez_compressed(a.out, C_retrain=C, reported_mask=mask_ref,
                        sigma=np.sqrt(np.clip(diag, 0, None)),
                        contributing=np.array([c["tag"] for c in contribs]))
    json.dump(summary, open(os.path.splitext(a.out)[0] + ".summary.json", "w"), indent=2)
    print(f"[cretrain] rank={len(contribs)} material bands; sqrt(tr)={sqrt_tr:.3e}; "
          f"min_eig={evmin}; wrote {a.out}")


if __name__ == "__main__":
    main()
