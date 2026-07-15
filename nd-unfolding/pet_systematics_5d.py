#!/usr/bin/env python3
"""PET point-cloud 5D vertical systematic + stat + ML covariance.

5D (pt,pz,Eavail,q3,W) extension of pet_systematics.py for the PET-vs-GBDT 5D
uncertainty campaign. Same frozen-reweighter methodology: the trained PET
reweighter is held FIXED (full-stats push weights w_push); per reweight/vertical
universe only the truth-side prior reweight rho_u changes -- no per-universe
re-inference. Per-event universe weights come from bank_uthrow (dimension-
independent per-event TRUTH ratios; verified bit-identical gen ordering to
of_inputs_pc.npz).

The ONLY differences vs the 4D driver:
  - the truth binning gains a 5th column, W, spliced row-aligned from the GBDT 5D
    inputs npz (of_inputs_5d.npz: MCgen[:,4]); the splice is exact -- the first 4
    columns of MCgen are bit-identical (max|diff|=0) to of_inputs_pc.npz
    truth_scalars on all 32,847,776 finite rows, w_truth diff=0, pass flags equal.
    The 1474 events carrying the W=-9999 sentinel fall below edges_4[0]=0 and are
    dropped by np.histogramdd, exactly as the GBDT 5D denom is built.
  - edges gains edges_4 (W) from of_inputs_5d.npz.
  - the CV completeness is anchored to the 5D GBDT product
    (products/5d/xsec_5d_MEFHC_5iter_lgbm.root : hCompletenessND_flat).

Outputs products/pet/pet_5d_covariance_combined.root (+ console summary). Run on a
compute node (32.85M-row 5D re-binning per universe).
"""
import argparse
import glob
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unfold_2d_omnifold_unbinned as u2d
from xsec_nd import extract_cross_section_nd, total_xsec
from uq_math import guarded_ratio, mat_covariance, require_truth_ratio_bank

KNOB_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2",
              "LowQ2", "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
RHO_CLIP = (1e-2, 1e2)


def _opt(bank, name):
    p = os.path.join(bank, name)
    return np.load(p).astype(np.float64) if os.path.exists(p) else None


class PETxsec5D:
    """Holds the frozen PET inputs and bins a universe's 5D xsec from a truth
    reweight. The W column is spliced row-aligned from the GBDT 5D inputs npz."""

    def __init__(self, pc_npz, weights_npz, mcfile, flux_hist, w_source, comp_ref_root=None):
        pc = np.load(pc_npz)
        truth4 = pc["truth_scalars"].astype(np.float64)            # (N,4) pt,pz,ea,q3
        self.w_truth = pc["w_truth"].astype(np.float64)
        self.pass_truth = pc["pass_truth"].astype(bool)
        self.pass_reco = pc["pass_reco"].astype(bool)
        edges4 = [pc[f"edges_{i}"].astype(float) for i in range(4)]
        self.data_pot = float(pc["data_pot"])

        # ---- splice the W column + edges_4 from the row-aligned GBDT 5D inputs ----
        g5 = np.load(w_source)
        mg = g5["MCgen"].astype(np.float64)
        if mg.shape[0] != truth4.shape[0]:
            raise SystemExit(f"[FAIL] W-source rows {mg.shape[0]} != PET rows {truth4.shape[0]}")
        # Row-alignment gate. The decisive proof is w_truth bit-identical on ALL
        # rows (random misalignment would break it). On the shared 4 coordinate
        # columns we then require EXACT equality wherever both are finite; the only
        # tolerated difference is the known q3 sanitization (PET truth_scalars keeps
        # 1327 NaN q3 rows that the GBDT driver sanitized to finite) -- those are
        # the same events, and we take only the W column (col 4) from this source,
        # so q3 still comes from PET's own truth_scalars (NaN -> dropped by
        # np.histogramdd on the PET path, exactly as in the 4D comparison).
        if np.abs(self.w_truth - g5["w_truth"]).max() != 0.0:
            raise SystemExit("[FAIL] W-source alignment: w_truth not bit-identical")
        a, b = truth4.astype(np.float32), mg[:, :4].astype(np.float32)
        both = np.isfinite(a) & np.isfinite(b)
        mism = int(((a != b) & both).sum())
        if mism:
            raise SystemExit(f"[FAIL] W-source alignment: {mism} finite-row coord mismatches")
        nanx = int((np.isnan(a) ^ np.isnan(b)).sum())
        if nanx > truth4.shape[0] // 1000:
            raise SystemExit(f"[FAIL] W-source alignment: {nanx} NaN-pattern rows exceed 0.1%")
        print(f"[pet5d] W-source alignment OK (w_truth bit-identical, finite coords exact; "
              f"{nanx} tolerated q3-sanitization NaN rows)")
        W = mg[:, 4]
        self.truth = np.column_stack([truth4, W])                  # (N,5) pt,pz,ea,q3,W
        self.edges = edges4 + [g5["edges_4"].astype(float)]
        self.shape = tuple(len(e) - 1 for e in self.edges)
        print(f"[pet5d] spliced W (sentinel<=0: {(W <= 0).sum()}) edges_4={self.edges[4]}")

        w = np.load(weights_npz)
        wp = w["w_push"].astype(np.float64)
        bf = (w["mc_bootstrap_factor"].astype(np.float64)
              if "mc_bootstrap_factor" in w.files else np.ones(wp.shape[0], dtype=float))
        if "mc_indices" in w.files:
            idx = w["mc_indices"]
            full = np.zeros(self.truth.shape[0], float)
            full[idx] = wp
            wp = full
            full_bf = np.ones(self.truth.shape[0], float)
            full_bf[idx] = bf
            bf = full_bf
        if wp.shape[0] != self.truth.shape[0] or bf.shape[0] != self.truth.shape[0]:
            raise ValueError(f"PET weight/bootstrap rows do not match truth rows: "
                             f"{wp.shape[0]}/{bf.shape[0]} vs {self.truth.shape[0]}")
        self.w_push = wp
        self.mc_bootstrap_factor = bf
        # flux on the pt axis (axis 0); n_nucleons -- same loaders as the GBDT path.
        # self.edges[0] may be an FPS-extended pT grid (more/different bins than the
        # frozen flux histogram) -- remap by bin-centre lookup into the standard-edge
        # flux (flux is pT-flat to ~2e-14%, so this is exact); identity when edges[0]
        # already IS the standard grid, same pattern as nn_dump_inputs.py.
        flux_ref, _ = u2d.load_flux_bins(mcfile, flux_hist, u2d.PT_EDGES)
        ref_e = np.asarray(u2d.PT_EDGES, float)
        pt_e0 = np.asarray(self.edges[0], float)
        ctrs = 0.5 * (pt_e0[:-1] + pt_e0[1:])
        ref_i = np.clip(np.digitize(ctrs, ref_e) - 1, 0, len(flux_ref) - 1)
        self.flux = flux_ref[ref_i]
        self.n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
        self.pt = self.pass_truth
        self.ptr = self.pass_truth & self.pass_reco
        # Anchor the absolute completeness to the validated GBDT 5D product (a FIXED
        # per-bin rescale -> invariant for the fractional covariance, but makes the
        # CV match the milestone).
        self.comp_rescale = np.ones(self.shape)
        # Fixed nominal detector anchor; replica fluctuations remain in _comp(wt).
        comp_pc_cv = self._comp(self.w_truth)
        if comp_ref_root and os.path.exists(comp_ref_root):
            import ROOT
            f = ROOT.TFile.Open(comp_ref_root)
            h = f.Get("hCompletenessND_flat")
            ref = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())]).reshape(self.shape, order="C")
            f.Close()
            good = (comp_pc_cv > 0) & (ref > 0)
            self.comp_rescale[good] = ref[good] / comp_pc_cv[good]
            print(f"[pet5d] anchored completeness to {os.path.basename(comp_ref_root)} "
                  f"(median rescale {np.median(self.comp_rescale[good]):.3f})")
        print(f"[pet5d] N={self.truth.shape[0]} pass_truth={self.pt.sum()} "
              f"pass_truth&reco={self.ptr.sum()} edges={list(self.shape)}")

    def _comp(self, wt):
        denom, _ = np.histogramdd(self.truth[self.pt], bins=self.edges, weights=wt[self.pt])
        ofin, _ = np.histogramdd(self.truth[self.ptr], bins=self.edges, weights=wt[self.ptr])
        comp = np.zeros_like(denom)
        nz = denom > 0
        comp[nz] = ofin[nz] / denom[nz]
        return comp

    def xsec(self, rho=None):
        """xsec for a per-event truth reweight rho (None = CV); completeness anchored."""
        wt = self.w_truth * self.mc_bootstrap_factor
        if rho is not None:
            wt = wt * rho
        counts, _ = np.histogramdd(self.truth[self.pt], bins=self.edges,
                                   weights=self.w_push[self.pt] * wt[self.pt])
        comp = self._comp(wt) * self.comp_rescale
        xs, _ = extract_cross_section_nd(counts, comp, self.flux, self.data_pot,
                                         self.n_nucleons, self.edges)
        return xs.ravel(order="C")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pc", default="of_inputs_pc.npz")
    ap.add_argument("--w-source", default="of_inputs_5d.npz",
                    help="GBDT 5D inputs npz providing the row-aligned W column + edges_4")
    ap.add_argument("--weights", default="products/pet/pet_weights_full.npz")
    ap.add_argument("--weights-alt", default="products/pet/pet_weights_full_hi.npz",
                    help="2nd PET training for the ML band")
    ap.add_argument("--bank", default="bank_uthrow")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--comp-ref", default="products/5d/xsec_5d_MEFHC_5iter_lgbm.root",
                    help="GBDT 5D product with hCompletenessND_flat to anchor the CV scale")
    ap.add_argument("--stat-replicas", required=True,
                    help="glob of measured-data-fluctuated, fully retrained PET xsec npz replicas")
    ap.add_argument("--stat-expected-ids", default="1-100")
    ap.add_argument("--invalid-ratio", choices=("error", "neutral"), default="error",
                    help="invalid bank-ratio policy; neutral is explicit and logged")
    ap.add_argument("--out-root", default="products/pet/pet_5d_covariance_combined.root")
    args = ap.parse_args()

    pet = PETxsec5D(args.pc, args.weights, args.mcfile, args.flux_hist, args.w_source, args.comp_ref)
    x_cv = pet.xsec(None)
    rep = x_cv > 0
    base = x_cv[rep]
    nrep = int(rep.sum())
    print(f"[pet5d] CV total sigma={total_xsec(x_cv.reshape(pet.shape, order='C'), pet.edges):.4e}; "
          f"reported bins={nrep}")

    # ---- C_syst: per-band mean-centered covariance (MAT 1/N), matching
    #      unified_throw_cov / analyze_universes. Knob bands use BOTH +/-1sigma
    #      endpoints (not one-sided vs CV); flux uses all PPFX universes. ----
    flux_ids = require_truth_ratio_bank(args.bank, KNOB_BANDS, expected_flux=100)
    ratio = lambda value, label: guarded_ratio(
        value, label, invalid_policy=args.invalid_ratio, clip=RHO_CLIP)
    C_syst = np.zeros((nrep, nrep))
    for b in KNOB_BANDS:
        sig_m = _opt(args.bank, f"sig_{b}_t_0.npy")
        sig_p = _opt(args.bank, f"sig_{b}_t_1.npy")
        x_m = pet.xsec(ratio(sig_m, f"{b}:-1"))[rep]
        x_p = pet.xsec(ratio(sig_p, f"{b}:+1"))[rep]
        cb = mat_covariance(np.stack([x_m, x_p]))
        C_syst += cb
        print(f"[syst] {b}: sqrt-tr={np.sqrt(np.trace(cb)):.3e} (mean-centered +/-)", flush=True)
    # flux universes: mean-centered covariance over all PPFX universes
    fX = [pet.xsec(ratio(_opt(args.bank, f"sig_flux_t_{u}.npy"), f"Flux:{u}"))[rep]
          for u in flux_ids]
    C_flux = mat_covariance(np.asarray(fX))
    C_syst += C_flux
    print(f"[syst] flux ({len(flux_ids)}): sqrt-tr={np.sqrt(np.trace(C_flux)):.3e} "
          "(mean-centered)")

    from replica_manifest import load_replica_manifest
    lo, hi = (int(v) for v in args.stat_expected_ids.split("-", 1))
    SX, stat_ids = load_replica_manifest(sorted(glob.glob(args.stat_replicas)),
                                         set(range(lo, hi + 1)))
    if SX.shape[1] != x_cv.size:
        raise SystemExit(f"[FAIL] PET stat replica bins {SX.shape[1]} != CV {x_cv.size}")
    C_stat = np.cov(SX[:, rep], rowvar=False, ddof=1)
    print(f"[stat] {SX.shape[0]} measured-data+retrained replicas: "
          f"sqrt-tr={np.sqrt(np.trace(C_stat)):.3e}")

    # ---- C_ML: spread between available PET trainings ----
    C_ML = np.zeros((nrep, nrep))
    if args.weights_alt and os.path.exists(args.weights_alt):
        pet2 = PETxsec5D(args.pc, args.weights_alt, args.mcfile, args.flux_hist, args.w_source, args.comp_ref)
        d_ml = pet2.xsec(None)[rep] - base
        C_ML = np.outer(d_ml, d_ml)
        print(f"[ml] CV-vs-alt training: ||delta||={np.linalg.norm(d_ml):.3e}")

    C_total = C_syst + C_stat + C_ML
    for nm, C in [("syst", C_syst), ("stat", C_stat), ("ML", C_ML), ("total", C_total)]:
        st = float(np.sqrt(np.trace(C)))
        med = float(np.median(np.sqrt(np.clip(np.diag(C), 0, None))[base > 0] / base[base > 0]))
        print(f"[cov] {nm}: sqrt-trace={st:.4e}  median frac={100*med:.1f}%")

    os.makedirs(os.path.dirname(args.out_root) or ".", exist_ok=True)
    import ROOT
    fo = ROOT.TFile.Open(args.out_root, "RECREATE")
    for nm, C in [("C_syst", C_syst), ("C_stat", C_stat), ("C_ML", C_ML), ("C_total", C_total)]:
        h = ROOT.TH2D(nm, nm, nrep, 0, nrep, nrep, 0, nrep)
        for i in range(nrep):
            for k in range(nrep):
                h.SetBinContent(i + 1, k + 1, float(C[i, k]))
        h.Write()
    hcv = ROOT.TH1D("hXSec_cv_flat", "PET CV xsec (reported bins)", nrep, 0, nrep)
    for i in range(nrep):
        hcv.SetBinContent(i + 1, float(base[i]))
    hcv.Write()
    ROOT.TParameter("int")("n_reported", nrep).Write()
    fo.Close()
    print(f"[pet5d] wrote {args.out_root}")


if __name__ == "__main__":
    main()
