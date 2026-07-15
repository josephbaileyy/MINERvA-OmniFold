#!/usr/bin/env python3
"""Rank the 100 flux universes by frozen-shift norm ||s_u|| to pick the single
'dominant flux universe' for the Phase-7 retraining-response test (predeclared).

s_u = PETxsec5D(nominal).xsec(r_u) - CV on the corrected-nominal reported mask
(CV>0). Same nominal cloud/weights/mask as every other Phase-7 component; only
the frozen map is used here (no retraining) -- this just SELECTS which flux
universe to retrain. PyROOT (root_6_28); self-reexec mirrors extract_compare.
PRELIMINARY when --bank is the pre-fix bank_uthrow_5d (KNOWN_ISSUES #13/#16).
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


def main():
    _ensure_pyroot()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pc", default=f"{_ND}/of_inputs_pc_fullcloud_bkgsub_5d.npz")
    ap.add_argument("--w-source", default=f"{_ND}/of_inputs_5d.npz")
    ap.add_argument("--nominal-weights",
                    default=f"{_ND}/products/pet/bkgsub/pet_nominal_bkgsub_5d_weights.npz")
    ap.add_argument("--bank", default=f"{_ND}/bank_uthrow_5d")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="neutral")
    ap.add_argument("--n-flux", type=int, default=100)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default=f"{_ND}/products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", default=f"{_ND}/products/pet/bkgsub/p7/pet_p7_flux_rank.json")
    a = ap.parse_args()

    from pet_systematics_5d import PETxsec5D, _opt, RHO_CLIP
    from uq_math import guarded_ratio

    pet = PETxsec5D(a.pc, a.nominal_weights, a.mcfile, a.flux_hist, a.w_source, a.comp_ref)
    x_cv = pet.xsec(None)
    rep = x_cv > 0
    print(f"[flux-rank] CV built; reported bins = {int(rep.sum())}", flush=True)

    rows = []
    for u in range(a.n_flux):
        fname = f"sig_flux_t_{u}.npy"
        arr = _opt(a.bank, fname)
        if arr is None:
            print(f"[flux-rank] u={u}: bank file missing ({fname}); skip", flush=True)
            continue
        r_u = guarded_ratio(arr, f"Flux:{u}", invalid_policy=a.invalid_ratio, clip=RHO_CLIP)
        s_u = (pet.xsec(np.asarray(r_u, dtype=np.float64)) - x_cv)[rep]
        rows.append({"u": u, "norm_s": float(np.linalg.norm(s_u)),
                     "max_abs_s": float(np.max(np.abs(s_u)))})
        if (u + 1) % 10 == 0:
            print(f"[flux-rank] {u+1}/{a.n_flux} done", flush=True)

    rows.sort(key=lambda d: d["norm_s"], reverse=True)
    top = rows[0] if rows else None
    out = {"campaign": "PET bkgsub Phase 7 flux-universe ranking",
           "bank": os.path.abspath(a.bank),
           "status": "bank-invariant (verified 2026-07-14): sig_flux_t_{u} bit-identical "
                     "bank_uthrow_5d vs bank_uthrow_5d_bkgaware"
                     if os.path.basename(a.bank) in ("bank_uthrow_5d", "bank_uthrow_5d_bkgaware")
                     else "final-bank",
           "n_ranked": len(rows), "n_reported_bins": int(rep.sum()),
           "dominant": top, "ranking": rows}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=2)
    if top:
        med = float(np.median([r["norm_s"] for r in rows]))
        print(f"[flux-rank] DOMINANT flux universe u={top['u']} "
              f"||s||={top['norm_s']:.3e} (median over {len(rows)} = {med:.3e}; "
              f"dominant/median = {top['norm_s']/med:.2f}x)")
    print(f"[flux-rank] wrote {a.out}")


if __name__ == "__main__":
    main()
