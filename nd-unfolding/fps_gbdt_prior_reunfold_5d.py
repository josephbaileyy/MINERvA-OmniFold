#!/usr/bin/env python3
"""5D FPS 3-prior envelope via GBDT re-unfolding + fractional transfer to PET (step 3).

The frozen-reweighter shortcut is invalid (verified: xsec_prior == prior ratio, no data
reconvergence). The model dependence must come from a REAL re-unfolding per prior. PET
re-training x3 is expensive, so -- exactly as for the lateral band and the unified-throw
adopt -- we do the full calculation with the CHEAP engine (LightGBM) and transfer the
per-bin FRACTIONAL model dependence onto the PET headline:

  for P in {MnvTune(rho=1), bareGENIE, NuWro}:  re-unfold GBDT with MCgen prior reweighted
      by rho_P  ->  xsec_gbdt_P  (data reconverges: spread ~0 where data constrains, blooms
      in the extrapolation region)
  ratio_P(bin) = xsec_gbdt_P / xsec_gbdt_tune
  xsec_PET_P   = xsec_PET_headline * ratio_P          (transfer the reconverged prior ratio)
  C_modeldep   = 0.5 * [ outer(d_genie) + outer(d_nuwro) ],  d_P = xsec_PET_P - xsec_PET_headline

Same 65856 grid as the PET headline. Reports two-tier by completeness. Writes the model-
dependence covariance (TH2D) to add to the PET FPS uncertainty budget.

  python fps_gbdt_prior_reunfold_5d.py --iters 5 --seed 1000
"""
import argparse
import json
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _rho_lookup(cols, ratio_npz):
    """cols = (pt,pz,ea,W) arrays; rho = 4D bin lookup; 1 outside the grid."""
    d = np.load(ratio_npz)
    R = d["ratio"]
    e = [d["edges_pt"], d["edges_pz"], d["edges_eav"], d["edges_W"]]
    idx = [np.digitize(c, ed) - 1 for c, ed in zip(cols, e)]
    inb = np.ones(cols[0].shape[0], bool)
    for j, ii in enumerate(idx):
        inb &= (ii >= 0) & (ii < R.shape[j])
    ic = [np.clip(ii, 0, R.shape[j] - 1) for j, ii in enumerate(idx)]
    rho = np.ones(cols[0].shape[0], np.float64)
    vals = R[ic[0], ic[1], ic[2], ic[3]]
    rho[inb] = vals[inb]
    rho[~np.isfinite(rho)] = 1.0
    return rho


def main():
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    from omnifold_nn_core import omnifold_loop
    from xsec_nd import extract_cross_section_nd
    import unfold_2d_omnifold_unbinned as u2d

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gbdt-in", default="of_inputs_5d_fps_full.npz")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_PC_FPS_MEFHC.root",
                    help="FPS omnifile providing the per-event truth denom (mc_truth_denom)")
    ap.add_argument("--pet-pc", default="of_inputs_pc_fps.npz")
    ap.add_argument("--pet-weights", default="products/pet/pet_weights_fps.npz")
    ap.add_argument("--pet-wsource", default="of_inputs_5d_fps.npz")
    ap.add_argument("--nuwro", default="products/5d/fps_prior_nuwro_ratio_5d.npz")
    ap.add_argument("--genie", default="products/5d/fps_prior_genie_ratio_5d.npz")
    ap.add_argument("--mcfile", default=f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated")
    ap.add_argument("--iters", type=int, default=5)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--comp-split", type=float, default=0.5)
    ap.add_argument("--outdir", default="products/pet/fps_envelope_5d")
    ap.add_argument("--full-phase-space", action="store_true",
                    help="lift the theta_mu truth gate for the truth-denom rebuild "
                         "(must match how --gbdt-in/--pet-pc/--pet-wsource were built)")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    if args.full_phase_space:
        import math
        u2d.MAX_MUON_THETA_RAD = math.pi
        print("[INFO] FULL PHASE SPACE: theta_mu truth gate lifted")

    # ---- GBDT FPS inputs (signal + measured) ----
    D = np.load(args.gbdt_in)
    MCgen = D["MCgen"].astype(np.float64); MCreco = D["MCreco"].astype(np.float64)
    measured = D["measured"].astype(np.float64)
    pass_reco = D["pass_reco"].astype(bool); pass_truth = D["pass_truth"].astype(bool)
    w_truth = D["w_truth"].astype(np.float64); w_reco = D["w_reco"].astype(np.float64)
    meas_w = D["measured_weights"].astype(np.float64)
    flux = D["flux"].astype(np.float64); data_pot = float(D["data_pot"])
    n_nucleons = float(D["n_nucleons"])
    edges = [D[f"edges_{i}"].astype(float) for i in range(int(D["nedges"]))]
    shape = tuple(len(e) - 1 for e in edges)
    print(f"[gbdt5d] MCgen{MCgen.shape} measured{measured.shape} grid{shape} "
          f"pass_truth={pass_truth.sum()} pass_reco={pass_reco.sum()}")

    # ---- per-event truth denom (fast RDF), rectangle + theta_mu<20deg gate (matches
    # the dump's denom_nd -- u2d.in_truth_phase_space: atan2(pt,pz) < MAX_MUON_THETA_RAD;
    # this dump was built WITHOUT --full-phase-space, i.e. the gate is ON) ----
    pt_lo, pt_hi = edges[0][0], edges[0][-1]
    pz_lo, pz_hi = edges[1][0], edges[1][-1]
    f = ROOT.TFile.Open(args.omnifile)
    _, _, pot_scale = u2d.get_pot_scales(f); f.Close()
    td = ROOT.RDataFrame("mc_truth_denom", args.omnifile).AsNumpy(
        ["MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W", "w_truth"])
    tdc = [td[b].astype(np.float64) for b in ("MC", "MC_pz", "MC_eavail", "MC_q3", "MC_W")]
    tdw = td["w_truth"].astype(np.float64) * pot_scale
    fin = np.all([np.isfinite(c) for c in tdc], axis=0)
    intheta = np.arctan2(tdc[0], tdc[1]) < u2d.MAX_MUON_THETA_RAD
    inrect = (fin & intheta & (tdc[0] >= pt_lo) & (tdc[0] <= pt_hi)
              & (tdc[1] >= pz_lo) & (tdc[1] <= pz_hi))
    tdc = [c[inrect] for c in tdc]; tdw = tdw[inrect]
    td_sample = np.column_stack(tdc)
    print(f"[gbdt5d] truth-denom kept {inrect.sum()}/{fin.size} (rectangle+theta)")

    # validate the tune denom against the dump's binned denom_nd (rho=1)
    denom_cv, _ = np.histogramdd(td_sample, bins=edges, weights=tdw)
    if "denom_nd" in D.files:
        dn = D["denom_nd"].astype(np.float64)
        rel = np.abs(denom_cv - dn).sum() / max(dn.sum(), 1e-30)
        print(f"[gbdt5d] denom check vs dump denom_nd: rel L1 diff = {rel:.3e}")

    # ---- per-event rho for signal (cols 0,1,2,4) and truth-denom ----
    sig_cols = (MCgen[:, 0], MCgen[:, 1], MCgen[:, 2], MCgen[:, 4])
    td_cols = (tdc[0], tdc[1], tdc[2], tdc[4])
    priors = {
        "tune":  (np.ones(MCgen.shape[0]), np.ones(td_sample.shape[0])),
        "genie": (_rho_lookup(sig_cols, args.genie), _rho_lookup(td_cols, args.genie)),
        "nuwro": (_rho_lookup(sig_cols, args.nuwro), _rho_lookup(td_cols, args.nuwro)),
    }

    def unfold_prior(rho_sig, rho_td):
        wt = w_truth * rho_sig
        wr = w_reco * rho_sig
        _, w_push = omnifold_loop(
            MCgen, MCreco, measured, pass_reco, pass_truth,
            np.ones(len(measured), bool), args.iters, kind="lgbm",
            MCgen_weights=wt, MCreco_weights=wr, measured_weights=meas_w,
            seed=args.seed, verbose=False)
        m = pass_truth
        unf, _ = np.histogramdd(MCgen[m], bins=edges, weights=w_push * wt[m])
        ofin, _ = np.histogramdd(MCgen[m], bins=edges, weights=wt[m])
        den, _ = np.histogramdd(td_sample, bins=edges, weights=tdw * rho_td)
        comp = np.zeros_like(den); nz = den > 0; comp[nz] = ofin[nz] / den[nz]
        xs, _ = extract_cross_section_nd(unf, comp, flux, data_pot, n_nucleons, edges)
        return xs.ravel(order="C"), comp.ravel(order="C")

    xs = {}
    comp_tune = None
    for name, (rs, rt) in priors.items():
        xs[name], c = unfold_prior(rs, rt)
        if name == "tune":
            comp_tune = c
        from xsec_nd import total_xsec
        print(f"[gbdt5d] unfolded {name}: total sigma = "
              f"{total_xsec(xs[name].reshape(tuple(len(e)-1 for e in edges), order='C'), edges):.4e}",
              flush=True)

    # ---- reconstruction-efficiency completeness (for the tier split / profile) ----
    # comp_tune (above) is sample-COVERAGE completeness (signal-tree truth vs the
    # truth-denom tree) -- it is the correct divisor for extract_cross_section_nd but
    # is ~1 by construction once FPS lifts the truth gate consistently, so it cannot
    # distinguish well- from poorly-constrained bins. comp_reco is the actual
    # reconstruction efficiency within the signal sample (pass_truth&pass_reco /
    # pass_truth, CV weights only, prior-independent) -- the FPS_PILOT.md tier
    # definition ("eff >= ~2%" vs "dead cells"). Same computation as
    # PETxsec5D._comp(self.w_truth) on the PET side.
    den_reco, _ = np.histogramdd(MCgen[pass_truth], bins=edges, weights=w_truth[pass_truth])
    num_reco, _ = np.histogramdd(MCgen[pass_truth & pass_reco], bins=edges,
                                 weights=w_truth[pass_truth & pass_reco])
    comp_reco = np.zeros_like(den_reco)
    nzr = den_reco > 0
    comp_reco[nzr] = num_reco[nzr] / den_reco[nzr]
    comp_reco = comp_reco.ravel(order="C")

    # ---- per-bin reconverged prior ratio (GBDT) ----
    tune = xs["tune"]
    ok = (tune > 0) & (xs["genie"] > 0) & (xs["nuwro"] > 0)
    ratio_g = np.ones_like(tune); ratio_n = np.ones_like(tune)
    ratio_g[ok] = xs["genie"][ok] / tune[ok]
    ratio_n[ok] = xs["nuwro"][ok] / tune[ok]

    # ---- PET headline xsec on the same 65856 grid, transfer the ratio ----
    from pet_systematics_5d import PETxsec5D
    pet = PETxsec5D(args.pet_pc, args.pet_weights, args.mcfile, args.flux_hist,
                    args.pet_wsource, None)
    x_pet = pet.xsec(None)
    rep = x_pet > 0
    x_pet_g = x_pet * ratio_g
    x_pet_n = x_pet * ratio_n
    d_g = x_pet_g - x_pet
    d_n = x_pet_n - x_pet
    r = np.where(rep)[0]
    # C = 0.5*(outer(d_g[r],d_g[r]) + outer(d_n[r],d_n[r])) is rank-2 by construction --
    # never materialize the dense n_reported x n_reported matrix (it crossed 1 GB and
    # crashed ROOT's TFile::Close() at the xps2 grid size). sqrt(trace(C)) reduces to a
    # sum of squares; consumers needing the full C rebuild it exactly from d_genie/d_nuwro.
    sqrt_tr_modeldep = float(np.sqrt(0.5 * (np.sum(d_g[r] ** 2) + np.sum(d_n[r] ** 2))))

    # ---- envelope fraction (transferred) + two-tier by RECO-EFFICIENCY completeness ----
    stack = np.stack([x_pet[r], x_pet_g[r], x_pet_n[r]])
    mean = stack.mean(0); half = 0.5 * (stack.max(0) - stack.min(0))
    env = np.where(mean > 0, half / mean, np.nan)
    comp_r = comp_reco[r]

    def tier(name, m):
        d = env[m & np.isfinite(env)]
        if d.size == 0:
            print(f"[gbdt5d] {name:24s} n=0"); return {}
        s = {"n": int(d.size), "median": float(np.median(d)),
             "p90": float(np.percentile(d, 90)), "max": float(d.max())}
        print(f"[gbdt5d] {name:24s} n={s['n']:5d}  spread/mean: median={100*s['median']:.2f}%  "
              f"p90={100*s['p90']:.2f}%  max={100*s['max']:.1f}%")
        return s

    from xsec_nd import total_xsec
    shape = tuple(len(e)-1 for e in edges)
    integ = lambda x: total_xsec(x.reshape(shape, order="C"), edges)
    print(f"[gbdt5d] GBDT totals tune={integ(tune):.4e} genie={integ(xs['genie']):.4e} "
          f"nuwro={integ(xs['nuwro']):.4e}")
    summary = {
        "method": "GBDT 3-prior re-unfold + fractional transfer to PET headline",
        "n_reported": int(rep.sum()), "iters": args.iters, "seed": args.seed,
        "comp_split": args.comp_split,
        "comp_variable": "comp_reco (reconstruction efficiency, pass_truth&pass_reco/pass_truth)",
        "sqrt_trace_C_modeldep": sqrt_tr_modeldep,
        "all": tier("all reported", np.ones(env.size, bool)),
        "measured(comp>=%.2f)" % args.comp_split: tier(f"measured comp>={args.comp_split}",
                                                        comp_r >= args.comp_split),
        "extrapolated(comp<%.2f)" % args.comp_split: tier(f"extrapolated comp<{args.comp_split}",
                                                          comp_r < args.comp_split),
    }
    prof = []
    for lo, hi in [(0.0, 0.1), (0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.01)]:
        m = (comp_r >= lo) & (comp_r < hi) & np.isfinite(env)
        if m.any():
            prof.append({"comp": f"[{lo},{hi})", "n": int(m.sum()),
                         "median_env_pct": float(100 * np.median(env[m]))})
    summary["completeness_profile"] = prof

    # ---- write arrays + summary FIRST (cheap, robust), ROOT artifact LAST (in case it
    # crashes -- ROOT/PyROOT has shown TFile::Close() instability on >1GB single objects;
    # the npz/json must not depend on the ROOT write surviving) ----
    np.savez_compressed(os.path.join(args.outdir, "fps_gbdt_prior_xsec_5d.npz"),
                        x_gbdt_tune=tune, x_gbdt_genie=xs["genie"], x_gbdt_nuwro=xs["nuwro"],
                        x_pet=x_pet, x_pet_genie=x_pet_g, x_pet_nuwro=x_pet_n,
                        comp_tune=comp_tune, comp_reco=comp_reco, rep=rep,
                        env_reported=env, comp_reported=comp_r,
                        d_genie=d_g[r], d_nuwro=d_n[r])
    with open(os.path.join(args.outdir, "fps_gbdt_envelope_5d_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[gbdt5d] wrote {args.outdir}/fps_gbdt_prior_xsec_5d.npz + summary.json "
          f"(sqrt-tr C_modeldep = {sqrt_tr_modeldep:.4e})")

    # C = 0.5*(outer(d_g,d_g) + outer(d_n,d_n)) is rank-2 -- store the two delta
    # vectors as TH1Ds (tiny) instead of ever materializing/writing the dense
    # n_reported x n_reported TH2D (that object crossed 1 GB at the xps2 grid size
    # and corrupted the ROOT file on write).
    nb = r.size
    fo = ROOT.TFile.Open(os.path.join(args.outdir, "fps_modeldep_cov_5d.root"), "RECREATE")
    hg = ROOT.TH1D("hD_genie", "PET FPS genie-tune delta (per reported bin)", nb, 0, nb)
    hn = ROOT.TH1D("hD_nuwro", "PET FPS nuwro-tune delta (per reported bin)", nb, 0, nb)
    for i in range(nb):
        hg.SetBinContent(i + 1, float(d_g[r][i]))
        hn.SetBinContent(i + 1, float(d_n[r][i]))
    hg.Write(); hn.Write()
    ROOT.TParameter("double")("sqrt_tr_modeldep", sqrt_tr_modeldep).Write()
    fo.Close()
    print(f"[gbdt5d] wrote {args.outdir}/fps_modeldep_cov_5d.root (hD_genie/hD_nuwro, "
          f"rank-2 C reconstructible offline)")


if __name__ == "__main__":
    main()
