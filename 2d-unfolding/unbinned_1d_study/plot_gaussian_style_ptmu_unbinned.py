#!/usr/bin/env python3
import argparse
from array import array

import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.TH1.AddDirectory(False)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)

_KEEP = []


def get_obj(f, name, required=True):
    obj = f.Get(name)
    if not obj:
        if required:
            raise RuntimeError(f"Missing '{name}' in {f.GetName()}")
        return None
    return obj


def clone_detached(h, name):
    c = h.Clone(name)
    c.SetDirectory(0)
    return c


def make_th1d_with_same_binning(src, name):
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


def to_th1d_copy(src, name):
    out = make_th1d_with_same_binning(src, name)
    for i in range(0, out.GetNbinsX() + 2):
        out.SetBinContent(i, src.GetBinContent(i))
        out.SetBinError(i, src.GetBinError(i))
    return out


def mnvh1d_to_th1d_stat(mnvh1d, name):
    if hasattr(mnvh1d, "GetCVHistoWithStatError"):
        h = mnvh1d.GetCVHistoWithStatError().Clone(name)
        h.SetDirectory(0)
        h.Sumw2()
        return h
    return to_th1d_copy(mnvh1d, name)


def normalize_to_density(h, name):
    hd = clone_detached(h, name)
    area = hd.Integral(1, hd.GetNbinsX(), "width")
    if area > 0:
        hd.Scale(1.0 / area)
    return hd


def ratio(num, den, name):
    r = clone_detached(num, name)
    r.Divide(den)
    return r


def truth_ratio_band(truth, name):
    b = clone_detached(truth, name)
    for i in range(1, b.GetNbinsX() + 1):
        y = truth.GetBinContent(i)
        e = truth.GetBinError(i)
        b.SetBinContent(i, 1.0)
        b.SetBinError(i, 0.0 if y == 0 else e / y)
    return b


def max_bin_content(h):
    m = 0.0
    for i in range(1, h.GetNbinsX() + 1):
        m = max(m, h.GetBinContent(i) + h.GetBinError(i))
    return m


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


def style_unbinned(h):
    h.SetLineColor(ROOT.kAzure + 1)
    h.SetLineWidth(3)
    h.SetMarkerStyle(0)
    h.SetFillStyle(0)


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


def draw_top(pad, h_data, h_sim, h_truth, h_ibu, h_unb, ytitle, iters, step, unfold_label):
    pad.cd()
    h_data.SetTitle(f";p_{{T}}^{{#mu}};{ytitle}")
    ymax = max(max_bin_content(h_data), max_bin_content(h_sim), max_bin_content(h_truth), max_bin_content(h_ibu), max_bin_content(h_unb))
    h_data.SetMaximum(1.35 * ymax)
    h_data.SetMinimum(0.0)
    h_data.GetXaxis().SetLabelSize(0)
    h_data.GetXaxis().SetTitleSize(0)

    h_data.Draw("E1")
    h_sim.Draw("HIST SAME")
    h_truth.Draw("E2 SAME")
    h_truth.Draw("HIST SAME")
    if step:
        h_ibu.SetMarkerSize(0)
        h_ibu.Draw("HIST SAME")
        h_ibu.Draw("E1 SAME")
        h_unb.SetMarkerSize(0)
        h_unb.Draw("HIST SAME")
        if any(h_unb.GetBinError(i) > 0 for i in range(1, h_unb.GetNbinsX() + 1)):
            h_unb.Draw("E1 SAME")
    else:
        h_ibu.Draw("E1 SAME")
        h_unb.Draw("E1 SAME" if any(h_unb.GetBinError(i) > 0 for i in range(1, h_unb.GetNbinsX() + 1)) else "HIST SAME")

    leg = ROOT.TLegend(0.55, 0.58, 0.87, 0.88)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0)
    leg.SetTextSize(0.033)
    leg.AddEntry(h_data, "Reco data (bkg sub)", "lep")
    leg.AddEntry(h_sim, "Sim. (signal reco)", "l")
    leg.AddEntry(h_truth, "Truth (MC truth sel)", "f")
    leg.AddEntry(h_ibu, "IBU (MINERvA, eff-corr) stat", "lep")
    leg.AddEntry(h_unb, f"{unfold_label} (iters={iters})", "l")
    leg.Draw()
    _KEEP.append(leg)


def draw_bottom(pad, r_ibu, r_unb, band, xmin, xmax):
    pad.cd()
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
    r_unb.Draw("E1 SAME")


def parse_args():
    ap = argparse.ArgumentParser(description="Gaussian-style comparison plot for unbinned OmniFold pTmu output.")
    ap.add_argument("--omnifold", default="pTmu_crossSection_omnifold.root")
    ap.add_argument("--ibu", default="pTmu_crossSection.root")
    ap.add_argument("--outpdf", default="ptmu_gaussian_style_unbinned.pdf")
    ap.add_argument("--outpng", default=None)
    ap.add_argument("--iters", type=int, default=None)
    ap.add_argument("--density", dest="density", action="store_true")
    ap.add_argument("--counts", dest="density", action="store_false")
    ap.set_defaults(density=True)
    ap.add_argument("--step", action="store_true")
    ap.add_argument("--label", default="OmniFold (unbinned)")
    return ap.parse_args()


def main():
    args = parse_args()
    f_o = ROOT.TFile.Open(args.omnifold, "READ")
    f_i = ROOT.TFile.Open(args.ibu, "READ")
    if not f_o or f_o.IsZombie():
        raise RuntimeError(f"Failed to open {args.omnifold}")
    if not f_i or f_i.IsZombie():
        raise RuntimeError(f"Failed to open {args.ibu}")

    hMeasSub = to_th1d_copy(get_obj(f_o, "hMeasSub"), "data_meassub")
    hSigReco = to_th1d_copy(get_obj(f_o, "hSigReco"), "sim_sigreco")
    hTruthSel = to_th1d_copy(get_obj(f_o, "hTruthSel"), "truth_sel")
    # Post-Phase-16: prefer the input-completeness-corrected unfold
    # (hUnfoldTruthSel divided by hOFCompleteness per bin) so this sits
    # on the canonical truth phase space (mc_truth_denom), apples-to-
    # apples with IBU's crossSection (whose efficiency denominator is
    # the canonical mc_truth-tree-loop denominator from runEventLoop).
    # Falls back to the bare hUnfoldTruthSel for pre-Phase-16 inputs
    # with a warning that the comparison is offset by ~1/c ~ 1.3x.
    h_unf_corr = get_obj(f_o, "hUnfoldTruthSel_completeness_corrected",
                         required=False)
    if h_unf_corr is not None:
        hUnfold = to_th1d_copy(h_unf_corr, "unbinned_unfold")
    else:
        print("[WARN] hUnfoldTruthSel_completeness_corrected not present; "
              "using hUnfoldTruthSel (pre-Phase-16 subset truth — "
              "comparison vs IBU is biased by ~1/c, ~1.3x at 1A).")
        hUnfold = to_th1d_copy(get_obj(f_o, "hUnfoldTruthSel"),
                               "unbinned_unfold")
    iters_obj = get_obj(f_o, "iters")
    iters = int(iters_obj.GetVal()) if args.iters is None else int(args.iters)

    # Both legs now sit on the canonical truth phase space (mc_truth_denom):
    # OmniFold via the Phase-16 input-completeness correction,
    # IBU via runEventLoop's hEffDen (the standard truth-tree denominator).
    # IBU's `crossSection` MnvH1D = efficiencyCorrected / flux / nucleons / dpt;
    # multiply by binwidth to get back to per-bin event-yield units that
    # match the OmniFold-side histograms.
    hIBU_mnv = get_obj(f_i, "crossSection")
    hIBU = mnvh1d_to_th1d_stat(hIBU_mnv, "ibu_stat")
    for ib in range(1, hIBU.GetNbinsX() + 1):
        w = hIBU.GetBinWidth(ib)
        hIBU.SetBinContent(ib, hIBU.GetBinContent(ib) * w)
        hIBU.SetBinError(ib, hIBU.GetBinError(ib) * w)

    if args.density:
        d_data = normalize_to_density(hMeasSub, "d_data")
        d_sim = normalize_to_density(hSigReco, "d_sim")
        d_truth = normalize_to_density(hTruthSel, "d_truth")
        d_ibu = normalize_to_density(hIBU, "d_ibu")
        d_unb = normalize_to_density(hUnfold, "d_unb")
        ytitle = "Probability density"
    else:
        d_data, d_sim, d_truth, d_ibu, d_unb = hMeasSub, hSigReco, hTruthSel, hIBU, hUnfold
        ytitle = "Events"

    for h in (d_data, d_sim, d_truth, d_ibu, d_unb):
        h.SetStats(False)
    style_data(d_data)
    style_sim(d_sim)
    style_truth_band(d_truth)
    style_ibu(d_ibu)
    style_unbinned(d_unb)

    r_ibu = ratio(d_ibu, d_truth, "r_ibu")
    r_unb = ratio(d_unb, d_truth, "r_unb")
    band = truth_ratio_band(d_truth, "truth_band")
    style_truth_band(band)

    xmin = d_truth.GetXaxis().GetXmin()
    xmax = d_truth.GetXaxis().GetXmax()

    c, p1, p2 = make_canvas()
    p1.SetBottomMargin(0.015)
    p2.SetTopMargin(0.02)
    draw_top(p1, d_data, d_sim, d_truth, d_ibu, d_unb, ytitle, iters, args.step, args.label)
    draw_bottom(p2, r_ibu, r_unb, band, xmin, xmax)
    c.SaveAs(args.outpdf)
    print(f"[OK] wrote {args.outpdf}")
    if args.outpng:
        c.SaveAs(args.outpng)
        print(f"[OK] wrote {args.outpng}")


if __name__ == "__main__":
    main()
