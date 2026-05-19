#!/usr/bin/env python3
"""Build 1D ExtractCrossSection inputs from the 2D OmniFold event-loop trees.

Projects the `data`, `mc_signal_reco`, `mc_background`, and `mc_truth_denom`
TTrees in `runEventLoopOmniFold_MEHFC.root` onto the paper's 1D p_T and
p_|| edges and writes MnvH1D / MnvH2D histograms that match
`ExtractCrossSection`'s input contract (`<prefix>_data`,
`<prefix>_migration`, `<prefix>_efficiency_*`, `<prefix>_background_*`,
`<prefix>_reweightedflux_integrated`, `<prefix>_fiducial_nucleons`, plus
`POTUsed`).

Phase-16 fix (2026-05-09): the efficiency denominator is filled from
`mc_truth_denom` (32.85M events, the canonical Truth-tree denominator),
**not** from the `mc_signal_reco` truth-pass subset. Filling from the
subset (24.5M events) drops the input-completeness factor c ≈ 0.745 and
under-corrects the IBU result by the same fraction the 2D OmniFold was
under-corrected pre-Phase-16. The 2D MC-truth yield used to build the
per-p_|| effective flux is also filled from `mc_truth_denom` for the
same reason.

For p_T, the per-bin flux histogram is copied from
`baseline_flux/runEventLoopMC_MEHFC.root:pTmu_reweightedflux_integrated`.
For p_||, no per-bin flux file ships, so each bin is filled via a
truth-yield-weighted harmonic mean of the per-p_T flux (see
`build_pz_flux`). Reading the truth yield from `mc_truth_denom`
preserves Phase-16 correctness.
"""

import argparse
import math
import os
import sys
from array import array

import ROOT


PT_EDGES = [0.0, 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85,
            1.0, 1.25, 1.5, 2.5, 4.5]
PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0,
            10.0, 15.0, 20.0, 40.0, 60.0]

PT_LO, PT_HI = PT_EDGES[0], PT_EDGES[-1]
PZ_LO, PZ_HI = PZ_EDGES[0], PZ_EDGES[-1]

AXES = {
    "pTmu": {"edges": PT_EDGES, "title": "p_{T,#mu} (GeV/c)"},
    "pZmu": {"edges": PZ_EDGES, "title": "p_{||,#mu} (GeV/c)"},
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--omnifile",
                   default="../runEventLoopOmniFold_MEHFC.root")
    p.add_argument("--flux",
                   default="../baseline_flux/runEventLoopMC_MEHFC.root")
    p.add_argument("--xsec-2d",
                   default="../2d_crossSection_omnifold_MEHFC_5iter.root")
    p.add_argument("--out-data", default="runEventLoop_proj_data.root")
    p.add_argument("--out-mc", default="runEventLoop_proj_mc.root")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def make_mnvh1d(name, title, edges):
    e = array("d", edges)
    h = ROOT.PlotUtils.MnvH1D(name, title, len(edges) - 1, e)
    h.SetDirectory(0)
    h.Sumw2()
    return h


def make_mnvh2d(name, title, edges_x, edges_y):
    ex = array("d", edges_x)
    ey = array("d", edges_y)
    h = ROOT.PlotUtils.MnvH2D(name, title,
                              len(edges_x) - 1, ex,
                              len(edges_y) - 1, ey)
    h.SetDirectory(0)
    h.Sumw2()
    return h


def in_phasespace(pt, pz):
    return (math.isfinite(pt) and math.isfinite(pz)
            and PT_LO <= pt <= PT_HI and PZ_LO <= pz <= PZ_HI)


def fill_data(t_data, hists):
    """Fill <prefix>_data MnvH1D histograms from the data tree."""
    measured = array("d", [0.0])
    measured_pz = array("d", [0.0])
    measured_pass = array("B", [0])
    t_data.SetBranchAddress("measured", measured)
    t_data.SetBranchAddress("measured_pz", measured_pz)
    t_data.SetBranchAddress("measured_pass", measured_pass)

    n_in, n_out = 0, 0
    for i in range(t_data.GetEntries()):
        t_data.GetEntry(i)
        if measured_pass[0] == 0:
            n_out += 1
            continue
        pt = float(measured[0])
        pz = float(measured_pz[0])
        if not in_phasespace(pt, pz):
            n_out += 1
            continue
        hists["pTmu"].Fill(pt)
        hists["pZmu"].Fill(pz)
        n_in += 1
    return n_in, n_out


def fill_signal(t_sig, mig, eff_num, fakes_bkg):
    """Fill migration, efficiency numerator (truth-axis) and fakes-as-bkg.

    Conventions matching the 2D path
    (`unfold_2d_omnifold_unbinned.py:240-316,540-560`):
    - reco-pass and truth-pass are derived from `sim_pass` and the truth-
      phase-space mask respectively (truth-pass is *not* a branch).
    - Migration MnvH2D: x = reco, y = truth, weight = w_reco. Fill only
      events that pass both reco-pass + reco-in-PS and truth-in-PS.
    - Efficiency numerator   (truth-axis): truth-in-PS AND reco-pass AND
      reco-in-PS, weight = w_truth.
    - Fakes (reco-pass AND reco-in-PS AND NOT truth-in-PS): added to the
      reco-side background, weight = w_reco. Mirrors `hBkgReco2D` putting
      fake reco yield into the bkg histogram so OmniFold/IBU see fake-free
      signal.

    Phase-16 note: the efficiency *denominator* and the 2D truth yield
    used by the p_|| harmonic-mean flux are filled separately from
    `mc_truth_denom` — see `fill_truth_denom`. Filling them from this
    `mc_signal_reco` loop drops the input-completeness factor and is the
    bug Phase 16 fixed.

    Weights are written un-pot-scaled; ExtractCrossSection applies
    dataPOT/mcPOT to background subtraction internally.
    """
    sim = array("d", [0.0])
    sim_pz = array("d", [0.0])
    sim_pass = array("B", [0])
    mc = array("d", [0.0])
    mc_pz = array("d", [0.0])
    w_reco = array("d", [1.0])
    w_truth = array("d", [1.0])
    t_sig.SetBranchAddress("sim", sim)
    t_sig.SetBranchAddress("sim_pz", sim_pz)
    t_sig.SetBranchAddress("sim_pass", sim_pass)
    t_sig.SetBranchAddress("MC", mc)
    t_sig.SetBranchAddress("MC_pz", mc_pz)
    t_sig.SetBranchAddress("w_reco", w_reco)
    t_sig.SetBranchAddress("w_truth", w_truth)

    n_eff_num, n_fakes, n_skip = 0, 0, 0
    n_total = t_sig.GetEntries()
    progress_step = max(1, n_total // 20)
    for i in range(n_total):
        t_sig.GetEntry(i)
        rp = (sim_pass[0] != 0)
        wt = float(w_truth[0])
        wr = float(w_reco[0])
        if not (math.isfinite(wt) and math.isfinite(wr)
                and 0 <= wt < 1e4 and 0 <= wr < 1e4):
            n_skip += 1
            continue

        tru_pt = float(mc[0])
        tru_pz = float(mc_pz[0])
        rec_pt = float(sim[0])
        rec_pz = float(sim_pz[0])

        truth_ok = in_phasespace(tru_pt, tru_pz)
        reco_ok = in_phasespace(rec_pt, rec_pz)

        if truth_ok:
            if rp and reco_ok:
                eff_num["pTmu"].Fill(tru_pt, wt)
                eff_num["pZmu"].Fill(tru_pz, wt)
                mig["pTmu"].Fill(rec_pt, tru_pt, wr)
                mig["pZmu"].Fill(rec_pz, tru_pz, wr)
                n_eff_num += 1
        elif rp and reco_ok:
            # reco-pass but truth out-of-PS = signal fake
            fakes_bkg["pTmu"].Fill(rec_pt, wr)
            fakes_bkg["pZmu"].Fill(rec_pz, wr)
            n_fakes += 1

        if i % progress_step == 0 and i > 0:
            print(f"  signal {i}/{n_total} "
                  f"(num={n_eff_num}, fakes={n_fakes})",
                  flush=True)
    return n_eff_num, n_fakes, n_skip


def fill_truth_denom(t_truth, eff_den, h2d_truth):
    """Fill efficiency denominator (1D) and 2D truth yield from
    `mc_truth_denom` — the canonical Truth-tree denominator (32.85M).

    Phase-16 fix: pre-Phase-16 these were filled from `mc_signal_reco`
    truth-pass events (24.5M), missing the 8.4M events that have no
    reco-tree entry. That left the IBU cross section low by the same
    input-completeness factor c ≈ 0.745 the 2D OmniFold was under-
    corrected by. Reading from `mc_truth_denom` is the analog of the
    2D fix in `unfold_2d_omnifold_unbinned.py::collect_truth_denom_arrays`.

    Weight = w_truth. No reco branches are read here — `mc_truth_denom`
    is a pure truth tree.
    """
    mc = array("d", [0.0])
    mc_pz = array("d", [0.0])
    w_truth = array("d", [1.0])
    t_truth.SetBranchAddress("MC", mc)
    t_truth.SetBranchAddress("MC_pz", mc_pz)
    t_truth.SetBranchAddress("w_truth", w_truth)

    n_kept, n_skip = 0, 0
    n_total = t_truth.GetEntries()
    progress_step = max(1, n_total // 20)
    for i in range(n_total):
        t_truth.GetEntry(i)
        wt = float(w_truth[0])
        if not (math.isfinite(wt) and 0 <= wt < 1e4):
            n_skip += 1
            continue
        tru_pt = float(mc[0])
        tru_pz = float(mc_pz[0])
        if not in_phasespace(tru_pt, tru_pz):
            n_skip += 1
            continue
        eff_den["pTmu"].Fill(tru_pt, wt)
        eff_den["pZmu"].Fill(tru_pz, wt)
        h2d_truth.Fill(tru_pt, tru_pz, wt)
        n_kept += 1

        if i % progress_step == 0 and i > 0:
            print(f"  truth_denom {i}/{n_total} (kept={n_kept})",
                  flush=True)
    return n_kept, n_skip


def fill_bkg(t_bkg, hists):
    """Fill background reco yields (un-pot-scaled, w_bkg)."""
    sim_b = array("d", [0.0])
    sim_b_pz = array("d", [0.0])
    sim_b_pass = array("B", [0])
    w_bkg = array("d", [1.0])
    t_bkg.SetBranchAddress("sim_background", sim_b)
    t_bkg.SetBranchAddress("sim_background_pz", sim_b_pz)
    t_bkg.SetBranchAddress("sim_background_pass", sim_b_pass)
    t_bkg.SetBranchAddress("w_bkg", w_bkg)

    n_in, n_out = 0, 0
    for i in range(t_bkg.GetEntries()):
        t_bkg.GetEntry(i)
        if sim_b_pass[0] == 0:
            n_out += 1
            continue
        pt = float(sim_b[0])
        pz = float(sim_b_pz[0])
        w = float(w_bkg[0])
        if not (math.isfinite(pt) and math.isfinite(pz)
                and math.isfinite(w) and 0 <= w < 1e6):
            n_out += 1
            continue
        if not in_phasespace(pt, pz):
            n_out += 1
            continue
        hists["pTmu"].Fill(pt, w)
        hists["pZmu"].Fill(pz, w)
        n_in += 1
    return n_in, n_out


def build_pt_flux(flux_path):
    """Copy pTmu_reweightedflux_integrated from baseline flux file as MnvH1D."""
    f = ROOT.TFile.Open(flux_path)
    src = f.Get("pTmu_reweightedflux_integrated")
    if not src:
        raise RuntimeError(
            f"pTmu_reweightedflux_integrated not in {flux_path}")
    nb = src.GetNbinsX()
    edges = [src.GetXaxis().GetBinLowEdge(i + 1) for i in range(nb)]
    edges.append(src.GetXaxis().GetBinUpEdge(nb))
    if [round(e, 4) for e in edges] != [round(e, 4) for e in PT_EDGES]:
        raise RuntimeError(
            f"Flux p_T edges {edges} do not match paper edges {PT_EDGES}")
    h = make_mnvh1d("pTmu_reweightedflux_integrated",
                    "Reweighted flux integrated;p_{T,#mu};Flux (m^{-2}/POT)",
                    PT_EDGES)
    for i in range(nb):
        h.SetBinContent(i + 1, src.GetBinContent(i + 1))
        h.SetBinError(i + 1, src.GetBinError(i + 1))
    f.Close()
    return h


def build_pz_flux(flux_pt_hist, h2d_truth):
    """Per-p_|| effective flux from MC-truth-weighted harmonic mean of
    per-p_T fluxes.

    Per-p_T flux Φ_i is known from the upstream flux file. To compare a
    1D dσ/dp_|| with the 1D projection of the paper 2D xsec, each p_||
    bin needs a flux value Φ_eff_j such that

        dσ/dp_||_j  =  Σ_i d²σ/(dp_T dp_||) · Δp_T_i

    (i.e., the 1D xsec equals the marginal of the 2D xsec). Solving for
    Φ_eff_j gives the harmonic mean of Φ_i weighted by the (pT,p||) yield,

        Φ_eff_j = Σ_i Y(i,j) / Σ_i (Y(i,j) / Φ_i),

    where Y is the 2D yield in the same pT-truth × p||-truth binning.
    Using MC truth (h2d_truth) as the weight ties the cross-check to
    the same MC weighting already in the efficiency correction.
    Replacing Y with the paper 2D xsec would change the ratio at the
    sub-percent level for our purposes; MC weighting keeps the cross-check
    fully self-contained.
    """
    n_pt = h2d_truth.GetNbinsX()
    n_pz = h2d_truth.GetNbinsY()
    if n_pt != len(PT_EDGES) - 1 or n_pz != len(PZ_EDGES) - 1:
        raise RuntimeError(
            f"h2d_truth shape {n_pt}x{n_pz} != "
            f"{len(PT_EDGES)-1}x{len(PZ_EDGES)-1}")
    flux_pt = [flux_pt_hist.GetBinContent(i + 1) for i in range(n_pt)]
    h = make_mnvh1d("pZmu_reweightedflux_integrated",
                    "Reweighted flux integrated (per-p_{||});"
                    "p_{||,#mu};Flux (m^{-2}/POT)",
                    PZ_EDGES)
    for j in range(1, n_pz + 1):
        num = 0.0
        den = 0.0
        for i in range(1, n_pt + 1):
            y = h2d_truth.GetBinContent(i, j)
            phi = flux_pt[i - 1]
            if y <= 0 or phi <= 0:
                continue
            num += y
            den += y / phi
        phi_eff = num / den if den > 0 else 0.0
        h.SetBinContent(j, phi_eff)
        h.SetBinError(j, 0.0)
    return h


def main():
    args = parse_args()
    ROOT.gROOT.SetBatch(True)
    ROOT.gErrorIgnoreLevel = ROOT.kError
    ROOT.gSystem.Load("libMAT")
    ROOT.TH1.AddDirectory(False)

    print(f"[INFO] omnifile = {args.omnifile}")
    print(f"[INFO] flux file = {args.flux}")
    print(f"[INFO] 2D xsec   = {args.xsec_2d}")
    print(f"[INFO] out data  = {args.out_data}")
    print(f"[INFO] out MC    = {args.out_mc}")

    f_om = ROOT.TFile.Open(args.omnifile)
    if not f_om or f_om.IsZombie():
        sys.exit(f"Cannot open {args.omnifile}")
    t_data = f_om.Get("data")
    t_sig = f_om.Get("mc_signal_reco")
    t_bkg = f_om.Get("mc_background")
    t_truth = f_om.Get("mc_truth_denom")
    if not (t_data and t_sig and t_bkg and t_truth):
        sys.exit("Missing one of data / mc_signal_reco / mc_background / "
                 "mc_truth_denom trees")
    data_pot = f_om.Get("dataPOTUsed").GetVal()
    mc_pot = f_om.Get("mcPOTUsed").GetVal()
    print(f"[INFO] dataPOTUsed = {data_pot:.4e}")
    print(f"[INFO] mcPOTUsed   = {mc_pot:.4e}")

    f_x = ROOT.TFile.Open(args.xsec_2d)
    n_nucleons = f_x.Get("nNucleons").GetVal()
    flux_total = f_x.Get("fluxIntegral_m2_per_POT").GetVal()
    print(f"[INFO] nNucleons = {n_nucleons:.4e}")
    print(f"[INFO] fluxIntegral_m2_per_POT = {flux_total:.4e}")
    f_x.Close()

    h_data = {ax: make_mnvh1d(f"{ax}_data", f"data;{AXES[ax]['title']};events",
                              AXES[ax]["edges"]) for ax in AXES}
    h_eff_num = {ax: make_mnvh1d(f"{ax}_efficiency_numerator",
                                 f"eff num;{AXES[ax]['title']};",
                                 AXES[ax]["edges"]) for ax in AXES}
    h_eff_den = {ax: make_mnvh1d(f"{ax}_efficiency_denominator",
                                 f"eff den;{AXES[ax]['title']};",
                                 AXES[ax]["edges"]) for ax in AXES}
    h_bkg = {ax: make_mnvh1d(f"{ax}_background_omnifoldtrees",
                             f"bkg+fakes;{AXES[ax]['title']};",
                             AXES[ax]["edges"]) for ax in AXES}
    h_mig = {ax: make_mnvh2d(f"{ax}_migration",
                             f"migration;{AXES[ax]['title']} reco;"
                             f"{AXES[ax]['title']} truth",
                             AXES[ax]["edges"], AXES[ax]["edges"])
             for ax in AXES}
    h2d_truth = make_mnvh2d("h2d_truth_yield",
                            "MC truth yield;p_{T,#mu};p_{||,#mu}",
                            PT_EDGES, PZ_EDGES)

    print("[INFO] filling data ...")
    n_in, n_out = fill_data(t_data, h_data)
    print(f"  data: kept={n_in}, dropped={n_out}")

    print("[INFO] filling mc_signal_reco (eff_num + migration + fakes)...")
    n_num, n_fake, n_skip = fill_signal(t_sig, h_mig, h_eff_num, h_bkg)
    print(f"  signal: eff_num={n_num}, fakes={n_fake}, skipped={n_skip}")

    print("[INFO] filling mc_truth_denom (eff_den + 2D truth yield) ...")
    nt_kept, nt_skip = fill_truth_denom(t_truth, h_eff_den, h2d_truth)
    print(f"  truth_denom: kept={nt_kept}, skipped={nt_skip}")

    print("[INFO] filling mc_background ...")
    nb_in, nb_out = fill_bkg(t_bkg, h_bkg)
    print(f"  bkg: kept={nb_in}, dropped={nb_out}")

    f_om.Close()

    print("[INFO] building flux histograms ...")
    flux_pt = build_pt_flux(args.flux)
    flux_pz = build_pz_flux(flux_pt, h2d_truth)

    print("[INFO] writing data file: " + args.out_data)
    fout_data = ROOT.TFile.Open(args.out_data, "RECREATE")
    fout_data.cd()
    for ax in AXES:
        h_data[ax].Write()
    ROOT.TParameter("double")("POTUsed", data_pot).Write()
    fout_data.Close()

    print("[INFO] writing MC file: " + args.out_mc)
    fout_mc = ROOT.TFile.Open(args.out_mc, "RECREATE")
    fout_mc.cd()
    for ax in AXES:
        h_eff_num[ax].Write()
        h_eff_den[ax].Write()
        h_bkg[ax].Write()
        h_mig[ax].Write()
    flux_pt.Write()
    flux_pz.Write()
    ROOT.TParameter("double")("POTUsed", mc_pot).Write()
    ROOT.TParameter("double")("pTmu_fiducial_nucleons", n_nucleons).Write()
    ROOT.TParameter("double")("pZmu_fiducial_nucleons", n_nucleons).Write()
    fout_mc.Close()

    print()
    print("[SUMMARY]")
    print(f"  pTmu_data           integral: {h_data['pTmu'].Integral():.4e}")
    print(f"  pZmu_data           integral: {h_data['pZmu'].Integral():.4e}")
    print(f"  pTmu_efficiency_num integral: {h_eff_num['pTmu'].Integral():.4e}")
    print(f"  pTmu_efficiency_den integral: {h_eff_den['pTmu'].Integral():.4e}")
    print(f"  pTmu_bkg+fakes      integral: {h_bkg['pTmu'].Integral():.4e}")
    print(f"  pZmu_bkg+fakes      integral: {h_bkg['pZmu'].Integral():.4e}")
    print(f"  pTmu_migration      integral: {h_mig['pTmu'].Integral():.4e}")
    print(f"  pTmu_flux           integral: {flux_pt.Integral():.4e}")
    print(f"  pZmu_flux           integral: {flux_pz.Integral():.4e}")


if __name__ == "__main__":
    main()
