#!/usr/bin/env python3
"""(E_avail, W) generator band vs the unfolded data -- the multi-generator answer
to open question 6 (is the high-E_avail/high-W excess generator/tune dependent?).

Reads the unfolded data (E_avail,W) cross section (products/5d/excess_eavail_W.root::
hData2D, 7x6 eavail x W) and one or more generator predictions in the SAME binning
(gen_to_xsec_eavailW.py / nuwro_to_xsec_eavailW.py output: hXSec_eavailW, hXSec_eavail,
hXSec_W). Reports, per generator: the dsigma/dEavail and dsigma/dW overlays, the
high-W (W>=1.8 GeV) integrated cross section vs data, and what fraction of the data's
high-Eavail x high-W excess each generator accounts for. Writes a 2-panel PNG.

  python overlay_eavailW_band.py \
      --data ../../nd-unfolding/products/5d/excess_eavail_W.root \
      --gen GENIE-CV:genie_cv_xsec_eavailW.root \
      --gen GENIE+MEC:genie_mec_xsec_eavailW.root \
      --gen NuWro:nuwro_cv_xsec_eavailW.root \
      --png eavailW_band.png --out eavailW_band.root
"""
import argparse
import os

import numpy as np
import ROOT
ROOT.gROOT.SetBatch(True)

EAVAIL_EDGES = np.asarray([0.0, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0, 100.0], float)
W_EDGES = np.asarray([0.0, 1.1, 1.4, 1.8, 2.2, 3.0, 100.0], float)


def th2_to_np(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    a = np.zeros((nx, ny))
    for i in range(nx):
        for j in range(ny):
            a[i, j] = h.GetBinContent(i + 1, j + 1)
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True)
    ap.add_argument("--gen", action="append", default=[],
                    help="label:file.root (repeatable)")
    ap.add_argument("--png", default="eavailW_band.png")
    ap.add_argument("--out", default="eavailW_band.root")
    args = ap.parse_args()

    fd = ROOT.TFile.Open(args.data)
    data2d = th2_to_np(fd.Get("hData2D"))           # (eavail, W) xsec
    fd.Close()
    dea = np.diff(EAVAIL_EDGES)[:, None]
    dw = np.diff(W_EDGES)[None, :]
    data_ea = (data2d * dw).sum(axis=1)             # dsigma/dEavail
    data_w = (data2d * dea).sum(axis=0)             # dsigma/dW
    data_tot = float((data2d * dea * dw).sum())

    # high-Eavail (>=0.8 -> index 4..) x high-W (>=1.8 -> index 3..) corner
    eav_hi = EAVAIL_EDGES[:-1] >= 0.8
    w_hi = W_EDGES[:-1] >= 1.8
    corner = np.outer(eav_hi, w_hi)
    data_corner = float((data2d * dea * dw)[corner].sum())

    gens = {}
    for spec in args.gen:
        label, fn = spec.split(":", 1)
        if not os.path.exists(fn):
            print(f"[band] MISSING {label}: {fn} (skip)"); continue
        f = ROOT.TFile.Open(fn)
        g2d = th2_to_np(f.Get("hXSec_eavailW"))
        f.Close()
        gens[label] = g2d
        g_tot = float((g2d * dea * dw).sum())
        g_corner = float((g2d * dea * dw)[corner].sum())
        # how much of the DATA-CV corner excess does this generator's deficit leave?
        print(f"[band] {label}: total={g_tot:.4e} (data {data_tot:.4e}, ratio {data_tot/g_tot:.3f}); "
              f"hiE-hiW corner={g_corner:.4e} (data {data_corner:.4e}, "
              f"data/gen={data_corner/g_corner:.3f})")

    # dsigma/dW: the decisive curve (does any generator rise into the high-W tail?)
    print("\n=== dsigma/dW (data vs generators) ===")
    hdr = "  W band      " + "  ".join(f"{'data':>10}") + "  " + "  ".join(f"{l:>10}" for l in gens)
    print("  W band         data   " + "   ".join(f"{l:>10}" for l in gens))
    for j in range(len(W_EDGES) - 1):
        row = f"  {W_EDGES[j]:4.1f}-{W_EDGES[j+1]:5.1f}  {data_w[j]:10.3e}"
        for l in gens:
            gw = (gens[l] * dea).sum(axis=0)[j]
            row += f"   {gw:10.3e}"
        print(row)

    # ROOT + PNG
    fo = ROOT.TFile.Open(args.out, "RECREATE")
    c = ROOT.TCanvas("c", "eavailW band", 1400, 600)
    c.Divide(2, 1)
    colors = [ROOT.kRed + 1, ROOT.kBlue + 1, ROOT.kGreen + 2, ROOT.kMagenta + 1, ROOT.kOrange + 7]

    def mk_th1(edges, vals, name, title, xmax):
        # drop the wide [last,100] catch bin from the PLOT (negligible content, but
        # its 100-GeV edge otherwise stretches the whole x-axis)
        e = np.asarray(edges[:-1], float)
        h = ROOT.TH1D(name, title, len(e) - 1, e)
        for i in range(len(e) - 1):
            h.SetBinContent(i + 1, float(vals[i]))
        h.SetStats(0)
        return h

    # panel 1: dsigma/dEavail  (physical range 0-3.5; the 3-100 catch bin is off-screen)
    c.cd(1); ROOT.gPad.SetLogy()
    hd = mk_th1(EAVAIL_EDGES, data_ea, "hData_ea", "d#sigma/dE_{avail};E_{avail} (GeV);d#sigma/dE_{avail}", 3.5)
    ymax = max(data_ea.max(), max((g * dw).sum(axis=1).max() for g in gens.values()) if gens else 0)
    hd.SetMaximum(ymax * 3); hd.SetMinimum(ymax * 1e-3)
    hd.SetLineColor(ROOT.kBlack); hd.SetLineWidth(3); hd.SetMarkerStyle(20); hd.SetMarkerSize(1.2); hd.Draw("P")
    hd.Write()
    leg1 = ROOT.TLegend(0.5, 0.65, 0.88, 0.88); leg1.AddEntry(hd, "data (unfolded)", "lep")
    keep = [hd]
    for k, l in enumerate(gens):
        ge = (gens[l] * dw).sum(axis=1)
        h = mk_th1(EAVAIL_EDGES, ge, f"hEa_{l}", l, 3.5)
        h.SetLineColor(colors[k % len(colors)]); h.SetLineWidth(2); h.Draw("HIST SAME")
        leg1.AddEntry(h, l, "l"); h.Write(); keep.append(h)
    leg1.Draw()

    # panel 2: dsigma/dW (the decisive one)
    c.cd(2); ROOT.gPad.SetLogy()
    hdw = mk_th1(W_EDGES, data_w, "hData_W", "d#sigma/dW;W (GeV);d#sigma/dW", 3.2)
    ywmax = max(data_w.max(), max((g * dea).sum(axis=0).max() for g in gens.values()) if gens else 0)
    hdw.SetMaximum(ywmax * 3); hdw.SetMinimum(ywmax * 1e-3)
    hdw.SetLineColor(ROOT.kBlack); hdw.SetLineWidth(3); hdw.SetMarkerStyle(20); hdw.SetMarkerSize(1.2); hdw.Draw("P")
    hdw.Write()
    leg2 = ROOT.TLegend(0.5, 0.65, 0.88, 0.88); leg2.AddEntry(hdw, "data (unfolded)", "lep")
    for k, l in enumerate(gens):
        gw = (gens[l] * dea).sum(axis=0)
        h = mk_th1(W_EDGES, gw, f"hW_{l}", l, 3.2)
        h.SetLineColor(colors[k % len(colors)]); h.SetLineWidth(2); h.Draw("HIST SAME")
        leg2.AddEntry(h, l, "l"); h.Write(); keep.append(h)
    leg2.Draw()
    c.SaveAs(args.png)
    c.Write()
    fo.Close()
    print(f"\n[band] wrote {args.png} and {args.out}")


if __name__ == "__main__":
    main()
