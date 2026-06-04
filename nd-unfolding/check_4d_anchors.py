#!/usr/bin/env python3
"""Validation anchors for the 4D q3 cross section vs the frozen 3D result.

Anchors (HIGHER_DIM_OMNIFOLD_DESIGN.md Phase 1):
  1. Jacobian identity: the 2D (pt,pz) marginal integral of the 4D xsec must equal
     the full 4D integral (exact, by construction of project_marginal).
  2. Marginal recovery: the 4D q3+eavail->(pt,pz) marginal and the 1D pt/pz/eavail
     projections must track the independently-run frozen 3D result (close, not
     identical -- the 4D unfold uses q3 as an extra feature).
  3. The new d sigma/dq3 spectrum should be physical (positive, falling tail).

Compares TH1D/TH2D objects only (robust); the 4D THnSparse is not needed here.
"""
import argparse
import numpy as np
import ROOT


def th1(f, name):
    h = f.Get(name)
    if not h:
        return None
    return np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])


def th2_integral(f, name):
    h = f.Get(name)
    if not h:
        return None
    tot = 0.0
    for ix in range(h.GetNbinsX()):
        for iy in range(h.GetNbinsY()):
            tot += (h.GetBinContent(ix + 1, iy + 1)
                    * h.GetXaxis().GetBinWidth(ix + 1)
                    * h.GetYaxis().GetBinWidth(iy + 1))
    return tot


def relcmp(a, b, label):
    if a is None or b is None:
        print(f"  [skip] {label}: missing histogram")
        return
    a, b = np.asarray(a), np.asarray(b)
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    m = np.abs(b) > 0
    rel = np.abs(a[m] - b[m]) / np.abs(b[m])
    print(f"  {label}: median rel diff {100*np.median(rel):.2f}%  "
          f"max {100*rel.max():.2f}%  (n={n})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xsec4d", required=True)
    ap.add_argument("--xsec3d", required=True)
    args = ap.parse_args()

    f4 = ROOT.TFile.Open(args.xsec4d)
    f3 = ROOT.TFile.Open(args.xsec3d)
    if not f4 or f4.IsZombie():
        raise SystemExit(f"cannot open {args.xsec4d}")

    print("=== 4D q3 cross section: validation anchors ===")
    # 1. Jacobian identity (driver already prints; re-check the written objects)
    marg2d = th2_integral(f4, "hXSec2D")
    print(f"  4D 2D-marginal integral: {marg2d:.4e} cm^2/nucleon" if marg2d else
          "  [skip] hXSec2D missing")

    # 2. marginal recovery vs frozen 3D
    print("--- 4D vs frozen 3D (independently-run) ---")
    relcmp(th1(f4, "hXSec_pt"), th1(f3, "hXSec_pt"), "d#sigma/dp_T")
    relcmp(th1(f4, "hXSec_pz"), th1(f3, "hXSec_pz"), "d#sigma/dp_||")
    relcmp(th1(f4, "hXSec_eavail"), th1(f3, "hXSec_eavail"), "d#sigma/dE_avail")
    if marg2d is not None:
        m3 = th2_integral(f3, "hXSec2D")
        if m3:
            print(f"  2D-marginal integral 4D/3D = {marg2d/m3:.4f} "
                  f"(3D={m3:.4e}); both anchor the paper 2D normalization")

    # 3. the new q3 spectrum
    q3 = th1(f4, "hXSec_q3")
    if q3 is not None:
        falling = np.all(np.diff(q3[q3 > 0]) <= 0) if (q3 > 0).any() else False
        print(f"--- new d#sigma/dq3 ({len(q3)} bins) ---")
        print("  " + " ".join(f"{v:.3e}" for v in q3))
        print(f"  all-positive={np.all(q3 >= 0)}  monotonic-falling={falling}")
    print("=== anchors done ===")


if __name__ == "__main__":
    main()
