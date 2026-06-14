#!/usr/bin/env python3
"""Build the 3D statistical-uncertainty band from the Poisson bootstrap replicas
(uq_3d/xsec_3d_boot*.root produced by sbatch_bootstrap_3d.sh).

Per bin, the statistical uncertainty is the std across replicas. We report it for
the Eavail-1D spectrum, the pT/p|| projections, and the Eavail-marginal 2D, and
write the band into a copy of the CV result (bin errors = bootstrap std) plus a
plot. The bootstrap mean should agree with the CV result (a closure check).

Run in the analysis env (root_6_28):
  python build_bootstrap_band_3d.py --cv xsec_3d_MEFHC_5iter_lgbm.root \
      --replicas 'uq_3d/xsec_3d_boot*.root' --out-prefix uq_3d/stat_band_3d
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT


def th1(f, name):
    h = f.Get(name)
    n = h.GetNbinsX()
    edges = np.array([h.GetBinLowEdge(i) for i in range(1, n + 2)])
    val = np.array([h.GetBinContent(i) for i in range(1, n + 1)])
    return edges, val


def th2(f, name):
    h = f.Get(name)
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return np.array([[h.GetBinContent(i, j) for j in range(1, ny + 1)]
                     for i in range(1, nx + 1)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cv", default="xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--replicas", default="uq_3d/xsec_3d_boot*.root")
    ap.add_argument("--out-prefix", default="uq_3d/stat_band_3d")
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    files = sorted(glob.glob(args.replicas))
    if not files:
        raise SystemExit(f"no replicas match {args.replicas}")
    axes = ["pt", "pz", "eavail"]
    stacks = {a: [] for a in axes}
    marg = []
    for fn in files:
        f = ROOT.TFile.Open(fn)
        if not f or f.IsZombie():
            continue
        ok = all(f.Get(f"hXSec_{a}") for a in axes) and f.Get("hXSec2D")
        if not ok:
            f.Close(); continue
        for a in axes:
            _, v = th1(f, f"hXSec_{a}")
            stacks[a].append(v)
        marg.append(th2(f, "hXSec2D"))
        f.Close()
    nrep = len(marg)
    print(f"[band] usable replicas: {nrep} / {len(files)} matched")
    if nrep < 2:
        raise SystemExit("need >=2 replicas")

    fcv = ROOT.TFile.Open(args.cv)
    edges = {a: th1(fcv, f"hXSec_{a}")[0] for a in axes}
    cv = {a: th1(fcv, f"hXSec_{a}")[1] for a in axes}
    cv_marg = th2(fcv, "hXSec2D")
    fcv.Close()

    # per-bin statistical band + bootstrap-mean closure
    band = {}
    print("\n=== statistical (bootstrap) uncertainty, median rel. per axis ===")
    for a in axes:
        arr = np.array(stacks[a])                 # (nrep, nbins)
        mean = arr.mean(0); std = arr.std(0, ddof=1)
        band[a] = (mean, std)
        nz = cv[a] > 0
        relmed = np.median(std[nz] / cv[a][nz]) if nz.any() else float("nan")
        bias = np.median((mean[nz] - cv[a][nz]) / cv[a][nz]) if nz.any() else 0
        print(f"  {a:7s}: median rel sigma = {relmed*100:5.2f} %   "
              f"(bootstrap-mean/CV-1 median = {bias*100:+.2f} %)")
    marr = np.array(marg)
    marg_std = marr.std(0, ddof=1)
    nz = cv_marg > 0
    print(f"  Eavail-marginal 2D: median rel sigma = "
          f"{np.median(marg_std[nz]/cv_marg[nz])*100:5.2f} %")

    # write band into a copy of the CV result (bin errors = bootstrap std)
    out_root = f"{args.out_prefix}.root"
    fo = ROOT.TFile.Open(out_root, "RECREATE")
    for a in axes:
        e = edges[a]; mean, std = band[a]
        h = ROOT.TH1D(f"hStat_{a}", f"3D xsec {a} CV +/- bootstrap stat",
                      len(e) - 1, np.asarray(e, float))
        for i in range(len(cv[a])):
            h.SetBinContent(i + 1, float(cv[a][i]))
            h.SetBinError(i + 1, float(std[i]))
        h.Write()
    fo.Close()

    # plot: CV +/- stat band on the 3 axes
    labels = {"pt": r"$p_T$ (GeV/c)", "pz": r"$p_\parallel$ (GeV/c)",
              "eavail": r"$E_{\rm avail}$ (GeV)"}
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, a in zip(axs, axes):
        e = edges[a]; c = e[:-1] + 0.5 * np.diff(e); _, std = band[a]
        sl = slice(0, len(cv[a]) - 1) if a == "eavail" else slice(0, len(cv[a]))
        ax.errorbar(c[sl], cv[a][sl], yerr=std[sl], fmt="o", ms=4, color="k",
                    capsize=2, label=f"unfolded $\\pm$ stat ({nrep} boot)")
        ax.set_xlabel(labels[a]); ax.set_ylabel(r"$d\sigma/d$" + a + " (cm$^2$/.../nucleon)")
        ax.grid(alpha=0.3)
        if a == "eavail":
            ax.legend(fontsize=9)
    fig.suptitle(f"3D unfolded result with bootstrap statistical band (N={nrep})")
    fig.tight_layout()
    fig.savefig(f"{args.out_prefix}.png", dpi=140)
    print(f"\n[band] wrote {out_root} and {args.out_prefix}.png")


if __name__ == "__main__":
    main()
