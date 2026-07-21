#!/usr/bin/env python3
"""PET-native per-lateral band via the event-aligned 5D join (KNOWN_ISSUES #3).

Replaces the engine-transferred GBDT lateral block in the PET 4D combined
covariance (pet_lateral_correction.py) with a PET-native one. Key facts that make
this cheap (verified 2026-06-10):
  - `PC_MEFHC.root` and `runEventLoopOmniFold_5D_MEFHC_universes_full.root` are
    exactly event-aligned (identical entry counts on all four trees), and the PC
    npz dump kept every mc_signal_reco entry, so npz rows == 5D tree rows. This
    script ASSERTS full-row alignment (CV truth scalars + weights) before using
    any universe branch.
  - The muon/beam lateral universes leave the recoil-cluster point clouds
    invariant (they touch only muon getters -- the Gap 1 finding), so the trained
    PET push weights w_push are reused FROZEN. What shifts per universe is joined
    from the 5D file: truth binning coordinates (MC/MC_pz/MC_q3_<band>_<idx>;
    eavail is lateral-invariant), the reco gate (sim/sim_pz_<band>_<idx>), and
    the universe weights (w_truth_<band>_<idx>).
  - GEANT_* and MinosEfficiency are weight-only bands: CV coordinates/gates,
    universe weights swapped.

Documented approximation: w_push is not re-trained per universe. Since PET's reco
features are the (invariant) clouds, re-training would differ only through the
training-set composition at the acceptance boundary and the weight swap --
second-order next to the coordinate/gate/weight shifts carried here. The GBDT
campaign DID re-train per lateral universe; comparing this band against the
GBDT-transferred one (printed at the end) is therefore also a check of the
engine-independence assumption used previously.

MISS-ROW HANDLING (KNOWN_ISSUES #12, discovered by this script's first run):
the 12.35M appended truth-only miss rows (37.6% of mc_signal_reco) carry
UNINITIALIZED GARBAGE in every per-universe branch (AppendTruthOnlyMisses never
rebinds them; dangling addresses). Miss rows are therefore pinned to their CV
coordinates and CV weights in every universe here. This is EXACT for 7 of the 9
detector bands (MuonResolution / Muon_Energy_* / MinosEfficiency / GEANT_* leave
truth untouched) and neglects only the ~1 mrad BeamAngleX/Y truth-frame rotation
of miss coordinates (<~10 MeV, far below bin widths). The detector-response
variation of the weight-only bands lives in w_reco, which enters the
completeness numerator as the per-event ratio rho_r = w_reco_<sfx>/w_reco on
reco-passing rows (whose universe branches ARE valid).

Per universe u:  x_u = PETxsec-style xsec with (coords_u, gates_u, w_truth_u)
Band covariance: C_b = (1/N) Z^T Z on de-meaned deviations vs the PET CV
                 (analyze_universes_nd.py convention), summed over the 9 bands.
Output: products/pet/pet_4d_covariance_combined_wlat.root (old file untouched).

  python pet_lateral_band.py   # compute node, ~64G, reads 5D file column-wise
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unfold_2d_omnifold_unbinned as u2d
from xsec_nd import extract_cross_section_nd
from pet_systematics import PETxsec

KINE_BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
              "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
WEIGHT_BANDS = ["MinosEfficiency", "GEANT_Neutron", "GEANT_Pion", "GEANT_Proton"]
NUNIV = 2  # +-1 sigma universes per band


def _np(d, k):
    return np.asarray(d[k], dtype=np.float64)


def main():
    import ROOT

    ap = argparse.ArgumentParser()
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--weights", default="products/pet/pet_weights_full.npz")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_MEFHC_universes_full.root")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default="products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--combined", default="products/pet/pet_4d_covariance_combined.root")
    ap.add_argument("--out-root", default="products/pet/pet_4d_covariance_combined_wlat.root")
    args = ap.parse_args()

    pet = PETxsec(args.pc, args.weights, args.mcfile, args.flux_hist, args.comp_ref)
    x_cv = pet.xsec(None)
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    from xsec_nd import total_xsec
    print(f"[wlat] PET CV total={total_xsec(x_cv.reshape(pet.shape, order='C'), pet.edges):.4e} "
          f"reported bins={nrep}")

    pt_lo, pt_hi = pet.edges[0][0], pet.edges[0][-1]
    pz_lo, pz_hi = pet.edges[1][0], pet.edges[1][-1]
    max_th = u2d.MAX_MUON_THETA_RAD

    f = ROOT.TFile.Open(args.omnifile, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.omnifile}")
    _, _, pot_scale = u2d.get_pot_scales(f)
    t = f.Get("mc_signal_reco")
    n_tree = t.GetEntries()
    if n_tree != pet.truth.shape[0]:
        raise SystemExit(f"[FAIL] tree entries {n_tree} != npz rows {pet.truth.shape[0]}")

    def cols(branches):
        return ROOT.RDataFrame(t).AsNumpy(list(branches))

    # ---------- FULL-ROW alignment assertion (the Step-A verification) ----------
    cv = cols(["MC", "MC_pz", "MC_eavail", "MC_q3", "sim", "sim_pz", "sim_pass",
               "w_truth", "w_reco"])
    mc_pt, mc_pz = _np(cv, "MC"), _np(cv, "MC_pz")
    sim_pt, sim_pz = _np(cv, "sim"), _np(cv, "sim_pz")
    sim_pass = np.asarray(cv["sim_pass"]).astype(bool)
    wr_cv_raw = _np(cv, "w_reco")
    # appended truth-only miss rows: universe branches are garbage there (#12)
    miss = sim_pt == -9999.0
    print(f"[wlat] miss rows: {miss.sum()} ({100*miss.mean():.1f}%) -- pinned to CV "
          f"in every universe (see docstring)")
    for j, k in enumerate(["MC", "MC_pz", "MC_eavail", "MC_q3"]):
        v = _np(cv, k).astype(np.float32)
        w = pet.truth[:, j].astype(np.float32)
        # NaN==NaN counts as a match (q3 has 1327 NaN truth rows; np.histogramdd
        # drops them on both paths, so aligned NaNs are equivalent)
        bad = int((~((v == w) | (np.isnan(v) & np.isnan(w)))).sum())
        if bad:
            raise SystemExit(f"[FAIL] alignment: column {k} mismatches in {bad} rows")
    wt_cv = _np(cv, "w_truth") * pot_scale
    if not np.allclose(wt_cv, pet.w_truth, rtol=1e-6, atol=0):
        raise SystemExit("[FAIL] alignment: w_truth mismatch")
    print(f"[wlat] ALIGNMENT VERIFIED: all {n_tree} rows, 4 truth columns + w_truth exact")

    cv_eavail = pet.truth[:, 2].astype(np.float64)
    cv_q3 = pet.truth[:, 3].astype(np.float64)

    def truth_gate(pt_, pz_):
        fin = np.isfinite(pt_) & np.isfinite(pz_)
        th = np.arctan2(np.abs(pt_), pz_)
        return fin & (pt_ >= pt_lo) & (pt_ <= pt_hi) & (pz_ >= pz_lo) & (pz_ <= pz_hi) & (th < max_th)

    def reco_gate(spt, spz):
        fin = np.isfinite(spt) & np.isfinite(spz)
        return sim_pass & fin & (spt >= pt_lo) & (spt <= pt_hi) & (spz >= pz_lo) & (spz <= pz_hi)

    def xsec_uni(coords, pt_mask, ptr_mask, wt, rho_r=None):
        """rho_r: per-event reco-weight ratio (w_reco_u/w_reco) carried by the
        completeness numerator only -- the detector-response variation of the
        weight-only bands, and the reco-weight shift of the kinematic bands."""
        counts, _ = np.histogramdd(coords[pt_mask], bins=pet.edges,
                                   weights=pet.w_push[pt_mask] * wt[pt_mask])
        denom, _ = np.histogramdd(coords[pt_mask], bins=pet.edges, weights=wt[pt_mask])
        w_of = wt if rho_r is None else wt * rho_r
        ofin, _ = np.histogramdd(coords[ptr_mask], bins=pet.edges, weights=w_of[ptr_mask])
        comp = np.zeros_like(denom)
        nz = denom > 0
        comp[nz] = ofin[nz] / denom[nz]
        comp *= pet.comp_rescale
        xs, _ = extract_cross_section_nd(counts, comp, pet.flux, pet.data_pot,
                                         pet.n_nucleons, pet.edges)
        return xs.ravel(order="C")

    def reco_rho(sfx):
        """Guarded w_reco_<sfx>/w_reco; misses never enter ofin (sim_pass false)."""
        wru = _np(cols([f"w_reco_{sfx}"]), f"w_reco_{sfx}")
        ok = (np.isfinite(wru) & (wru >= 0) & (wru < 1e4)
              & np.isfinite(wr_cv_raw) & (wr_cv_raw > 0) & ~miss)
        return np.where(ok, np.divide(wru, wr_cv_raw, out=np.ones_like(wru),
                                      where=wr_cv_raw > 0), 1.0)

    # sanity: CV through the universe path must reproduce the PETxsec CV
    cv_check = xsec_uni(pet.truth.astype(np.float64), pet.pt,
                        pet.pt & reco_gate(sim_pt, sim_pz), wt_cv)
    dmax = np.max(np.abs(cv_check[rep] / base - 1))
    print(f"[wlat] CV-path consistency: max|ratio-1|={dmax:.2e}"
          + ("" if dmax < 5e-3 else "  [WARN] paths disagree"))

    band_cov, C_lat = {}, np.zeros((nrep, nrep))
    for band in KINE_BANDS + WEIGHT_BANDS:
        devs = []
        for idx in range(NUNIV):
            sfx = f"{band}_{idx}"
            wraw = _np(cols([f"w_truth_{sfx}"]), f"w_truth_{sfx}")
            # same per-event weight guard as the driver's collectors (pre-POT-scale)
            wraw = np.where(np.isfinite(wraw) & (wraw >= 0) & (wraw < 1e4), wraw, 0.0)
            # miss rows: universe branches are garbage (#12) -> pin to CV
            wt_u = np.where(miss, wt_cv, wraw * pot_scale)
            rho_r = reco_rho(sfx)
            if band in KINE_BANDS:
                u = cols([f"MC_{sfx}", f"MC_pz_{sfx}", f"MC_q3_{sfx}",
                          f"sim_{sfx}", f"sim_pz_{sfx}"])
                tpt = np.where(miss, mc_pt, _np(u, f"MC_{sfx}"))
                tpz = np.where(miss, mc_pz, _np(u, f"MC_pz_{sfx}"))
                tq3 = np.where(miss, cv_q3, _np(u, f"MC_q3_{sfx}"))
                coords = np.column_stack([tpt, tpz, cv_eavail, tq3])
                pt_m = truth_gate(tpt, tpz)
                # misses have sim_pass False -> garbage sim_<sfx> never enters
                ptr_m = pt_m & reco_gate(_np(u, f"sim_{sfx}"), _np(u, f"sim_pz_{sfx}"))
            else:
                coords = pet.truth.astype(np.float64)
                pt_m = pet.pt
                ptr_m = pt_m & reco_gate(sim_pt, sim_pz)
            x_u = xsec_uni(coords, pt_m, ptr_m, wt_u, rho_r)
            devs.append(x_u[rep] - base)
            print(f"[wlat] {sfx:26s} pass_truth={pt_m.sum()} ||d||={np.linalg.norm(devs[-1]):.3e}",
                  flush=True)
        D = np.stack(devs)
        Z = D - D.mean(axis=0, keepdims=True)
        cb = (Z.T @ Z) / D.shape[0]
        band_cov[band] = cb
        C_lat += cb
        print(f"[wlat] {band:22s} sqrt-tr={np.sqrt(max(np.trace(cb), 0)):.3e}")
    f.Close()

    # ---------- compare with the transferred block + rebuild the combined file ----------
    fc = ROOT.TFile.Open(args.combined, "READ")

    def _th2(h):
        nn = h.GetNbinsX()
        a = np.empty((nn, nn))
        for i in range(nn):
            for k in range(nn):
                a[i, k] = h.GetBinContent(i + 1, k + 1)
        return a

    blocks = {k.GetName(): _th2(fc.Get(k.GetName()))
              for k in fc.GetListOfKeys() if k.GetName().startswith("C_")}
    fc.Close()
    C_old_lat = blocks["C_lateral"]
    s_old = np.sqrt(np.clip(np.diag(C_old_lat), 0, None))
    s_new = np.sqrt(np.clip(np.diag(C_lat), 0, None))
    print(f"\n[wlat] lateral band OLD (GBDT transfer) median frac="
          f"{100*np.median(s_old[base > 0]/base[base > 0]):.2f}%  "
          f"NEW (PET-native) median frac={100*np.median(s_new[base > 0]/base[base > 0]):.2f}%")
    print(f"[wlat] sqrt-tr old={np.sqrt(np.trace(C_old_lat)):.3e} new={np.sqrt(np.trace(C_lat)):.3e}")

    C_total = blocks["C_syst"] + blocks["C_stat"] + blocks["C_ML"] + C_lat
    for nm, C in [("syst", blocks["C_syst"]), ("stat", blocks["C_stat"]),
                  ("ML", blocks["C_ML"]), ("lateral(PET-native)", C_lat), ("total", C_total)]:
        med = float(np.median(np.sqrt(np.clip(np.diag(C), 0, None))[base > 0] / base[base > 0]))
        print(f"[cov] {nm}: sqrt-trace={np.sqrt(max(np.trace(C),0)):.4e}  median frac={100*med:.1f}%")

    os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
    fo = ROOT.TFile.Open(args.out_root, "RECREATE")
    out_blocks = [("C_syst", blocks["C_syst"]), ("C_stat", blocks["C_stat"]),
                  ("C_ML", blocks["C_ML"]), ("C_lateral", C_lat), ("C_total", C_total)]
    for nm, C in out_blocks:
        h = ROOT.TH2D(nm, nm, nrep, 0, nrep, nrep, 0, nrep)
        for i in range(nrep):
            for k in range(nrep):
                h.SetBinContent(i + 1, k + 1, float(C[i, k]))
        h.Write()
    for band, cb in band_cov.items():
        h = ROOT.TH2D(f"C_lateral_{band}", f"C_lateral_{band}", nrep, 0, nrep, nrep, 0, nrep)
        for i in range(nrep):
            for k in range(nrep):
                h.SetBinContent(i + 1, k + 1, float(cb[i, k]))
        h.Write()
    hcv = ROOT.TH1D("hXSec_cv_flat", "PET CV xsec (reported bins)", nrep, 0, nrep)
    for i in range(nrep):
        hcv.SetBinContent(i + 1, float(base[i]))
    hcv.Write()
    ROOT.TParameter("int")("n_reported", nrep).Write()
    fo.Close()
    print(f"[wlat] wrote {args.out_root}")


if __name__ == "__main__":
    main()
