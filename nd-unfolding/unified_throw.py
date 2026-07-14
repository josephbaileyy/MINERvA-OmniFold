#!/usr/bin/env python3
"""Full unified-throw covariance (prepub item #1, the rigorous version).

CAVEAT (2026-06-04): multiplying single-band reweight ratios across bands is an
ARTIFACT-prone proxy (compounds low-w_cv tail events -> inflated low-stat bins; gave a
spurious 25x vs block-sum). NOT a valid block-sum test. The sound cross-check is the
jitter-null superposition (compare_unified_throw.py --null). A rigorous unified throw needs
TRUE multi-band universes (event-loop dump), not this ratio product.

The block-sum covariance C = sum_band C_band assumes the bands are uncorrelated AND that
the unfolding responds linearly to each shift. The +1sigma superposition probe
(compare_unified_throw.py) was inconclusive (jitter floor). The rigorous object is a UNIFIED
THROW: in each of T throws, draw ALL (vertical) systematics together, build one combined
per-event weight, re-unfold, and accumulate ONE covariance. In the linear regime this equals
the block sum exactly; the difference is the genuine cross-band nonlinearity (and jitter,
which averages down over throws). Compare C_unified to the block sum of the SAME vertical
bands -> a *measured* validation (or refutation) of the block-sum assumption.

Scope: VERTICAL (weight-only) bands only -- Flux (100 PPFX universes) + the top vertical
GENIE/FSI bands. The lateral muon/beam bands shift kinematics and cannot be composed from
weights; they are excluded (documented limitation; a correlated-throw event loop would be
needed for them). So the comparison is C_unified(vertical) vs blocksum(vertical).

Three stages (the 120 GB read is split across parallel dump-group jobs into an mmap'd
ratio bank, so throws are then lean):

  # 1) DUMP the ratio bank (array over groups; group 0 also writes CV inputs)
  python unified_throw.py --dump --group G --ngroups N --bankdir bank_uthrow
  # 2) RUN throws from the bank (array; each job does a chunk)
  python unified_throw.py --run --bankdir bank_uthrow --throw-start S --throw-count C
  # 3) COMBINE -> unified cov + block-sum comparison
  python unified_throw.py --combine --bankdir bank_uthrow \
      --blocksum ../3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root
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

# Vertical bands for the throw: Flux (special, many-universe) + 2-universe bands.
# Ordered by covariance contribution (analyze_universes_3d). top-12 ~ 99% of vertical.
TWO_UNIV_BANDS = ["2p2h", "MaCCQE", "CCQEPauliSupViaKF", "MaRES", "FrElas_N", "LowQ2",
                  "MvRES", "Rvp2pi", "Rvn2pi", "HighQ2", "MFP_N", "FrAbs_pi"]
N_FLUX = 100


# --------------------------------------------------------------------------- dump
def do_dump(args):
    import ROOT
    import unfold_2d_omnifold_unbinned as u2d
    import unfold_nd_omnifold_unbinned as und

    os.makedirs(args.bankdir, exist_ok=True)
    axis_names = [a.strip() for a in args.axes.split(",") if a.strip()]
    extras = [dict(und.EXTRA_AXES[a], name=a) for a in axis_names]
    pt_e = ([float(x) for x in args.pt_edges.split(",")] if args.pt_edges
            else u2d.PT_EDGES)
    pz_e = ([float(x) for x in args.pz_edges.split(",")] if args.pz_edges
            else u2d.PZ_EDGES)
    if args.full_phase_space:
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[dump] FULL PHASE SPACE: theta_mu truth gate lifted")
    pt_lo, pt_hi, pz_lo, pz_hi = pt_e[0], pt_e[-1], pz_e[0], pz_e[-1]

    # which bands does THIS group dump? round-robin split for balance.
    flux_idx = [k for k in range(N_FLUX) if k % args.ngroups == args.group]
    my_bands = [b for i, b in enumerate(TWO_UNIV_BANDS) if i % args.ngroups == args.group]
    san = u2d._sanitize_band_for_branch
    print(f"[dump g{args.group}/{args.ngroups}] flux idx {len(flux_idx)}, bands {my_bands}",
          flush=True)

    f = ROOT.TFile.Open(args.omnifile)
    t = f.Get("mc_signal_reco"); td = f.Get("mc_truth_denom")
    data_pot, mc_pot, pot_scale = u2d.get_pot_scales(f)

    # ---- signal tree: gate, dump CV (group 0) + this group's band ratios ----
    sig_branches = ["MC", "MC_pz", "sim", "sim_pz", "w_truth", "w_reco"]
    for ax in extras:
        sig_branches += [ax["truth"], ax["reco"]]
    sc = {b: carray("d", [0.0]) for b in sig_branches}
    sp = carray("B", [0])
    # only read the branches this group needs (the universe branches are most of
    # the file; full-branch GetEntry made each of 8 group tasks re-read ~all of it)
    t.SetBranchStatus("*", 0)
    for b in sig_branches + ["sim_pass"]:
        t.SetBranchStatus(b, 1)
    for k in flux_idx:
        t.SetBranchStatus(f"w_truth_Flux_{k}", 1)
        t.SetBranchStatus(f"w_reco_Flux_{k}", 1)
    for b in my_bands:
        for j in (0, 1):
            t.SetBranchStatus(f"w_truth_{san(b)}_{j}", 1)
            t.SetBranchStatus(f"w_reco_{san(b)}_{j}", 1)
    for b, a in sc.items():
        t.SetBranchAddress(b, a)
    t.SetBranchAddress("sim_pass", sp)
    # band weight branches this group needs (truth + reco)
    fl_t = {k: carray("d", [0.0]) for k in flux_idx}
    fl_r = {k: carray("d", [0.0]) for k in flux_idx}
    for k in flux_idx:
        t.SetBranchAddress(f"w_truth_Flux_{k}", fl_t[k])
        t.SetBranchAddress(f"w_reco_Flux_{k}", fl_r[k])
    bd_t = {(b, j): carray("d", [0.0]) for b in my_bands for j in (0, 1)}
    bd_r = {(b, j): carray("d", [0.0]) for b in my_bands for j in (0, 1)}
    for b in my_bands:
        for j in (0, 1):
            t.SetBranchAddress(f"w_truth_{san(b)}_{j}", bd_t[(b, j)])
            t.SetBranchAddress(f"w_reco_{san(b)}_{j}", bd_r[(b, j)])

    n = t.GetEntries()
    if args.max_entries:
        n = min(n, args.max_entries)
    # typed arrays (float32 'f' / int8 'b') -- ~8x leaner than python lists, which OOM
    # at 33M events x ~26 ratio components.
    _f = lambda: carray("f")
    keep_pt, keep_pz = _f(), _f()                     # CV truth coords (group 0)
    keep_rpt, keep_rpz = _f(), _f()
    keep_ex = [_f() for _ in extras]
    keep_rex = [_f() for _ in extras]
    keep_pr, keep_ptru = carray("b"), carray("b")
    keep_wt, keep_wr = carray("d"), carray("d")
    fl_rt = {k: _f() for k in flux_idx}; fl_rr = {k: _f() for k in flux_idx}
    bd_rt = {(b, j): _f() for b in my_bands for j in (0, 1)}
    bd_rr = {(b, j): _f() for b in my_bands for j in (0, 1)}
    for i in range(n):
        t.GetEntry(i)
        a_pt, a_pz = float(sc["MC"][0]), float(sc["MC_pz"][0])
        b_pt, b_pz = float(sc["sim"][0]), float(sc["sim_pz"][0])
        passed = sp[0] != 0
        wt = float(sc["w_truth"][0]); wr = float(sc["w_reco"][0])
        if not (math.isfinite(wt) and math.isfinite(wr) and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            continue
        tru_ok = u2d.in_truth_phase_space(a_pt, a_pz, pt_lo, pt_hi, pz_lo, pz_hi)
        rec_ok = (math.isfinite(b_pt) and math.isfinite(b_pz)
                  and pt_lo <= b_pt <= pt_hi and pz_lo <= b_pz <= pz_hi)
        if not (tru_ok or (passed and rec_ok)):
            continue
        wt *= pot_scale; wr *= pot_scale
        # KNOWN_ISSUES #12: on appended truth-only miss rows (sim_pass==0) the
        # per-universe branches of pre-2026-06-10 dumps are uninitialized
        # garbage. Pin the miss-row ratios to 1.0 -- identical to the post-fix
        # event loop, which writes deterministic CV proxies there; the true
        # vertical miss variation enters through the (clean) mc_truth_denom
        # ratios. Signal-loop rows (sim_pass==1) keep their genuine ratios
        # even if the reco fell outside the grid.
        ok = passed and rec_ok
        if args.group == 0:
            keep_pt.append(a_pt if math.isfinite(a_pt) else -9999.0)
            keep_pz.append(a_pz if math.isfinite(a_pz) else -9999.0)
            keep_rpt.append(b_pt if ok else -9999.0)
            keep_rpz.append(b_pz if ok else -9999.0)
            for x, rx, ax in zip(keep_ex, keep_rex, extras):
                x.append(float(sc[ax["truth"]][0]))
                rx.append(float(sc[ax["reco"]][0]) if ok else -9999.0)
            keep_pr.append(ok); keep_ptru.append(tru_ok)
            keep_wt.append(wt); keep_wr.append(wr)
        for k in flux_idx:
            fl_rt[k].append((float(fl_t[k][0]) * pot_scale) / wt if (passed and wt > 0) else 1.0)
            fl_rr[k].append((float(fl_r[k][0]) * pot_scale) / wr if (passed and wr > 0) else 1.0)
        for b in my_bands:
            for j in (0, 1):
                bd_rt[(b, j)].append((float(bd_t[(b, j)][0]) * pot_scale) / wt if (passed and wt > 0) else 1.0)
                bd_rr[(b, j)].append((float(bd_r[(b, j)][0]) * pot_scale) / wr if (passed and wr > 0) else 1.0)
        if i % 500000 == 0:
            print(f"  signal {i}/{n} kept={len(fl_rt[flux_idx[0]]) if flux_idx else len(bd_rt[(my_bands[0],0)]) if my_bands else 0}", flush=True)

    def sv(name, arr, dt=np.float16):
        np.save(os.path.join(args.bankdir, name), np.asarray(arr, dt))
    for k in flux_idx:
        sv(f"sig_flux_t_{k}", fl_rt[k]); sv(f"sig_flux_r_{k}", fl_rr[k])
    for b in my_bands:
        for j in (0, 1):
            sv(f"sig_{b}_t_{j}", bd_rt[(b, j)]); sv(f"sig_{b}_r_{j}", bd_rr[(b, j)])

    # ---- truth_denom tree: same for the completeness denominator (truth only) ----
    td_branches = ["MC", "MC_pz", "w_truth"] + [ax["truth"] for ax in extras]
    dc = {b: carray("d", [0.0]) for b in td_branches}
    td.SetBranchStatus("*", 0)
    for b in td_branches:
        td.SetBranchStatus(b, 1)
    for k in flux_idx:
        td.SetBranchStatus(f"w_truth_Flux_{k}", 1)
    for b in my_bands:
        for j in (0, 1):
            td.SetBranchStatus(f"w_truth_{san(b)}_{j}", 1)
    for b, a in dc.items():
        td.SetBranchAddress(b, a)
    dfl = {k: carray("d", [0.0]) for k in flux_idx}
    for k in flux_idx:
        td.SetBranchAddress(f"w_truth_Flux_{k}", dfl[k])
    dbd = {(b, j): carray("d", [0.0]) for b in my_bands for j in (0, 1)}
    for b in my_bands:
        for j in (0, 1):
            td.SetBranchAddress(f"w_truth_{san(b)}_{j}", dbd[(b, j)])
    nd = td.GetEntries()
    if args.max_entries:
        nd = min(nd, args.max_entries)
    d_pt, d_pz = carray("f"), carray("f")
    d_ex = [carray("f") for _ in extras]
    d_w = carray("d")
    dfl_r = {k: carray("f") for k in flux_idx}
    dbd_r = {(b, j): carray("f") for b in my_bands for j in (0, 1)}
    for i in range(nd):
        td.GetEntry(i)
        pt, pz = float(dc["MC"][0]), float(dc["MC_pz"][0]); w = float(dc["w_truth"][0])
        if not (math.isfinite(pt) and math.isfinite(pz) and math.isfinite(w) and 0 <= w < 1e4):
            continue
        if not u2d.in_truth_phase_space(pt, pz, pt_lo, pt_hi, pz_lo, pz_hi):
            continue
        w *= pot_scale
        if args.group == 0:
            d_pt.append(pt); d_pz.append(pz); d_w.append(w)
            for x, ax in zip(d_ex, extras):
                x.append(float(dc[ax["truth"]][0]))
        for k in flux_idx:
            dfl_r[k].append((float(dfl[k][0]) * pot_scale) / w if w > 0 else 1.0)
        for b in my_bands:
            for j in (0, 1):
                dbd_r[(b, j)].append((float(dbd[(b, j)][0]) * pot_scale) / w if w > 0 else 1.0)
    for k in flux_idx:
        sv(f"td_flux_{k}", dfl_r[k])
    for b in my_bands:
        for j in (0, 1):
            sv(f"td_{b}_{j}", dbd_r[(b, j)])

    if args.group == 0:
        # CV inputs + measured + flux + meta (read measured/bkg via the nd readers)
        edges = [pt_e, pz_e] + [ax["edges"] for ax in extras]
        t_data, t_bkg = f.Get("data"), f.Get("mc_background")
        meas_pt, meas_pz, meas_ex = und.collect_data_nd(t_data, extras, pt_lo, pt_hi, pz_lo, pz_hi)
        bkg_pt, bkg_pz, bkg_ex, bkg_w = und.collect_bkg_nd(t_bkg, extras, pot_scale,
                                                           pt_lo, pt_hi, pz_lo, pz_hi)
        data_nd, _ = und.histnd([meas_pt, meas_pz] + meas_ex, np.ones(meas_pt.size), edges)
        bkg_nd, _ = und.histnd([bkg_pt, bkg_pz] + bkg_ex, bkg_w, edges)
        meas_w = und.build_measured_training_nd([meas_pt, meas_pz] + meas_ex, data_nd, bkg_nd, edges)
        ref_pt = np.asarray(u2d.PT_EDGES, float)
        if args.pt_edges:
            # extended pT binning: bin-centre remap of the (pT-constant) flux,
            # exactly as the nd driver does
            flux_ref, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, u2d.PT_EDGES)
            ctrs = 0.5 * (np.asarray(pt_e[:-1]) + np.asarray(pt_e[1:]))
            ref_i = np.clip(np.digitize(ctrs, ref_pt) - 1, 0, len(flux_ref) - 1)
            flux_bins = flux_ref[ref_i]
        else:
            flux_bins, _ = u2d.load_flux_bins(args.mcfile, args.flux_hist, pt_e)
            ref_i = None
        td_extra_cols = {f"td_{nm}": np.asarray(x)
                         for nm, x in zip(["ea" if a["name"] == "eavail" else a["name"]
                                           for a in extras], d_ex)}
        np.savez(os.path.join(args.bankdir, "cv.npz"),
                 MCgen=np.column_stack([keep_pt, keep_pz] + keep_ex).astype(np.float32),
                 MCreco=np.column_stack([keep_rpt, keep_rpz] + keep_rex).astype(np.float32),
                 measured=np.column_stack([meas_pt, meas_pz] + meas_ex).astype(np.float32),
                 measured_weights=meas_w,
                 pass_reco=np.asarray(keep_pr, bool), pass_truth=np.asarray(keep_ptru, bool),
                 w_truth=np.asarray(keep_wt), w_reco=np.asarray(keep_wr),
                 td_pt=np.asarray(d_pt), td_pz=np.asarray(d_pz),
                 td_w=np.asarray(d_w),
                 flux=np.asarray(flux_bins, float), data_pot=data_pot,
                 n_nucleons=u2d.TRACKER_FIDUCIAL_N_NUCLEONS,
                 **td_extra_cols,
                 **{f"edges_{i}": np.asarray(e, float) for i, e in enumerate(edges)})
        # flux-universe per-pT ratios (for Flux integral re-scaling per throw);
        # built on the frozen flux-histogram edges, then remapped if extended
        fu = ROOT.TFile.Open(args.flux_universe_file)
        hcv, hun = fu.Get("hFluxCV"), fu.Get("hFluxUniv")
        nb_ref = len(ref_pt) - 1
        fr = np.ones((N_FLUX, nb_ref))
        if hcv and hun:
            for b in range(nb_ref):
                cvf = hcv.GetBinContent(b + 1)
                for k in range(N_FLUX):
                    uf = hun.GetBinContent(b + 1, k + 1)
                    if cvf > 0 and uf > 0:
                        fr[k, b] = uf / cvf
        fu.Close()
        if ref_i is not None:
            fr = fr[:, np.clip(ref_i, 0, nb_ref - 1)]
        np.save(os.path.join(args.bankdir, "flux_univ_ratio.npy"), fr)
        print(f"[dump g0] wrote cv.npz ({len(keep_wt)} signal, {len(d_w)} denom) + flux_univ_ratio")
    f.Close()
    print(f"[dump g{args.group}] done", flush=True)


# --------------------------------------------------------------------------- run
def _interp_2univ(theta, r0, r1):
    """Piecewise-linear ratio through (-1->r1, 0->1, +1->r0) for a Gaussian throw theta."""
    out = np.where(theta >= 0, 1.0 + theta * (r0 - 1.0), 1.0 + theta * (1.0 - r1))
    return np.clip(out, 0.0, 50.0)


def do_run(args):
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd, total_xsec
    bd = args.bankdir
    cv = np.load(os.path.join(bd, "cv.npz"))
    edges = [cv["edges_0"], cv["edges_1"], cv["edges_2"]]
    MCgen, MCreco, measured = cv["MCgen"], cv["MCreco"], cv["measured"]
    pass_reco, pass_truth = cv["pass_reco"], cv["pass_truth"]
    w_truth, w_reco = cv["w_truth"], cv["w_reco"]
    td_pt, td_pz, td_ea, td_w = cv["td_pt"], cv["td_pz"], cv["td_ea"], cv["td_w"]
    flux0 = cv["flux"].astype(float)
    fr = np.load(os.path.join(bd, "flux_univ_ratio.npy"))
    n_nucleons, data_pot = float(cv["n_nucleons"]), float(cv["data_pot"])
    bins = [np.asarray(e, float) for e in edges]
    m = pass_truth
    sample_sig = np.column_stack([MCgen[m, a] for a in range(MCgen.shape[1])])
    sample_td = np.column_stack([td_pt, td_pz, td_ea])
    # pt-bin index of each signal/denom truth event (for Flux per-pT ratio)
    pt_e = edges[0]
    sig_ptbin = np.clip(np.digitize(MCgen[m, 0], pt_e) - 1, 0, len(pt_e) - 2)
    td_ptbin = np.clip(np.digitize(td_pt, pt_e) - 1, 0, len(pt_e) - 2)

    def mm(name):
        return np.load(os.path.join(bd, name + ".npy"), mmap_mode="r")

    os.makedirs(os.path.join(bd, "throws"), exist_ok=True)
    for t in range(args.throw_start, args.throw_start + args.throw_count):
        rng = np.random.default_rng(10_000 + t)
        rt = np.ones(len(w_truth)); rr = np.ones(len(w_truth)); rtd = np.ones(len(td_w))
        # Flux: pick one PPFX universe
        k = int(rng.integers(0, N_FLUX))
        rt *= np.asarray(mm(f"sig_flux_t_{k}"), float)
        rr *= np.asarray(mm(f"sig_flux_r_{k}"), float)
        rtd *= np.asarray(mm(f"td_flux_{k}"), float)
        flux_thrown = flux0 * fr[k]
        # 2-universe bands: Gaussian theta each
        for b in TWO_UNIV_BANDS:
            th = rng.standard_normal()
            rt *= _interp_2univ(th, np.asarray(mm(f"sig_{b}_t_0"), float),
                                np.asarray(mm(f"sig_{b}_t_1"), float))
            rr *= _interp_2univ(th, np.asarray(mm(f"sig_{b}_r_0"), float),
                                np.asarray(mm(f"sig_{b}_r_1"), float))
            rtd *= _interp_2univ(th, np.asarray(mm(f"td_{b}_0"), float),
                                 np.asarray(mm(f"td_{b}_1"), float))
        wt = w_truth * rt; wr = w_reco * rr; wtd = td_w * rtd
        # Cap the per-event COMBINED throw weights at the 99.9th pct (isolated to the
        # throw path -- does NOT touch the canonical omnifold_nn_core estimator). A few
        # throws produce an extreme weight tail (product of a Flux universe + 12 band
        # draws) that triggers LightGBM's degenerate-split error
        # (Check failed: best_split_info.right_count > 0). Capping the tail removes it
        # without changing the bulk; the unfold then runs.
        def _cap(w):
            hi = np.percentile(w[w > 0], 99.9) if np.any(w > 0) else 1.0
            return np.minimum(w, hi)
        wt, wr, wtd = _cap(wt), _cap(wr), _cap(wtd)
        try:
            w_pull, w_push = omnifold_loop(
                MCgen, MCreco, measured, pass_reco, pass_truth,
                np.ones(len(measured), bool), args.iters, kind="lgbm",
                MCgen_weights=wt, MCreco_weights=wr, measured_weights=cv["measured_weights"],
                seed=42, verbose=False)
        except Exception as e:
            raise RuntimeError(f"throw {t} unfold failed; refusing a partial ensemble") from e
        unfold_nd, _ = np.histogramdd(sample_sig, bins=bins, weights=w_push * wt[m])
        of_in, _ = np.histogramdd(sample_sig, bins=bins, weights=wt[m])
        denom_nd, _ = np.histogramdd(sample_td, bins=bins, weights=wtd)
        comp = np.zeros_like(of_in); nz = denom_nd > 0; comp[nz] = of_in[nz] / denom_nd[nz]
        xsec, _ = extract_cross_section_nd(unfold_nd, comp, flux_thrown, data_pot, n_nucleons, edges)
        np.save(os.path.join(bd, "throws", f"xsec_throw_{t}.npy"), xsec.ravel(order="C").astype(np.float64))
        print(f"[run] throw {t}: flux_univ={k}  total_xsec={total_xsec(xsec, edges):.4e}", flush=True)


# --------------------------------------------------------------------------- combine
def do_combine(args):
    import glob
    import ROOT
    bd = args.bankdir
    cv = np.load(os.path.join(bd, "cv.npz"))
    paths = sorted(glob.glob(os.path.join(bd, "throws", "xsec_throw_*.npy")))
    if not paths:
        raise SystemExit("[FAIL] no throws found")
    X = np.stack([np.load(p) for p in paths], axis=0)
    # CV xsec (mean of throws is the unified central value; reported = CV>0)
    # reported mask from the frozen CV product for a clean comparison to block sum
    f = ROOT.TFile.Open(args.cv); h = f.Get("hXSec3D")
    nx, ny, nz = h.GetNbinsX(), h.GetNbinsY(), h.GetNbinsZ()
    cvflat = np.array([h.GetBinContent(ix, iy, iz)
                       for ix in range(1, nx + 1) for iy in range(1, ny + 1)
                       for iz in range(1, nz + 1)])
    f.Close()
    rep = cvflat > 0
    Xr = X[:, rep]; cvr = cvflat[rep]
    mean = Xr.mean(axis=0); Z = Xr - mean
    C_uni = (Z.T @ Z) / (Xr.shape[0] - 1)
    print(f"[unified] {Xr.shape[0]} throws, reported bins {int(rep.sum())}")

    # block sum of the SAME vertical bands (Flux + TWO_UNIV_BANDS) from the per-band cov file
    bf = ROOT.TFile.Open(args.blocksum)
    incl = ["Flux"] + TWO_UNIV_BANDS
    C_bs = np.zeros_like(C_uni)
    for b in incl:
        hb = bf.Get(f"hCov_universe3d_{b}")
        if not hb:
            print(f"  [warn] block band {b} missing"); continue
        nb = hb.GetNbinsX()
        C_bs += np.array([[hb.GetBinContent(i + 1, j + 1) for j in range(nb)] for i in range(nb)])
    bf.Close()

    def stt(C):
        return np.sqrt(max(np.trace(C), 0))
    du, db = np.sqrt(np.maximum(np.diag(C_uni), 0)), np.sqrt(np.maximum(np.diag(C_bs), 0))
    with np.errstate(divide="ignore", invalid="ignore"):
        ru = np.where(cvr > 0, du / cvr, 0); rb = np.where(cvr > 0, db / cvr, 0)
    print(f"[unified ] sqrt-trace={stt(C_uni):.3e}  median rel={100*np.median(ru):.3f}%")
    print(f"[block-sum] sqrt-trace={stt(C_bs):.3e}  median rel={100*np.median(rb):.3f}%  "
          f"(SAME vertical bands)")
    print(f"  unified/blocksum sqrt-trace ratio = {stt(C_uni)/stt(C_bs):.3f}")
    # diagonal agreement + leading-eigenmode overlap
    with np.errstate(divide="ignore", invalid="ignore"):
        dr = np.where(db > 0, du / db, np.nan)
    print(f"  per-bin sigma ratio (unified/blocksum): median={np.nanmedian(dr):.3f} "
          f"p16={np.nanpercentile(dr,16):.3f} p84={np.nanpercentile(dr,84):.3f}")
    eu = np.linalg.eigvalsh(0.5 * (C_uni + C_uni.T))[::-1]
    eb = np.linalg.eigvalsh(0.5 * (C_bs + C_bs.T))[::-1]
    print(f"  leading eigenvalues unified: {eu[:4]}")
    print(f"  leading eigenvalues blocksum:{eb[:4]}")
    out = os.path.join(bd, "unified_throw_cov.root")
    rf = ROOT.TFile.Open(out, "RECREATE")
    for nm, C in [("hCov_unified_vertical", C_uni), ("hCov_blocksum_vertical", C_bs)]:
        nn = C.shape[0]; hh = ROOT.TH2D(nm, nm, nn, 0, nn, nn, 0, nn)
        for i in range(nn):
            for j in range(nn):
                hh.SetBinContent(i + 1, j + 1, float(C[i, j]))
        hh.Write()
    rf.Close()
    print(f"[wrote] {out}")
    print("\n  INTERPRETATION: ratio ~1 and per-bin sigma ratio ~1 => the unified throw")
    print("  reproduces the block sum -> the block-sum (uncorrelated, linear) assumption is")
    print("  VALIDATED for the vertical bands. A ratio far from 1 localizes nonlinearity.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--combine", action="store_true")
    ap.add_argument("--omnifile",
                    default=f"{_REPO}/3d-unfolding/runEventLoopOmniFold_MEFHC_3D_universes_full.root")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--flux-universe-file",
                    default=f"{_REPO}/2d-unfolding/baseline_flux/flux_integral_universes_MEFHC.root")
    ap.add_argument("--bankdir", default="bank_uthrow")
    ap.add_argument("--axes", default="eavail",
                    help="csv of EXTRA_AXES names beyond (pt,pz); '' for 2D (FPS)")
    ap.add_argument("--pt-edges", default=None,
                    help="comma-separated pT edge override (FPS extended grid)")
    ap.add_argument("--pz-edges", default=None,
                    help="comma-separated p|| edge override (FPS extended grid)")
    ap.add_argument("--full-phase-space", action="store_true",
                    help="lift the theta_mu truth gate (mirror the nd driver)")
    ap.add_argument("--max-entries", type=int, default=0,
                    help="smoke-test cap on tree entries (0 = all)")
    ap.add_argument("--group", type=int, default=0)
    ap.add_argument("--ngroups", type=int, default=1)
    ap.add_argument("--throw-start", type=int, default=0)
    ap.add_argument("--throw-count", type=int, default=10)
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--cv", default=f"{_REPO}/3d-unfolding/xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--blocksum",
                    default=f"{_REPO}/3d-unfolding/uq_3d/universe_stage2_3d/uq_universe_3d_covariance.root")
    args = ap.parse_args()
    if args.dump:
        do_dump(args)
    elif args.run:
        raise SystemExit("[FAIL] legacy --run is disabled; use unified_throw_cov.py "
                         "for asymmetric fixed-seed throws with strict manifests")
    elif args.combine:
        raise SystemExit("[FAIL] legacy --combine is disabled; use unified_throw_cov.py "
                         "for mean-centered covariance and strict inventory checks")
    else:
        ap.error("pass --dump, --run, or --combine")


if __name__ == "__main__":
    main()
