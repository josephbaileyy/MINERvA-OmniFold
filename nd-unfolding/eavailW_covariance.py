#!/usr/bin/env python3
"""(E_avail, W) systematic+stat covariance and per-generator significance (task 13).

The (E_avail,W) generator BAND established that unfolded data sits above every generator in
the high-W DIS corner (open question 6). This turns the band into a NUMBER -- a chi^2 / N-sigma
per generator on d^2 sigma/(dE_avail dW) -- via a frozen-reweighter block-sum covariance built
from the 5D _universes_full omnifile (the SAME methodology as pet_systematics.py: the CV OmniFold
push weights step2_w are held FIXED and only the per-event TRUTH reweight ratios change, re-binning
each systematic universe -- no per-universe re-inference / no 187-universe sweep).

  C_syst = sum_b outer(y_b - y_cv) [13 +-1sig knob bands] + (1/Nflux) sum_u outer(y_u - y_cv)
  y_*    = project_(eavail,W)[ extract_xsec( bin5D(truth-pass, step2_w * w_truth * rho), comp_* ) ]
  C_stat = diag(marginalized CV unfold Poisson variance)
  C_lat  = transferred 4D detector (lateral) bands, marginalized to E_avail, spread over W by the
           CV (E_avail,W) shape -- documented approximation (W-resolved laterals need reco
           re-inference, deferred; laterals are subdominant ~4%).
  chi^2_g = (y_data - y_g)^T C_total^-1 (y_data - y_g);  also the high-W DIS corner sub-block.

Validates against the frozen 5D product (E_avail and W marginals must match) before trusting the
covariance. Run on a compute node (sbatch) after the 5D universes_full merge.

  python eavailW_covariance.py --omnifile runEventLoopOmniFold_5D_MEFHC_universes_full.root
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding", f"{_REPO}/unbinned_unfolding/python"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

VERT_BANDS = ["2p2h", "CCQEPauliSupViaKF", "FrAbs_pi", "FrElas_N", "HighQ2", "LowQ2",
              "MaCCQE", "MaRES", "MFP_N", "MvRES", "Rvn2pi", "Rvp2pi"]
# detector (lateral) bands carried in the 4D combined cov -> transferred to (E_avail,W)
LATERAL_BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution", "Muon_Energy_MINERvA",
                 "Muon_Energy_MINOS", "MinosEfficiency", "GEANT_Neutron", "GEANT_Pion",
                 "GEANT_Proton"]


def _th1(h):
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def _th2(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    b = np.frombuffer(h.GetArray(), dtype=np.float64, count=(nx + 2) * (ny + 2)).reshape(ny + 2, nx + 2)
    return b[1:ny + 1, 1:nx + 1].T.copy()


def main():
    import ROOT
    from scipy import stats
    import unfold_nd_omnifold_unbinned as und
    import unfold_2d_omnifold_unbinned as u2d
    from xsec_nd import extract_cross_section_nd
    from omnifold import OmniFold_helper_functions as ohf

    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_MEFHC_universes_full.root")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--prod5d", default="products/5d/xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--cov4d", default="uq_4d/universe_stage2_4d/uq_universe_4d_covariance_combined.root")
    ap.add_argument("--gendir", default="../3d-unfolding/genie")
    ap.add_argument("--gens", default="GENIE-CV:genie_cv_xsec_eavailW.root,"
                    "GENIE+MEC:genie_mec_xsec_eavailW.root,"
                    "NuWro:nuwro_cv_xsec_eavailW.root,GiBUU:gibuu_cv_xsec_eavailW.root")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--nflux", type=int, default=100)
    ap.add_argument("--lateral-sweep-cv", default=None,
                    help="matched-CV 5D unfold ROOT from the detector-band sweep "
                         "(sbatch_unfold_5d_detector.sh task 0); enables the "
                         "W-resolved lateral block in place of the 4D transfer")
    ap.add_argument("--lateral-sweep-glob", default=None,
                    help="glob of per-universe 5D unfold ROOTs "
                         "(5d_xsec_*_uni_full_<band>_<idx>.root)")
    ap.add_argument("--out", default="products/5d/eavailW_covariance.root")
    args = ap.parse_args()
    if (args.lateral_sweep_cv is None) != (args.lateral_sweep_glob is None):
        ap.error("--lateral-sweep-cv and --lateral-sweep-glob must be given together")

    # --- binning (pt,pz,eavail,q3,W) ---
    pt_e = np.asarray(u2d.PT_EDGES, float); pz_e = np.asarray(u2d.PZ_EDGES, float)
    ea_e = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    q3_e = np.asarray(und.EXTRA_AXES["q3"]["edges"], float)
    w_e = np.asarray(und.EXTRA_AXES["W"]["edges"], float)
    edges = [pt_e, pz_e, ea_e, q3_e, w_e]
    n_ea, n_w = len(ea_e) - 1, len(w_e) - 1
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]
    dpt, dpz, dq3 = np.diff(pt_e), np.diff(pz_e), np.diff(q3_e)
    dea, dw = np.diff(ea_e), np.diff(w_e)

    f = ROOT.TFile.Open(args.omnifile, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.omnifile}")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS
    print(f"[ew] pot_scale={pot_scale:.6g} data_pot={data_pot:.4g} n_nucl={n_nucleons:.4g}", flush=True)

    flux_t = [f"w_truth_Flux_{u}" for u in range(args.nflux)]
    flux_r = [f"w_reco_Flux_{u}" for u in range(args.nflux)]
    vt = [f"w_truth_{b}_1" for b in VERT_BANDS]
    vr = [f"w_reco_{b}_1" for b in VERT_BANDS]

    # ---------- bulk-read signal (gate replicates collect_signal_nd) ----------
    sb = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "sim", "sim_pz",
          "sim_eavail", "sim_q3", "sim_W", "sim_pass", "w_truth", "w_reco"] + vt + vr + flux_t + flux_r
    S = ROOT.RDataFrame("mc_signal_reco", f).AsNumpy(sb)
    g = lambda k: np.asarray(S[k], float)
    mcpt, mcpz = g("MC"), g("MC_pz")
    simpt, simpz = g("sim"), g("sim_pz")
    wt, wr = g("w_truth"), g("w_reco")
    sim_pass = np.asarray(S["sim_pass"]).astype(bool)
    wgood = np.isfinite(wt) & np.isfinite(wr) & (wt >= 0) & (wt < 1e4) & (wr >= 0) & (wr < 1e4)
    th = np.arctan2(mcpt, mcpz)
    tru_ok = (mcpt >= pt_lo) & (mcpt <= pt_hi) & (mcpz >= pz_lo) & (mcpz <= pz_hi) & (th < u2d.MAX_MUON_THETA_RAD)
    rec_ok = np.isfinite(simpt) & np.isfinite(simpz) & (simpt >= pt_lo) & (simpt <= pt_hi) \
        & (simpz >= pz_lo) & (simpz <= pz_hi)
    passrec = sim_pass & rec_ok
    keep = wgood & (tru_ok | passrec)
    k = keep
    NEG = -9999.0
    truth_pt = np.where(np.isfinite(mcpt[k]), mcpt[k], NEG)
    truth_pz = np.where(np.isfinite(mcpz[k]), mcpz[k], NEG)
    reco_pt = np.where(passrec[k], simpt[k], NEG)
    reco_pz = np.where(passrec[k], simpz[k], NEG)

    def tex(name):
        v = g(name)[k]; return np.where(np.isfinite(v), v, NEG)

    def rex(name):
        v = g(name)[k]; return np.where(passrec[k] & np.isfinite(v), v, NEG)
    t_ea, t_q3, t_w = tex("MC_eavail"), tex("MC_q3"), tex("MC_W")
    r_ea, r_q3, r_w = rex("sim_eavail"), rex("sim_q3"), rex("sim_W")
    w_truth = wt[k] * pot_scale
    w_reco = wr[k] * pot_scale
    pass_truth = tru_ok[k]
    pass_reco = passrec[k]
    # per-band absolute universe weights (truth side, POT-scaled), aligned to kept signal events
    sig_vt = {b: g(f"w_truth_{b}_1")[k] * pot_scale for b in VERT_BANDS}
    sig_ft = [g(c)[k] * pot_scale for c in flux_t]
    print(f"[ew] signal kept={k.sum()} pass_truth={pass_truth.sum()} pass_reco={pass_reco.sum()}", flush=True)

    # ---------- bulk-read truth_denom (gate replicates collect_truth_denom_nd) ----------
    db = ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth"] + vt + flux_t
    D = ROOT.RDataFrame("mc_truth_denom", f).AsNumpy(db)
    gd = lambda key: np.asarray(D[key], float)
    dpt_, dpz_ = gd("MC"), gd("MC_pz")
    dwt = gd("w_truth")
    dea_ = gd("MC_eavail"); dq3_ = gd("MC_q3"); dw_ = gd("MC_W")
    dfin = np.isfinite(dpt_) & np.isfinite(dpz_) & np.isfinite(dwt) & np.isfinite(dea_) \
        & np.isfinite(dq3_) & np.isfinite(dw_)
    dth = np.arctan2(dpt_, dpz_)
    dkeep = dfin & (dwt >= 0) & (dwt < 1e4) & (dpt_ >= pt_lo) & (dpt_ <= pt_hi) \
        & (dpz_ >= pz_lo) & (dpz_ <= pz_hi) & (dth < u2d.MAX_MUON_THETA_RAD)
    dk = dkeep
    td_cols = [dpt_[dk], dpz_[dk], dea_[dk], dq3_[dk], dw_[dk]]
    td_w = dwt[dk] * pot_scale
    td_vt = {b: gd(f"w_truth_{b}_1")[dk] * pot_scale for b in VERT_BANDS}
    td_ft = [gd(c)[dk] * pot_scale for c in flux_t]
    print(f"[ew] truth_denom kept={dk.sum()}", flush=True)

    # ---------- data + bkg (small trees: per-event collectors) ----------
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in ("eavail", "q3", "W")]
    t_data = f.Get("data"); t_bkg = f.Get("mc_background")
    meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(t_bkg, extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi)
    f.Close()

    data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
    bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
    measured_weights = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)

    # ---------- CV OmniFold (frozen push weights) ----------
    MCgen = np.column_stack([truth_pt, truth_pz, t_ea, t_q3, t_w])
    MCreco = np.column_stack([reco_pt, reco_pz, r_ea, r_q3, r_w])
    measured = np.column_stack([meas_pt, meas_pz] + meas_ex)
    print(f"[ew] OmniFold {args.iters} iters ndim={MCgen.shape[1]}", flush=True)
    _, step2_w = ohf.omnifold(
        MCgen, MCreco, measured, pass_reco, pass_truth, np.ones(meas_pt.size, dtype=bool),
        int(args.iters), MCgen_weights=w_truth, MCreco_weights=w_reco,
        measured_weights=measured_weights,
        classifier1_params={"random_state": args.seed}, classifier2_params={"random_state": args.seed + 1},
        regressor_params={"random_state": args.seed + 2}, parameter_format="dict",
        estimator="lgbm", device="cpu")
    print(f"[ew] step2 mean={step2_w.mean():.4f}", flush=True)

    # ---------- (E_avail,W) cross section for a per-event truth reweight ----------
    m = pass_truth
    tcols = [truth_pt[m], truth_pz[m], t_ea[m], t_q3[m], t_w[m]]
    tw_m = w_truth[m]; push = step2_w * tw_m            # frozen numerator weight (CV)
    # completeness numerator = ALL truth-pass signal events (NOT reco-restricted): OmniFold
    # step2 already performs the efficiency correction in truth space, so the completeness is
    # signal/truth_denom (~1, phase-space match), matching the N-D driver (lines 642-647).

    def marginal_ew(xsec5d):
        # integrate out pt,pz,q3 -> d^2 sigma/(dEavail dW); weight = dpt dpz dq3
        wcell = (dpt[:, None, None, None, None] * dpz[None, :, None, None, None]
                 * dq3[None, None, None, :, None])
        return (xsec5d * wcell).sum(axis=(0, 1, 3))     # -> (n_ea, n_w)

    RHO_CLIP = (1e-2, 1e2)     # per-event ratio guard (positivity / tail), as in unified_throw_cov

    def xsec_ew(rho_sig=None, rho_td=None):
        if rho_sig is not None:
            rho_sig = np.clip(rho_sig, *RHO_CLIP)
        if rho_td is not None:
            rho_td = np.clip(rho_td, *RHO_CLIP)
        wn = push if rho_sig is None else push * rho_sig[m]
        wo = tw_m if rho_sig is None else tw_m * rho_sig[m]
        unfold_nd, unfold_err = und.histnd(tcols, wn, edges)
        of_in, _ = und.histnd(tcols, wo, edges)         # full truth-pass numerator (driver-conformant)
        dw_u = td_w if rho_td is None else td_w * rho_td
        denom_nd, _ = und.histnd(td_cols, dw_u, edges)
        comp = np.zeros_like(of_in); nz = denom_nd > 0
        comp[nz] = of_in[nz] / denom_nd[nz]
        xs, _ = extract_cross_section_nd(unfold_nd, comp, np.asarray(flux_bins, float),
                                         data_pot, n_nucleons, edges)
        return marginal_ew(xs), marginal_ew(np.where(unfold_nd > 0, unfold_err / np.maximum(unfold_nd, 1e-300), 0) * xs)

    y_cv, yerr_cv = xsec_ew()
    y_cv = y_cv.ravel(); n = y_cv.size
    print(f"[ew] CV (E_avail,W): {n} bins, total int={ (y_cv*np.outer(dea,dw).ravel()).sum():.3e}", flush=True)

    # ---------- validation vs frozen 5D product (E_avail and W marginals) ----------
    fp = ROOT.TFile.Open(args.prod5d)
    pe = _th1(fp.Get("hXSec_eavail")); pw = _th1(fp.Get("hXSec_W")); fp.Close()
    y2 = y_cv.reshape(n_ea, n_w)
    my_e = (y2 * dw[None, :]).sum(axis=1)        # dsigma/dEavail
    my_w = (y2 * dea[:, None]).sum(axis=0)       # dsigma/dW
    re = np.abs(my_e / np.where(pe > 0, pe, np.nan) - 1)
    rw = np.abs(my_w / np.where(pw > 0, pw, np.nan) - 1)
    print(f"[ew] VALIDATION vs frozen 5D product: max|ratio-1| eavail={np.nanmax(re):.3f}  W={np.nanmax(rw):.3f}")
    if np.nanmax(re) > 0.05 or np.nanmax(rw) > 0.05:
        print("[ew][WARN] CV marginals deviate >5% from the frozen product -- gate/unfold mismatch?")

    # ---------- C_syst: frozen-reweighter block-sum ----------
    C_syst = np.zeros((n, n))
    for b in VERT_BANDS:
        rho_s = np.ones(truth_pt.size); rho_d = np.ones(td_w.size)
        mm = w_truth > 0; rho_s[mm] = sig_vt[b][mm] / w_truth[mm]
        dd = td_w > 0; rho_d[dd] = td_vt[b][dd] / td_w[dd]
        y_b, _ = xsec_ew(rho_s, rho_d)
        d = y_b.ravel() - y_cv
        C_syst += np.outer(d, d)
        print(f"[syst] {b:18s} dsqrt-tr += {np.sqrt(d@d):.3e}", flush=True)
    # flux universes
    fX = np.zeros((args.nflux, n))
    for u in range(args.nflux):
        rho_s = np.ones(truth_pt.size); rho_d = np.ones(td_w.size)
        mm = w_truth > 0; rho_s[mm] = sig_ft[u][mm] / w_truth[mm]
        dd = td_w > 0; rho_d[dd] = td_ft[u][dd] / td_w[dd]
        y_u, _ = xsec_ew(rho_s, rho_d)
        fX[u] = y_u.ravel() - y_cv
    C_flux = (fX.T @ fX) / args.nflux
    C_syst += C_flux
    print(f"[syst] flux({args.nflux}) sqrt-tr={np.sqrt(np.trace(C_flux)):.3e}  "
          f"C_syst sqrt-tr={np.sqrt(np.trace(C_syst)):.3e}", flush=True)

    # ---------- C_stat: diagonal marginalized CV unfold Poisson variance ----------
    C_stat = np.diag(yerr_cv.ravel() ** 2)
    print(f"[stat] diag sqrt-tr={np.sqrt(np.trace(C_stat)):.3e}")

    # ---------- C_lateral: transfer 4D detector bands -> (E_avail,W) ----------
    # marginalize each 4D lateral band cov to E_avail (M C M^T), take its per-eavail variance as a
    # FRACTIONAL detector uncertainty, and spread it over W by the CV (E_avail,W) shape (flat-in-W
    # fractional -- documented approximation; superseded by the W-resolved sweep mode below).
    fc = ROOT.TFile.Open(args.cov4d)
    fp4 = ROOT.TFile.Open("products/4d/xsec_4d_MEFHC_5iter_lgbm.root")
    x4 = _th1(fp4.Get("hXSecND_flat")); fp4.Close()
    gmask = np.where(x4 > 0)[0]
    sh4 = (len(pt_e) - 1, len(pz_e) - 1, n_ea, len(q3_e) - 1)
    ip, iz, ie, iq = np.unravel_index(gmask, sh4)
    wcell4 = dpt[ip] * dpz[iz] * dq3[iq]
    Me = np.zeros((n_ea, gmask.size)); Me[ie, np.arange(gmask.size)] = wcell4
    x4rep = x4[gmask]; y4_e = Me @ x4rep                     # dsigma/dEavail (4D CV)
    C_lat_e = np.zeros((n_ea, n_ea))
    for b in LATERAL_BANDS:
        h = fc.Get(f"hCov_universe4d_{b}")
        if not h:
            print(f"[lat] (skip missing {b})"); continue
        C_lat_e += Me @ _th2(h) @ Me.T
    fc.Close()
    frac_e = np.sqrt(np.clip(np.diag(C_lat_e), 0, None)) / np.where(y4_e > 0, y4_e, np.nan)
    frac_e = np.nan_to_num(frac_e)
    sig_lat = (frac_e[:, None] * y2)                          # per-(eavail,W) lateral sigma
    C_lateral = np.diag((sig_lat.ravel()) ** 2)
    print(f"[lat] transferred eavail frac={np.array2string(100*frac_e,precision=1)}%  "
          f"sqrt-tr={np.sqrt(np.trace(C_lateral)):.3e}")

    # ---------- W-resolved detector block from the 5D per-universe sweep ----------
    # KNOWN_ISSUES #4 fix: replace the transfer above with REAL re-inference -- each
    # detector universe (6 muon/beam laterals with shifted pt/pz/q3/W branches + 3
    # weight-only GEANT bands, 18 universes) was unfolded on the full 5D axes by
    # sbatch_unfold_5d_detector.sh. Marginalize each to (E_avail,W), difference vs
    # the MATCHED sweep CV (same seed/config), and band-sum with the
    # analyze_universes_nd.py convention: C_b = (1/N) Z^T Z on de-meaned deviations.
    # Off-diagonal (E_avail,W) correlations are now carried; the transfer was
    # diagonal-only by construction.
    if args.lateral_sweep_cv:
        import glob as _glob
        import re as _re
        sh5 = (len(pt_e) - 1, len(pz_e) - 1, n_ea, len(q3_e) - 1, n_w)

        def _sweep_ew(path):
            fs = ROOT.TFile.Open(path)
            x5 = _th1(fs.Get("hXSecND_flat")); fs.Close()
            return marginal_ew(x5.reshape(sh5)).ravel()

        y_scv = _sweep_ew(args.lateral_sweep_cv)
        uni_re = _re.compile(r".*_uni(?:_full)?_(?P<band>[A-Za-z0-9_]+?)_(?P<idx>\d+)\.root$")
        by_band = {}
        for p in sorted(_glob.glob(args.lateral_sweep_glob)):
            mm_ = uni_re.match(os.path.basename(p))
            if not mm_ or mm_.group("band") == "CV":
                continue
            by_band.setdefault(mm_.group("band"), []).append(
                (int(mm_.group("idx")), _sweep_ew(p) - y_scv))
        n_uni = sum(len(v) for v in by_band.values())
        if n_uni < 18:
            raise SystemExit(f"[FAIL] lateral sweep incomplete: {n_uni}/18 universes "
                             f"matched {args.lateral_sweep_glob}")
        C_lat_sweep = np.zeros((n, n))
        for b_, entries in sorted(by_band.items()):
            Dm = np.stack([d for _, d in sorted(entries)], axis=0)
            Zm = Dm - Dm.mean(axis=0, keepdims=True)
            cb = (Zm.T @ Zm) / Dm.shape[0]
            C_lat_sweep += cb
            print(f"[wlat] {b_:22s} N={Dm.shape[0]} sqrt-tr={np.sqrt(max(np.trace(cb),0)):.3e}",
                  flush=True)
        # old-vs-new comparison before adopting
        s_old = np.sqrt(np.clip(np.diag(C_lateral), 0, None))
        s_new = np.sqrt(np.clip(np.diag(C_lat_sweep), 0, None))
        with np.errstate(divide="ignore", invalid="ignore"):
            f_old = np.where(y_cv > 0, s_old / y_cv, 0)
            f_new = np.where(y_cv > 0, s_new / y_cv, 0)
        print(f"[wlat] sweep-CV vs frozen-CV marginal: max|ratio-1|="
              f"{np.nanmax(np.abs(y_scv/np.where(y_cv>0,y_cv,np.nan)-1)):.3f}")
        print(f"[wlat] OLD (transferred) median frac={100*np.median(f_old[y_cv>0]):.2f}%  "
              f"NEW (W-resolved) median frac={100*np.median(f_new[y_cv>0]):.2f}%")
        print(f"[wlat] sqrt-tr old={np.sqrt(np.trace(C_lateral)):.3e} "
              f"new={np.sqrt(np.trace(C_lat_sweep)):.3e}  -- ADOPTING W-resolved block")
        C_lateral = C_lat_sweep

    C_total = C_syst + C_stat + C_lateral
    sig_tot = np.sqrt(np.clip(np.diag(C_total), 0, None))
    print(f"[ew] C_total sqrt-tr={np.sqrt(np.trace(C_total)):.3e}; "
          f"median frac/bin={100*np.median(sig_tot/np.where(y_cv>0,y_cv,np.nan)):.1f}%")

    # ---------- per-generator significance ----------
    def chi2_sig(d, Cinv, ndf):
        chi2 = float(d @ Cinv @ d); p = stats.chi2.sf(chi2, ndf)
        z = stats.norm.isf(p / 2.0) if p > 0 else float("inf")
        return chi2, p, z
    Cinv = np.linalg.pinv(C_total)
    # high-W DIS corner: W >= 1.8 GeV (bins 2..5) AND E_avail >= 0.4 (the open-question-6 corner)
    ew_idx = np.arange(n).reshape(n_ea, n_w)
    corner = ((ea_e[:-1] >= 0.4)[:, None] & (w_e[:-1] >= 1.8)[None, :])
    cidx = ew_idx[corner]
    Cinv_c = np.linalg.pinv(C_total[np.ix_(cidx, cidx)])
    print(f"\n[ew] high-W DIS corner = {cidx.size} bins (E_avail>=0.4 & W>=1.8 GeV)")
    print(f"   {'generator':12s} {'chi2/ndf(all)':>16s} {'Nsig':>6s} | {'chi2/ndf(corner)':>17s} {'Nsig':>6s}")
    gen_hists = {}
    for spec in args.gens.split(","):
        tag, fn = spec.split(":")
        path = os.path.join(args.gendir, fn)
        if not os.path.exists(path):
            print(f"   {tag:12s} (missing {fn})"); continue
        fg = ROOT.TFile.Open(path); hg = _th2(fg.Get("hXSec_eavailW")); fg.Close()
        if hg.shape != (n_ea, n_w):
            print(f"   {tag:12s} (shape {hg.shape} != {(n_ea,n_w)})"); continue
        y_g = hg.ravel(); gen_hists[tag] = y_g
        d = y_cv - y_g
        c_all, p_all, z_all = chi2_sig(d, Cinv, n)
        dc = d[cidx]; c_c, p_c, z_c = chi2_sig(dc, Cinv_c, cidx.size)
        print(f"   {tag:12s} {c_all:9.1f}/{n:<5d} {z_all:6.2f} | {c_c:10.1f}/{cidx.size:<5d} {z_c:6.2f}")

    # ---------- write ----------
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    def wr_th2(name, C):
        h = ROOT.TH2D(name, name, n, 0, n, n, 0, n)
        for i in range(n):
            for j in range(n):
                h.SetBinContent(i + 1, j + 1, C[i, j])
        h.Write()
    for nm, C in [("C_syst", C_syst), ("C_stat", C_stat), ("C_lateral", C_lateral), ("C_total", C_total)]:
        wr_th2(nm, C)
    hd = ROOT.TH2D("hData_ew", "data d2sigma/(dEavail dW)", n_ea, ea_e, n_w, w_e)
    for ie_ in range(n_ea):
        for iw_ in range(n_w):
            hd.SetBinContent(ie_ + 1, iw_ + 1, y2[ie_, iw_])
    hd.Write()
    fo.Close()
    print(f"\n[ew] wrote {args.out}")


if __name__ == "__main__":
    main()
