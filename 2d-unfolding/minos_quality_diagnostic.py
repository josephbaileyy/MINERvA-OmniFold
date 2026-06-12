#!/usr/bin/env python3
"""MINOS muon-quality cut diagnostic for the low-p_|| sum-ratio gradient (KNOWN_ISSUES #5).

Hypothesis: the residual data/MC sum-ratio gradient (0.6 at p_||=1.5-2 GeV/c rising
to ~1.0 above 20; see 2D_OMNIFOLD_REFERENCE.md SS IsMinosMatchMuon) comes from the
official MasterAnaDev muon-quality selection that the MINERvA-101 tutorial path
omits: MINOS track quality (minos_trk_quality==1; 23.5% of matched MC events are
quality-2) and the curvature-significance cut for curvature-momentum tracks
(|eqp_qp / qp| < 0.3 when minos_used_curvature). fit_pass is already implied by our
patched IsMinosMatchMuon (verified: 100% of matched events), and NoDeadtime(1) is
already in the preCuts, so those are NOT candidates.

Method (no event-loop rebuild, no unfold): conditional efficiency among
already-selected events. Over the 1A AnaTuples (data + MC, read via xrootd):

  base   = isMinosMatchTrack==1 && minos_trk_is_ok==1 && tdead==0 && fiducial vertex
  eff_X(p) = N(base && newcut)(p) / N(base)(p)     for X = data, MC

binned in p_MINOS = minos_trk_p (the variable the quality cuts act on; ~p_|| minus
the MINERvA-side energy at theta<20deg). The corrected sum ratio would be
baseline_ratio x eff_data/eff_MC, so the diagnostic answers: does the double ratio
eff_data/eff_MC rise from <1 at low p toward 1 at high p (cuts close the gradient),
or is it flat ~1 (cuts are not the cause)?

Counts are unweighted on both sides (reco-quality cut efficiency; MC event weights
cancel to first order in the double ratio). Helicity / muon-angle cuts are not
re-applied -- they are common to numerator and denominator and cancel in the
conditional efficiency.

  python minos_quality_diagnostic.py --max-mc-files 41 --max-data-files 120
"""
import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
_PL = f"{_REPO}/MINERvA101/MINERvA-101-Cross-Section/playlists"

# CCInclusive fiducial (runEventLoopOmniFold.cpp preCuts: ZRange Tracker, Apothem)
MIN_Z, MAX_Z, APOTHEM = 5980.0, 8422.0, 850.0

P_EDGES = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 60.0]

# Fiducial here is a RADIAL approximation of the hexagonal apothem cut -- it is
# part of the conditioning common to numerator and denominator, so the exact
# hexagon cancels in the eff_data/eff_MC double ratio.
BASE = ("isMinosMatchTrack==1 && MasterAnaDev_minos_trk_is_ok==1 "
        "&& phys_n_dead_discr_pair_upstream_prim_track_proj==0 "
        f"&& vtx[2]>{MIN_Z} && vtx[2]<{MAX_Z} "
        f"&& sqrt(vtx[0]*vtx[0]+vtx[1]*vtx[1])<{APOTHEM}")
Q1 = "MasterAnaDev_minos_trk_quality==1"
# Two readings of the curvature-significance branch (the official cut is sigma(q/p)
# significance < 0.3 for curvature-momentum tracks; eqp_qp is named like the
# already-fractional error but we test both interpretations):
CURV_A = ("(MasterAnaDev_minos_used_curvature==0 || "
          "fabs(MasterAnaDev_minos_trk_eqp_qp)<0.3)")
CURV_B = ("(MasterAnaDev_minos_used_curvature==0 || "
          "(MasterAnaDev_minos_trk_qp!=0 && "
          "fabs(MasterAnaDev_minos_trk_eqp_qp/MasterAnaDev_minos_trk_qp)<0.3))")
PVAR = "MasterAnaDev_minos_trk_p/1000.0"


def chain_files(playlist, nmax):
    with open(playlist) as fh:
        files = [l.strip() for l in fh if l.strip()]
    return files[:nmax] if nmax else files


def counts(df, edges):
    import ROOT  # noqa: F401
    eb = np.asarray(edges, float)
    d = df.Define("p_minos", PVAR).Filter(BASE)
    dq = d.Filter(Q1)
    hists = [d.Histo1D(("b", "b", len(eb) - 1, eb), "p_minos"),
             dq.Histo1D(("q", "q", len(eb) - 1, eb), "p_minos"),
             dq.Filter(CURV_A).Histo1D(("qa", "qa", len(eb) - 1, eb), "p_minos"),
             dq.Filter(CURV_B).Histo1D(("qb", "qb", len(eb) - 1, eb), "p_minos")]
    return [np.array([h.GetBinContent(i + 1) for i in range(h.GetNbinsX())])
            for h in hists]  # base, q1, q1+curvA, q1+curvB


def main():
    import ROOT
    ROOT.EnableImplicitMT()

    ap = argparse.ArgumentParser()
    ap.add_argument("--mc-playlist", default=f"{_PL}/MAD_minervame1A_MC_xrd.txt")
    ap.add_argument("--data-playlist", default=f"{_PL}/MAD_minervame1A_DATA_xrd.txt")
    ap.add_argument("--max-mc-files", type=int, default=41)
    ap.add_argument("--max-data-files", type=int, default=120)
    ap.add_argument("--out-png", default="products/minos_quality_diagnostic.png")
    args = ap.parse_args()

    res = {}
    for tag, pl, nmax in (("mc", args.mc_playlist, args.max_mc_files),
                          ("data", args.data_playlist, args.max_data_files)):
        files = chain_files(pl, nmax)
        print(f"[{tag}] {len(files)} files", flush=True)
        ch = ROOT.TChain("MasterAnaDev")
        for fn in files:
            ch.Add(fn)
        df = ROOT.RDataFrame(ch)
        res[tag] = counts(df, P_EDGES)
        print(f"[{tag}] base={res[tag][0].sum():.0f} q1={res[tag][1].sum():.0f} "
              f"q1+curvA={res[tag][2].sum():.0f} q1+curvB={res[tag][3].sum():.0f}", flush=True)

    e = np.asarray(P_EDGES)
    ctr = 0.5 * (e[:-1] + e[1:])

    def eff(tag, i):
        b = res[tag][0]
        return np.divide(res[tag][i], b, out=np.zeros_like(b), where=b > 0)

    def dr(i):
        return np.divide(eff("data", i), eff("mc", i),
                         out=np.zeros_like(ctr), where=eff("mc", i) > 0)

    labels = {1: "q1", 2: "q1+curvA(|eqp_qp|<0.3)", 3: "q1+curvB(/qp<0.3)"}
    print(f"\n{'p_MINOS bin':>14s} | " + " | ".join(
        f"{'effD':>7s} {'effMC':>7s} {'DR':>7s} [{labels[i]}]" for i in (1, 2, 3)))
    drs = {i: dr(i) for i in (1, 2, 3)}
    for k in range(len(ctr)):
        row = " | ".join(f"{eff('data',i)[k]:7.4f} {eff('mc',i)[k]:7.4f} {drs[i][k]:7.4f}"
                         for i in (1, 2, 3))
        print(f"{e[k]:6.1f}-{e[k+1]:<6.1f} | {row}")

    lo = slice(0, 3)   # 1.0-2.5 GeV
    hi = slice(8, 12)  # 10-60 GeV
    for i in (1, 2, 3):
        print(f"[verdict inputs] DR({labels[i]}): low-p (1-2.5 GeV) mean="
              f"{np.nanmean(drs[i][lo]):.4f}  high-p (10-60 GeV) mean={np.nanmean(drs[i][hi]):.4f}")
    print("[verdict] corrected sum ratio = baseline x DR. Baseline is ~0.6 at low p_||,"
          " ~1.0 at high p_||. The cuts CLOSE the gradient only if DR rises to ~1.67"
          " at low p (cuts remove far more MC than data there) while staying ~1.0 at"
          " high p. DR ~ 1 everywhere = quality cuts are NOT the cause.")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    styles = {1: "-", 2: "--", 3: ":"}
    for i in (1, 2, 3):
        axes[0].plot(ctr, eff("data", i), "o" + styles[i], color="k", label=f"data {labels[i]}")
        axes[0].plot(ctr, eff("mc", i), "s" + styles[i], color="tab:red", label=f"MC {labels[i]}")
        axes[1].plot(ctr, drs[i], "o" + styles[i], label=f"DR {labels[i]}")
    axes[0].set_xscale("log"); axes[0].set_xlabel("p(MINOS) [GeV/c]")
    axes[0].set_ylabel("efficiency of added cut(s) | base"); axes[0].legend(fontsize=7)
    axes[1].axhline(1.0, color="gray", lw=0.8)
    axes[1].set_xscale("log"); axes[1].set_xlabel("p(MINOS) [GeV/c]")
    axes[1].set_ylabel("eff_data / eff_MC"); axes[1].legend(fontsize=8)
    fig.suptitle("MINOS muon-quality cut diagnostic (1A, conditional on base selection)")
    fig.tight_layout()
    os.makedirs(os.path.dirname(args.out_png) or ".", exist_ok=True)
    fig.savefig(args.out_png, dpi=140)
    print(f"[done] wrote {args.out_png}")


if __name__ == "__main__":
    main()
