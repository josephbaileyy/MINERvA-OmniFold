#!/usr/bin/env python3
"""Read-once bank for the q3 (4D) universe sweep -- durable speedup for re-runs.

The per-universe sweep (sbatch_unfold_4d_universes_full.sh) re-reads the 120 GB omnifile
once PER universe (~25 min single-threaded GetEntry x 187). This banks the per-universe
inputs in a few file passes so each unfold reads an mmap'd slice instead:

  STAGE 1 (dump, parallel groups): one GetEntry pass per group over the 4D
    _universes_full omnifile, storing the VERTICAL universes' weights
    (w_truth/w_reco signal + w_truth denom, POT-scaled, float32) and -- once, by
    group 0 -- the shared CV block (4D coords, pass flags, measured, denom coords,
    flux). Vertical universes gate on CV (pt,pz) so they share one block; the 12
    LATERAL universes gate on shifted kinematics (different kept-set each) and are
    left to the per-universe re-read path (only 12, cheap).
  STAGE 2 (run, per universe): mmap the CV block + that universe's 3 weight arrays,
    run the SAME omnifold_loop + xsec_nd, write hXSecND_flat to the sweep's own
    filename with skip-if-exists -- so it COOPERATES with the shared sweep (whichever
    produces a universe first, the other skips) and feeds analyze_universes_nd.

Reuse value (see ND_OMNIFOLD_RUN_LOG): re-running with different iters/binning/estimator,
and the 4D vertical unified throw, both consume this bank without touching the 120 GB file.

  python sweep_bank.py --dump --group G --ngroups N --bankdir bank_sweep
  python sweep_bank.py --run  --universe MaCCQE:0 --bankdir bank_sweep
"""
import argparse
import glob
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
LIST = f"{_REPO}/3d-unfolding/uq_3d/universes_full_list.txt"


def vertical_universes():
    out = []
    for l in open(LIST):
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
    ea_e = und.EXTRA_AXES["eavail"]["edges"]; q3_e = und.EXTRA_AXES["q3"]["edges"]
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    allv = vertical_universes()
    mine = [u for k, u in enumerate(allv) if k % args.ngroups == args.group]
    print(f"[dump g{args.group}/{args.ngroups}] {len(mine)} vertical universes", flush=True)

    f = ROOT.TFile.Open(args.omnifile)
    t, td = f.Get("mc_signal_reco"), f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)

    # ---- signal ----
    sc = {b: carray("d", [0.0]) for b in ("MC", "MC_pz", "MC_eavail", "MC_q3",
                                          "sim", "sim_pz", "sim_eavail", "sim_q3",
                                          "w_truth", "w_reco")}
    sp = carray("B", [0])
    for b, a in sc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    uwt = {u: carray("d", [0.0]) for u in mine}; uwr = {u: carray("d", [0.0]) for u in mine}
    for (b, i) in mine:
        t.SetBranchAddress(f"w_truth_{san(b)}_{i}", uwt[(b, i)])
        t.SetBranchAddress(f"w_reco_{san(b)}_{i}", uwr[(b, i)])
    _f = lambda: carray("f")
    g0 = (args.group == 0)
    k_pt, k_pz, k_ea, k_q3 = _f(), _f(), _f(), _f()
    k_rpt, k_rpz, k_rea, k_rq3 = _f(), _f(), _f(), _f()
    k_pr, k_ptru = carray("b"), carray("b")
    a_wt = {u: _f() for u in mine}; a_wr = {u: _f() for u in mine}
    n = t.GetEntries()
    for e in range(n):
        t.GetEntry(e)
        a_pt, a_pz = float(sc["MC"][0]), float(sc["MC_pz"][0])
        b_pt, b_pz = float(sc["sim"][0]), float(sc["sim_pz"][0])
        passed = sp[0] != 0
        wt = float(sc["w_truth"][0]); wr = float(sc["w_reco"][0])
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
            k_ea.append(float(sc["MC_eavail"][0])); k_q3.append(float(sc["MC_q3"][0]))
            k_rpt.append(b_pt if (passed and rec) else -9999.0)
            k_rpz.append(b_pz if (passed and rec) else -9999.0)
            k_rea.append(float(sc["sim_eavail"][0]) if (passed and rec) else -9999.0)
            k_rq3.append(float(sc["sim_q3"][0]) if (passed and rec) else -9999.0)
            k_pr.append(passed and rec); k_ptru.append(tru)
        for u in mine:
            a_wt[u].append(float(uwt[u][0]) * pot_scale)
            a_wr[u].append(float(uwr[u][0]) * pot_scale)
        if e % 1000000 == 0:
            print(f"  signal {e}/{n}", flush=True)
    for (b, i) in mine:
        np.save(f"{args.bankdir}/{b}_{i}_wt.npy", np.asarray(a_wt[(b, i)], np.float32))
        np.save(f"{args.bankdir}/{b}_{i}_wr.npy", np.asarray(a_wr[(b, i)], np.float32))

    # ---- truth_denom ----
    dc = {b: carray("d", [0.0]) for b in ("MC", "MC_pz", "MC_eavail", "MC_q3", "w_truth")}
    for b, a in dc.items():
        td.SetBranchAddress(b, a)
    duw = {u: carray("d", [0.0]) for u in mine}
    for (b, i) in mine:
        td.SetBranchAddress(f"w_truth_{san(b)}_{i}", duw[(b, i)])
    d_pt, d_pz, d_ea, d_q3 = _f(), _f(), _f(), _f()
    da_w = {u: _f() for u in mine}
    nd = td.GetEntries()
    for e in range(nd):
        td.GetEntry(e)
        pt, pz = float(dc["MC"][0]), float(dc["MC_pz"][0]); w = float(dc["w_truth"][0])
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(w) and 0 <= w < 1e4):
            continue
        if not u2d.in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
            continue
        if g0:
            d_pt.append(pt); d_pz.append(pz)
            d_ea.append(float(dc["MC_eavail"][0])); d_q3.append(float(dc["MC_q3"][0]))
        for u in mine:
            da_w[u].append(float(duw[u][0]) * pot_scale)
    for (b, i) in mine:
        np.save(f"{args.bankdir}/{b}_{i}_tdw.npy", np.asarray(da_w[(b, i)], np.float32))

    if g0:
        extras = [dict(und.EXTRA_AXES["eavail"], name="eavail"),
                  dict(und.EXTRA_AXES["q3"], name="q3")]
        edges = [pt_e, pz_e, ea_e, q3_e]
        t_data, t_bkg = f.Get("data"), f.Get("mc_background")
        meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
        bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(t_bkg, extras, pot_scale,
                                                           pt_lo, pt_hi, pz_lo, pz_hi)
        data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
        bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
        meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)
        flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)
        np.savez(f"{args.bankdir}/cv.npz",
                 MCgen=np.column_stack([k_pt, k_pz, k_ea, k_q3]).astype(np.float32),
                 MCreco=np.column_stack([k_rpt, k_rpz, k_rea, k_rq3]).astype(np.float32),
                 measured=np.column_stack([meas_pt, meas_pz] + meas_ex).astype(np.float32),
                 measured_weights=meas_w,
                 pass_reco=np.asarray(k_pr, bool), pass_truth=np.asarray(k_ptru, bool),
                 td_pt=np.asarray(d_pt), td_pz=np.asarray(d_pz),
                 td_ea=np.asarray(d_ea), td_q3=np.asarray(d_q3),
                 flux=np.asarray(flux_bins, float), data_pot=data_pot,
                 n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
                 edges_0=pt_e, edges_1=pz_e, edges_2=np.asarray(ea_e, float),
                 edges_3=np.asarray(q3_e, float))
        print(f"[dump g0] wrote cv.npz ({len(k_pt)} signal, {len(d_pt)} denom)")
    f.Close()
    print(f"[dump g{args.group}] done", flush=True)


def do_run(args):
    import ROOT
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd, total_xsec
    band, _, idx = args.universe.partition(":")
    tag = f"{band}_{idx}"
    outdir = f"{_REPO}/nd-unfolding/uq_4d/universe_sweep"
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/4d_xsec_MEFHC_5iter_lgbm_uni_full_{tag}.root"
    if os.path.exists(out) and os.path.getsize(out) > 0:
        print(f"[run] SKIP {tag}: {out} exists"); return
    bd = args.bankdir
    cv = np.load(f"{bd}/cv.npz")
    edges = [cv[f"edges_{i}"] for i in range(4)]
    MCgen, MCreco, measured = cv["MCgen"], cv["MCreco"], cv["measured"]
    pass_reco, pass_truth = cv["pass_reco"], cv["pass_truth"]
    wt = np.load(f"{bd}/{tag}_wt.npy", mmap_mode="r").astype(np.float64)
    wr = np.load(f"{bd}/{tag}_wr.npy", mmap_mode="r").astype(np.float64)
    tdw = np.load(f"{bd}/{tag}_tdw.npy", mmap_mode="r").astype(np.float64)
    # Sanitize non-finite reweights -> 0. Some normalization knobs (e.g. NormDISCC) leave
    # an undefined (0/0) per-event weight for events with no nominal contribution; the dump
    # stored those as NaN (NormDISCC_0_wt had 83727), which crashes the LGBM fit with
    # "sample_weight contains NaN". An undefined reweight contributes nothing to that
    # universe's spectrum, so 0 is the correct fallback. No-op on healthy universes.
    for _w in (wt, wr, tdw):
        np.nan_to_num(_w, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    w_pull, w_push = omnifold_loop(
        MCgen, MCreco, measured, pass_reco, pass_truth, np.ones(len(measured), bool),
        args.iters, kind="lgbm", MCgen_weights=wt, MCreco_weights=wr,
        measured_weights=cv["measured_weights"], seed=42, verbose=False)
    m = pass_truth
    bins = [np.asarray(e, float) for e in edges]
    sample = np.column_stack([MCgen[m, a] for a in range(MCgen.shape[1])])
    unfold_nd, _ = np.histogramdd(sample, bins=bins, weights=w_push * wt[m])
    of_in, _ = np.histogramdd(sample, bins=bins, weights=wt[m])
    denom_nd, _ = np.histogramdd(np.column_stack([cv["td_pt"], cv["td_pz"], cv["td_ea"], cv["td_q3"]]),
                                 bins=bins, weights=tdw)
    comp = np.zeros_like(of_in); nz = denom_nd > 0; comp[nz] = of_in[nz] / denom_nd[nz]
    cglob = of_in.sum() / denom_nd.sum() if denom_nd.sum() > 0 else float("nan")
    xsec, _ = extract_cross_section_nd(unfold_nd, comp, cv["flux"],
                                       float(cv["data_pot"]), float(cv["n_nucleons"]), edges)
    flat = xsec.ravel(order="C")
    rf = ROOT.TFile.Open(out, "RECREATE")
    ROOT.TParameter("int")("ndim", 4).Write()
    ROOT.TParameter("double")("globalCompleteness", cglob).Write()
    ROOT.TParameter("double")("dataPOT", float(cv["data_pot"])).Write()
    h = ROOT.TH1D("hXSecND_flat", "d^{4}sigma flat (bank)", len(flat), 0, len(flat))
    for i, v in enumerate(flat):
        h.SetBinContent(i + 1, float(v))
    h.Write(); rf.Close()
    print(f"[run] {tag}: completeness={cglob:.4f} total={total_xsec(xsec, edges):.4e} -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--omnifile", default=f"{_REPO}/nd-unfolding/runEventLoopOmniFold_4D_MEFHC_universes_full.root")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--bankdir", default="bank_sweep")
    ap.add_argument("--group", type=int, default=0)
    ap.add_argument("--ngroups", type=int, default=1)
    ap.add_argument("--universe", default=None)
    ap.add_argument("--iters", type=int, default=5)
    args = ap.parse_args()
    if args.dump:
        do_dump(args)
    elif args.run:
        do_run(args)
    else:
        ap.error("pass --dump or --run")


if __name__ == "__main__":
    main()
