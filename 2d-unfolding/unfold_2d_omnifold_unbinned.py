#!/usr/bin/env python3
"""
2D unbinned OmniFold unfolding for MINERvA CC inclusive cross section.

Unfolds the double-differential cross section d^2 sigma / (dp_T dp_||) in
muon transverse momentum (p_T) and longitudinal momentum (p_||), reproducing
arXiv:2106.16210 with OmniFold instead of D'Agostini (IBU).

Reads unbinned TTrees from runEventLoopOmniFold (with p_T and p_|| branches),
runs 2D OmniFold via the RooUnfoldOmnifold C++ wrapper, and extracts the
double-differential cross section.

Created: 2026-04-17
"""

import argparse
import math
from array import array

import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)


# ---------------------------------------------------------------------------
# Paper binning (arXiv:2106.16210, Phys. Rev. D 106, 032001)
# ---------------------------------------------------------------------------
PT_EDGES = [0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
            0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50]  # GeV/c, 14 bins

PZ_EDGES = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
            6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0]  # GeV/c, 16 bins

TRACKER_MIN_Z_MM = 5980.0
TRACKER_MAX_Z_MM = 8422.0
TRACKER_APOTHEM_MM = 850.0
# From PlotUtils::TargetUtils::GetTrackerNNucleons(minZ=5980 mm, maxZ=8422 mm,
# isMC=true, apothem=850 mm). Keep this local so the 2D workflow is not
# sensitive to hadd summing a per-playlist TParameter<double>.
TRACKER_FIDUCIAL_N_NUCLEONS = 3.2352943296224835e30


# ---------------------------------------------------------------------------
# Utility helpers (shared with 1D script)
# ---------------------------------------------------------------------------
def make_th2d(name, title, xedges, yedges):
    h = ROOT.TH2D(name, title,
                   len(xedges) - 1, array("d", xedges),
                   len(yedges) - 1, array("d", yedges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def make_th1d(name, title, edges):
    h = ROOT.TH1D(name, title, len(edges) - 1, array("d", edges))
    h.Sumw2()
    h.SetDirectory(0)
    return h


def make_flux_hist(name, edges, vals):
    h = make_th1d(name,
                  "Flux integral per p_{T} bin;"
                  "p_{T} (GeV/c);Flux (m^{-2}/POT)",
                  edges)
    for i, x in enumerate(vals, start=1):
        h.SetBinContent(i, float(x))
    return h


def np_to_tvector(mask):
    v = ROOT.TVector(len(mask))
    for i, x in enumerate(mask):
        v[i] = 1.0 if bool(x) else 0.0
    return v


def np_to_tvectord(vals):
    v = ROOT.TVectorD(len(vals))
    for i, x in enumerate(vals):
        v[i] = float(x)
    return v


def tvectord_to_np(v):
    return np.asarray([float(v[i]) for i in range(v.GetNoElements())], dtype=float)


def get_pot_scales(f_in):
    data_par = f_in.Get("dataPOTUsed")
    mc_par = f_in.Get("mcPOTUsed")
    if not data_par or not mc_par:
        raise RuntimeError("Missing POT metadata in input file")
    data_pot = float(data_par.GetVal())
    mc_pot = float(mc_par.GetVal())
    if not (math.isfinite(data_pot) and math.isfinite(mc_pot) and mc_pot > 0):
        raise RuntimeError(f"Invalid POT: data={data_pot}, mc={mc_pot}")
    return data_pot, mc_pot, data_pot / mc_pot


def load_flux_bins(mc_path, hist_name, pt_edges):
    f_mc = ROOT.TFile.Open(mc_path, "READ")
    if not f_mc or f_mc.IsZombie():
        raise RuntimeError(f"Could not open {mc_path} (needed for flux histogram)")
    h_flux = f_mc.Get(hist_name)
    if not h_flux:
        raise RuntimeError(f"Missing {hist_name} in {mc_path}")
    if h_flux.GetNbinsX() != len(pt_edges) - 1:
        raise RuntimeError(
            f"Flux histogram has {h_flux.GetNbinsX()} bins but pt_edges expects "
            f"{len(pt_edges) - 1}")

    flux_bins = np.asarray(
        [h_flux.GetBinContent(i) for i in range(1, h_flux.GetNbinsX() + 1)],
        dtype=float)
    f_mc.Close()
    return flux_bins, make_flux_hist("hFlux_pt", pt_edges, flux_bins)


def count_negative_bins_2d(h):
    nneg = 0
    for ix in range(1, h.GetNbinsX() + 1):
        for iy in range(1, h.GetNbinsY() + 1):
            if h.GetBinContent(ix, iy) < 0:
                nneg += 1
    return nneg


# ---------------------------------------------------------------------------
# TTree readers — 2D versions
# ---------------------------------------------------------------------------
def fill_data_reco_2d(t_data, h_data_2d, pt_lo, pt_hi, pz_lo, pz_hi,
                      guard_max=1e3, verbose=False):
    """Read selected data events, return (pt_arr, pz_arr) and fill h_data_2d."""
    measured = array("d", [0.0])
    measured_pz = array("d", [0.0])
    measured_pass = array("B", [0])
    t_data.SetBranchAddress("measured", measured)
    t_data.SetBranchAddress("measured_pz", measured_pz)
    t_data.SetBranchAddress("measured_pass", measured_pass)

    pts, pzs = [], []
    n_skip = 0
    for i in range(t_data.GetEntries()):
        t_data.GetEntry(i)
        if measured_pass[0] == 0:
            n_skip += 1
            continue
        pt = float(measured[0])
        pz = float(measured_pz[0])
        if not (math.isfinite(pt) and math.isfinite(pz)):
            n_skip += 1
            continue
        if abs(pt) > guard_max or abs(pz) > guard_max:
            n_skip += 1
            continue
        if not (pt_lo <= pt <= pt_hi and pz_lo <= pz <= pz_hi):
            n_skip += 1
            continue
        pts.append(pt)
        pzs.append(pz)
        h_data_2d.Fill(pt, pz)

    if verbose:
        print(f"[INFO] data: kept={len(pts)}, skipped={n_skip}")
    return np.asarray(pts, dtype=float), np.asarray(pzs, dtype=float)


def fill_bkg_reco_2d(t_bkg, h_bkg_2d, pot_scale, guard_max=1e3, verbose=False):
    """Fill background TH2D with POT-scaled MC background events."""
    sim_bkg = array("d", [0.0])
    sim_bkg_pz = array("d", [0.0])
    sim_bkg_pass = array("B", [0])
    w_bkg = array("d", [1.0])
    t_bkg.SetBranchAddress("sim_background", sim_bkg)
    t_bkg.SetBranchAddress("sim_background_pz", sim_bkg_pz)
    t_bkg.SetBranchAddress("sim_background_pass", sim_bkg_pass)
    t_bkg.SetBranchAddress("w_bkg", w_bkg)

    n_filled, n_skip = 0, 0
    for i in range(t_bkg.GetEntries()):
        t_bkg.GetEntry(i)
        if sim_bkg_pass[0] == 0:
            n_skip += 1
            continue
        pt = float(sim_bkg[0])
        pz = float(sim_bkg_pz[0])
        w = float(w_bkg[0])
        if not (math.isfinite(pt) and math.isfinite(pz) and
                math.isfinite(w) and 0 <= w < 1e6):
            n_skip += 1
            continue
        h_bkg_2d.Fill(pt, pz, w * pot_scale)
        n_filled += 1

    if verbose:
        print(f"[INFO] bkg: filled={n_filled}, skipped={n_skip}")


def build_measured_training_2d(meas_pt, meas_pz, h_data_2d, h_bkg_2d, verbose=False):
    """Build a non-negative measured training target and per-event weights.

    OmniFold's measured-side interface accepts per-event sample weights but not
    negative weights. We therefore keep the raw `data - bkg` histogram for
    diagnostics and construct a separate training target that floors any
    negative reco-space bins to zero.
    """
    if meas_pt.shape != meas_pz.shape:
        raise RuntimeError("Measured p_T and p_|| arrays have mismatched shapes")

    h_train_2d = h_data_2d.Clone("hMeasTrain2D")
    h_train_2d.SetTitle("Measured (training, floored);p_{T} (GeV/c);p_{||} (GeV/c)")
    h_train_2d.Reset("ICES")

    xaxis = h_data_2d.GetXaxis()
    yaxis = h_data_2d.GetYaxis()
    weights = np.zeros(meas_pt.shape[0], dtype=float)
    n_zero = 0

    for i, (pt, pz) in enumerate(zip(meas_pt, meas_pz)):
        ix = xaxis.FindFixBin(float(pt))
        iy = yaxis.FindFixBin(float(pz))
        data_bin = h_data_2d.GetBinContent(ix, iy)
        if data_bin <= 0.0:
            n_zero += 1
            continue
        target_bin = max(0.0, data_bin - h_bkg_2d.GetBinContent(ix, iy))
        weight = target_bin / data_bin
        weights[i] = weight
        h_train_2d.Fill(float(pt), float(pz), weight)
        if weight <= 0.0:
            n_zero += 1

    if verbose:
        print(f"[INFO] measured training: effective sum={weights.sum():.6g}, "
              f"zero-weight events={n_zero}/{weights.size}")
    return weights, h_train_2d


def collect_signal_arrays_2d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi,
                              pot_scale, use_weights=False, verbose=False):
    """Read mc_signal_reco TTree, return dict of 2D arrays for OmniFold."""
    mc_pt = array("d", [0.0])
    mc_pz = array("d", [0.0])
    sim_pt = array("d", [0.0])
    sim_pz_arr = array("d", [0.0])
    sim_pass = array("B", [0])
    t_sig.SetBranchAddress("MC", mc_pt)
    t_sig.SetBranchAddress("MC_pz", mc_pz)
    t_sig.SetBranchAddress("sim", sim_pt)
    t_sig.SetBranchAddress("sim_pz", sim_pz_arr)
    t_sig.SetBranchAddress("sim_pass", sim_pass)

    wt_arr = array("d", [1.0])
    wr_arr = array("d", [1.0])
    if use_weights:
        t_sig.SetBranchAddress("w_truth", wt_arr)
        t_sig.SetBranchAddress("w_reco", wr_arr)

    truth_pt_list, truth_pz_list = [], []
    reco_pt_list, reco_pz_list = [], []
    pass_reco_list, pass_truth_list = [], []
    w_truth_list, w_reco_list = [], []
    dropped, bad_w = 0, 0

    for i in range(t_sig.GetEntries()):
        t_sig.GetEntry(i)
        tru_pt = float(mc_pt[0])
        tru_pz = float(mc_pz[0])
        rec_pt = float(sim_pt[0])
        rec_pz = float(sim_pz_arr[0])
        passed = sim_pass[0] != 0

        wt = float(wt_arr[0]) if use_weights else 1.0
        wr = float(wr_arr[0]) if use_weights else wt
        if not (math.isfinite(wt) and math.isfinite(wr) and
                0 <= wt < 1e4 and 0 <= wr < 1e4):
            bad_w += 1
            continue
        wt *= pot_scale
        wr *= pot_scale

        # Check if truth is in the 2D phase space
        tru_ok = (math.isfinite(tru_pt) and math.isfinite(tru_pz) and
                  pt_lo <= tru_pt <= pt_hi and pz_lo <= tru_pz <= pz_hi)
        # Check if reco is in the 2D binning range
        rec_ok = (math.isfinite(rec_pt) and math.isfinite(rec_pz) and
                  pt_lo <= rec_pt <= pt_hi and pz_lo <= rec_pz <= pz_hi)

        if not (tru_ok or (passed and rec_ok)):
            dropped += 1
            continue

        truth_pt_list.append(tru_pt if math.isfinite(tru_pt) else -9999.0)
        truth_pz_list.append(tru_pz if math.isfinite(tru_pz) else -9999.0)
        reco_pt_list.append(rec_pt if (passed and rec_ok) else -9999.0)
        reco_pz_list.append(rec_pz if (passed and rec_ok) else -9999.0)
        pass_reco_list.append(passed and rec_ok)
        pass_truth_list.append(tru_ok)
        w_truth_list.append(wt)
        w_reco_list.append(wr)

    if verbose:
        print(f"[INFO] signal: kept={len(truth_pt_list)}, dropped={dropped}, bad_w={bad_w}")

    return {
        "truth_pt": np.asarray(truth_pt_list, dtype=float),
        "truth_pz": np.asarray(truth_pz_list, dtype=float),
        "reco_pt": np.asarray(reco_pt_list, dtype=float),
        "reco_pz": np.asarray(reco_pz_list, dtype=float),
        "pass_reco": np.asarray(pass_reco_list, dtype=bool),
        "pass_truth": np.asarray(pass_truth_list, dtype=bool),
        "w_truth": np.asarray(w_truth_list, dtype=float),
        "w_reco": np.asarray(w_reco_list, dtype=float),
    }


# ---------------------------------------------------------------------------
# Cross-section calculation
# ---------------------------------------------------------------------------
def compute_efficiency_2d(sig, pt_edges, pz_edges):
    """Compute 2D efficiency from signal MC arrays (original MC weights)."""
    hNum = make_th2d("hEffNum", "eff numerator", pt_edges, pz_edges)
    hDen = make_th2d("hEffDen", "eff denominator", pt_edges, pz_edges)

    for pt, pz, pr, ptru, wt, wr in zip(
            sig["truth_pt"], sig["truth_pz"],
            sig["pass_reco"], sig["pass_truth"],
            sig["w_truth"], sig["w_reco"]):
        if ptru:
            hDen.Fill(pt, pz, wt)
            if pr:
                hNum.Fill(pt, pz, wr)

    hEff = hNum.Clone("hEff2D")
    hEff.SetTitle("Selection efficiency;p_{T} (GeV/c);p_{||} (GeV/c)")
    hEff.Divide(hDen)
    # NB: empty-denominator bins stay at 0. The cross-section extraction
    # treats eff<=0 as undefined and sets the bin xsec to 0. Flooring to
    # 1e-12 here would blow up any OmniFold weight that leaks into an
    # empty-truth bin (observed for p_T bin 14, p_|| bin 5: U=0.29 but
    # zero truth denominator floored the eff to 1e-12, inflating xsec
    # by 12 orders of magnitude).
    return hEff, hNum, hDen


def extract_cross_section_2d(hUnfold, hEff, flux_bins, data_pot,
                              n_nucleons, pt_edges, pz_edges):
    """Convert unfolded event counts to d^2 sigma / (dp_T dp_||).

    OmniFold returns a truth-side *reweighting ratio* (`weights_push` in the
    helper), not a standalone truth-yield weight. `hUnfold2D` is therefore
    built from `step2_weights * truth_w_in` and already carries the acceptance
    correction through the step-1 miss regression plus the truth-mask-restricted
    step-2 update. Keep `hEff2D` for diagnostics only; do not divide by it
    again here.

    Mirrors the normalization stage of ExtractCrossSection.cpp once the
    efficiency correction has already been applied:
        Divide(eff-corrected, fluxIntegral)  # per p_T bin, flux in m^-2/POT
        Scale(1/(nNucleons * POT))
        Scale(1e4)                           # m^-2 -> cm^-2
        Scale(1, "width")                    # / bin width

    `flux_bins` is a numpy array of length nPtBins giving the flux (m^-2/POT)
    in each p_T bin (neutrino flux is independent of p_||, so the same flux
    value broadcasts across all p_|| rows within a given p_T column).
    """
    del hEff  # Retained in the function signature for script compatibility.
    hXSec = hUnfold.Clone("hXSec2D")
    hXSec.SetTitle("d^{2}#sigma/(dp_{T}dp_{||});p_{T} (GeV/c);p_{||} (GeV/c)")
    hXSec.Reset("ICES")

    nx = hUnfold.GetNbinsX()
    if flux_bins.shape[0] != nx:
        raise RuntimeError(
            f"flux_bins length ({flux_bins.shape[0]}) != hUnfold nBinsX ({nx})")

    for ix in range(1, nx + 1):
        dpt = hUnfold.GetXaxis().GetBinWidth(ix)
        flux_i = float(flux_bins[ix - 1])  # m^-2/POT
        for iy in range(1, hUnfold.GetNbinsY() + 1):
            dpz = hUnfold.GetYaxis().GetBinWidth(iy)
            u = hUnfold.GetBinContent(ix, iy)
            if flux_i > 0 and n_nucleons > 0 and data_pot > 0:
                denom = flux_i * n_nucleons * data_pot * dpt * dpz
                xsec = (u / denom) * 1.0e4  # m^2 -> cm^2
                u_err = hUnfold.GetBinError(ix, iy)
                xerr = (u_err / denom) * 1.0e4
            else:
                xsec = 0.0
                xerr = 0.0
            hXSec.SetBinContent(ix, iy, xsec)
            hXSec.SetBinError(ix, iy, xerr)

    return hXSec


def project_xsec_1d(hXSec2D, axis, pt_edges, pz_edges):
    """
    Project 2D cross section onto one axis by summing over the other.

    d sigma / dp_T = sum_j [ d^2 sigma/(dp_T dp_||) * Delta_pz(j) ]
    d sigma / dp_|| = sum_i [ d^2 sigma/(dp_T dp_||) * Delta_pT(i) ]
    """
    if axis == "pt":
        h1d = make_th1d("hXSec_pt",
                         "d#sigma/dp_{T};p_{T} (GeV/c);d#sigma/dp_{T} (cm^{2}/GeV/nucleon)",
                         pt_edges)
        for ix in range(1, hXSec2D.GetNbinsX() + 1):
            val, err2 = 0.0, 0.0
            for iy in range(1, hXSec2D.GetNbinsY() + 1):
                dpz = hXSec2D.GetYaxis().GetBinWidth(iy)
                val += hXSec2D.GetBinContent(ix, iy) * dpz
                err2 += (hXSec2D.GetBinError(ix, iy) * dpz) ** 2
            h1d.SetBinContent(ix, val)
            h1d.SetBinError(ix, math.sqrt(err2))
        return h1d
    elif axis == "pz":
        h1d = make_th1d("hXSec_pz",
                         "d#sigma/dp_{||};p_{||} (GeV/c);d#sigma/dp_{||} (cm^{2}/GeV/nucleon)",
                         pz_edges)
        for iy in range(1, hXSec2D.GetNbinsY() + 1):
            val, err2 = 0.0, 0.0
            for ix in range(1, hXSec2D.GetNbinsX() + 1):
                dpt = hXSec2D.GetXaxis().GetBinWidth(ix)
                val += hXSec2D.GetBinContent(ix, iy) * dpt
                err2 += (hXSec2D.GetBinError(ix, iy) * dpt) ** 2
            h1d.SetBinContent(iy, val)
            h1d.SetBinError(iy, math.sqrt(err2))
        return h1d
    else:
        raise ValueError(f"Unknown axis: {axis}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="2D unbinned OmniFold unfolding for MINERvA CC inclusive (p_T, p_||).")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold.root",
                     help="Input ROOT file with unbinned TTrees (from runEventLoopOmniFold)")
    ap.add_argument("--iters", type=int, default=5,
                     help="Number of OmniFold iterations")
    ap.add_argument("--use-weights", action="store_true",
                     help="Use MC event weights (w_truth, w_reco) in OmniFold training")
    ap.add_argument("--out", default="2d_crossSection_omnifold.root",
                     help="Output ROOT file")
    ap.add_argument("--mcfile", default="runEventLoopMC.root",
                     help="ROOT file containing the flux histogram used for normalization")
    ap.add_argument("--flux-hist", default="pTmu_reweightedflux_integrated",
                     help="Histogram name inside --mcfile containing per-bin flux")
    ap.add_argument("--closure", action="store_true",
                     help="Closure test: use MC reco events (pass_reco) as "
                          "pseudo-data instead of real data. Unfolded result "
                          "should recover the MC truth prior within GBT noise.")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    pt_edges = PT_EDGES
    pz_edges = PZ_EDGES
    pt_lo, pt_hi = pt_edges[0], pt_edges[-1]
    pz_lo, pz_hi = pz_edges[0], pz_edges[-1]
    print(f"[INFO] p_T range: [{pt_lo}, {pt_hi}] GeV/c ({len(pt_edges)-1} bins)")
    print(f"[INFO] p_|| range: [{pz_lo}, {pz_hi}] GeV/c ({len(pz_edges)-1} bins)")

    # --- Open input file ---
    f_in = ROOT.TFile.Open(args.omnifile, "READ")
    if not f_in or f_in.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")

    t_sig = f_in.Get("mc_signal_reco")
    t_bkg = f_in.Get("mc_background")
    t_data = f_in.Get("data")
    if not t_sig or not t_bkg or not t_data:
        raise RuntimeError("Missing required TTrees")

    # Verify p_|| branches exist
    for tree, bname in [(t_sig, "sim_pz"), (t_sig, "MC_pz"),
                         (t_bkg, "sim_background_pz"), (t_data, "measured_pz")]:
        if not tree.GetListOfBranches().FindObject(bname):
            raise RuntimeError(
                f"Branch '{bname}' not found in TTree '{tree.GetName()}'. "
                "Re-run runEventLoopOmniFold with the updated C++ code that writes p_|| branches.")

    data_pot, mc_pot, pot_scale = get_pot_scales(f_in)
    print(f"[INFO] POT: data={data_pot:.4g}, mc={mc_pot:.4g}, scale={pot_scale:.6g}")

    # Fiducial nucleons: do not trust the merged TParameter<double> because
    # hadd sums it across playlists. Use the known tracker geometry constant.
    nuc_par = f_in.Get("pTmu_fiducial_nucleons")
    n_nucleons = TRACKER_FIDUCIAL_N_NUCLEONS
    if nuc_par:
        file_nucleons = float(nuc_par.GetVal())
        print(f"[INFO] Fiducial nucleons (file metadata)  = {file_nucleons:.16e}")
        if not np.isclose(file_nucleons, n_nucleons, rtol=0.0, atol=0.0):
            print("[WARN] Ignoring merge-sensitive pTmu_fiducial_nucleons metadata; "
                  "using the tracker geometry constant instead.")
    print(f"[INFO] Fiducial nucleons (geometry)      = {n_nucleons:.16e}")

    # Load flux histogram from binned MC file. MINERvA flux histograms are
    # stored in units of m^-2/POT (per p_T bin); ExtractCrossSection.cpp:127
    # applies a 1e4 factor to convert to cm^-2 at the end of normalization.
    flux_bins, hFlux_pt = load_flux_bins(args.mcfile, args.flux_hist, pt_edges)
    # Keep integrated flux in both native m^-2/POT units and correctly-converted
    # cm^-2/POT units for metadata reporting.
    flux_total_m2 = float(np.sum(flux_bins))
    flux_total_cm2 = flux_total_m2 / 1.0e4
    flux_source = f"{args.mcfile}:{args.flux_hist}"
    print(f"[INFO] Flux source: {flux_source}")
    print(f"[INFO] Flux bins (m^-2/POT): {flux_bins}")
    print(f"[INFO] Flux sum = {flux_total_m2:.4g} m^-2/POT "
          f"= {flux_total_cm2:.4g} cm^-2/POT")

    # --- Read data and MC ---
    hDataReco2D = make_th2d("hDataReco2D", "Data reco", pt_edges, pz_edges)
    hBkgReco2D = make_th2d("hBkgReco2D", "Background reco (POT-scaled)", pt_edges, pz_edges)

    meas_pt, meas_pz = fill_data_reco_2d(
        t_data, hDataReco2D, pt_lo, pt_hi, pz_lo, pz_hi, verbose=args.verbose)
    fill_bkg_reco_2d(t_bkg, hBkgReco2D, pot_scale, verbose=args.verbose)

    # --- Read signal MC arrays ---
    sig = collect_signal_arrays_2d(t_sig, pt_lo, pt_hi, pz_lo, pz_hi,
                                    pot_scale, use_weights=args.use_weights,
                                    verbose=args.verbose)
    if sig["truth_pt"].size == 0:
        raise RuntimeError("No signal events for OmniFold")
    if meas_pt.size == 0:
        raise RuntimeError("No measured data entries")

    # Signal fakes: MC signal-truth events with reco inside the binning but
    # truth outside the measurement phase space. These are present in measured
    # data at reco level, and the upstream mc_background TTree does NOT contain
    # them (runEventLoopOmniFold.cpp:234 drops signal-truth from mc_background).
    # Meanwhile omnifold.py:98-101 drops ~pass_truth events from the MC arrays
    # before step-1 training. Without this extra subtraction, measured would
    # contain fakes while MC reco would not, inducing a reco-level mismatch that
    # the step-1 classifier absorbs as a spurious reweight. Treat fakes as
    # background (paper convention) by adding their POT-scaled reco weights
    # into hBkgReco2D before the data-bkg subtraction.
    is_fake = sig["pass_reco"] & (~sig["pass_truth"])
    n_fakes = int(is_fake.sum())
    if n_fakes:
        fake_pt = sig["reco_pt"][is_fake]
        fake_pz = sig["reco_pz"][is_fake]
        fake_wr = sig["w_reco"][is_fake]  # already POT-scaled in collect_signal_arrays_2d
        fake_sum = 0.0
        for pt, pz, w in zip(fake_pt, fake_pz, fake_wr):
            hBkgReco2D.Fill(float(pt), float(pz), float(w))
            fake_sum += float(w)
        if args.verbose:
            print(f"[INFO] signal fakes added to bkg: n={n_fakes}, "
                  f"sum(w_reco)={fake_sum:.6g}")

    # Background subtraction (bkg now includes real backgrounds + signal fakes)
    hMeasSub2D = hDataReco2D.Clone("hMeasSub2D")
    hMeasSub2D.SetTitle("Measured (data - bkg)")
    hMeasSub2D.Add(hBkgReco2D, -1.0)
    measured_weights, hMeasTrain2D = build_measured_training_2d(
        meas_pt, meas_pz, hDataReco2D, hBkgReco2D, verbose=args.verbose)
    nneg_meas = count_negative_bins_2d(hMeasSub2D)

    print(f"[INFO] Data reco entries: {len(meas_pt)}")
    print(f"[INFO] hDataReco2D integral: {hDataReco2D.Integral():.6g}")
    print(f"[INFO] hBkgReco2D integral (incl. fakes): {hBkgReco2D.Integral():.6g}")
    print(f"[INFO] hMeasSub2D integral: {hMeasSub2D.Integral():.6g}")
    print(f"[INFO] hMeasTrain2D integral: {hMeasTrain2D.Integral():.6g}")
    if nneg_meas:
        print(f"[INFO] hMeasSub2D negative bins (floored in training target): {nneg_meas}")

    # --- Closure mode: replace measured arrays with MC reco pseudo-data ---
    # For a closure test, we substitute the `measured` input to OmniFold with
    # the MC reco events (where pass_reco is True). Since the pseudo-data and
    # the MCreco training sample come from the same MC, step1 should weight
    # to ~1 per event, and step2 should recover the MC truth prior within GBT
    # approximation noise. Tests normalization, fills, and phase-space
    # handling end-to-end without being confounded by data/MC mismodeling.
    if args.closure:
        print("[INFO] *** CLOSURE MODE: using MC reco as pseudo-data ***")
        # Restrict pseudo-data to truth-in-PS + reco-passing events. Excluding
        # fakes (pass_reco & ~pass_truth) matches what OmniFold unfolds against
        # (omnifold.py drops ~pass_truth events before training), so closure is
        # self-consistent.
        closure_mask = sig["pass_reco"] & sig["pass_truth"]
        meas_pt = sig["reco_pt"][closure_mask].copy()
        meas_pz = sig["reco_pz"][closure_mask].copy()
        # Measured weights must be on the same footing as MCreco_weights for the
        # step-1 classifier to learn ~identity. With --use-weights, MCreco is
        # passed as sig["w_reco"]; closure measured_weights must mirror that on
        # the same event subset. Unit weights here would induce a bias scaling
        # with the spread of w_reco.
        if args.use_weights:
            measured_weights = sig["w_reco"][closure_mask].copy()
        else:
            measured_weights = np.ones(meas_pt.shape[0], dtype=float)
        hDataReco2D.Reset("ICES")
        hBkgReco2D.Reset("ICES")
        for pt, pz, w in zip(meas_pt, meas_pz, measured_weights):
            hDataReco2D.Fill(float(pt), float(pz), float(w))
        hMeasSub2D = hDataReco2D.Clone("hMeasSub2D")
        hMeasSub2D.SetTitle("Pseudo-data (MC reco, closure test)")
        hMeasTrain2D = hDataReco2D.Clone("hMeasTrain2D")
        hMeasTrain2D.SetTitle("Pseudo-data (training, closure test)")
        print(f"[INFO] Closure pseudo-data entries: {meas_pt.size}, "
              f"sum(w)={float(measured_weights.sum()):.6g}")
        print(f"[INFO] hDataReco2D (closure) integral: {hDataReco2D.Integral():.6g}")

    # --- Run 2D OmniFold via direct Python helper call ---
    # NB: we bypass ROOT.RooUnfoldOmnifold().UnbinnedOmnifold() because its
    # DataFrame_to_python path (RooUnfoldOmnifold.cxx:216-249) column-order
    # handling is unreliable for multi-column RDataFrames, which produced a
    # 6.3x inflation of hUnfold2D on the first 2D run. The direct call with
    # explicit numpy arrays gives the correct step2 normalization. See
    # 2d-unfolding/2D_OMNIFOLD_STUDY_STATUS.md for the debug narrative.
    import sys
    _OF_PY = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/unbinned_unfolding/python"
    if _OF_PY not in sys.path:
        sys.path.insert(0, _OF_PY)
    from omnifold import OmniFold_helper_functions as ohf

    print(f"[INFO] Running 2D OmniFold with {args.iters} iterations...")
    print(f"[INFO] MC events: {sig['truth_pt'].shape[0]}, "
          f"pass_truth: {sig['pass_truth'].sum()}, pass_reco: {sig['pass_reco'].sum()}")
    print(f"[INFO] Measured events: {meas_pt.shape[0]}, "
          f"effective training sum={measured_weights.sum():.6g}")

    MCgen = np.column_stack([sig["truth_pt"], sig["truth_pz"]])
    MCreco = np.column_stack([sig["reco_pt"], sig["reco_pz"]])
    measured = np.column_stack([meas_pt, meas_pz])

    step1_weights, step2_weights = ohf.omnifold(
        MCgen, MCreco, measured,
        sig["pass_reco"], sig["pass_truth"],
        np.ones(meas_pt.shape[0], dtype=bool),
        int(args.iters),
        MCgen_weights=sig["w_truth"] if args.use_weights else None,
        MCreco_weights=sig["w_reco"] if args.use_weights else None,
        measured_weights=measured_weights,
    )
    print(f"[INFO] OmniFold complete. step1 weights: {step1_weights.shape[0]}, "
          f"step2 weights: {step2_weights.shape[0]}")
    print(f"[INFO] step2 sum={step2_weights.sum():.4g}, "
          f"mean={step2_weights.mean():.4f}, "
          f"min={step2_weights.min():.4f}, max={step2_weights.max():.4f}")

    # --- Fill unfolded histograms ---
    # The weights apply to MC events that pass truth (pass_truth mask was applied
    # internally by OmniFold before training)
    truth_pt_in = sig["truth_pt"][sig["pass_truth"]]
    truth_pz_in = sig["truth_pz"][sig["pass_truth"]]
    truth_w_in = sig["w_truth"][sig["pass_truth"]]

    if truth_pt_in.shape[0] != step2_weights.shape[0]:
        raise RuntimeError(
            f"Weight size mismatch: truth={truth_pt_in.shape[0]}, "
            f"step2={step2_weights.shape[0]}")

    # MC truth prior (original weights)
    hTruth2D = make_th2d("hTruth2D", "MC truth prior", pt_edges, pz_edges)
    for pt, pz, w in zip(truth_pt_in, truth_pz_in, truth_w_in):
        hTruth2D.Fill(float(pt), float(pz), float(w))

    # OmniFold unfolded: step2 returns a truth-side density ratio. Convert it
    # back to event-count units by multiplying by the original truth weights.
    hUnfold2D = make_th2d("hUnfold2D", "Unfolded (2D OmniFold)", pt_edges, pz_edges)
    for pt, pz, ratio, wt in zip(truth_pt_in, truth_pz_in, step2_weights, truth_w_in):
        hUnfold2D.Fill(float(pt), float(pz), float(ratio) * float(wt))

    print(f"[CHECK] hTruth2D integral: {hTruth2D.Integral():.6g}")
    print(f"[CHECK] hUnfold2D integral: {hUnfold2D.Integral():.6g}")
    print(f"[CHECK] hMeasSub2D integral: {hMeasSub2D.Integral():.6g}")
    print(f"[CHECK] hMeasTrain2D integral: {hMeasTrain2D.Integral():.6g}")

    # --- Compute efficiency and cross section ---
    hEff2D, hEffNum, hEffDen = compute_efficiency_2d(sig, pt_edges, pz_edges)

    hXSec2D = extract_cross_section_2d(hUnfold2D, hEff2D, flux_bins,
                                         data_pot, n_nucleons, pt_edges, pz_edges)

    # 1D projections
    hXSec_pt = project_xsec_1d(hXSec2D, "pt", pt_edges, pz_edges)
    hXSec_pz = project_xsec_1d(hXSec2D, "pz", pt_edges, pz_edges)

    # --- Summary checks ---
    pt_integral = sum(hXSec_pt.GetBinContent(i) * hXSec_pt.GetBinWidth(i)
                      for i in range(1, hXSec_pt.GetNbinsX() + 1))
    pz_integral = sum(hXSec_pz.GetBinContent(i) * hXSec_pz.GetBinWidth(i)
                      for i in range(1, hXSec_pz.GetNbinsX() + 1))
    print(f"[CHECK] Total xsec from p_T projection: {pt_integral:.4g} cm^2/nucleon")
    print(f"[CHECK] Total xsec from p_|| projection: {pz_integral:.4g} cm^2/nucleon")

    # --- Write output ---
    f_out = ROOT.TFile.Open(args.out, "RECREATE")
    if not f_out or f_out.IsZombie():
        raise RuntimeError(f"Could not create {args.out}")
    f_out.cd()

    # Metadata
    ROOT.TParameter("double")("dataPOT", data_pot).Write()
    ROOT.TParameter("double")("mcPOT", mc_pot).Write()
    ROOT.TParameter("double")("potScale", pot_scale).Write()
    ROOT.TParameter("int")("nIterations", int(args.iters)).Write()
    ROOT.TParameter("double")("fluxIntegral_m2_per_POT", flux_total_m2).Write()
    ROOT.TParameter("double")("fluxIntegral_cm2_per_POT", flux_total_cm2).Write()
    ROOT.TParameter("double")("nNucleons", n_nucleons).Write()
    ROOT.TNamed("fluxSource", flux_source).Write()

    # Histograms
    for h in [hDataReco2D, hBkgReco2D, hMeasSub2D, hMeasTrain2D,
              hTruth2D, hUnfold2D, hEff2D, hEffNum, hEffDen,
              hXSec2D, hXSec_pt, hXSec_pz, hFlux_pt]:
        h.Write()

    f_out.Close()
    print(f"[OK] Wrote {args.out}")


if __name__ == "__main__":
    main()
