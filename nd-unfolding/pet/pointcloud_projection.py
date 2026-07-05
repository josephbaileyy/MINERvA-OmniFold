#!/usr/bin/env python3
"""Demonstrate reweight-then-project on the OmniFold/PET truth point cloud.

The truth side of the PET unfold is ALREADY a point cloud (of_inputs_pc.npz
'part_gen', (N,12,5) = E,px,py,pz,pdg of the top-12-by-energy truth FS hadrons,
muon+nu removed; see nd-unfolding/pet/dump_pointcloud_inputs.py). The trained-PET
push weights (products/pet/pet_weights_full.npz 'w_push') give the unfolded truth
spectrum w_truth*w_push on pass_truth events. So ANY truth observable computable
from the cloud can be PROJECTED post-hoc by re-binning -- no re-unfolding.

This script (read-only on existing files; writes new outputs under products/pet/):
  1. computes from the cloud: Eavail (same formula as CVUniverse.h
     GetEAvailableTrue), hadronic-system invariant mass W_had, n_proton, n_pi;
  2. VALIDATES the truncation loss: Eavail_cloud vs the stored MC_eavail
     (truth_scalars[:,2]) -- SAME formula+inputs, so the residual is a clean
     top-12-hadron truncation bound; W_had vs the stored leptonic MC_W (read from
     the row-aligned 5D universes file) -- carries an ADDITIONAL definitional
     offset (experimenter's W is leptonic, single-nucleon-at-rest);
  3. PROJECTS dsigma/dEavail and dsigma/dW_had by binning the push-weighted truth
     events, overlaid against the GBDT 5D product (hXSec_eavail / hXSec_W).
"""
import json
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import unfold_2d_omnifold_unbinned as u2d            # noqa: E402
from xsec_nd import extract_cross_section_nd, project_marginal  # noqa: E402
import unfold_nd_omnifold_unbinned as und            # noqa: E402

# Paths are env-overridable so the same script serves the baseline run and the
# full-cloud re-dump (of_inputs_pc_fullcloud.npz + retrained weights). OMNI must
# be the omnifile the npz was built from (row-aligned for the MC_W assert).
PC = os.environ.get("PCPROJ_PC", f"{_REPO}/nd-unfolding/of_inputs_pc.npz")
WEIGHTS = os.environ.get("PCPROJ_WEIGHTS", f"{_REPO}/nd-unfolding/products/pet/pet_weights_full.npz")
OMNI = os.environ.get("PCPROJ_OMNI", f"{_REPO}/nd-unfolding/runEventLoopOmniFold_5D_MEFHC_universes_full.root")
MCFILE = f"{_REPO}/2d-unfolding/baseline_flux/runEventLoopMC_MEFHC.root"
FLUXH = "pTmu_reweightedflux_integrated"
GBDT5D = f"{_REPO}/nd-unfolding/products/5d/xsec_5d_MEFHC_5iter_lgbm.root"
OUTDIR = os.environ.get("PCPROJ_OUTDIR", f"{_REPO}/nd-unfolding/products/pet")

# GetEAvailableTrue() constants (CVUniverse.h:330-343), MeV
M_PION_EAVAIL = 135.0
M_PROTON_EAVAIL = 938.27
# multiplicity thresholds (CVUniverse.h GetNProtonsTrue / GetNChargedPionsTrue)
M_P = 938.272
M_PI = 139.57
PROTON_KE_THRESH = 110.0


def main():
    print("[load] npz cloud + weights ...", flush=True)
    d = np.load(PC, allow_pickle=True)
    pg = d["part_gen"]                       # (N,12,5) E,px,py,pz,pdg  (MeV)
    N = pg.shape[0]
    truth_sc = d["truth_scalars"].astype(np.float64)   # pt,pz,eavail,q3 (GeV)
    w_truth = d["w_truth"].astype(np.float64)
    pass_truth = d["pass_truth"].astype(bool)
    pass_reco = d["pass_reco"].astype(bool)
    pt = truth_sc[:, 0]
    mc_eavail = truth_sc[:, 2]               # GeV, stored GetEAvailableTrue/1000
    pt_edges = d["edges_0"].astype(float)
    ea_edges = np.asarray(und.EXTRA_AXES["eavail"]["edges"], float)
    w_edges = np.asarray(und.EXTRA_AXES["W"]["edges"], float)
    data_pot = float(d["data_pot"])
    print(f"[load] N={N}  pass_truth={pass_truth.sum()}  "
          f"pass_truth&reco={(pass_truth&pass_reco).sum()}", flush=True)

    w = np.load(WEIGHTS)
    wp = w["w_push"].astype(np.float64)
    if "mc_indices" in w.files and len(wp) != N:
        full = np.zeros(N, float); full[w["mc_indices"]] = wp; wp = full
    assert len(wp) == N, f"w_push len {len(wp)} != N {N}"
    print(f"[load] w_push: N={len(wp)} (model={w['model']})", flush=True)

    # ---- cloud observables (vectorized; float32 views, float64-promoted sums to
    #      keep peak memory modest -- this runs as a batch job, but stay lean) ----
    E = pg[:, :, 0]      # (N,12) float32 strided views (MeV); no full float64 copies
    px = pg[:, :, 1]; py = pg[:, :, 2]; pz = pg[:, :, 3]; pdgf = pg[:, :, 4]
    real = E > 0                             # padding rows are all-zero
    n_had = real.sum(axis=1).astype(np.int64)
    saturated = n_had == pg.shape[1]         # top-12 saturated -> possible truncation

    # hadronic-system invariant mass W_had = sqrt(Esum^2 - |psum|^2)  (MeV->GeV)
    Es = E.sum(axis=1, dtype=np.float64)
    pxs = px.sum(axis=1, dtype=np.float64)
    pys = py.sum(axis=1, dtype=np.float64)
    pzs = pz.sum(axis=1, dtype=np.float64)
    w2 = Es * Es - (pxs * pxs + pys * pys + pzs * pzs)
    W_had = np.sqrt(np.clip(w2, 0, None)) / 1000.0     # GeV
    del Es, pxs, pys, pzs, w2

    # Eavail (same formula as GetEAvailableTrue), MeV -> GeV.  Build the per-particle
    # contribution in float32 (N,12) ~1.6GB, then promote on the reduction.
    is_g = pdgf == 22; is_pic = (pdgf == 211) | (pdgf == -211)
    is_pi0 = pdgf == 111; is_p = pdgf == 2212
    contrib = np.zeros_like(E)               # float32 (N,12)
    np.copyto(contrib, E, where=is_g)
    np.copyto(contrib, E - np.float32(M_PION_EAVAIL), where=is_pic)
    np.copyto(contrib, E, where=is_pi0)
    np.copyto(contrib, E - np.float32(M_PROTON_EAVAIL), where=is_p)
    contrib[~real] = 0.0
    eavail_cloud = contrib.sum(axis=1, dtype=np.float64) / 1000.0   # GeV
    del contrib

    # multiplicities from pdg (thresholded)
    n_proton = (is_p & real & ((E - np.float32(M_P)) > PROTON_KE_THRESH)).sum(axis=1)
    n_pi = (is_pic & real & ((E - np.float32(M_PI)) > 0)).sum(axis=1)
    del is_g, is_pic, is_pi0, is_p, real

    # ---- read stored leptonic MC_W from the row-aligned 5D file + assert ----
    print("[root] reading MC_W, MC from 5D universes file (one column pass) ...", flush=True)
    import ROOT
    f = ROOT.TFile.Open(OMNI, "READ")
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {OMNI}")
    t = f.Get("mc_signal_reco")
    n_tree = t.GetEntries()
    if n_tree != N:
        raise SystemExit(f"[FAIL] tree entries {n_tree} != npz rows {N}")
    cols = ROOT.RDataFrame(t).AsNumpy(["MC", "MC_W"])
    mc_pt = np.asarray(cols["MC"], np.float64)
    mc_W = np.asarray(cols["MC_W"], np.float64)        # GeV, GetTrueExperimentersW/1000
    f.Close()
    # alignment assertion (pet_lateral_band pattern): truth pt column must match
    bad = int((~((mc_pt.astype(np.float32) == truth_sc[:, 0].astype(np.float32))
                 | (np.isnan(mc_pt) & np.isnan(truth_sc[:, 0])))).sum())
    if bad:
        raise SystemExit(f"[FAIL] alignment: MC vs truth_scalars pt mismatch in {bad} rows")
    print(f"[root] ALIGNMENT VERIFIED: all {N} rows, MC==truth_scalars[:,0]", flush=True)

    # ---- which events actually carry a truth cloud? ----
    # The cloud (part_gen) is dumped only in the reco-signal loop
    # (runEventLoopOmniFold.cpp:916); AppendTruthOnlyMisses appends truth-only
    # rows WITHOUT filling part_gen (KNOWN_ISSUES #12), so those rows have an
    # EMPTY cloud (n_had==0) and would pile into bin 0 of any cloud observable.
    has_cloud = n_had > 0
    rep = {}
    rep["event_census"] = dict(
        N=int(N), pass_truth=int(pass_truth.sum()),
        pass_truth_and_reco=int((pass_truth & pass_reco).sum()),
        truth_only_miss=int((pass_truth & ~pass_reco).sum()),
        has_cloud=int(has_cloud.sum()), empty_cloud=int((~has_cloud).sum()))
    print("\n=== EVENT CENSUS (cloud availability) ===")
    for k, v in rep["event_census"].items():
        print(f"  {k:22s} {v:>12d}  ({100*v/N:5.2f}%)")
    # cross-tab: is empty-cloud the same set as truth-only-miss?
    ec = ~has_cloud
    print("  cross-tab empty_cloud vs pass_reco:")
    print(f"    empty & ~reco (miss)   : {int((ec & ~pass_reco).sum()):>12d}")
    print(f"    empty &  reco          : {int((ec &  pass_reco).sum()):>12d}")
    print(f"    cloud &  reco          : {int((has_cloud & pass_reco).sum()):>12d}")
    print(f"    cloud & ~reco (miss)   : {int((has_cloud & ~pass_reco).sum()):>12d}")

    # ================= VALIDATION (cloud-carrying events only) =================
    mt = pass_truth & has_cloud
    rep["n_validation_events"] = int(mt.sum())

    def resid_stats(cloud, stored, mask, tol):
        r = cloud[mask] - stored[mask]
        finite = np.isfinite(r) & np.isfinite(stored[mask])
        r = r[finite]
        return dict(n=int(r.size),
                    median=float(np.median(r)), mean=float(np.mean(r)),
                    q16=float(np.percentile(r, 16)), q84=float(np.percentile(r, 84)),
                    frac_within=float(np.mean(np.abs(r) < tol)),
                    rms=float(np.sqrt(np.mean(r ** 2))))

    # Eavail: same formula+inputs -> residual isolates truncation (always a deficit)
    ea_res = resid_stats(eavail_cloud, mc_eavail, mt, tol=0.010)   # 10 MeV
    rep["eavail_validation"] = ea_res
    print("\n=== VALIDATION: Eavail_cloud vs stored MC_eavail (truncation bound) ===")
    print(f"  pass_truth events: {ea_res['n']}")
    print(f"  residual (GeV) median={ea_res['median']:+.4f}  mean={ea_res['mean']:+.4f}  "
          f"rms={ea_res['rms']:.4f}  [16,84]%=[{ea_res['q16']:+.4f},{ea_res['q84']:+.4f}]")
    print(f"  fraction |resid|<10 MeV: {100*ea_res['frac_within']:.2f}%")
    # bias vs multiplicity / saturation
    ea_r = (eavail_cloud - mc_eavail)
    print("  Eavail deficit vs n_had (median resid, GeV):")
    nh_bias = {}
    for lo, hi, lab in [(1, 4, "1-4"), (5, 8, "5-8"), (9, 11, "9-11"), (12, 12, "12 (sat)")]:
        m = mt & (n_had >= lo) & (n_had <= hi) & np.isfinite(ea_r)
        if m.sum():
            med = float(np.median(ea_r[m]))
            nh_bias[lab] = dict(n=int(m.sum()), median=med)
            print(f"    n_had {lab:9s}: n={int(m.sum()):>9d}  median={med:+.4f}")
    rep["eavail_bias_vs_nhad"] = nh_bias
    rep["frac_saturated"] = float(np.mean(saturated[mt]))
    print(f"  fraction of pass_truth events at n_had=12 (saturated): "
          f"{100*rep['frac_saturated']:.2f}%")

    # W_had vs leptonic MC_W (definitional offset on top of truncation)
    w_res = resid_stats(W_had, mc_W, mt, tol=0.050)
    rep["W_validation"] = w_res
    print("\n=== W_had(cloud, hadronic-system mass) vs stored MC_W (leptonic) ===")
    print(f"  residual (GeV) median={w_res['median']:+.4f}  mean={w_res['mean']:+.4f}  "
          f"rms={w_res['rms']:.4f}  [16,84]%=[{w_res['q16']:+.4f},{w_res['q84']:+.4f}]")
    print("  NOTE: GetTrueExperimentersW (CVUniverse.h:365-379) is leptonic "
          "(Enu,Emu,theta,Q^2; single nucleon at rest) -> differs from the FS-hadron\n"
          "  invariant mass by Fermi motion + multi-baryon rest masses, NOT just truncation.")

    # ================= PROJECTIONS =================
    flux, _ = u2d.load_flux_bins(MCFILE, FLUXH, pt_edges)
    n_nucleons = u2d.TRACKER_FIDUCIAL_N_NUCLEONS

    def project_xsec_1d(obs, obs_edges, base=None):
        """dsigma/dobs from push-weighted truth via a 2D (pt,obs) bin + flux-on-pt
        marginalization (project_marginal drops the pt axis).

        base: truth-event mask to include (default = all pass_truth). Use
        `has_cloud` for cloud-recomputed observables (misses have no cloud)."""
        mtb = pass_truth if base is None else (pass_truth & base)
        mtr = mtb & pass_reco
        ct = np.column_stack([pt[mtb], obs[mtb]])
        ctr = np.column_stack([pt[mtr], obs[mtr]])
        edges2 = [pt_edges, obs_edges]
        counts, _ = np.histogramdd(ct, bins=edges2, weights=(wp * w_truth)[mtb])
        denom, _ = np.histogramdd(ct, bins=edges2, weights=w_truth[mtb])
        ofin, _ = np.histogramdd(ctr, bins=edges2, weights=w_truth[mtr])
        comp = np.zeros_like(denom); nz = denom > 0; comp[nz] = ofin[nz] / denom[nz]
        xs2, _ = extract_cross_section_nd(counts, comp, flux, data_pot,
                                          n_nucleons, edges2, flux_axis=0)
        return project_marginal(xs2, edges2, drop_axes=[0])   # dsigma/dobs

    # cloud observables: restricted to has_cloud (the only events with a cloud)
    dsig_ea_cloud = project_xsec_1d(eavail_cloud, ea_edges, base=has_cloud)
    dsig_W_cloud = project_xsec_1d(W_had, w_edges, base=has_cloud)
    # stored observables on the SAME has_cloud subset (isolate truncation, not the miss gap)
    dsig_ea_stored_hc = project_xsec_1d(mc_eavail, ea_edges, base=has_cloud)
    dsig_W_stored_hc = project_xsec_1d(np.where(np.isfinite(mc_W), mc_W, -1.0), w_edges, base=has_cloud)
    # stored observables on the FULL pass_truth set (the proper unfold; miss rows included)
    dsig_ea_stored = project_xsec_1d(mc_eavail, ea_edges)
    dsig_W_stored = project_xsec_1d(np.where(np.isfinite(mc_W), mc_W, -1.0), w_edges)
    # multiplicity projection (integer axis, pdg-derived; cloud-only -> has_cloud)
    npmax = 6
    np_edges = np.arange(-0.5, npmax + 1.0, 1.0)
    dsig_nproton = project_xsec_1d(n_proton.astype(float).clip(0, npmax), np_edges, base=has_cloud)
    dsig_npi = project_xsec_1d(n_pi.astype(float).clip(0, npmax), np_edges, base=has_cloud)

    # GBDT reference projections
    def read_th1(path, name):
        ff = ROOT.TFile.Open(path)
        h = ff.Get(name)
        vals = np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
        ff.Close()
        return vals
    gbdt_ea = read_th1(GBDT5D, "hXSec_eavail")
    gbdt_W = read_th1(GBDT5D, "hXSec_W")

    rep["projection_eavail"] = dict(edges=ea_edges.tolist(),
                                    pet_cloud_hascloud=dsig_ea_cloud.tolist(),
                                    pet_stored_hascloud=dsig_ea_stored_hc.tolist(),
                                    pet_stored_full=dsig_ea_stored.tolist(),
                                    gbdt=gbdt_ea.tolist())
    rep["projection_W"] = dict(edges=w_edges.tolist(),
                               pet_cloud_hascloud=dsig_W_cloud.tolist(),
                               pet_stored_hascloud=dsig_W_stored_hc.tolist(),
                               pet_stored_full=dsig_W_stored.tolist(),
                               gbdt=gbdt_W.tolist())
    rep["projection_nproton"] = dict(edges=np_edges.tolist(), pet_cloud=dsig_nproton.tolist())
    rep["projection_npi"] = dict(edges=np_edges.tolist(), pet_cloud=dsig_npi.tolist())

    print("\n=== PROJECTED dsigma/dEavail ===")
    print("  bin   PETcloud(hc)  PETstored(hc)  PETstored(full)  GBDT(ref)")
    for i in range(len(dsig_ea_cloud)):
        print(f"  {i}: {dsig_ea_cloud[i]:.3e}  {dsig_ea_stored_hc[i]:.3e}  "
              f"{dsig_ea_stored[i]:.3e}  {gbdt_ea[i]:.3e}")
    print("=== PROJECTED dsigma/dW ===")
    print("  bin   PETcloud Whad(hc)  PETstored MC_W(hc)  PETstored MC_W(full)  GBDT(ref)")
    for i in range(len(dsig_W_cloud)):
        print(f"  {i}: {dsig_W_cloud[i]:.3e}  {dsig_W_stored_hc[i]:.3e}  "
              f"{dsig_W_stored[i]:.3e}  {gbdt_W[i]:.3e}")

    # ================= FIGURES =================
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, _REPO)
    import technote_style as ts   # noqa: F401  (sets rcParams)

    # --- validation figure ---
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    # Eavail residual hist (zoom)
    er = ea_r[mt & np.isfinite(ea_r)]
    ax[0].hist(np.clip(er, -0.3, 0.05), bins=120, color="#4C72B0")
    ax[0].axvline(0, color="k", lw=0.8)
    ax[0].set_xlabel(r"$E_{\rm avail}^{\rm cloud}-E_{\rm avail}^{\rm stored}$ (GeV)")
    ax[0].set_ylabel("pass_truth events")
    ax[0].set_title(f"Eavail: same formula -> truncation only\n"
                    f"median {ea_res['median']:+.4f} GeV, "
                    f"{100*ea_res['frac_within']:.1f}% within 10 MeV", fontsize=9)
    ax[0].set_yscale("log")
    # Eavail deficit vs n_had
    labs = list(nh_bias.keys()); meds = [nh_bias[l]["median"] for l in labs]
    ax[1].bar(range(len(labs)), meds, color="#C44E52")
    ax[1].set_xticks(range(len(labs))); ax[1].set_xticklabels(labs)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xlabel(r"$n_{\rm had}$ stored in cloud")
    ax[1].set_ylabel("median Eavail deficit (GeV)")
    ax[1].set_title("truncation deficit grows with multiplicity\n(saturates at n_had=12)",
                    fontsize=9)
    # MC-only truncation-validation figure (Eavail_cloud vs stored, deficit vs
    # n_had): no sample tag, per the technote_style convention for MC-only plots.
    fig.tight_layout()
    p1 = f"{OUTDIR}/pet_cloud_projection_validation.png"
    fig.savefig(p1, dpi=130); plt.close(fig)
    print(f"\n[fig] {p1}")

    # --- W_had vs MC_W 2D hexbin + projection overlays ---
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
    mm = mt & np.isfinite(mc_W) & np.isfinite(W_had)
    hb = ax[0].hexbin(mc_W[mm], W_had[mm], gridsize=80, bins="log",
                      extent=(0, 4, 0, 4), cmap=ts.SEQ_CMAP)
    ax[0].plot([0, 4], [0, 4], "r--", lw=1)
    ax[0].set_xlabel(r"stored leptonic $W$ (MC_W, GeV)")
    ax[0].set_ylabel(r"cloud hadronic-mass $W_{\rm had}$ (GeV)")
    ax[0].set_title(f"definitional offset (NOT truncation)\nmedian "
                    f"{w_res['median']:+.3f} GeV", fontsize=9)
    fig.colorbar(hb, ax=ax[0], label="events")
    # dsigma/dEavail overlay (validated observable)
    ax[1].step(range(len(dsig_ea_cloud)), dsig_ea_cloud, where="mid", lw=2,
               color=ts.gen_color("data"), label="PET cloud Eavail (has-cloud)")
    ax[1].step(range(len(dsig_ea_stored_hc)), dsig_ea_stored_hc, where="mid",
               color="#dd8452", ls=":", label="PET stored MC_eavail (has-cloud)")
    ax[1].step(range(len(dsig_ea_stored)), dsig_ea_stored, where="mid",
               color="#4C72B0", ls="--", label="PET stored MC_eavail (full unfold)")
    ax[1].step(range(len(gbdt_ea)), gbdt_ea, where="mid",
               color="#2ca02c", ls="-.", label="GBDT 5D (ref)")
    ax[1].set_xlabel(r"$E_{\rm avail}$ bin index"); ax[1].set_ylabel(r"$d\sigma/dE_{\rm avail}$")
    ax[1].set_title("projected dsigma/dEavail: cloud==stored on has-cloud;\n"
                    "gap to full unfold = truth-only-miss rows", fontsize=8)
    ax[1].legend(fontsize=6.5); ax[1].set_yscale("log")
    # dsigma/dW overlay
    ax[2].step(range(len(dsig_W_cloud)), dsig_W_cloud, where="mid", lw=2,
               color=ts.gen_color("data"), label=r"PET cloud $W_{\rm had}$ (has-cloud)")
    ax[2].step(range(len(dsig_W_stored_hc)), dsig_W_stored_hc, where="mid",
               color="#dd8452", ls=":", label="PET stored MC_W (has-cloud)")
    ax[2].step(range(len(dsig_W_stored)), dsig_W_stored, where="mid",
               color="#4C72B0", ls="--", label="PET stored MC_W (full unfold)")
    ax[2].step(range(len(gbdt_W)), gbdt_W, where="mid",
               color="#2ca02c", ls="-.", label="GBDT 5D MC_W (ref)")
    ax[2].set_xlabel(r"$W$ bin index"); ax[2].set_ylabel(r"$d\sigma/dW$")
    ax[2].set_title("projected dsigma/dW: cloud $W_{\\rm had}$ (hadronic mass)\n"
                    "differs from leptonic MC_W by definition", fontsize=8)
    ax[2].legend(fontsize=6.5); ax[2].set_yscale("log")
    # data-bearing panels (projected cross sections): tag the dsigma/dEavail
    # panel, matching pet_vs_gbdt.py.  (ax[0] is an MC-vs-MC hexbin, so the tag
    # goes on ax[1], not the whole figure.)
    ts.minerva_tag(ax[1])
    fig.tight_layout()
    p2 = f"{OUTDIR}/pet_cloud_projection_xsec.png"
    fig.savefig(p2, dpi=130); plt.close(fig)
    print(f"[fig] {p2}")

    # ================= persist =================
    pj = f"{OUTDIR}/pointcloud_projection_summary.json"
    with open(pj, "w") as fh:
        json.dump(rep, fh, indent=2)
    print(f"[json] {pj}")

    # small root with the projected xsecs + per-event cloud obs summary
    fo = ROOT.TFile.Open(f"{OUTDIR}/pointcloud_projection.root", "RECREATE")

    def write_h(name, edges, vals):
        h = ROOT.TH1D(name, name, len(vals), np.asarray(edges, float)
                      if len(edges) == len(vals) + 1 else np.arange(len(vals) + 1.0))
        for i, v in enumerate(vals):
            h.SetBinContent(i + 1, float(v))
        h.Write()
    write_h("dsig_eavail_pet_cloud_hascloud", ea_edges, dsig_ea_cloud)
    write_h("dsig_eavail_pet_stored_hascloud", ea_edges, dsig_ea_stored_hc)
    write_h("dsig_eavail_pet_stored_full", ea_edges, dsig_ea_stored)
    write_h("dsig_eavail_gbdt", ea_edges, gbdt_ea)
    write_h("dsig_W_pet_cloud_hascloud", w_edges, dsig_W_cloud)
    write_h("dsig_W_pet_stored_hascloud", w_edges, dsig_W_stored_hc)
    write_h("dsig_W_pet_stored_full", w_edges, dsig_W_stored)
    write_h("dsig_W_gbdt", w_edges, gbdt_W)
    write_h("dsig_nproton_pet_cloud", np_edges, dsig_nproton)
    write_h("dsig_npi_pet_cloud", np_edges, dsig_npi)
    fo.Close()
    print(f"[root] {OUTDIR}/pointcloud_projection.root")
    print("\n[DONE] pointcloud projection demonstration complete.")


if __name__ == "__main__":
    main()
