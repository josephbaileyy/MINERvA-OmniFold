#!/usr/bin/env python3
"""Did enabling Valencia 2p2h/MEC move GENIE toward the data in the low-Eavail
dip? Compare dsigma/dEavail for data vs base GENIE-CV (no MEC) vs GENIE-CV+MEC
(--event-generator-list Default+CCMEC), with the combined-covariance band on the
data, and quantify how much of the dip deficit the MEC fills, per bin.

Run in the analysis env (root_6_28):
  python compare_mec_eavail.py --plot compare_mec_eavail.png
"""
import argparse
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d
from overlay_generators_band import (build_projectors, project_cov, load_cov,
                                      load_th3)

EA = np.asarray(u3d.EAVAIL_EDGES, float)
PT = np.asarray(u3d.PT_EDGES, float)
PZ = np.asarray(u3d.PZ_EDGES, float)


def get_h(path, hname):
    p = path if os.path.isabs(path) else os.path.join(HERE, path)
    f = ROOT.TFile.Open(p)
    h = f.Get(hname)
    v = np.array([h.GetBinContent(b) for b in range(1, h.GetNbinsX() + 1)])
    f.Close()
    return v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="../xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--cv", default="genie_cv_xsec3d.root")
    ap.add_argument("--mec", default="genie_mec_cv_xsec3d.root")
    ap.add_argument("--cov", default="uq_3d/universe_stage2_3d/"
                    "uq_universe_3d_covariance.root")
    ap.add_argument("--plot", default=None)
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError

    data = get_h(args.data, "hXSec_eavail")
    cv = get_h(args.cv, "hXSec_eavail")
    mec_tot = get_h(args.mec, "hXSec_eavail")          # CV+MEC
    mec_only = get_h(args.mec, "hXSec_eavail_mec")      # MEC contribution
    nb = data.size
    dea = np.diff(EA)

    # combined-cov band on E_avail
    Cfull = load_cov(args.cov + ":hCov_combined3d_total")
    cv3d, _ = load_th3(args.data, "hXSec3D")
    J, _ = build_projectors(cv3d, (PT, PZ, EA))
    sig = project_cov(Cfull, J)["eavail"][1]

    hdr = ("bin  Eavail[GeV]    data       CV    CV+MEC   MEC   | (d-CV)/s "
           "(d-CV-MEC)/s | dip closed%")
    print(hdr); print("-" * len(hdr))
    for b in range(nb):
        rcv = (data[b] - cv[b]) / sig[b]
        rmec = (data[b] - mec_tot[b]) / sig[b]
        closed = (100 * (mec_tot[b] - cv[b]) / (data[b] - cv[b])
                  if (data[b] - cv[b]) > 1e-42 else float("nan"))
        tag = " catch" if b == nb - 1 else ""
        print(f"{b:3d} [{EA[b]:4.2f},{EA[b+1]:5.2f}) {data[b]:.2e} {cv[b]:.2e} "
              f"{mec_tot[b]:.2e} {mec_only[b]:.1e} | {rcv:+6.2f} {rmec:+8.2f}  "
              f"| {closed:6.1f}{tag}")

    s = slice(0, nb - 1)
    iD = (data[s] * dea[s]).sum(); iCV = (cv[s] * dea[s]).sum()
    iM = (mec_tot[s] * dea[s]).sum()
    print(f"\n[integrated, catch bin dropped]")
    print(f"  data={iD:.3e}  CV={iCV:.3e} ({100*(iCV-iD)/iD:+.1f}%)  "
          f"CV+MEC={iM:.3e} ({100*(iM-iD)/iD:+.1f}%)")
    print(f"  MEC added {iM-iCV:+.2e} = {100*(iM-iCV)/(iD-iCV):.0f}% of the "
          f"integrated deficit")
    # dip-only (Eavail <= 0.4): bins 1,2 (and 0)
    dip = (EA[1:nb] <= 0.4)
    dD = (data[:nb-1][dip] - cv[:nb-1][dip]); dM = (mec_tot[:nb-1][dip] - cv[:nb-1][dip])
    print(f"  in the dip (Eavail<=0.4): MEC fills {100*dM.sum()/dD.sum():.0f}% "
          f"of the data-CV gap")

    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        n = nb - 1
        ctr = 0.5 * (EA[:n] + EA[1:n+1]); w = dea[:n]
        fig, ax = plt.subplots(figsize=(7.6, 5.3))
        ax.bar(ctr, cv[:n], width=w*0.92, color="#cfe3ff", edgecolor="#1f77b4",
               label="GENIE-CV (no 2p2h)")
        ax.bar(ctr, mec_only[:n], width=w*0.92, bottom=cv[:n], color="#d62728",
               alpha=0.75, label="+ Valencia MEC (2p2h)")
        ax.errorbar(ctr, data[:n], yerr=sig[:n], fmt="o", color="k", ms=5,
                    capsize=3, label="unfolded data $\\pm$ total", zorder=5)
        ax.set_xlabel("$E_{avail}$ (GeV)")
        ax.set_ylabel(r"$d\sigma/dE_{avail}$ (cm$^2$/nucleon/GeV)")
        ax.set_title("Enabling Valencia 2p2h fills part of the low-$E_{avail}$ dip")
        ax.legend(fontsize=9); ax.set_xlim(EA[0], EA[n])
        fig.tight_layout(); fig.savefig(args.plot, dpi=130)
        print(f"[compare-mec] wrote {args.plot}")


if __name__ == "__main__":
    main()
