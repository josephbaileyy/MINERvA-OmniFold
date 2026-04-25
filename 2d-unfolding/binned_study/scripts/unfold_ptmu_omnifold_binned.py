#!/usr/bin/env python3
import argparse
import math
import sys
from array import array
from pathlib import Path

import ROOT
ROOT.gROOT.SetBatch(True)

# POTs for MINERvA-101 style scaling
DATA_POT = 8.9727561e19
MC_POT   = 4.0692592e20


def get_edges_from_hist(h):
    ax = h.GetXaxis()
    nb = ax.GetNbins()
    edges = [ax.GetBinLowEdge(1)]
    for i in range(1, nb + 1):
        edges.append(ax.GetBinUpEdge(i))
    return edges


def make_th1d(name, title, edges):
    arr = array("d", edges)
    h = ROOT.TH1D(name, title, len(edges) - 1, arr)
    h.Sumw2()
    h.SetDirectory(0)
    return h


def make_th2d(name, title, x_edges, y_edges):
    x_arr = array("d", x_edges)
    y_arr = array("d", y_edges)
    h = ROOT.TH2D(name, title, len(x_edges) - 1, x_arr, len(y_edges) - 1, y_arr)
    h.Sumw2()
    h.SetDirectory(0)
    return h


def rebuild_response_hist_with_physical_binning(response, verbose=False):
    src = response.HresponseNoOverflow() if hasattr(response, "HresponseNoOverflow") else response.Hresponse()
    if not src:
        raise RuntimeError("Response histogram is missing")

    h_measured = response.Hmeasured()
    h_truth = response.Htruth()
    if not h_measured or not h_truth:
        raise RuntimeError("Response is missing measured/truth templates needed to rebuild physical binning")

    x_edges = get_edges_from_hist(h_measured)
    y_edges = get_edges_from_hist(h_truth)
    if src.GetNbinsX() != len(x_edges) - 1 or src.GetNbinsY() != len(y_edges) - 1:
        raise RuntimeError(
            "Response matrix dimensions do not match measured/truth templates: "
            f"src={src.GetNbinsX()}x{src.GetNbinsY()}, "
            f"expected={(len(x_edges) - 1)}x{(len(y_edges) - 1)}"
        )

    rebuilt = make_th2d("resp_ptmu_physical_binning", "Response pTmu (physical binning)", x_edges, y_edges)
    max_abs_diff = 0.0
    for ix in range(1, src.GetNbinsX() + 1):
        for iy in range(1, src.GetNbinsY() + 1):
            content = float(src.GetBinContent(ix, iy))
            error = float(src.GetBinError(ix, iy))
            rebuilt.SetBinContent(ix, iy, content)
            rebuilt.SetBinError(ix, iy, error)
            max_abs_diff = max(max_abs_diff, abs(content - rebuilt.GetBinContent(ix, iy)))

    rebuilt.SetEntries(src.GetEntries())

    if verbose:
        print(
            "[INFO] response axis repair: "
            f"source x=[{src.GetXaxis().GetXmin():.6g}, {src.GetXaxis().GetXmax():.6g}] "
            f"y=[{src.GetYaxis().GetXmin():.6g}, {src.GetYaxis().GetXmax():.6g}] "
            f"bins={src.GetNbinsX()}x{src.GetNbinsY()}"
        )
        print(
            "[INFO] response axis repair: "
            f"rebuilt x=[{rebuilt.GetXaxis().GetXmin():.6g}, {rebuilt.GetXaxis().GetXmax():.6g}] "
            f"y=[{rebuilt.GetYaxis().GetXmin():.6g}, {rebuilt.GetYaxis().GetXmax():.6g}] "
            f"bins={rebuilt.GetNbinsX()}x{rebuilt.GetNbinsY()}"
        )
        print(
            "[INFO] response axis repair: "
            f"source integral={float(src.Integral(1, src.GetNbinsX(), 1, src.GetNbinsY())):.6g}, "
            f"rebuilt integral={float(rebuilt.Integral(1, rebuilt.GetNbinsX(), 1, rebuilt.GetNbinsY())):.6g}, "
            f"max_abs_bin_diff={max_abs_diff:.6g}"
        )

    if max_abs_diff != 0.0:
        raise RuntimeError(f"Rebuilt response histogram content mismatch detected: max_abs_bin_diff={max_abs_diff}")

    return rebuilt


def integral_inrange(h):
    return float(h.Integral(1, h.GetNbinsX()))


def integral_with_ufof(h):
    return float(h.Integral(0, h.GetNbinsX() + 1))


def integral_inrange_width(h):
    return float(h.Integral(1, h.GetNbinsX(), "width"))


def assert_no_negative_bins(h, name):
    for ib in range(1, h.GetNbinsX() + 1):
        v = h.GetBinContent(ib)
        if v < 0:
            raise RuntimeError(f"{name}: negative bin {ib} content={v}")


def floor_nonpositive_bins(h, floor=1e-3):
    """Floor <=0 bins to a tiny positive value for OmniFold training stability."""
    n = 0
    for ib in range(1, h.GetNbinsX() + 1):
        if h.GetBinContent(ib) <= 0:
            h.SetBinContent(ib, floor)
            n += 1
    return n


def regularize_response(resp, hRecoTemplate, hTruthTemplate, eps=1e-6):
    """
    Add tiny support everywhere to prevent zero-support pathologies during iterative reweighting.
    This is purely numerical regularization (eps is tiny).
    """
    nb = hRecoTemplate.GetNbinsX()
    axr = hRecoTemplate.GetXaxis()
    axt = hTruthTemplate.GetXaxis()

    for ib in range(1, nb + 1):
        resp.Miss(axt.GetBinCenter(ib), eps)
        resp.Fake(axr.GetBinCenter(ib), eps)
        x = axr.GetBinCenter(ib)
        resp.Fill(x, x, eps)


def fill_data_reco(tData, hData, pt_guard_max=1e3, verbose=False):
    measured = array("d", [0.0])
    measured_pass = array("B", [0])

    # Required branches (in your production this exists; keep it strict for readability)
    tData.SetBranchAddress("measured", measured)
    tData.SetBranchAddress("measured_pass", measured_pass)

    n_pass_skip = 0
    n_guard_skip = 0
    n = tData.GetEntries()

    for i in range(n):
        tData.GetEntry(i)

        if measured_pass[0] == 0:
            n_pass_skip += 1
            continue

        x = float(measured[0])
        if not math.isfinite(x) or abs(x) > pt_guard_max:
            n_guard_skip += 1
            continue

        hData.Fill(x)

    if verbose:
        print(f"[INFO] data filled: pass-skipped={n_pass_skip}, guard-skipped={n_guard_skip}")

    return n


def fill_bkg_reco(tBkg, hBkg, potScale, pt_guard_max=1e3, verbose=False):
    sim_bkg = array("d", [0.0])
    sim_bkg_pass = array("B", [0])
    w_bkg = array("d", [1.0])

    # Required branches
    tBkg.SetBranchAddress("sim_background", sim_bkg)
    tBkg.SetBranchAddress("sim_background_pass", sim_bkg_pass)
    has_w = bool(tBkg.GetListOfBranches().FindObject("w_bkg"))
    if has_w:
        tBkg.SetBranchAddress("w_bkg", w_bkg)

    n_pass_skip = 0
    n_guard_skip = 0
    n_w_skip = 0
    n = tBkg.GetEntries()

    for i in range(n):
        tBkg.GetEntry(i)

        if sim_bkg_pass[0] == 0:
            n_pass_skip += 1
            continue

        x = float(sim_bkg[0])
        if not math.isfinite(x) or abs(x) > pt_guard_max:
            n_guard_skip += 1
            continue

        w = float(w_bkg[0]) if has_w else 1.0
        if not (math.isfinite(w) and w >= 0.0 and w < 1e6):
            n_w_skip += 1
            continue

        hBkg.Fill(x, w * potScale)

    if verbose:
        print(f"[INFO] bkg filled: pass-skipped={n_pass_skip}, guard-skipped={n_guard_skip}, weight-skipped={n_w_skip}, has_w_bkg={has_w}")

    return n, has_w


def fill_response_and_mc_reco(
    tSig,
    response,
    hTruthSel,
    hSigReco,
    pt_lo,
    pt_hi,
    responsePotScale,
    response_weight_mode="truth",
    use_weights=False,
    verbose=False,
    hResp2D=None,
):
    """
    Build a RooUnfoldResponse for pTmu using:
      - Fill(rec, tru) when reco selected and in-range, tru in-range
      - Miss(tru) when not selected but tru in-range
      - Fake(rec) when selected and rec in-range, tru out-of-range
    response_weight_mode:
      - "truth": Fill/Miss/Fake use wt
      - "legacy-mixed": Fill/Fake use wr, Miss uses wt
    """
    # Required branches
    for b in ("MC", "sim", "sim_pass"):
        if not tSig.GetListOfBranches().FindObject(b):
            raise RuntimeError(f"mc_signal_reco missing required branch: {b}")

    MC_true  = array("d", [0.0])
    sim_reco = array("d", [0.0])
    sim_pass = array("B", [0])

    tSig.SetBranchAddress("MC", MC_true)
    tSig.SetBranchAddress("sim", sim_reco)
    tSig.SetBranchAddress("sim_pass", sim_pass)

    # Optional weights
    wt_arr = array("d", [1.0])
    wr_arr = array("d", [1.0])
    has_wt = use_weights and bool(tSig.GetListOfBranches().FindObject("w_truth"))
    has_wr = use_weights and bool(tSig.GetListOfBranches().FindObject("w_reco"))
    if has_wt:
        tSig.SetBranchAddress("w_truth", wt_arr)
    if has_wr:
        tSig.SetBranchAddress("w_reco", wr_arr)

    n_fill = n_miss = n_fake = 0
    n_skip = n_skip_w = 0
    sum_w_fill = 0.0
    sum_w_miss = 0.0
    sum_w_fake = 0.0
    n = tSig.GetEntries()

    for i in range(n):
        tSig.GetEntry(i)

        tru = float(MC_true[0])
        rec = float(sim_reco[0])
        passed = (sim_pass[0] != 0)

        wt = float(wt_arr[0]) if has_wt else 1.0
        wr = float(wr_arr[0]) if has_wr else wt

        # Minimal weight sanity (keep; prevents silent NaNs)
        if not (math.isfinite(wt) and math.isfinite(wr) and wt >= 0.0 and wr >= 0.0 and wt < 1e4 and wr < 1e4):
            n_skip_w += 1
            continue

        wt *= responsePotScale
        wr *= responsePotScale
        if response_weight_mode == "legacy-mixed":
            w_evt_fill_fake = wr
            w_evt_miss = wt
        else:
            w_evt_fill_fake = wt
            w_evt_miss = wt

        tru_ok = math.isfinite(tru) and (pt_lo <= tru <= pt_hi)
        rec_ok = math.isfinite(rec) and (pt_lo <= rec <= pt_hi)

        if passed and rec_ok and tru_ok:
            hTruthSel.Fill(tru, wt)
            hSigReco.Fill(rec, wr)
            response.Fill(rec, tru, w_evt_fill_fake)
            if hResp2D is not None:
                hResp2D.Fill(rec, tru, w_evt_fill_fake)
            sum_w_fill += w_evt_fill_fake
            n_fill += 1
        elif (not passed) and tru_ok:
            hTruthSel.Fill(tru, wt)
            response.Miss(tru, w_evt_miss)
            sum_w_miss += w_evt_miss
            n_miss += 1
        elif passed and rec_ok and (not tru_ok):
            hSigReco.Fill(rec, wr)
            response.Fake(rec, w_evt_fill_fake)
            sum_w_fake += w_evt_fill_fake
            n_fake += 1
        else:
            n_skip += 1

    if verbose:
        print(f"[INFO] response: Fill={n_fill}, Miss={n_miss}, Fake={n_fake}, skipped={n_skip}, bad-weight={n_skip_w}")
    else:
        print(f"[INFO] response fill summary: Fill={n_fill}, Miss={n_miss}, Fake={n_fake}")

    return {
        "n_entries": n,
        "n_fill": n_fill,
        "n_miss": n_miss,
        "n_fake": n_fake,
        "n_skip": n_skip,
        "n_skip_w": n_skip_w,
        "sum_w_fill": sum_w_fill,
        "sum_w_miss": sum_w_miss,
        "sum_w_fake": sum_w_fake,
        "sum_w_fill_evt": sum_w_fill,
        "sum_w_miss_evt": sum_w_miss,
        "sum_w_fake_evt": sum_w_fake,
    }


def get_pot_scales(f_in):
    data_pot = DATA_POT
    mc_pot = MC_POT
    src = "fallback constants"

    data_par = f_in.Get("dataPOTUsed")
    mc_par = f_in.Get("mcPOTUsed")
    if data_par and mc_par:
        data_pot = float(data_par.GetVal())
        mc_pot = float(mc_par.GetVal())
        src = "input file metadata"

    if not (math.isfinite(data_pot) and math.isfinite(mc_pot) and mc_pot > 0.0):
        raise RuntimeError(f"Invalid POT values: dataPOT={data_pot}, mcPOT={mc_pot}")

    return data_pot, mc_pot, data_pot / mc_pot, src


def import_binned_helper():
    repo_root = Path(__file__).resolve().parents[3]
    omni_python_dir = repo_root / "OmniFold" / "unbinned_unfolding" / "python"
    if not omni_python_dir.exists():
        raise RuntimeError(f"Cannot find OmniFold python helper dir: {omni_python_dir}")
    sys.path.insert(0, str(omni_python_dir))
    from omnifold import OmniFold_helper_functions
    return OmniFold_helper_functions


def run_binned_omnifold_direct(response, measured_hist, niter, use_density=False, verbose=False,
                               hResp2D=None, hTruthSel=None):
    """Return (h_post_eff, h_pre_eff).  h_pre_eff is the raw OmniFold output
    before the efficiency correction; h_post_eff has been divided by ε_j."""
    helper = import_binned_helper()
    if hResp2D is not None:
        resp_hist = hResp2D
    else:
        resp_hist = rebuild_response_hist_with_physical_binning(response, verbose=verbose)
    h_unfold = helper.binned_omnifold(resp_hist, measured_hist, int(niter), bool(use_density))

    # Save pre-efficiency copy
    h_pre_eff = h_unfold.Clone("hUnfoldPreEff")
    h_pre_eff.SetDirectory(0)

    if hResp2D is not None and hTruthSel is not None:
        # Compute correct efficiency from the properly-binned TH2D.
        # ε_j = (Y-projection of hResp2D at truth bin j) / hTruthSel[j]
        # Y-projection = sum over reco bins = Fill-only truth distribution.
        nb = h_unfold.GetNbinsX()
        for j in range(nb):
            fill_truth_j = 0.0
            for i in range(1, hResp2D.GetNbinsX() + 1):
                fill_truth_j += float(hResp2D.GetBinContent(i, j + 1))
            total_truth_j = float(hTruthSel.GetBinContent(j + 1))
            eff_j = fill_truth_j / total_truth_j if total_truth_j > 0 else 0.0
            if verbose:
                old_eff_j = float(response.Vefficiency()[j])
                print(f"  [EFF] bin {j+1}: correct={eff_j:.6g}, Vefficiency={old_eff_j:.6g}, ratio={eff_j/old_eff_j if old_eff_j > 0 else float('inf'):.4g}")
            if eff_j > 0.0:
                h_unfold.SetBinContent(j + 1, h_unfold.GetBinContent(j + 1) / eff_j)
    else:
        # Fallback: use (garbled) Vefficiency from response.
        eff = response.Vefficiency()
        for i in range(h_unfold.GetNbinsX()):
            e = float(eff[i])
            if e > 0.0:
                h_unfold.SetBinContent(i + 1, h_unfold.GetBinContent(i + 1) / e)
    h_unfold.SetDirectory(0)
    return h_unfold, h_pre_eff


def run_binned_omnifold_wrapper(response, measured_hist, niter):
    unfold = ROOT.RooUnfoldOmnifold(response, measured_hist, int(niter))
    h_unfold = unfold.Hunfold()
    h_unfold.SetDirectory(0)
    return h_unfold


def convert_hunfold_weights_to_counts(h_unfold_weights, h_prior_truth, out_name="hUnfoldTruthSel"):
    """
    Some RooUnfoldOmnifold builds return per-bin truth reweight factors from Hunfold().
    Convert those weights to event counts using a truth prior histogram.
    """
    h_counts = h_prior_truth.Clone(out_name)
    h_counts.SetDirectory(0)
    h_counts.Multiply(h_unfold_weights)
    return h_counts


def main():
    ap = argparse.ArgumentParser(description="1D binned OmniFold unfolding for MINERvA pTmu with selectable wrapper/helper engines.")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold.root", help="Input ROOT file with trees (data/mc_signal_reco/mc_background).")
    ap.add_argument("--datafile", default="runEventLoopData.root", help="Reference ROOT file containing pTmu_data histogram for binning.")
    ap.add_argument("--datahist", default="pTmu_data", help="Histogram name inside --datafile used for variable bin edges.")
    ap.add_argument("--iters", type=int, default=5, help="Number of OmniFold iterations.")
    ap.add_argument("--use-weights", action="store_true", help="Use w_truth/w_reco branches if present in mc_signal_reco.")
    ap.add_argument("--no-scale-response-to-data-pot", action="store_true", help="Disable data/MC POT scaling inside response Fill/Miss/Fake.")
    ap.add_argument("--scale-response-to-data-pot", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--iter-scan-max", type=int, default=0, help="If >0, scan OmniFold unfolded integrals for iterations 1..N (debug only).")
    ap.add_argument("--binned-use-density", action="store_true", help="Use helper density mode for binned OmniFold.")
    ap.add_argument("--rescale-unfold-to-meas", action="store_true", help="Also write a copy of unfolded scaled to match data-bkg in-range integral.")
    ap.add_argument("--engine", choices=("wrapper", "helper"), default="wrapper", help="OmniFold engine: RooUnfold wrapper (default) or direct helper.")
    ap.add_argument("--response-weight-mode", choices=("truth", "legacy-mixed"), default="truth", help="Response Fill/Fake/Miss event weight mode.")
    ap.add_argument("--hunfold-mode", choices=("counts", "weights"), default="counts", help="Interpretation of Hunfold output: direct counts or per-bin weights (multiplied by hTruthSel).")
    ap.add_argument("--closure-test", action="store_true", help="Replace measured (data-bkg) with response.Hmeasured() for a self-consistent closure test.")
    ap.add_argument("--out", default="omnifold_ptmu_unfold.root", help="Output ROOT file.")
    ap.add_argument("--verbose", action="store_true", help="Print detailed counters.")
    args = ap.parse_args()

    # --- reference binning
    fRef = ROOT.TFile.Open(args.datafile, "READ")
    if not fRef or fRef.IsZombie():
        raise RuntimeError(f"Could not open {args.datafile}")
    hRef = fRef.Get(args.datahist)
    if not hRef:
        raise RuntimeError(f"Could not find {args.datahist} in {args.datafile}")
    edges = get_edges_from_hist(hRef)
    pt_lo, pt_hi = edges[0], edges[-1]
    print(f"[INFO] Using pTmu range from reference binning: [{pt_lo}, {pt_hi}]")

    # --- input trees
    fIn = ROOT.TFile.Open(args.omnifile, "READ")
    if not fIn or fIn.IsZombie():
        raise RuntimeError(f"Could not open {args.omnifile}")

    tSig  = fIn.Get("mc_signal_reco")
    tBkg  = fIn.Get("mc_background")
    tData = fIn.Get("data")
    if not tSig or not tBkg or not tData:
        raise RuntimeError("Missing required TTrees: mc_signal_reco, mc_background, data")

    data_pot, mc_pot, potScale, pot_src = get_pot_scales(fIn)
    print(f"[INFO] POT source={pot_src}: dataPOT={data_pot:.6g}, mcPOT={mc_pot:.6g}, potScale={potScale:.6g}")
    scale_response_to_data_pot = (not args.no_scale_response_to_data_pot) or args.scale_response_to_data_pot
    response_pot_scale = potScale if scale_response_to_data_pot else 1.0
    print(f"[INFO] response POT scale mode: {'data/MC' if scale_response_to_data_pot else 'none'} (responsePotScale={response_pot_scale:.6g})")
    print(f"[INFO] engine={args.engine}, responseWeightMode={args.response_weight_mode}, hunfoldMode={args.hunfold_mode}")

    if args.verbose:
        print(f"[INFO] tData entries = {tData.GetEntries()}")
        print(f"[INFO] tBkg entries  = {tBkg.GetEntries()}")
        print(f"[INFO] tSig entries  = {tSig.GetEntries()}")

    # --- histograms
    hDataReco  = make_th1d("hDataReco",  "Data reco;p_{T}^{#mu,reco};Events", edges)
    hSigReco   = make_th1d("hSigReco",   "Sim. (signal reco);p_{T}^{#mu,reco};Events", edges)
    hBkgReco   = make_th1d("hBkgReco",   "Sim. (bkg reco, POT-scaled);p_{T}^{#mu,reco};Events", edges)
    hMeasSub   = make_th1d("hMeasSub",   "Measured (data - bkg);p_{T}^{#mu,reco};Events", edges)
    hMeasTrain = make_th1d("hMeasTrain", "Measured (training);p_{T}^{#mu,reco};Events", edges)
    hTruthSel  = make_th1d("hTruthSel",  "Truth (MC truth sel);p_{T}^{#mu,true};Events", edges)

    # Response templates + object
    hRecoTmp  = make_th1d("hRecoTemplate",  "", edges)
    hTruthTmp = make_th1d("hTruthTemplate", "", edges)
    response = ROOT.RooUnfoldResponse(hRecoTmp, hTruthTmp, "resp_ptmu", "Response pTmu")

    # Properly-binned 2D response for the helper path.
    # RooUnfoldResponse._res uses internal [0,1] binning; this TH2D uses the physical bin edges.
    hResp2D = make_th2d("hResp2D_physical", "Response 2D (physical binning)", edges, edges)

    # --- fill reco data/bkg and build measured-subtracted
    fill_data_reco(tData, hDataReco, verbose=args.verbose)
    fill_bkg_reco(tBkg, hBkgReco, potScale, verbose=args.verbose)

    print(f"[INFO] hDataReco integral(in-range)={integral_inrange(hDataReco):.6g}")
    print(f"[INFO] hDataReco integral(UF/OF)={integral_with_ufof(hDataReco):.6g}")
    print(f"[INFO] hBkgReco  integral(in-range)={integral_inrange(hBkgReco):.6g}")
    print(f"[INFO] hBkgReco  integral(UF/OF)={integral_with_ufof(hBkgReco):.6g}")

    hMeasSub.Add(hDataReco)
    hMeasSub.Add(hBkgReco, -1.0)
    print(f"[INFO] hMeasSub (data-bkg) integral(in-range)={integral_inrange(hMeasSub):.6g}")
    print(f"[INFO] hMeasSub (data-bkg) integral(UF/OF)={integral_with_ufof(hMeasSub):.6g}")

    # Meas-sub should be non-negative bin-by-bin for this workflow.
    assert_no_negative_bins(hMeasSub, "hMeasSub")
    min_meas_sub_bin = min(hMeasSub.GetBinContent(ib) for ib in range(1, hMeasSub.GetNbinsX() + 1))
    print(f"[CHECK] hMeasSub minimum in-range bin content = {min_meas_sub_bin:.6g}")

    # Training copy: floor zeros for numerical stability
    hMeasTrain.Add(hMeasSub)
    n_floor = floor_nonpositive_bins(hMeasTrain, floor=1e-12)
    if args.verbose:
        print(f"[INFO] floored non-positive bins in training hist: {n_floor}")

    train_int = float(hMeasTrain.Integral(0, hMeasTrain.GetNbinsX() + 1))
    if train_int <= 0.0:
        raise RuntimeError("Training histogram is empty/non-positive; cannot run OmniFold.")

    # --- fill response + MC reco/true hists
    resp_stats = fill_response_and_mc_reco(
        tSig, response, hTruthSel, hSigReco,
        pt_lo, pt_hi, response_pot_scale,
        response_weight_mode=args.response_weight_mode,
        use_weights=args.use_weights,
        verbose=args.verbose,
        hResp2D=hResp2D,
    )

    print(f"[CHECK] response sum_w_fill={resp_stats['sum_w_fill']:.6g}, sum_w_miss={resp_stats['sum_w_miss']:.6g}, sum_w_fake={resp_stats['sum_w_fake']:.6g}")
    print(f"[CHECK] response evt-weight sums fill/miss/fake = {resp_stats['sum_w_fill_evt']:.6g}, {resp_stats['sum_w_miss_evt']:.6g}, {resp_stats['sum_w_fake_evt']:.6g}")
    hRespTruth = response.Htruth()
    nb = hTruthSel.GetNbinsX()
    resp_truth_inrange = float(hRespTruth.Integral(1, nb))
    truth_sel_inrange = integral_inrange(hTruthSel)
    print(f"[CHECK] response.Htruth in-range={resp_truth_inrange:.6g}")
    print(f"[CHECK] hTruthSel in-range={truth_sel_inrange:.6g}")
    if truth_sel_inrange > 0.0:
        rel = abs(resp_truth_inrange - truth_sel_inrange) / truth_sel_inrange
        if args.response_weight_mode == "truth":
            if rel > 1e-3:
                raise RuntimeError(
                    f"Response truth normalization mismatch: response={resp_truth_inrange}, hTruthSel={truth_sel_inrange}, rel={rel}"
                )
        else:
            # In legacy-mixed mode Fill/Fake can use reco-side weights, so this
            # truth-side equality check is not expected to hold exactly.
            print(
                f"[INFO] response truth-vs-hTruthSel mismatch allowed in legacy-mixed mode: "
                f"response={resp_truth_inrange:.6g}, hTruthSel={truth_sel_inrange:.6g}, rel={rel:.6g}"
            )

    # --- diagnostic: compare garbled _res to properly-binned hResp2D
    hRespInternal = response.Hresponse()
    internal_inrange = float(hRespInternal.Integral(1, hRespInternal.GetNbinsX(), 1, hRespInternal.GetNbinsY()))
    proper_inrange = float(hResp2D.Integral(1, hResp2D.GetNbinsX(), 1, hResp2D.GetNbinsY()))
    print(f"[DIAG] internal _res (in-range) = {internal_inrange:.6g}  (range [{hRespInternal.GetXaxis().GetXmin():.4g}, {hRespInternal.GetXaxis().GetXmax():.4g}])")
    print(f"[DIAG] proper hResp2D (in-range) = {proper_inrange:.6g}  (range [{hResp2D.GetXaxis().GetXmin():.4g}, {hResp2D.GetXaxis().GetXmax():.4g}])")
    print(f"[DIAG] internal/proper = {internal_inrange/proper_inrange:.6g}" if proper_inrange > 0 else "[DIAG] proper hResp2D is empty!")

    # --- epsilon-regularize response to prevent zero-support issues in OmniFold iterations
    regularize_response(response, hRecoTmp, hTruthTmp, eps=1e-6)
    if args.verbose:
        print("[INFO] applied epsilon-regularization to response (Miss/Fake/Fill diagonal).")

    # --- closure test: replace measured with response.Hmeasured()
    if args.closure_test:
        hRespMeas = response.Hmeasured()
        hRespMeas.SetDirectory(0)
        print(f"[CLOSURE] replacing hMeasSub and hMeasTrain with response.Hmeasured()")
        print(f"[CLOSURE] original hMeasSub integral(in-range)={integral_inrange(hMeasSub):.6g}")
        print(f"[CLOSURE] response.Hmeasured integral(in-range)={integral_inrange(hRespMeas):.6g}")
        # Overwrite measured histograms
        hMeasSub.Reset("ICES")
        for ib in range(0, hMeasSub.GetNbinsX() + 2):
            hMeasSub.SetBinContent(ib, hRespMeas.GetBinContent(ib))
            hMeasSub.SetBinError(ib, hRespMeas.GetBinError(ib))
        hMeasTrain.Reset("ICES")
        hMeasTrain.Add(hMeasSub)
        n_floor_closure = floor_nonpositive_bins(hMeasTrain, floor=1e-12)
        print(f"[CLOSURE] floored non-positive bins in closure training hist: {n_floor_closure}")
        print(f"[CLOSURE] hMeasSub integral(in-range) after replacement={integral_inrange(hMeasSub):.6g}")
        print(f"[CLOSURE] data-bkg / response.Hmeasured = {integral_inrange(hMeasSub)/integral_inrange(hRespMeas):.6g} (should be exactly 1.0)")

    print(f"[CHECK] meas-sub integral(in-range)={integral_inrange(hMeasSub):.6g}")
    print(f"[CHECK] meas-train integral(in-range)={integral_inrange(hMeasTrain):.6g}")
    print(f"[CHECK] truthSel integral(in-range)={integral_inrange(hTruthSel):.6g}")
    print(f"[CHECK] truthTmp integral(in-range)={integral_inrange(hTruthTmp):.6g}")
    if integral_inrange(hTruthSel) > 0.0:
        print(f"[CHECK] ratio measSub/truthSel (in-range)={integral_inrange(hMeasSub)/integral_inrange(hTruthSel):.6g}")

    if args.iter_scan_max > 0:
        max_iter = max(1, args.iter_scan_max)
        print(f"[SCAN] unfolded in-range integrals for iterations 1..{max_iter}")
        scan_results = []
        prev = None
        for n_iter in range(1, max_iter + 1):
            if args.engine == "wrapper":
                u_scan = run_binned_omnifold_wrapper(response, hMeasTrain, n_iter)
            else:
                u_scan, _ = run_binned_omnifold_direct(
                    response,
                    hMeasTrain,
                    n_iter,
                    use_density=args.binned_use_density,
                    verbose=args.verbose,
                    hResp2D=hResp2D,
                    hTruthSel=hTruthSel,
                )
            total = integral_inrange(u_scan)
            r = (total / prev) if (prev is not None and prev != 0.0) else float("nan")
            scan_results.append((n_iter, total, r))
            if prev is None:
                print(f"[SCAN] iter={n_iter:2d}, unfolded_inrange={total:.6g}")
            else:
                print(f"[SCAN] iter={n_iter:2d}, unfolded_inrange={total:.6g}, ratio_to_prev={r:.6g}")
            prev = total

        # Persist scan results next to the output file
        scan_path = Path(args.out).with_suffix(".iter_scan.tsv")
        with open(scan_path, "w") as sf:
            sf.write("iter\tunfolded_inrange\tratio_to_prev\n")
            for n_iter, total, r in scan_results:
                sf.write(f"{n_iter}\t{total:.6g}\t{r:.6g}\n")
        print(f"[SCAN] wrote {scan_path}")


    # --- run OmniFold
    hUnfoldPreEff = None
    if args.engine == "wrapper":
        hUnfoldRaw = run_binned_omnifold_wrapper(response, hMeasTrain, args.iters)
    else:
        hUnfoldRaw, hUnfoldPreEff = run_binned_omnifold_direct(
            response,
            hMeasTrain,
            args.iters,
            use_density=args.binned_use_density,
            verbose=args.verbose,
            hResp2D=hResp2D,
            hTruthSel=hTruthSel,
        )
    hUnfoldRaw.SetName("hUnfoldPostEff")
    hUnfoldRaw.SetDirectory(0)
    if hUnfoldPreEff is not None:
        hUnfoldPreEff.SetName("hUnfoldPreEff")
        print(f"[CHECK] pre-efficiency unfolded integral(in-range)={integral_inrange(hUnfoldPreEff):.6g}")
        print(f"[CHECK] post-efficiency unfolded integral(in-range)={integral_inrange(hUnfoldRaw):.6g}")

    if args.hunfold_mode == "weights":
        hUnfoldCounts = convert_hunfold_weights_to_counts(hUnfoldRaw, hTruthSel, out_name="hUnfoldTruthSel")
        print("[INFO] hunfold-mode=weights: converted hUnfoldRaw to counts using hTruthSel prior.")
        print(f"[CHECK] raw Hunfold integral(in-range)={integral_inrange(hUnfoldRaw):.6g}")
        print(f"[CHECK] converted unfolded integral(in-range)={integral_inrange(hUnfoldCounts):.6g}")
    else:
        hUnfoldCounts = hUnfoldRaw.Clone("hUnfoldTruthSel")
        hUnfoldCounts.SetDirectory(0)
    hUnfoldCounts.SetName("hUnfoldTruthSel")
    hUnfoldCounts.SetDirectory(0)

    # --- Effective per-truth-bin weights: w_i = unfolded / truth
    hWbin = hUnfoldCounts.Clone("hWbin_final")
    hWbin.SetDirectory(0)
    hWbin.Reset("ICES")
    
    for ib in range(1, hWbin.GetNbinsX() + 1):
        u = hUnfoldCounts.GetBinContent(ib)
        t = hTruthSel.GetBinContent(ib)
        hWbin.SetBinContent(ib, (u / t) if t > 0 else 0.0)
    
    # --- Distribution of weights
    hWlog = ROOT.TH1D("hWlog_final", "log10(weight);log10(w);# truth bins", 80, -6, 6)
    for ib in range(1, hWbin.GetNbinsX()+1):
        w = hWbin.GetBinContent(ib)
        if w > 0:
            hWlog.Fill(math.log10(w))



    # Normalize unfolded to measured-subtracted total yield (data normalization)
    target = integral_inrange(hMeasSub)
    curr = integral_inrange(hUnfoldCounts)
    resp_meas_inrange = integral_inrange(response.Hmeasured())
    resp_truth_inrange_postreg = integral_inrange(response.Htruth())

    print(f"[CHECK] total unfolded(in-range)={curr:.6g}")
    print(f"[CHECK] total unfolded(UF/OF)={integral_with_ufof(hUnfoldCounts):.6g}")
    print(f"[CHECK] total unfolded(in-range,width)={integral_inrange_width(hUnfoldCounts):.6g}")
    print(f"[CHECK] target data-bkg(in-range)={target:.6g}")
    print(f"[CHECK] target data-bkg(in-range,width)={integral_inrange_width(hMeasSub):.6g}")
    print(f"[CHECK] response.Hmeasured(in-range)={resp_meas_inrange:.6g}")
    print(f"[CHECK] response.Hmeasured(in-range,width)={integral_inrange_width(response.Hmeasured()):.6g}")
    print(f"[CHECK] response.Htruth(in-range, post-reg)={resp_truth_inrange_postreg:.6g}")
    print(f"[CHECK] response.Htruth(in-range,width, post-reg)={integral_inrange_width(response.Htruth()):.6g}")
    if resp_meas_inrange > 0.0:
        print(f"[CHECK] ratio data-bkg / response.Hmeasured = {target/resp_meas_inrange:.6g}")
    ratio_data_to_response_measured = (target / resp_meas_inrange) if resp_meas_inrange > 0.0 else float("nan")
    if curr > 0.0:
        print(f"[CHECK] ratio data-bkg / unfolded = {target/curr:.6g}")
    ratio_data_to_unfolded = (target / curr) if curr > 0.0 else float("nan")
    if args.engine == "wrapper" and math.isfinite(ratio_data_to_unfolded):
        if not (0.8 <= ratio_data_to_unfolded <= 1.25):
            print(f"[WARN] wrapper normalization check: ratio data-bkg/unfolded={ratio_data_to_unfolded:.6g} outside [0.8, 1.25]")

    hUnfoldCountsScaled = hUnfoldCounts.Clone("hUnfoldTruthSel_rescaled")
    hUnfoldCountsScaled.SetDirectory(0)
    if curr > 0.0:
        hUnfoldCountsScaled.Scale(target / curr)
    if args.rescale_unfold_to_meas:
        print("[INFO] enabled --rescale-unfold-to-meas: writing scaled unfolded copy for shape-vs-scale debugging.")

    # --- write output
    fOut = ROOT.TFile.Open(args.out, "RECREATE")
    if not fOut or fOut.IsZombie():
        raise RuntimeError(f"Could not create output file: {args.out}")
    fOut.cd()

    write_failures = []
    if ROOT.TParameter("double")("dataPOT", data_pot).Write() <= 0:
        write_failures.append("dataPOT")
    if ROOT.TParameter("double")("mcPOT", mc_pot).Write() <= 0:
        write_failures.append("mcPOT")
    if ROOT.TParameter("double")("potScale", potScale).Write() <= 0:
        write_failures.append("potScale")
    if ROOT.TParameter("int")("iters", int(args.iters)).Write() <= 0:
        write_failures.append("iters")
    if ROOT.TParameter("int")("engineMode", 0 if args.engine == "wrapper" else 1).Write() <= 0:
        write_failures.append("engineMode")
    if ROOT.TParameter("int")("responseWeightMode", 0 if args.response_weight_mode == "truth" else 1).Write() <= 0:
        write_failures.append("responseWeightMode")
    if ROOT.TParameter("int")("hunfoldMode", 0 if args.hunfold_mode == "counts" else 1).Write() <= 0:
        write_failures.append("hunfoldMode")
    if ROOT.TParameter("double")("ratio_data_to_unfolded", ratio_data_to_unfolded).Write() <= 0:
        write_failures.append("ratio_data_to_unfolded")
    if ROOT.TParameter("double")("ratio_data_to_response_measured", ratio_data_to_response_measured).Write() <= 0:
        write_failures.append("ratio_data_to_response_measured")

    write_list = [hDataReco, hSigReco, hBkgReco, hMeasSub, hMeasTrain, hTruthSel, response, hUnfoldRaw, hUnfoldCounts, hWbin, hWlog]
    if hUnfoldPreEff is not None:
        write_list.append(hUnfoldPreEff)
    for obj in write_list:
        if obj.Write() <= 0:
            write_failures.append(obj.GetName())
    if args.rescale_unfold_to_meas and hUnfoldCountsScaled.Write() <= 0:
        write_failures.append(hUnfoldCountsScaled.GetName())

    if write_failures:
        raise RuntimeError("Failed to write ROOT objects: " + ", ".join(write_failures))


    fOut.Close()
    print(f"[OK] wrote {args.out}")
    print(f"     potScale={potScale:.6g}, iters={args.iters}")


if __name__ == "__main__":
    main()
