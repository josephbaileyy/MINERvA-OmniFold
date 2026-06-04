#!/usr/bin/env python3
"""Unified-throw vs block-sum covariance cross-check (prepub item #1).

The combined systematic covariance is built band-by-band and SUMMED
(analyze_universes_3d.py): C_total = sum_band C_band, which assumes the bands are
uncorrelated AND that the unfolding responds linearly to each shift. A "unified throw"
(all systematics shifted together, then re-unfolded) would, in the linear regime,
reproduce the block sum EXACTLY; the only thing it adds is the unfolding's NONLINEAR
cross-term between bands. So the decisive, cheap test of the block-sum assumption is a
SUPERPOSITION test on the re-unfolded cross sections:

    Delta_A   = xsec(band A shifted +1sigma) - xsec(CV)
    Delta_B   = xsec(band B shifted +1sigma) - xsec(CV)
    Delta_AB  = xsec(A and B shifted together) - xsec(CV)
    residual  = Delta_AB - (Delta_A + Delta_B)      <- the cross term block-sum DROPS

If residual is small vs (Delta_A + Delta_B) for the largest bands, the unfolding combines
systematics linearly and the block-sum covariance is validated. A large residual would
mean the unified throw and the block sum disagree (cross-band nonlinearity).

This is restricted to VERTICAL (weight-only) bands so the combined weight is the exact
product of per-band weight ratios (lateral muon/beam bands shift kinematics and cannot be
composed from single-band dumps -- a separate correlated-throw event-loop run would be
needed for those; noted as a documented limitation).

Two phases (so the 120 GB read happens once, on a compute node):
  python compare_unified_throw.py --dump --omnifile <3D_universes_full.root> \
      --bands MaCCQE,2p2h,MaRES --out combo_inputs.npz
  python compare_unified_throw.py --analyze --npz combo_inputs.npz --iters 5 \
      --cv ../3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root
"""
import argparse
import itertools
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _sanitize(b):
    import unfold_2d_omnifold_unbinned as u2d
    return u2d._sanitize_band_for_branch(b)


def do_dump(args):
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und

    bands = [b.strip() for b in args.bands.split(",") if b.strip()]
    idx = args.idx
    extras = [dict(und.EXTRA_AXES["eavail"], name="eavail")]
    pt_e, pz_e = u2d.PT_EDGES, u2d.PZ_EDGES
    edges = [pt_e, pz_e, extras[0]["edges"]]
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    sig_wb = [(f"w_truth_{_sanitize(b)}_{idx}", f"w_reco_{_sanitize(b)}_{idx}") for b in bands]
    td_wb = [f"w_truth_{_sanitize(b)}_{idx}" for b in bands]

    f = ROOT.TFile.Open(args.omnifile, "READ")
    t_sig, t_bkg = f.Get("mc_signal_reco"), f.Get("mc_background")
    t_data, t_td = f.Get("data"), f.Get("mc_truth_denom")
    have = {b.GetName() for b in t_sig.GetListOfBranches()}
    missing = [n for pair in sig_wb for n in pair if n not in have]
    if missing:
        raise SystemExit(f"[FAIL] missing weight branches: {missing}")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)
    flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)

    print(f"[dump] reading signal (CV + {len(bands)} band weight cols)...", flush=True)
    sig = und.collect_signal_nd(t_sig, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                use_weights=True, extra_wbranches=sig_wb, verbose=True)
    print(f"[dump] reading truth_denom...", flush=True)
    td = und.collect_truth_denom_nd(t_td, extras, pt_lo, pt_hi, pz_lo, pz_hi, pot_scale,
                                    use_weights=True, extra_wbranches=td_wb, verbose=True)
    print(f"[dump] reading data + background...", flush=True)
    meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
    bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(t_bkg, extras, pot_scale,
                                                       pt_lo, pt_hi, pz_lo, pz_hi)
    data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
    bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
    meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"], sig["truth_extras"][0]]).astype(np.float32)
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"], sig["reco_extras"][0]]).astype(np.float32)
    measured = np.column_stack([meas_pt, meas_pz, meas_ex[0]]).astype(np.float32)
    f.Close()

    np.savez_compressed(
        args.out, bands=np.array(bands, dtype=object), idx=idx,
        MCgen=MCgen, MCreco=MCreco, measured=measured,
        pass_reco=sig["pass_reco"], pass_truth=sig["pass_truth"],
        w_truth=sig["w_truth"], w_reco=sig["w_reco"], measured_weights=meas_w,
        # per-band signal universe weights (truth/reco), aligned to MC rows
        sig_extra_wt=np.array(sig["extra_wt"]), sig_extra_wr=np.array(sig["extra_wr"]),
        # truth-denom CV + per-band universe weights, with truth coords for re-binning
        td_pt=td["pt"], td_pz=td["pz"], td_ea=td["extras"][0], td_w=td["w"],
        td_extra_w=np.array(td["extra_w"]),
        flux=np.asarray(flux_bins, float), data_pot=data_pot,
        n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
        **{f"edges_{i}": np.asarray(e, float) for i, e in enumerate(edges)},
        nedges=len(edges))
    print(f"[dump] wrote {args.out}: MCgen{MCgen.shape}, bands={bands}")


def _xsec_for_weights(d, edges, wt_sig, wr_sig, wt_td, iters, seed):
    """Run OmniFold with given (per-event) signal truth/reco weights + denom weights,
    return the reported-bin xsec (flat, C order over the nd shape)."""
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd
    MCgen, MCreco, measured = d["MCgen"], d["MCreco"], d["measured"]
    pass_reco, pass_truth = d["pass_reco"], d["pass_truth"]
    w_pull, w_push = omnifold_loop(
        MCgen, MCreco, measured, pass_reco, pass_truth, np.ones(len(measured), bool),
        iters, kind="lgbm", MCgen_weights=wt_sig, MCreco_weights=wr_sig,
        measured_weights=d["measured_weights"], seed=seed, verbose=False)
    m = pass_truth
    sample = np.column_stack([MCgen[m, a] for a in range(MCgen.shape[1])])
    bins = [np.asarray(e, float) for e in edges]
    unfold_nd, _ = np.histogramdd(sample, bins=bins, weights=w_push * wt_sig[m])
    of_in, _ = np.histogramdd(sample, bins=bins, weights=wt_sig[m])
    # universe-shifted completeness denominator
    denom_nd, _ = np.histogramdd(np.column_stack([d["td_pt"], d["td_pz"], d["td_ea"]]),
                                 bins=bins, weights=wt_td)
    completeness = np.zeros_like(of_in)
    nz = denom_nd > 0
    completeness[nz] = of_in[nz] / denom_nd[nz]
    xsec, _ = extract_cross_section_nd(unfold_nd, completeness, d["flux"],
                                       float(d["data_pot"]), float(d["n_nucleons"]), edges)
    return xsec


def do_analyze(args):
    d = np.load(args.npz, allow_pickle=True)
    bands = list(d["bands"])
    nedges = int(d["nedges"])
    edges = [d[f"edges_{i}"] for i in range(nedges)]
    sig_wt = d["sig_extra_wt"]; sig_wr = d["sig_extra_wr"]; td_w = d["td_extra_w"]
    w_truth, w_reco, td_cv = d["w_truth"], d["w_reco"], d["td_w"]

    def ratio(uni, cv):
        r = np.ones_like(cv)
        good = cv > 0
        r[good] = uni[good] / cv[good]
        return r

    # CV xsec
    print("[analyze] CV unfold...", flush=True)
    x_cv = _xsec_for_weights(d, edges, w_truth, w_reco, td_cv, args.iters, args.seed)
    rep = x_cv.ravel(order="C") > 0
    base = x_cv.ravel(order="C")[rep]

    # single-band shifted xsecs
    single = {}
    for k, b in enumerate(bands):
        print(f"[analyze] single band {b}+ ...", flush=True)
        wt = w_truth * ratio(sig_wt[k], w_truth)
        wr = w_reco * ratio(sig_wr[k], w_reco)
        wtd = td_cv * ratio(td_w[k], td_cv)
        xb = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed)
        single[b] = xb.ravel(order="C")[rep] - base

    # joint shifts (all pairs)
    print("\n===== Unified-throw / superposition cross-check =====")
    print(f"reported bins: {rep.sum()}; bands: {bands}\n")
    rows = []
    for a, b in itertools.combinations(bands, 2):
        ia, ib = bands.index(a), bands.index(b)
        print(f"[analyze] joint {a}+{b}+ ...", flush=True)
        wt = w_truth * ratio(sig_wt[ia], w_truth) * ratio(sig_wt[ib], w_truth)
        wr = w_reco * ratio(sig_wr[ia], w_reco) * ratio(sig_wr[ib], w_reco)
        wtd = td_cv * ratio(td_w[ia], td_cv) * ratio(td_w[ib], td_cv)
        xab = _xsec_for_weights(d, edges, wt, wr, wtd, args.iters, args.seed).ravel(order="C")[rep] - base
        lin = single[a] + single[b]
        resid = xab - lin
        rel = np.linalg.norm(resid) / (np.linalg.norm(lin) + 1e-300)
        # per-bin: cross term vs the linear (block-sum) combination
        with np.errstate(divide="ignore", invalid="ignore"):
            perbin = np.where(np.abs(lin) > 0, np.abs(resid) / np.abs(lin), 0.0)
        rows.append((a, b, np.linalg.norm(lin), np.linalg.norm(resid), rel,
                     float(np.median(perbin[np.abs(lin) > 0]))))

    print(f"\n{'band A':14s} {'band B':14s} {'||lin||':>11s} {'||cross||':>11s} "
          f"{'cross/lin':>9s} {'med/bin':>8s}")
    worst = 0.0
    for a, b, nl, nr, rel, med in rows:
        print(f"{a:14s} {b:14s} {nl:11.3e} {nr:11.3e} {100*rel:8.2f}% {100*med:7.2f}%")
        worst = max(worst, rel)
    print(f"\nVERDICT: largest cross-term / linear = {100*worst:.2f}%.")
    print("  << ~10% => the unfolding combines these systematics linearly; the block-sum")
    print("  covariance (sum of per-band C_band) is validated for the dominant bands.")
    print("  A large value would flag cross-band nonlinearity the block sum omits.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--omnifile",
                    default=f"{_REPO}/3d-unfolding/runEventLoopOmniFold_MEFHC_3D_universes_full.root")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--bands", default="MaCCQE,2p2h,MaRES")
    ap.add_argument("--idx", type=int, default=0, help="universe index (0 = +1sigma)")
    ap.add_argument("--out", default="combo_inputs.npz")
    ap.add_argument("--npz", default="combo_inputs.npz")
    ap.add_argument("--cv", default=f"{_REPO}/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.dump:
        do_dump(args)
    if args.analyze:
        do_analyze(args)
    if not (args.dump or args.analyze):
        ap.error("pass --dump and/or --analyze")


if __name__ == "__main__":
    main()
