#!/usr/bin/env python3
"""Read-once bank for the 5D (pt,pz,eavail,q3,W) universe sweep.

Faithful 5D extension of sweep_bank.py (4D). The vertical universes are weight-only
(they reweight CV kinematics), so the bank stores per-event POT-scaled universe weights
plus a shared CV block that now carries the W coordinate (MC_W / sim_W, row-aligned in
runEventLoopOmniFold_5D_MEFHC_universes_full.root) and edges_4 (the W binning).

  STAGE 1 (dump, parallel groups): one GetEntry pass per group over the 5D
    _universes_full omnifile, storing the VERTICAL universes' weights
    (w_truth/w_reco signal + w_truth denom, POT-scaled, float32) and -- once, by
    group 0 -- the shared CV block (5D coords, pass flags, measured, denom coords, flux).
  STAGE 2 (run, per universe): mmap the CV block + that universe's 3 weight arrays,
    run the SAME omnifold_loop + xsec_nd over 5 axes, write hXSecND_flat (ndim=5) to
    uq_5d/universe_sweep/ with skip-if-exists.

The lateral universes (muon/beam) gate on shifted kinematics and are produced by the
per-universe driver (sbatch_unfold_5d_detector.sh); they are NOT in the vertical list.

  python sweep_bank_5d.py --dump --group G --ngroups N --bankdir bank_sweep_5d
  python sweep_bank_5d.py --run  --universe MaCCQE:0 --bankdir bank_sweep_5d
"""
import argparse
import math
import os
import sys
from array import array as carray

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

LATERAL = {"BeamAngleX", "BeamAngleY", "MuonResolution",
           "Muon_Energy_MINERvA", "Muon_Energy_MINOS", "MinosEfficiency"}
VLIST = f"{_REPO}/nd-unfolding/uq_4d/vertical_universes.txt"
OMNIFILE_5D = f"{_REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root"
SWEEPDIR = f"{_REPO}/nd-unfolding/uq_5d/universe_sweep"
NDIM = 5


def vertical_universes(vlist):
    out = []
    for l in open(vlist):
        l = l.strip()
        if not l:
            continue
        b, _, i = l.partition(":")
        if b not in LATERAL:
            out.append((b, int(i)))
    return out


def do_dump(args):
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und
    os.makedirs(args.bankdir, exist_ok=True)
    san = u2d._sanitize_band_for_branch
    pt_e, pz_e = u2d.PT_EDGES, u2d.PZ_EDGES
    ea_e = und.EXTRA_AXES["eavail"]["edges"]
    q3_e = und.EXTRA_AXES["q3"]["edges"]
    w_e = und.EXTRA_AXES["W"]["edges"]
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    allv = vertical_universes(args.vlist)
    mine = [u for k, u in enumerate(allv) if k % args.ngroups == args.group]
    print(f"[dump g{args.group}/{args.ngroups}] {len(mine)} vertical universes", flush=True)

    f = ROOT.TFile.Open(args.omnifile)
    t, td = f.Get("mc_signal_reco"), f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)

    # ---- signal ----
    sc = {b: carray("d", [0.0]) for b in ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W",
                                          "sim", "sim_pz", "sim_eavail", "sim_q3", "sim_W",
                                          "w_truth", "w_reco")}
    sp = carray("B", [0])
    for b, a in sc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    uwt = {u: carray("d", [0.0]) for u in mine}
    uwr = {u: carray("d", [0.0]) for u in mine}
    for (b, i) in mine:
        t.SetBranchAddress(f"w_truth_{san(b)}_{i}", uwt[(b, i)])
        t.SetBranchAddress(f"w_reco_{san(b)}_{i}", uwr[(b, i)])
    _f = lambda: carray("f")
    g0 = (args.group == 0)
    k_pt, k_pz, k_ea, k_q3, k_w = _f(), _f(), _f(), _f(), _f()
    k_rpt, k_rpz, k_rea, k_rq3, k_rw = _f(), _f(), _f(), _f(), _f()
    k_pr, k_ptru = carray("b"), carray("b")
    a_wt = {u: _f() for u in mine}
    a_wr = {u: _f() for u in mine}
    n = t.GetEntries()
    for e in range(n):
        t.GetEntry(e)
        a_pt, a_pz = float(sc["MC"][0]), float(sc["MC_pz"][0])
        b_pt, b_pz = float(sc["sim"][0]), float(sc["sim_pz"][0])
        passed = sp[0] != 0
        wt = float(sc["w_truth"][0])
        wr = float(sc["w_reco"][0])
        if not (math.isfinite(wt) and math.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            continue
        tru = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec = (math.isfinite(b_pt) and math.isfinite(b_pz)
               and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru or (passed and rec)):
            continue
        if g0:
            k_pt.append(a_pt if math.isfinite(a_pt) else -9999.0)
            k_pz.append(a_pz if math.isfinite(a_pz) else -9999.0)
            k_ea.append(float(sc["MC_eavail"][0]))
            k_q3.append(float(sc["MC_q3"][0]))
            k_w.append(float(sc["MC_W"][0]))
            k_rpt.append(b_pt if (passed and rec) else -9999.0)
            k_rpz.append(b_pz if (passed and rec) else -9999.0)
            k_rea.append(float(sc["sim_eavail"][0]) if (passed and rec) else -9999.0)
            k_rq3.append(float(sc["sim_q3"][0]) if (passed and rec) else -9999.0)
            k_rw.append(float(sc["sim_W"][0]) if (passed and rec) else -9999.0)
            k_pr.append(passed and rec)
            k_ptru.append(tru)
        for u in mine:
            a_wt[u].append(float(uwt[u][0]) * pot_scale)
            a_wr[u].append(float(uwr[u][0]) * pot_scale)
        if e % 1000000 == 0:
            print(f"  signal {e}/{n}", flush=True)
    for (b, i) in mine:
        np.save(f"{args.bankdir}/{b}_{i}_wt.npy", np.asarray(a_wt[(b, i)], np.float32))
        np.save(f"{args.bankdir}/{b}_{i}_wr.npy", np.asarray(a_wr[(b, i)], np.float32))

    # ---- truth_denom ----
    dc = {b: carray("d", [0.0]) for b in ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth")}
    for b, a in dc.items():
        td.SetBranchAddress(b, a)
    duw = {u: carray("d", [0.0]) for u in mine}
    for (b, i) in mine:
        td.SetBranchAddress(f"w_truth_{san(b)}_{i}", duw[(b, i)])
    d_pt, d_pz, d_ea, d_q3, d_w = _f(), _f(), _f(), _f(), _f()
    da_w = {u: _f() for u in mine}
    nd = td.GetEntries()
    for e in range(nd):
        td.GetEntry(e)
        pt, pz = float(dc["MC"][0]), float(dc["MC_pz"][0])
        w = float(dc["w_truth"][0])
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(w) and 0 <= w < 1e4):
            continue
        if not u2d.in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
            continue
        if g0:
            d_pt.append(pt)
            d_pz.append(pz)
            d_ea.append(float(dc["MC_eavail"][0]))
            d_q3.append(float(dc["MC_q3"][0]))
            d_w.append(float(dc["MC_W"][0]))
        for u in mine:
            da_w[u].append(float(duw[u][0]) * pot_scale)
    for (b, i) in mine:
        np.save(f"{args.bankdir}/{b}_{i}_tdw.npy", np.asarray(da_w[(b, i)], np.float32))

    # ---- background: per-universe w_bkg (KNOWN_ISSUES #13) ----
    # Vertical bands keep CV bkg kinematics -> universe-independent kept-set;
    # bank CV bkg columns once (g0) + each universe's w_bkg column, do_run rebins
    # to recompute the measured purity down-weight. Lateral bands run on the
    # direct driver's re-read path. (Mirrors sweep_bank.py.)
    extras = [dict(und.EXTRA_AXES["eavail"], name="eavail"),
              dict(und.EXTRA_AXES["q3"], name="q3"),
              dict(und.EXTRA_AXES["W"], name="W")]
    edges = [pt_e, pz_e, ea_e, q3_e, w_e]
    t_bkg = f.Get("mc_background")
    bkg_wbranches = [f"w_bkg_{san(b)}_{i}" for (b, i) in mine]
    bkg_pt, bkg_pz, bkg_ex, bkg_w, bkg_uw = und.collect_bkg_nd(
        t_bkg, extras, pot_scale, pt_lo, pt_hi, pz_lo, pz_hi,
        extra_wbranches=bkg_wbranches)
    for k, (b, i) in enumerate(mine):
        np.save(f"{args.bankdir}/{b}_{i}_bkgw.npy", bkg_uw[k].astype(np.float32))

    if g0:
        t_data = f.Get("data")
        meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
        data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
        bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
        meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)
        flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)
        np.savez(f"{args.bankdir}/cv.npz",
                 MCgen=np.column_stack([k_pt, k_pz, k_ea, k_q3, k_w]).astype(np.float32),
                 MCreco=np.column_stack([k_rpt, k_rpz, k_rea, k_rq3, k_rw]).astype(np.float32),
                 measured=np.column_stack([meas_pt, meas_pz] + meas_ex).astype(np.float32),
                 measured_weights=meas_w,
                 bkg_cols=np.column_stack([bkg_pt, bkg_pz] + bkg_ex).astype(np.float32),
                 pass_reco=np.asarray(k_pr, bool), pass_truth=np.asarray(k_ptru, bool),
                 td_pt=np.asarray(d_pt), td_pz=np.asarray(d_pz),
                 td_ea=np.asarray(d_ea), td_q3=np.asarray(d_q3), td_w=np.asarray(d_w),
                 flux=np.asarray(flux_bins, float), data_pot=data_pot,
                 n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
                 edges_0=pt_e, edges_1=pz_e, edges_2=np.asarray(ea_e, float),
                 edges_3=np.asarray(q3_e, float), edges_4=np.asarray(w_e, float))
        print(f"[dump g0] wrote cv.npz ({len(k_pt)} signal, {len(d_pt)} denom, "
              f"{len(bkg_pt)} bkg)")
    f.Close()
    print(f"[dump g{args.group}] done", flush=True)


def do_run(args):
    import ROOT
    import unfold_nd_omnifold_unbinned as und
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd, total_xsec
    band, _, idx = args.universe.partition(":")
    tag = f"{band}_{idx}"
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/5d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f"[run] SKIP {tag}: {out} exists")
        return
    bd = args.bankdir
    cv = np.load(f"{bd}/cv.npz")
    edges = [cv[f"edges_{i}"] for i in range(NDIM)]
    MCgen, MCreco, measured = cv["MCgen"], cv["MCreco"], cv["measured"]
    pass_reco, pass_truth = cv["pass_reco"], cv["pass_truth"]
    wt = np.load(f"{bd}/{tag}_wt.npy", mmap_mode="r").astype(np.float64)
    wr = np.load(f"{bd}/{tag}_wr.npy", mmap_mode="r").astype(np.float64)
    tdw = np.load(f"{bd}/{tag}_tdw.npy", mmap_mode="r").astype(np.float64)
    # Sanitize non-finite reweights -> 0 (mirrors sweep_bank.py: NormDISCC etc. leave
    # undefined 0/0 per-event weights stored as NaN; 0 is the correct fallback).
    for _w in (wt, wr, tdw):
        np.nan_to_num(_w, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    # KNOWN_ISSUES #13: rebin CV background with this universe's w_bkg to
    # recompute the measured purity down-weight. Production is fail-closed.
    bkgw_path = f"{bd}/{tag}_bkgw.npy"
    if "bkg_cols" in cv and os.path.exists(bkgw_path):
        bkgw = np.load(bkgw_path, mmap_mode="r").astype(np.float64).copy()
        np.nan_to_num(bkgw, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
        bkg_cols = cv["bkg_cols"].astype(np.float64)
        meas_cols = [measured[:, a] for a in range(measured.shape[1])]
        bkg_cols_l = [bkg_cols[:, a] for a in range(bkg_cols.shape[1])]
        data_nd_m, _ = und.histnd(meas_cols, np.ones(measured.shape[0]), edges)
        bkg_nd_m, _ = und.histnd(bkg_cols_l, bkgw, edges)
        measured_weights = und.build_measured_training_nd(meas_cols, data_nd_m, bkg_nd_m, edges)
    else:
        if not args.allow_cv_background:
            raise SystemExit(f"[FAIL] {tag}: bank lacks bkg_cols or {bkgw_path}; "
                             "regenerate the post-#13 event loop/bank or explicitly pass "
                             "--allow-cv-background for a legacy diagnostic")
        print(f"[run][WARN] {tag}: explicitly using legacy CV-frozen background", flush=True)
        measured_weights = cv["measured_weights"]
    w_pull, w_push = omnifold_loop(
        MCgen, MCreco, measured, pass_reco, pass_truth, np.ones(len(measured), bool),
        args.iters, kind="lgbm", MCgen_weights=wt, MCreco_weights=wr,
        measured_weights=measured_weights, seed=42, verbose=False)
    m = pass_truth
    bins = [np.asarray(e, float) for e in edges]
    sample = np.column_stack([MCgen[m, a] for a in range(MCgen.shape[1])])
    unfold_nd, _ = np.histogramdd(sample, bins=bins, weights=w_push * wt[m])
    of_in, _ = np.histogramdd(sample, bins=bins, weights=wt[m])
    denom_nd, _ = np.histogramdd(
        np.column_stack([cv["td_pt"], cv["td_pz"], cv["td_ea"], cv["td_q3"], cv["td_w"]]),
        bins=bins, weights=tdw)
    comp = np.zeros_like(of_in)
    nz = denom_nd > 0
    comp[nz] = of_in[nz] / denom_nd[nz]
    cglob = of_in.sum() / denom_nd.sum() if denom_nd.sum() > 0 else float("nan")
    xsec, _ = extract_cross_section_nd(unfold_nd, comp, cv["flux"],
                                       float(cv["data_pot"]), float(cv["n_nucleons"]), edges)
    flat = xsec.ravel(order="C")
    rf = ROOT.TFile.Open(out, "RECREATE")
    ROOT.TParameter("int")("ndim", NDIM).Write()
    ROOT.TParameter("double")("globalCompleteness", cglob).Write()
    ROOT.TParameter("double")("dataPOT", float(cv["data_pot"])).Write()
    h = ROOT.TH1D("hXSecND_flat", "d^{5}sigma flat (bank)", len(flat), 0, len(flat))
    for i, v in enumerate(flat):
        h.SetBinContent(i + 1, float(v))
    h.Write()
    rf.Close()
    print(f"[run] {tag}: completeness={cglob:.4f} total={total_xsec(xsec, edges):.4e} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--omnifile", default=OMNIFILE_5D)
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--bankdir", default=f"{_REPO}/nd-unfolding/bank_sweep_5d")
    ap.add_argument("--vlist", default=VLIST)
    ap.add_argument("--outdir", default=SWEEPDIR)
    ap.add_argument("--group", type=int, default=0)
    ap.add_argument("--ngroups", type=int, default=1)
    ap.add_argument("--universe", default=None)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--allow-cv-background", action="store_true",
                    help="legacy diagnostic only; production must use banked universe background")
    args = ap.parse_args()
    if args.dump:
        do_dump(args)
    elif args.run:
        do_run(args)
    else:
        ap.error("pass --dump or --run")


if __name__ == "__main__":
    main()
