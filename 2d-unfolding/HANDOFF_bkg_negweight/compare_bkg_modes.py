#!/usr/bin/env python
"""Phase 3b analysis: purity vs negweight background-subtraction comparison.

Reads the hist-estimator comparison unfolds in runs/ and reports:
  - total cross section per (mode, seed) from the p_T projection (matches the
    driver's [CHECK] Total xsec print);
  - matched-seed direct comparison (negweight_s1 vs purity_s1): per-bin
    negweight/purity ratio map over hXSec2D and the total ratio;
  - per-method seed spread (purity {1,2}, negweight {1,2,3}).

Expectation (HANDOFF): negweight and purity agree at/below the ~3%
purity-correction scale, with differences concentrated where background
concentrates. No ROOT writing; read-only.
"""
import os
import sys
import ROOT
ROOT.gROOT.SetBatch(True)

RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
PURITY_SEEDS = [1, 2]
NEGWEIGHT_SEEDS = [1, 2, 3]
# Estimator tag selects which run set to compare: "hist" (default) or "exact".
EST = sys.argv[1] if len(sys.argv) > 1 else "hist"


def path(mode, seed):
    return os.path.join(RUNS, f"2d_xsec_{mode}_seed{seed}_{EST}5.root")


def total_from_projection(f, hname="hXSec_pt"):
    h = f.Get(hname)
    if not h:
        return None
    return sum(h.GetBinContent(i) * h.GetBinWidth(i)
               for i in range(1, h.GetNbinsX() + 1))


def load(mode, seed):
    p = path(mode, seed)
    if not os.path.exists(p):
        return None
    f = ROOT.TFile.Open(p)
    if not f or f.IsZombie():
        return None
    return f


def perbin_ratio(f_num, f_den, hname="hXSec2D", rel_floor=1e-3):
    """negweight/purity per-bin ratio over bins where purity is well-defined."""
    hn = f_num.Get(hname)
    hd = f_den.Get(hname)
    if not hn or not hd:
        return None
    vmax = max(hd.GetBinContent(ix, iy)
               for ix in range(1, hd.GetNbinsX() + 1)
               for iy in range(1, hd.GetNbinsY() + 1))
    ratios = []
    worst = (1.0, None)
    for ix in range(1, hd.GetNbinsX() + 1):
        for iy in range(1, hd.GetNbinsY() + 1):
            d = hd.GetBinContent(ix, iy)
            n = hn.GetBinContent(ix, iy)
            if d <= rel_floor * vmax:      # skip empty / negligible bins
                continue
            r = n / d
            ratios.append(r)
            if abs(r - 1.0) > abs(worst[0] - 1.0):
                worst = (r, (ix, iy,
                             hd.GetXaxis().GetBinCenter(ix),
                             hd.GetYaxis().GetBinCenter(iy)))
    if not ratios:
        return None
    ratios.sort()
    n = len(ratios)
    med = ratios[n // 2]
    import math
    rms = math.sqrt(sum((r - 1.0) ** 2 for r in ratios) / n)
    return dict(n=n, min=ratios[0], med=med, max=ratios[-1], rms=rms, worst=worst)


def main():
    print("=" * 74)
    print(f"Phase 3b: purity vs negweight ({EST} estimator, 5 iter, MEFHC)")
    print("=" * 74)

    # --- totals table ---
    print("\n[totals]  sigma_tot (p_T projection), cm^2/nucleon")
    files = {}
    for mode, seeds in [("purity", PURITY_SEEDS), ("negweight", NEGWEIGHT_SEEDS)]:
        for s in seeds:
            f = load(mode, s)
            files[(mode, s)] = f
            if f is None:
                print(f"  {mode:9s} seed {s}:  (missing)")
                continue
            tot = total_from_projection(f)
            print(f"  {mode:9s} seed {s}:  {tot:.4e}")

    def totals(mode, seeds):
        vals = [total_from_projection(files[(mode, s)])
                for s in seeds if files.get((mode, s))]
        return [v for v in vals if v is not None]

    pt = totals("purity", PURITY_SEEDS)
    nt = totals("negweight", NEGWEIGHT_SEEDS)
    if pt:
        mp = sum(pt) / len(pt)
        sp = (max(pt) - min(pt)) if len(pt) > 1 else 0.0
        print(f"\n[spread]  purity   : mean {mp:.4e}, range {sp:.2e} "
              f"({100*sp/mp:.2f}% over {len(pt)} seed(s))")
    if nt:
        mn = sum(nt) / len(nt)
        sn = (max(nt) - min(nt)) if len(nt) > 1 else 0.0
        print(f"[spread]  negweight: mean {mn:.4e}, range {sn:.2e} "
              f"({100*sn/mn:.2f}% over {len(nt)} seed(s))")
    if pt and nt:
        print(f"\n[compare] negweight/purity total (seed-mean): "
              f"{mn/mp:.4f}  ({100*(mn/mp-1):+.2f}%)")

    # --- matched-seed direct comparison (seed 1) ---
    fp1, fn1 = files.get(("purity", 1)), files.get(("negweight", 1))
    if fp1 and fn1:
        tp1 = total_from_projection(fp1)
        tn1 = total_from_projection(fn1)
        print(f"\n[matched seed 1] total: purity {tp1:.4e}, negweight {tn1:.4e}, "
              f"ratio {tn1/tp1:.4f} ({100*(tn1/tp1-1):+.2f}%)")
        r = perbin_ratio(fn1, fp1)
        if r:
            ix, iy, cx, cy = r["worst"][1]
            print(f"[matched seed 1] per-bin negweight/purity over hXSec2D "
                  f"({r['n']} populated bins):")
            print(f"    min={r['min']:.3f}  median={r['med']:.3f}  "
                  f"max={r['max']:.3f}  rms(dev from 1)={r['rms']:.3f}")
            print(f"    worst bin: ratio={r['worst'][0]:.3f} at "
                  f"(p_T={cx:.2f}, p_||={cy:.2f}) [bin {ix},{iy}]")
    print("\nCOMPARE_DONE")


if __name__ == "__main__":
    main()
