#!/usr/bin/env python3
"""
plot_gaussian_style_ptmu.py

Readable plotting script for MINERvA pTmu comparisons.

Inputs
------
OmniFold ROOT file (from unfold_ptmu_omnifold-4.py) containing:
  - hMeasSub         (TH1D) data - background in reco space
  - hSigReco         (TH1D) signal reco (MC)
  - hTruthSel        (TH1D) truth selected-signal (MC truth space)
  - hUnfoldTruthSel  (TH1D) OmniFold unfolded truth (binned)
  - iters            (TParameter<int>) number of OmniFold iterations

IBU ROOT file containing:
  - unfolded (PlotUtils::MnvH1D) MINERvA IBU unfolded result

Behavior
--------
--density (default): normalize *each* curve to unit area using bin widths.
--counts:            plot raw counts as stored in the file(s).

Uncertainties
-------------
- IBU: uses MnvH1D.GetCVHistoWithStatError() so TH1D bin errors are MINERvA stat errors.
- OmniFold: draws error bars only if hUnfoldTruthSel has nonzero bin errors.
"""

import argparse
from array import array
import ROOT

# ROOT style / batch
ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

_KEEP = []

# -------------------------
# Helpers: I/O and conversion
# -------------------------
def get_obj(f: ROOT.TFile, name: str):
    obj = f.Get(name)
    if not obj:
        raise RuntimeError(f"Missing '{name}' in {f.GetName()}")
    return obj


def clone_detached(h, name: str):
    c = h.Clone(name)
    c.SetDirectory(0)
    return c


def make_th1d_with_same_binning(src, name: str) -> ROOT.TH1D:
    """Create an empty TH1D with the same bin edges as src."""
    ax = src.GetXaxis()
    nb = ax.GetNbins()
    edges = [ax.GetBinLowEdge(1)]
    for i in range(1, nb + 1):
        edges.append(ax.GetBinUpEdge(i))
    out = ROOT.TH1D(name, src.GetTitle(), nb, array("d", edges))
    out.Sumw2()
    out.SetDirectory(0)
    out.GetXaxis().SetTitle(ax.GetTitle())
    out.GetYaxis().SetTitle(src.GetYaxis().GetTitle())
    return out


def to_th1d_copy(src, name: str) -> ROOT.TH1D:
    """Copy contents+errors from any TH1-like object into a TH1D with identical binning."""
    out = make_th1d_with_same_binning(src, name)
    nb = out.GetNbinsX()
    for i in range(0, nb + 2):  # include UF/OF
        out.SetBinContent(i, src.GetBinContent(i))
        out.SetBinError(i, src.GetBinError(i))
    return out


def mnvh1d_to_th1d_stat(mnvh1d, name: str) -> ROOT.TH1D:
    """
    Convert PlotUtils::MnvH1D to TH1D using MINERvA STAT uncertainties.
    This is the critical piece for plotting correct IBU error bars.
    """
    if hasattr(mnvh1d, "GetCVHistoWithStatError"):
        h = mnvh1d.GetCVHistoWithStatError().Clone(name)
        h.SetDirectory(0)
        h.Sumw2()
        return h
    # fallback (less ideal)
    return to_th1d_copy(mnvh1d, name)


def remap_to_template_binning(src: ROOT.TH1, tmpl: ROOT.TH1, name: str) -> ROOT.TH1D:
    """
    Map src bin contents/errors into tmpl binning by src-bin-center lookup.
    This avoids ROOT divide warnings from mismatched axis limits/binning.
    """
    out = make_th1d_with_same_binning(tmpl, name)
    out.Reset("ICES")
    for ib in range(1, src.GetNbinsX() + 1):
        x = src.GetXaxis().GetBinCenter(ib)
        v = src.GetBinContent(ib)
        e = src.GetBinError(ib)
        tb = out.GetXaxis().FindBin(x)
        if tb < 1 or tb > out.GetNbinsX():
            continue
        prev = out.GetBinContent(tb)
        prev_e = out.GetBinError(tb)
        out.SetBinContent(tb, prev + v)
        out.SetBinError(tb, (prev_e * prev_e + e * e) ** 0.5)
    return out


# -------------------------
# Helpers: math
# -------------------------
def normalize_to_density(h: ROOT.TH1, name: str) -> ROOT.TH1:
    """
    Normalize to unit area using bin widths:
      area = sum_i content_i * width_i
    """
    hd = clone_detached(h, name)
    area = hd.Integral(1, hd.GetNbinsX(), "width")
    if area > 0:
        hd.Scale(1.0 / area)
    return hd


def same_binning(a: ROOT.TH1, b: ROOT.TH1) -> bool:
    """Require identical visible-bin edges, not just matching xmin/xmax."""
    if a.GetNbinsX() != b.GetNbinsX():
        return False
    ax = a.GetXaxis()
    bx = b.GetXaxis()
    for i in range(1, a.GetNbinsX() + 1):
        if ax.GetBinLowEdge(i) != bx.GetBinLowEdge(i):
            return False
        if ax.GetBinUpEdge(i) != bx.GetBinUpEdge(i):
            return False
    return True


def ratio(num: ROOT.TH1, den: ROOT.TH1, name: str) -> ROOT.TH1:
    if not same_binning(num, den):
        num = remap_to_template_binning(num, den, name + "_num_aligned")
    r = clone_detached(num, name)
    r.Divide(den)
    return r


def truth_ratio_band(truth: ROOT.TH1, name: str) -> ROOT.TH1:
    """Band centered at 1 with relative error = err/content from truth."""
    b = clone_detached(truth, name)
    for i in range(1, b.GetNbinsX() + 1):
        y = truth.GetBinContent(i)
        e = truth.GetBinError(i)
        b.SetBinContent(i, 1.0)
        b.SetBinError(i, 0.0 if y == 0 else e / y)
    return b


def max_bin_content(h: ROOT.TH1) -> float:
    """Max bin content over visible bins only (exclude UF/OF)."""
    m = 0.0
    for i in range(1, h.GetNbinsX() + 1):
        m = max(m, h.GetBinContent(i) + h.GetBinError(i))
    return m


# -------------------------
# Styling
# -------------------------
def style_data(h):
    h.SetLineColor(ROOT.kBlack)
    h.SetMarkerColor(ROOT.kBlack)
    h.SetMarkerStyle(20)
    h.SetMarkerSize(0.9)
    h.SetLineWidth(2)


def style_sim(h):
    h.SetLineColor(ROOT.kOrange + 7)
    h.SetLineWidth(2)
    h.SetFillStyle(0)


def style_truth_band(h):
    h.SetLineColor(ROOT.kGreen + 2)
    h.SetLineWidth(2)
    h.SetFillColorAlpha(ROOT.kGreen + 2, 0.25)
    h.SetFillStyle(1001)


def style_ibu(h):
    h.SetLineColor(ROOT.kGray + 2)
    h.SetLineWidth(2)
    h.SetMarkerStyle(0)
    h.SetFillStyle(0)


def style_bdt(h):
    h.SetLineColor(ROOT.kViolet + 1)
    h.SetLineWidth(3)
    h.SetMarkerStyle(0)
    h.SetFillStyle(0)


def style_unbinned(h):
    h.SetLineColor(ROOT.kAzure + 1)
    h.SetLineWidth(3)
    h.SetMarkerStyle(0)
    h.SetFillStyle(0)


# -------------------------
# Canvas / pads
# -------------------------
def make_canvas():
    c = ROOT.TCanvas("c", "c", 900, 900)
    p1 = ROOT.TPad("p1", "p1", 0.0, 0.30, 1.0, 1.0)
    p2 = ROOT.TPad("p2", "p2", 0.0, 0.00, 1.0, 0.30)

    p1.SetBottomMargin(0.02)
    p2.SetTopMargin(0.04)
    p2.SetBottomMargin(0.30)

    for p in (p1, p2):
        p.SetLeftMargin(0.12)
        p.SetRightMargin(0.05)

    p1.Draw()
    p2.Draw()
    return c, p1, p2


# -------------------------
# Draw
# -------------------------
def draw_top(pad, h_data, h_sim, h_truth, h_ibu, h_bdt, ytitle: str, iters: int, step: bool,
             h_unbinned=None, xsec_mode=False, post_eff=False):
    pad.cd()

    # Use data hist as axis frame
    h_data.SetTitle(f";p_{{T}}^{{#mu}};{ytitle}")

    candidates = [h_data, h_sim, h_truth, h_ibu, h_bdt]
    if h_unbinned is not None:
        candidates.append(h_unbinned)
    ymax = max(max_bin_content(h) for h in candidates)
    h_data.SetMaximum(1.35 * ymax)
    h_data.SetMinimum(0.0)

    # Hide x-axis labels on the top pad (prevents overlap with ratio plot)
    h_data.GetXaxis().SetLabelSize(0)
    h_data.GetXaxis().SetTitleSize(0)

    # Step option: draw central values as step histograms
    sim_opt   = "HIST SAME" if step else "HIST SAME"   # sim is already hist
    truth_opt = "HIST SAME" if step else "HIST SAME"

    # Data always as points
    if not xsec_mode:
        h_data.Draw("E1")
        h_sim.Draw(sim_opt)

    h_truth.Draw("E2 SAME" if not xsec_mode else "E2")
    h_truth.Draw(truth_opt)

    # IBU: draw as step + error bars (error bars are optional but nice)
    if step:
        h_ibu.SetMarkerSize(0)
        h_ibu.Draw("HIST SAME")
        h_ibu.Draw("E1 SAME")   # overlay stat error bars
    else:
        h_ibu.Draw("E1 SAME")

    # OmniFold binned
    has_bdt_errors = any(h_bdt.GetBinError(i) > 0 for i in range(1, h_bdt.GetNbinsX() + 1))
    if step:
        h_bdt.SetMarkerSize(0)
        h_bdt.Draw("HIST SAME")
        if has_bdt_errors:
            h_bdt.Draw("E1 SAME")
    else:
        h_bdt.Draw("E1 SAME" if has_bdt_errors else "HIST SAME")

    # Unbinned OmniFold (optional)
    if h_unbinned is not None:
        if step:
            h_unbinned.SetMarkerSize(0)
            h_unbinned.Draw("HIST SAME")
        else:
            h_unbinned.Draw("HIST SAME")

    leg_y_lo = 0.55 if h_unbinned is not None else 0.60
    leg = ROOT.TLegend(0.48, leg_y_lo, 0.85, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.033)
    if not xsec_mode:
        leg.AddEntry(h_data, "Data (meas sub)", "lep")
        leg.AddEntry(h_sim, "Sim. (signal reco)", "l")
    if xsec_mode:
        truth_label = "Sim. truth (MC)"
    elif post_eff:
        truth_label = "Truth (MC eff. denom.)"
    else:
        truth_label = "Truth (MC truth sel)"
    leg.AddEntry(h_truth, truth_label, "f")
    leg.AddEntry(h_ibu, "IBU (MINERvA)", "lep")
    leg.AddEntry(h_bdt, f"OmniFold (binned, iters={iters})", "l")
    if h_unbinned is not None:
        leg.AddEntry(h_unbinned, "OmniFold (unbinned)", "l")
    leg.Draw()
    _KEEP.append(leg)



def draw_bottom(pad, r_ibu, r_bdt, band, xmin: float, xmax: float, r_unbinned=None):
    pad.cd()

    # Proper frame (fixes the broken lower plot)
    frame = pad.DrawFrame(xmin, 0.7, xmax, 1.3)
    frame.SetTitle(";p_{T}^{#mu};Ratio to Truth")
    frame.GetYaxis().SetNdivisions(505)

    frame.GetYaxis().SetTitleSize(0.09)
    frame.GetYaxis().SetLabelSize(0.08)
    frame.GetYaxis().SetTitleOffset(0.55)

    frame.GetXaxis().SetTitleSize(0.11)
    frame.GetXaxis().SetLabelSize(0.09)

    band.Draw("E2 SAME")
    r_ibu.Draw("E1 SAME")
    r_bdt.Draw("E1 SAME")
    if r_unbinned is not None:
        r_unbinned.Draw("E1 SAME")


# -------------------------
# Main
# -------------------------
def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--omnifold", default="omnifold_ptmu_unfold.root")
    ap.add_argument("--ibu", default="pTmu_crossSection_clean.root")
    ap.add_argument("--outpdf", default="ptmu_gaussian_style.pdf")
    ap.add_argument("--iters", type=int, default=None, help="Override iters shown in legend")

    # default: density ON (matches your previous behavior)
    ap.add_argument("--density", dest="density", action="store_true", help="Plot probability densities")
    ap.add_argument("--counts", dest="density", action="store_false", help="Plot raw counts")
    ap.set_defaults(density=True)

    ap.add_argument("--step", action="store_true",
                help="Draw MC/Truth/IBU/OmniFold as step histograms (hist) instead of smooth lines")
    ap.add_argument("--post-eff", action="store_true",
                help="Use post-efficiency histograms (hUnfoldPostEff for OmniFold, efficiency-corrected for IBU)")
    ap.add_argument("--cross-section", action="store_true",
                help="Compare cross-section histograms (applies same normalization chain to all)")
    ap.add_argument("--unbinned", default=None,
                help="Unbinned OmniFold cross-section file for three-way comparison")
    ap.add_argument("--binned-xsec", default=None,
                help="Binned OmniFold cross-section file (overrides --omnifold for cross-section mode)")
    ap.add_argument("--mcfile", default=None,
                help="MC file (runEventLoopMC.root) for efficiency denominator in post-eff mode")
    ap.add_argument("--prefix", default="pTmu",
                help="Histogram prefix in MC file")
    return ap.parse_args()


def main():
    args = parse_args()
    xsec_mode = args.cross_section

    fO = ROOT.TFile.Open(args.omnifold, "READ")
    fI = ROOT.TFile.Open(args.ibu, "READ")
    if not fO or fO.IsZombie():
        raise RuntimeError(f"Failed to open {args.omnifold}")
    if not fI or fI.IsZombie():
        raise RuntimeError(f"Failed to open {args.ibu}")

    # Optional files
    fB = None
    if args.binned_xsec:
        fB = ROOT.TFile.Open(args.binned_xsec, "READ")
    fU = None
    if args.unbinned:
        fU = ROOT.TFile.Open(args.unbinned, "READ")

    iters_obj = fO.Get("iters")
    iters = int(iters_obj.GetVal()) if args.iters is None and iters_obj else (args.iters or 5)

    if xsec_mode:
        # Cross-section comparison: all histograms from cross-section files
        hIBU_mnv = get_obj(fI, "crossSection")
        hIBU_raw = mnvh1d_to_th1d_stat(hIBU_mnv, "ibu_xsec_raw")
        hTruth_mnv = get_obj(fI, "simulatedCrossSection")
        hTruthSel = mnvh1d_to_th1d_stat(hTruth_mnv, "truth_xsec")

        # Binned OmniFold cross-section
        if fB:
            hBdt_mnv = get_obj(fB, "crossSection")
            hUnfold = mnvh1d_to_th1d_stat(hBdt_mnv, "bdt_xsec")
        else:
            hUnfold = mnvh1d_to_th1d_stat(get_obj(fI, "crossSection"), "bdt_xsec_fallback")

        hIBU = remap_to_template_binning(hIBU_raw, hTruthSel, "ibu_xsec")

        # Dummy data/sim (not drawn in xsec mode)
        hMeasSub = hTruthSel.Clone("dummy_data")
        hSigReco = hTruthSel.Clone("dummy_sim")
    elif args.post_eff:
        # Post-efficiency: compare eff-corrected results against truth-denominator
        # (the full truth spectrum, NOT truth-selected)
        hMeasSub = to_th1d_copy(get_obj(fO, "hMeasSub"), "data_meassub")
        hSigReco = to_th1d_copy(get_obj(fO, "hSigReco"), "sim_sigreco")
        hUnfold = to_th1d_copy(get_obj(fO, "hUnfoldPostEff"), "omnifold_unfold")

        # Truth reference for post-eff is the efficiency denominator (full truth)
        if args.mcfile:
            fMC = ROOT.TFile.Open(args.mcfile, "READ")
            hTruthDen_mnv = get_obj(fMC, f"{args.prefix}_efficiency_denominator")
            hTruthSel = mnvh1d_to_th1d_stat(hTruthDen_mnv, "truth_den")
        else:
            # Fallback: compute truth_den = truth_sel / eff from binned-xsec file
            hTruthSelOrig = to_th1d_copy(get_obj(fO, "hTruthSel"), "truth_sel_orig")
            if fB:
                hEff_mnv = get_obj(fB, "efficiency")
                hEff = mnvh1d_to_th1d_stat(hEff_mnv, "eff_tmp")
                hTruthSel = hTruthSelOrig.Clone("truth_den")
                hTruthSel.Divide(hEff)
            else:
                hTruthSel = hTruthSelOrig

        # IBU post-eff: apply efficiency correction to IBU unfolded
        hIBU_pre = mnvh1d_to_th1d_stat(get_obj(fI, "unfolded"), "ibu_pre_raw")
        if fB:
            hEff_mnv = get_obj(fB, "efficiency")
            hEff = mnvh1d_to_th1d_stat(hEff_mnv, "eff_for_ibu")
            hIBU_raw = hIBU_pre.Clone("ibu_posteff_raw")
            hIBU_raw.Divide(hEff)
        else:
            hIBU_raw = hIBU_pre
        hIBU = remap_to_template_binning(hIBU_raw, hTruthSel, "ibu_stat")
    else:
        # Default: pre-efficiency comparison
        hMeasSub = to_th1d_copy(get_obj(fO, "hMeasSub"), "data_meassub")
        hSigReco = to_th1d_copy(get_obj(fO, "hSigReco"), "sim_sigreco")
        hTruthSel = to_th1d_copy(get_obj(fO, "hTruthSel"), "truth_sel")
        try:
            hUnfold = to_th1d_copy(get_obj(fO, "hUnfoldPreEff"), "omnifold_unfold")
        except RuntimeError:
            hUnfold = to_th1d_copy(get_obj(fO, "hUnfoldTruthSel"), "omnifold_unfold")
        hIBU_mnv = get_obj(fI, "unfolded")
        hIBU_raw = mnvh1d_to_th1d_stat(hIBU_mnv, "ibu_stat_raw")
        hIBU = remap_to_template_binning(hIBU_raw, hTruthSel, "ibu_stat")

    # Unbinned OmniFold (optional)
    h_unbinned_raw = None
    if fU:
        if xsec_mode:
            hUB_mnv = get_obj(fU, "crossSection")
            hUB_th1 = mnvh1d_to_th1d_stat(hUB_mnv, "ub_raw")
        else:
            # Try hUnfoldTruthSel first (raw OmniFold output), fall back to MnvH1D
            hUB_obj = fU.Get("hUnfoldTruthSel")
            if hUB_obj:
                hUB_th1 = to_th1d_copy(hUB_obj, "ub_raw")
            else:
                hUB_th1 = mnvh1d_to_th1d_stat(get_obj(fU, "unfolded_omnifold_sel"), "ub_raw")
            if args.post_eff and fB:
                # Apply efficiency correction: divide by efficiency
                hEff_ub = mnvh1d_to_th1d_stat(get_obj(fB, "efficiency"), "eff_for_ub")
                hUB_aligned = remap_to_template_binning(hUB_th1, hEff_ub, "ub_preeff_aligned")
                hUB_aligned.Divide(hEff_ub)
                hUB_th1 = hUB_aligned
        h_unbinned_raw = remap_to_template_binning(hUB_th1, hTruthSel, "ub_aligned")

    # Choose density vs counts
    if args.density:
        d_data = normalize_to_density(hMeasSub, "d_data")
        d_sim = normalize_to_density(hSigReco, "d_sim")
        d_truth = normalize_to_density(hTruthSel, "d_truth")
        d_ibu = normalize_to_density(hIBU, "d_ibu")
        d_bdt = normalize_to_density(hUnfold, "d_bdt")
        ytitle = "Probability density"
    else:
        d_data, d_sim, d_truth, d_ibu, d_bdt = hMeasSub, hSigReco, hTruthSel, hIBU, hUnfold
        ytitle = "Events"
    d_unbinned = None
    if h_unbinned_raw is not None:
        d_unbinned = normalize_to_density(h_unbinned_raw, "d_unbinned") if args.density else h_unbinned_raw

    # Style
    for h in (d_data, d_sim, d_truth, d_ibu, d_bdt):
        h.SetStats(False)
    style_data(d_data)
    style_sim(d_sim)
    style_truth_band(d_truth)
    style_ibu(d_ibu)
    style_bdt(d_bdt)
    if d_unbinned is not None:
        d_unbinned.SetStats(False)
        style_unbinned(d_unbinned)

    # Ratios (to truth)
    r_ibu = ratio(d_ibu, d_truth, "r_ibu")
    r_bdt = ratio(d_bdt, d_truth, "r_bdt")
    r_unbinned = None
    if d_unbinned is not None:
        r_unbinned = ratio(d_unbinned, d_truth, "r_unbinned")
        style_unbinned(r_unbinned)
    band = truth_ratio_band(d_truth, "truth_band")
    style_truth_band(band)

    # X range for ratio frame
    xmin = d_truth.GetXaxis().GetXmin()
    xmax = d_truth.GetXaxis().GetXmax()

    # Draw
    c, p1, p2 = make_canvas()
    p1.SetBottomMargin(0.015)
    p2.SetTopMargin(0.02)
    draw_top(p1, d_data, d_sim, d_truth, d_ibu, d_bdt, ytitle=ytitle, iters=iters,
             step=args.step, h_unbinned=d_unbinned, xsec_mode=xsec_mode, post_eff=args.post_eff)
    draw_bottom(p2, r_ibu, r_bdt, band, xmin, xmax, r_unbinned=r_unbinned)

    c.SaveAs(args.outpdf)
    print(f"[OK] wrote {args.outpdf}")


if __name__ == "__main__":
    main()
