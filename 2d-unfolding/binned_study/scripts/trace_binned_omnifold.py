#!/usr/bin/env python3
"""
Diagnostic script: trace the binned OmniFold algorithm step by step.
Self-contained — no imports from the main unfolding script.
"""
import sys
import math
from array import array
from pathlib import Path

import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)

# POTs
DATA_POT = 8.9727561e19
MC_POT   = 4.0692592e20


def get_edges(h):
    ax = h.GetXaxis()
    return [ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 1)] + [ax.GetBinUpEdge(ax.GetNbins())]


def make_h(name, edges):
    h = ROOT.TH1D(name, "", len(edges) - 1, array("d", edges))
    h.Sumw2(); h.SetDirectory(0)
    return h


def main():
    omnifile = "Documents/runEventLoopOmniFold.root"
    datafile = "Documents/runEventLoopData.root"

    # Import OmniFold helpers
    repo_root = Path(__file__).resolve().parents[3]
    omni_dir = repo_root / "OmniFold" / "unbinned_unfolding" / "python"
    sys.path.insert(0, str(omni_dir))
    from omnifold import OmniFold_helper_functions
    from sklearn.ensemble import GradientBoostingClassifier

    # Reference binning
    fRef = ROOT.TFile.Open(datafile, "READ")
    hRef = fRef.Get("pTmu_data")
    edges = get_edges(hRef)
    bin_edges = np.array(edges)
    nbins = len(edges) - 1
    print(f"[INFO] {nbins} bins, edges: {[f'{e:.2f}' for e in edges]}")

    # Input
    fIn = ROOT.TFile.Open(omnifile, "READ")
    tSig = fIn.Get("mc_signal_reco")
    tData = fIn.Get("data")
    tBkg = fIn.Get("mc_background")

    data_pot = float(fIn.Get("dataPOTUsed").GetVal())
    mc_pot = float(fIn.Get("mcPOTUsed").GetVal())
    potScale = data_pot / mc_pot
    print(f"[INFO] potScale={potScale:.6g}")

    # Reuse fill functions from the main script (import directly)
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from unfold_ptmu_omnifold_binned import (
        fill_data_reco, fill_bkg_reco, fill_response_and_mc_reco,
        regularize_response, floor_nonpositive_bins,
    )

    hData = make_h("hData", edges)
    hBkg = make_h("hBkg", edges)
    hTruth = make_h("hTruth", edges)
    hSigReco = make_h("hSigReco", edges)
    hRecoTmp = make_h("hRecoTmp", edges)
    hTruthTmp = make_h("hTruthTmp", edges)
    response = ROOT.RooUnfoldResponse(hRecoTmp, hTruthTmp, "resp", "")

    fill_data_reco(tData, hData, verbose=True)
    fill_bkg_reco(tBkg, hBkg, potScale, verbose=True)

    hMeas = make_h("hMeas", edges)
    hMeas.Add(hData)
    hMeas.Add(hBkg, -1.0)
    print(f"[INFO] hData={hData.Integral(1,nbins):.0f}, hBkg={hBkg.Integral(1,nbins):.1f}, hMeas={hMeas.Integral(1,nbins):.1f}")

    pt_lo, pt_hi = edges[0], edges[-1]
    fill_response_and_mc_reco(
        tSig, response, hTruth, hSigReco,
        pt_lo, pt_hi, potScale,
        response_weight_mode="truth",
        use_weights=True,
        verbose=True,
    )
    regularize_response(response, hRecoTmp, hTruthTmp)

    print(f"[INFO] hTruth={hTruth.Integral(1,nbins):.1f}")
    print(f"[INFO] response.Hmeasured={response.Hmeasured().Integral(1,nbins):.1f}")
    print(f"[INFO] response.Htruth={response.Htruth().Integral(1,nbins):.1f}")

    # ---- Per-bin input summary ----
    print(f"\n{'='*70}")
    print(f"INPUT HISTOGRAMS (per-bin)")
    print(f"{'='*70}")
    print(f"{'Bin':>4s} {'Range':>14s} {'Measured':>12s} {'Truth':>12s} {'Meas/Truth':>12s} {'RespMeas':>12s}")
    hRespMeas = response.Hmeasured()
    for ib in range(1, nbins + 1):
        lo = hMeas.GetXaxis().GetBinLowEdge(ib)
        hi = hMeas.GetXaxis().GetBinUpEdge(ib)
        m = hMeas.GetBinContent(ib)
        t = hTruth.GetBinContent(ib)
        rm = hRespMeas.GetBinContent(ib)
        r = m / t if t > 0 else float('inf')
        print(f"{ib:4d} [{lo:5.2f},{hi:5.2f}) {m:12.1f} {t:12.1f} {r:12.4f} {rm:12.1f}")

    # ---- Efficiency ----
    eff_vec = response.Vefficiency()
    print(f"\n{'='*70}")
    print(f"EFFICIENCY per truth bin")
    print(f"{'='*70}")
    for ib in range(nbins):
        lo = hTruth.GetXaxis().GetBinLowEdge(ib + 1)
        hi = hTruth.GetXaxis().GetBinUpEdge(ib + 1)
        print(f"  Bin {ib+1:2d} [{lo:5.2f},{hi:5.2f}): eff={eff_vec[ib]:.6f}, truth={hTruth.GetBinContent(ib+1):.1f}")

    # ---- Convert to pseudo-events ----
    resp_hist = response.Hresponse()
    resp_counts, resp_centers, resp_widths = OmniFold_helper_functions.TH2_to_numpy(resp_hist)
    meas_counts, meas_centers, meas_widths = OmniFold_helper_functions.TH1_to_numpy(hMeas)

    n_resp_total = int(np.sum(resp_counts.flatten()))
    n_meas_total = int(np.sum(meas_counts))

    print(f"\n{'='*70}")
    print(f"PSEUDO-EVENT CONVERSION")
    print(f"{'='*70}")
    print(f"  Response 2D non-zero bins: {np.count_nonzero(resp_counts)}/{resp_counts.size}")
    print(f"  Response sum of content: {np.sum(resp_counts):.4g}")
    print(f"  int(sum) -> MC pseudo-events: {n_resp_total}")
    print(f"  Measured sum of content: {np.sum(meas_counts):.4g}")
    print(f"  int(sum) -> Data pseudo-events: {n_meas_total}")

    # Check fractional content loss
    frac_loss_resp = np.sum(resp_counts) - n_resp_total
    frac_loss_meas = np.sum(meas_counts) - n_meas_total
    print(f"  Fractional truncation loss (response): {frac_loss_resp:.4g}")
    print(f"  Fractional truncation loss (measured): {frac_loss_meas:.4g}")

    # Check per-bin pseudo-event counts
    print(f"\n  Measured per-bin: int(content) -> pseudo-events")
    for ib in range(nbins):
        c = meas_counts[ib]
        print(f"    Bin {ib+1:2d}: content={c:.2f}, int={int(c)}, loss={c-int(c):.4f}")

    MCgen, MCreco, MCgen_w, MCreco_w = OmniFold_helper_functions.prepare_response_data(
        resp_counts.flatten(), resp_centers.flatten(), resp_widths.flatten())
    meas_entries, meas_w = OmniFold_helper_functions.prepare_hist_data(
        meas_counts, meas_centers, meas_widths)

    # Override weights to 1 (use_density=False)
    MCgen_w = np.ones_like(MCgen_w)
    MCreco_w = np.ones_like(MCreco_w)
    meas_w = np.ones_like(meas_w)

    n_mc = len(MCgen)
    n_meas = len(meas_entries)
    print(f"\n  MC pseudo-events: {n_mc}")
    print(f"  Measured pseudo-events: {n_meas}")
    print(f"  Unique MC reco values: {len(np.unique(MCreco.flatten()))}")
    print(f"  Unique MC gen values: {len(np.unique(MCgen.flatten()))}")
    print(f"  Unique meas values: {len(np.unique(meas_entries.flatten()))}")

    # ---- Per-bin pseudo-event counts ----
    print(f"\n  Per-bin pseudo-event counts (reco level):")
    print(f"  {'Bin':>4s} {'Range':>14s} {'MC_reco':>10s} {'Measured':>10s} {'Data/MC':>10s}")
    for ib in range(nbins):
        lo, hi = edges[ib], edges[ib+1]
        center = (lo + hi) / 2.0
        mc_n = np.sum(np.isclose(MCreco.flatten(), center, atol=0.01))
        da_n = np.sum(np.isclose(meas_entries.flatten(), center, atol=0.01))
        r = da_n / mc_n if mc_n > 0 else float('inf')
        print(f"  {ib+1:4d} [{lo:5.2f},{hi:5.2f}) {mc_n:10d} {da_n:10d} {r:10.4f}")

    # ---- STEP 1: Reco-level classifier ----
    print(f"\n{'='*70}")
    print(f"STEP 1: Reco-level classifier (MC vs Data)")
    print(f"{'='*70}")

    weights_push = np.ones(n_mc)
    step1_data = np.concatenate((MCreco.flatten(), meas_entries.flatten())).reshape(-1, 1)
    step1_labels = np.concatenate((np.zeros(n_mc), np.ones(n_meas)))
    step1_weights = np.concatenate((weights_push * MCreco_w.flatten(), np.ones(n_meas) * meas_w.flatten()))

    clf1 = GradientBoostingClassifier()
    print("  Training step 1 classifier...")
    clf1.fit(step1_data, step1_labels, sample_weight=step1_weights)

    mc_proba = clf1.predict_proba(MCreco.reshape(-1, 1))[:, 1]
    p_safe = np.clip(mc_proba, 1e-6, 1 - 1e-6)
    new_weights = p_safe / (1.0 - p_safe)

    print(f"\n  Step 1 per-bin classifier weights (on MC events):")
    print(f"  {'Bin':>4s} {'Range':>14s} {'N_MC':>8s} {'Mean_w':>12s} {'Min_w':>12s} {'Max_w':>12s}")
    for ib in range(nbins):
        lo, hi = edges[ib], edges[ib+1]
        center = (lo + hi) / 2.0
        mask = np.isclose(MCreco.flatten(), center, atol=0.01)
        if np.any(mask):
            w = new_weights[mask]
            print(f"  {ib+1:4d} [{lo:5.2f},{hi:5.2f}) {np.sum(mask):8d} {np.mean(w):12.4g} {np.min(w):12.4g} {np.max(w):12.4g}")

    print(f"\n  Overall: min={np.min(new_weights):.4g}, max={np.max(new_weights):.4g}, "
          f"mean={np.mean(new_weights):.4g}")
    print(f"  Sum of step1 weights on MC: {np.sum(new_weights):.4g} (should be ~{n_meas})")

    weights_pull = weights_push * new_weights

    # ---- STEP 2: Gen-level classifier ----
    print(f"\n{'='*70}")
    print(f"STEP 2: Gen-level classifier (original vs reweighted MC)")
    print(f"{'='*70}")

    step2_data = np.concatenate((MCgen.flatten(), MCgen.flatten())).reshape(-1, 1)
    step2_labels = np.concatenate((np.zeros(n_mc), np.ones(n_mc)))
    step2_weights = np.concatenate((np.ones(n_mc) * MCgen_w.flatten(), weights_pull * MCgen_w.flatten()))

    print("  Training step 2 classifier...")
    clf2 = GradientBoostingClassifier()
    clf2.fit(step2_data, step2_labels, sample_weight=step2_weights)

    gen_proba = clf2.predict_proba(MCgen.reshape(-1, 1))[:, 1]
    p2_safe = np.clip(gen_proba, 1e-6, 1 - 1e-6)
    weights_push_new = p2_safe / (1.0 - p2_safe)

    print(f"\n  Step 2 per-bin classifier weights (push):")
    print(f"  {'Bin':>4s} {'Range':>14s} {'N_MC':>8s} {'Mean_w':>12s} {'Min_w':>12s} {'Max_w':>12s}")
    for ib in range(nbins):
        lo, hi = edges[ib], edges[ib+1]
        center = (lo + hi) / 2.0
        mask = np.isclose(MCgen.flatten(), center, atol=0.01)
        if np.any(mask):
            w = weights_push_new[mask]
            print(f"  {ib+1:4d} [{lo:5.2f},{hi:5.2f}) {np.sum(mask):8d} {np.mean(w):12.4g} {np.min(w):12.4g} {np.max(w):12.4g}")

    print(f"\n  Overall: min={np.min(weights_push_new):.4g}, max={np.max(weights_push_new):.4g}, "
          f"mean={np.mean(weights_push_new):.4g}")

    # ---- Build unfolded histogram ----
    h_raw = ROOT.TH1D("h_raw", "", nbins,
                       resp_hist.GetYaxis().GetBinLowEdge(1),
                       resp_hist.GetYaxis().GetBinLowEdge(nbins) + resp_hist.GetYaxis().GetBinWidth(nbins))
    for w, mc in zip(weights_push_new, MCgen.flatten()):
        h_raw.Fill(mc, w)

    print(f"\n{'='*70}")
    print(f"UNFOLDED (1 iter, before efficiency)")
    print(f"{'='*70}")
    raw_int = h_raw.Integral(1, nbins)
    print(f"  Integral: {raw_int:.4g}")
    print(f"  {'Bin':>4s} {'Range':>14s} {'Raw':>12s}")
    for ib in range(1, nbins + 1):
        lo = h_raw.GetXaxis().GetBinLowEdge(ib)
        hi = h_raw.GetXaxis().GetBinUpEdge(ib)
        print(f"  {ib:4d} [{lo:5.2f},{hi:5.2f}) {h_raw.GetBinContent(ib):12.4g}")

    # ---- Efficiency correction ----
    print(f"\n{'='*70}")
    print(f"EFFICIENCY CORRECTION")
    print(f"{'='*70}")
    corr_int = 0.0
    print(f"  {'Bin':>4s} {'Range':>14s} {'Raw':>12s} {'Eff':>10s} {'Corrected':>12s}")
    for ib in range(nbins):
        raw = h_raw.GetBinContent(ib + 1)
        e = float(eff_vec[ib])
        corrected = raw / e if e > 0 else raw
        lo = h_raw.GetXaxis().GetBinLowEdge(ib + 1)
        hi = h_raw.GetXaxis().GetBinUpEdge(ib + 1)
        corr_int += corrected
        print(f"  {ib+1:4d} [{lo:5.2f},{hi:5.2f}) {raw:12.4g} {e:10.6f} {corrected:12.4g}")

    target_int = hMeas.Integral(1, nbins)
    print(f"\n  Target (measured): {target_int:.4g}")
    print(f"  Unfolded (corrected, 1 iter): {corr_int:.4g}")
    print(f"  Ratio target/unfolded: {target_int/corr_int:.4g}" if corr_int > 0 else "  Unfolded is zero!")


if __name__ == "__main__":
    main()
