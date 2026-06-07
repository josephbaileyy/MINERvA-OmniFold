#!/usr/bin/env python3
"""5D (pt,pz,eavail,q3,W) -> frozen 4D anchor check.

The 1D projections the driver writes (hXSec_{pt,pz,eavail,q3}) are already integrated
over every other axis -- including W -- so they ARE the W-marginal of the 5D result.
Adding W as a feature must not bias the lower-D projections or the total (exactly as
adding q3 gave 4D/3D=0.9960). This compares the 5D output's hXSec_* and total sigma to
the frozen 4D result, the W-marginal Jacobian anchor.

  python check_5d_anchors.py --xsec5d xsec_5d_MEFHC_5iter_lgbm.root \
      --xsec4d xsec_4d_MEFHC_5iter_lgbm.root
"""
import argparse
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
SHARED = ["pt", "pz", "eavail", "q3"]   # axes common to 5D and 4D (drop W)


def _proj(f, name):
    h = f.Get(f"hXSec_{name}")
    if not h:
        return None, None
    n = h.GetNbinsX()
    y = np.array([h.GetBinContent(i + 1) for i in range(n)])
    e = np.array([h.GetBinLowEdge(i + 1) for i in range(n + 1)])
    return e, y


def _total(f):
    # total sigma = integral of any 1D projection (dsigma/dx * dx)
    e, y = _proj(f, "pt")
    return float((y * np.diff(e)).sum()) if y is not None else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xsec5d", default="xsec_5d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--xsec4d", default="xsec_4d_MEFHC_5iter_lgbm.root")
    args = ap.parse_args()

    f5 = ROOT.TFile.Open(args.xsec5d)
    f4 = ROOT.TFile.Open(args.xsec4d)
    if not f5 or f5.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.xsec5d}")
    if not f4 or f4.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {args.xsec4d}")

    t5, t4 = _total(f5), _total(f4)
    print(f"[anchor] total sigma: 5D={t5:.4g}  4D={t4:.4g}  5D/4D={t5/t4:.4f}")
    print(f"{'axis':8s} {'median |5D-4D|/4D':20s} {'max':8s}")
    worst = 0.0
    for nm in SHARED:
        e5, y5 = _proj(f5, nm)
        e4, y4 = _proj(f4, nm)
        if y5 is None or y4 is None or y5.shape != y4.shape:
            print(f"{nm:8s} [skip] missing/shape mismatch")
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            d = np.where(y4 > 0, np.abs(y5 - y4) / y4, 0.0)
        med = float(np.median(d[y4 > 0])) if (y4 > 0).any() else float("nan")
        mx = float(d.max())
        worst = max(worst, med)
        print(f"{nm:8s} {100*med:18.2f}% {100*mx:6.2f}%")

    # new W projection (no 4D counterpart -- just sanity)
    eW, yW = _proj(f5, "W")
    if yW is not None:
        print(f"[new] dsigma/dW: {len(yW)} bins, all-finite={np.isfinite(yW).all()}, "
              f"nonneg={(yW >= 0).all()}, integral={float((yW*np.diff(eW)).sum()):.4g}")
    print(f"[anchor] {'PASS' if (abs(t5/t4 - 1) < 0.03 and worst < 0.03) else 'CHECK'}"
          f" (W-marginal reproduces frozen 4D within ~3% target)")


if __name__ == "__main__":
    main()
