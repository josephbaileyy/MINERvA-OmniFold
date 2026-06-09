#!/usr/bin/env python3
"""Fold the lateral (detector-response) systematic band into the PET 4D budget.

The PET combined covariance (pet_systematics.py) holds the trained reco point clouds
FIXED, so it captures the reweight/vertical systematics + flux + stat + ML, but the
LATERAL universes (muon-energy scale, beam angle, MINOS efficiency, muon resolution)
shift the reco KINEMATICS -- they would move the clouds, which the frozen-reweighter
path cannot do. So lateral contributes ZERO to the PET budget as shipped (its one
documented approximation).

This closes that gap with an engine-INDEPENDENT correction. The lateral bands are pure
detector response: the response of the unfolded cross section to a muon-energy/beam
shift is set by the detector smearing, not by which density-ratio estimator (GBDT vs
PET) performs the OmniFold step. So the lateral FRACTIONAL covariance measured in the
GBDT 4D campaign (uq_universe_4d_covariance_combined.root, where the laterals WERE
re-unfolded as discrete +-1sigma universes) transfers to PET on the shared (pt,pz,
eavail,q3) grid:

    F_ab           = C^GBDT_lateral_ab / (x^GBDT_a x^GBDT_b)      (fractional, GBDT bins)
    C^PET_lateral_ij = F_(map i)(map j) * x^PET_i x^PET_j         (PET bins, shared grid)

mapped bin-to-bin through the full 10976-cell grid (reported = xsec>0). A full per-lateral
PET re-inference (re-dump the lateral reco clouds, re-run PET inference per universe) is
the residual refinement, recorded as deferred. Lateral is subdominant (the GBDT budget is
flux/model-dominated), so this correction is small but removes the one zero in the budget.

  python pet_lateral_correction.py     # updates products/pet/pet_4d_covariance_combined.root
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

LATERAL = ["BeamAngleX", "BeamAngleY", "MinosEfficiency", "MuonResolution",
           "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]


def _th2(h):
    n = h.GetNbinsX()
    a = np.empty((n, n))
    for i in range(n):
        for k in range(n):
            a[i, k] = h.GetBinContent(i + 1, k + 1)
    return a


def main():
    import ROOT
    from pet_systematics import PETxsec
    ap = argparse.ArgumentParser()
    ap.add_argument("--gbdt-cov", default="uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined.root")
    ap.add_argument("--gbdt-prod", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--pet-cov", default="products/pet/pet_4d_covariance_combined.root")
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--weights", default="products/pet/pet_weights_full.npz")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    args = ap.parse_args()

    # --- GBDT full-grid CV + reported mask (mask = xsec>0 over the 10976 grid) ---
    g = ROOT.TFile.Open(args.gbdt_prod)
    hx = g.Get("hXSecND_flat")
    xg_full = np.array([hx.GetBinContent(i + 1) for i in range(hx.GetNbinsX())])
    g.Close()
    gmask = np.where(xg_full > 0)[0]              # full-grid indices of GBDT reported bins
    xg = xg_full[gmask]
    print(f"[lat] GBDT grid={xg_full.size} reported={gmask.size}")

    # --- GBDT lateral covariance (sum of the 6 detector bands), on GBDT reported bins ---
    fc = ROOT.TFile.Open(args.gbdt_cov)
    C_lat_g = None
    used = []
    for b in LATERAL:
        h = fc.Get(f"hCov_universe4d_{b}")
        if not h:
            print(f"[lat] WARN missing band {b}"); continue
        A = _th2(h)
        C_lat_g = A if C_lat_g is None else C_lat_g + A
        used.append(b)
    fc.Close()
    if C_lat_g is None:
        raise SystemExit("[FAIL] no lateral bands found in the GBDT cov")
    assert C_lat_g.shape[0] == gmask.size, "GBDT cov dim != reported mask"
    st_lat_g = float(np.sqrt(np.trace(C_lat_g)))
    medfrac_g = float(np.median(np.sqrt(np.clip(np.diag(C_lat_g), 0, None))[xg > 0] / xg[xg > 0]))
    print(f"[lat] GBDT lateral bands {used}: sqrt-tr={st_lat_g:.3e}  median frac={100*medfrac_g:.2f}%")

    # fractional lateral covariance on the GBDT grid
    inv = np.where(xg > 0, 1.0 / xg, 0.0)
    F = C_lat_g * np.outer(inv, inv)              # dimensionless

    # --- PET full-grid CV + reported mask (recompute; fast single binning pass) ---
    pet = PETxsec(args.pc, args.weights, args.mcfile, args.flux_hist,
                  comp_ref_root=args.gbdt_prod)
    xpet_full = pet.xsec(None)                    # full grid (10976)
    pmask = np.where(xpet_full > 0)[0]
    xpet = xpet_full[pmask]
    print(f"[lat] PET grid={xpet_full.size} reported={pmask.size}")

    # map each PET reported bin -> its position in the GBDT reported list (or -1)
    g_pos = -np.ones(xg_full.size, dtype=int)
    g_pos[gmask] = np.arange(gmask.size)
    pet_to_g = g_pos[pmask]                       # (n_pet,) GBDT-reported pos or -1
    have = pet_to_g >= 0
    print(f"[lat] PET bins with GBDT lateral info: {int(have.sum())}/{pmask.size} "
          f"(missing {int((~have).sum())} -> 0 lateral)")

    # C_pet_lateral_ij = F[pet_to_g[i], pet_to_g[j]] * xpet_i * xpet_j  (0 where unmapped)
    Fsub = np.zeros((pmask.size, pmask.size))
    idx = np.where(have)[0]
    Fsub[np.ix_(idx, idx)] = F[np.ix_(pet_to_g[idx], pet_to_g[idx])]
    C_pet_lat = Fsub * np.outer(xpet, xpet)
    st_lat_p = float(np.sqrt(np.trace(C_pet_lat)))
    medfrac_p = float(np.median(np.sqrt(np.clip(np.diag(C_pet_lat), 0, None))[xpet > 0] / xpet[xpet > 0]))
    print(f"[lat] PET lateral (transferred): sqrt-tr={st_lat_p:.3e}  median frac={100*medfrac_p:.2f}%")

    # --- add to the PET budget, rewrite the cov file (C_lateral new; C_total updated) ---
    p = ROOT.TFile.Open(args.pet_cov, "UPDATE")
    C = {nm: _th2(p.Get(nm)) for nm in ("C_syst", "C_stat", "C_ML")}
    assert C["C_syst"].shape[0] == pmask.size, "PET cov dim != recomputed PET reported mask"
    C_total = C["C_syst"] + C["C_stat"] + C["C_ML"] + C_pet_lat
    n = pmask.size
    for nm, M in [("C_lateral", C_pet_lat), ("C_total", C_total)]:
        old = p.Get(nm)
        if old:
            old.Delete()       # replace the existing C_total
        h = ROOT.TH2D(nm, nm, n, 0, n, n, 0, n)
        for i in range(n):
            for k in range(n):
                h.SetBinContent(i + 1, k + 1, float(M[i, k]))
        h.Write(nm, ROOT.TObject.kOverwrite)
    p.Close()

    base = xpet
    print("\n===== PET 4D budget (median frac per reported bin) =====")
    for nm, M in [("syst", C["C_syst"]), ("stat", C["C_stat"]), ("ML", C["C_ML"]),
                  ("lateral", C_pet_lat), ("TOTAL", C_total)]:
        st = float(np.sqrt(np.trace(M)))
        med = float(np.median(np.sqrt(np.clip(np.diag(M), 0, None))[base > 0] / base[base > 0]))
        print(f"  {nm:8s} sqrt-trace={st:.4e}  median frac={100*med:.2f}%")
    print(f"\n[lat] updated {args.pet_cov} (+C_lateral, C_total refreshed)")


if __name__ == "__main__":
    main()
