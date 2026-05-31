#!/usr/bin/env python3
"""Apply GENIE single-parameter reweight (grwght1p) weights to the CV gst events
and rebuild d^3 sigma/(dpT dp|| dEavail) at each tweak-dial value -- to quantify
an FSI dial's effect (default FrInel_pi), especially on the Eavail spectrum, the
FSI-sensitive axis (uq_statistical_methods open question #2).

Each shard pairs (gst, weights_<DIAL>.root); the weight tree's `eventnum` ==
gst `iev`, so weights align to events per row. FSI only redistributes the final
state -- the total CC cross section is fixed -- so each dial's spectrum is
normalised by *that dial's* weighted CC sum (sigma_nuc x w_bin / w_allCC). The
dial=0 column therefore reproduces the CV result exactly (built-in closure);
the off-CV columns are the +-Nsigma FSI variations.

Reuses genie_to_xsec3d's truth-Eavail / phase-space / splines-normalisation
machinery. Run in the analysis env (root_6_28); source setup_genie.sh first (or
pass --graphs/--flux).

  python fsi_variation_xsec3d.py --shards 'work_p*' --dial FrInel_pi \
      --graphs <xsec_graphs.root> --flux "$GENIE_FLUX" \
      --out genie_fsi_FrInel_pi_xsec3d.root
"""
import argparse
import glob
import os
import sys

import numpy as np
import ROOT

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))          # 3d-unfolding/
sys.path.insert(0, HERE)
import unfold_3d_omnifold_unbinned as u3d
from xsec_3d import project_eavail_marginal, project_axis
import genie_to_xsec3d as g3  # eavail_true, flux_avg_sigma_cc_per_nucleon, edges

PT, PZ, EA = g3.PT_EDGES, g3.PZ_EDGES, g3.EAVAIL_EDGES
in_ps = g3.in_ps

# genie_xsec product ships xsec_graphs.root on CVMFS (not beside the local
# reduced splines); same default the CV run used.
GRAPHS_DEFAULT = ("/cvmfs/larsoft.opensciencegrid.org/products/genie_xsec/"
                  "v2_12_10/NULL/DefaultPlusValenciaMEC/data/xsec_graphs.root")


def read_weights(path, dial):
    """Return (twkdials[n_points], weights[n_events, n_points]) indexed by
    eventnum (== gst iev; grwght1p writes a contiguous [0,N) range)."""
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open weights file {path}")
    t = f.Get(dial)
    if not t:
        raise RuntimeError(f"weight tree '{dial}' not in {path}")
    n = int(t.GetEntries())
    t.GetEntry(0)
    npts = int(t.twkdials.GetSize())
    twk = np.array([t.twkdials.At(k) for k in range(npts)], float)
    W = np.empty((n, npts), float)
    emax = -1
    for i in range(n):
        t.GetEntry(i)
        ev = int(t.eventnum)
        emax = max(emax, ev)
        W[ev] = [t.weights.At(k) for k in range(npts)]
    f.Close()
    if emax != n - 1:
        raise RuntimeError(f"{path}: eventnum range [0,{emax}] != [0,{n-1}]")
    return twk, W


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--shards", default="work_p*",
                    help="glob for shard dirs holding gst + weights (rel to genie/)")
    ap.add_argument("--dial", default="FrInel_pi")
    ap.add_argument("--gst-glob", default="genie_mefhc_*.gst.root",
                    help="gst basename glob within each shard dir")
    ap.add_argument("--out", default=None)
    ap.add_argument("--graphs", default=GRAPHS_DEFAULT)
    ap.add_argument("--flux", default=os.environ.get("GENIE_FLUX"))
    ap.add_argument("--flux-hist",
                    default=os.environ.get("GENIE_FLUX_HIST", "flux_E_unweighted"))
    args = ap.parse_args()
    ROOT.gErrorIgnoreLevel = ROOT.kError
    out = args.out or os.path.join(HERE, f"genie_fsi_{args.dial}_xsec3d.root")

    shard_dirs = sorted(glob.glob(os.path.join(HERE, args.shards)))
    shard_dirs = [d for d in shard_dirs if os.path.isdir(d)]
    if not shard_dirs:
        raise SystemExit(f"no shard dirs match {args.shards}")

    pt_l, pz_l, ea_l, w_l = [], [], [], []   # in-PS events (+ per-dial weights)
    wsum_allCC = None                        # weighted CC sum per dial (norm denom)
    n_cc = 0
    twk = None
    for d in shard_dirs:
        tag = os.path.basename(d)
        gst_hits = glob.glob(os.path.join(d, args.gst_glob))
        wf = os.path.join(d, f"weights_{args.dial}.root")
        if not (gst_hits and os.path.exists(wf)):
            print(f"[fsi] skip {tag}: missing gst or weights")
            continue
        gst = gst_hits[0]
        twk_d, W = read_weights(wf, args.dial)
        if twk is None:
            twk = twk_d
            wsum_allCC = np.zeros(twk.size)
        elif not np.allclose(twk, twk_d):
            raise SystemExit(f"{tag}: dial grid {twk_d} != {twk}")
        ncc_d = nps_d = 0
        nw = W.shape[0]
        for ev in g3.READERS["genie"](gst):
            if ev["iev"] >= nw:     # gst is iev-ordered; stop at weighted range
                break               # (== full sample in production; subset in smoke runs)
            if not ev["cc"]:
                continue
            wrow = W[ev["iev"]]
            wsum_allCC += wrow
            n_cc += 1; ncc_d += 1
            _, pxl, pyl, pzl = ev["lep"]
            p_t = float(np.hypot(pxl, pyl)); p_z = float(pzl)
            if not in_ps(p_t, p_z, PT[0], PT[-1], PZ[0], PZ[-1]):
                continue
            pt_l.append(p_t); pz_l.append(p_z)
            ea_l.append(g3.eavail_true(ev["fs"])); w_l.append(wrow)
            nps_d += 1
        print(f"[fsi] {tag}: CC={ncc_d} in-PS={nps_d}")

    pt = np.asarray(pt_l); pz = np.asarray(pz_l); ea = np.asarray(ea_l)
    w = np.asarray(w_l)                         # (n_inps, n_points)
    npts = twk.size
    print(f"[fsi] dial={args.dial} grid(sigma)={twk}  total CC={n_cc} "
          f"in-PS={pt.size}")
    print(f"[fsi] weighted CC sum / dial = "
          f"{np.array2string(wsum_allCC, precision=1)} (CV ~ {n_cc})")

    sigma_nuc, info = g3.flux_avg_sigma_cc_per_nucleon(
        args.graphs, args.flux, args.flux_hist)
    print(f"[fsi] norm: {info}; <sigmaCC>/nucleon={sigma_nuc:.4e} cm^2")

    dpt = np.diff(PT)[:, None, None]; dpz = np.diff(PZ)[None, :, None]
    dea = np.diff(EA)[None, None, :]
    widths = dpt * dpz * dea
    sample = np.column_stack([pt, pz, ea])

    xs3d, xs_ea, totals = [], [], []
    for k in range(npts):
        wc, _ = np.histogramdd(sample, bins=[PT, PZ, EA], weights=w[:, k])
        x3 = sigma_nuc * (wc / wsum_allCC[k]) / widths
        xs3d.append(x3)
        _, xea = project_axis(x3, PT, PZ, EA, "eavail")
        xs_ea.append(xea)
        totals.append((x3 * widths).sum())

    # CV is the middle (dial 0) column
    icv = int(np.argmin(np.abs(twk)))
    print(f"\n[fsi] total sigma in PS (cm^2/nucleon) per dial:")
    for k in range(npts):
        print(f"   {twk[k]:+.2f} sigma : {totals[k]:.4e}  "
              f"({100*(totals[k]/totals[icv]-1):+.2f}% vs CV)")

    # Eavail-spectrum shift table (the headline: FSI moves the hadronic energy)
    ea_lo, ea_hi = EA[:-1], EA[1:]
    print(f"\n[fsi] dsigma/dEavail fractional shift vs CV (the FSI-sensitive axis):")
    print(f"   Eavail bin (GeV)      CV          -dial%     +dial%")
    lines = ["# FrInel_pi (and any GSyst dial) effect on the Eavail spectrum",
             f"# dial={args.dial}  grid(sigma)={list(twk)}  CV col={icv}",
             f"# <sigmaCC>/nucleon={sigma_nuc:.4e} cm^2; total CC={n_cc}, "
             f"in-PS={pt.size}",
             "# total sigma in PS per dial (cm^2/nucleon):"]
    for k in range(npts):
        lines.append(f"#   {twk[k]:+.2f}sig {totals[k]:.6e} "
                     f"({100*(totals[k]/totals[icv]-1):+.3f}% vs CV)")
    lines.append("# Eavail_lo Eavail_hi  " +
                 " ".join(f"dsdEa[{twk[k]:+.2f}sig]" for k in range(npts)))
    for b in range(len(ea_lo)):
        cv = xs_ea[icv][b]
        shifts = "  ".join(
            f"{100*(xs_ea[k][b]/cv-1):+6.2f}%" if cv > 0 else "   n/a "
            for k in range(npts) if k != icv)
        print(f"   [{ea_lo[b]:5.2f},{ea_hi[b]:6.2f}]  {cv:.3e}   {shifts}")
        lines.append(f"{ea_lo[b]:.3f} {ea_hi[b]:.3f}  " +
                     " ".join(f"{xs_ea[k][b]:.6e}" for k in range(npts)))

    fo = ROOT.TFile.Open(out, "RECREATE")
    for k in range(npts):
        sfx = f"_d{k}"
        ttl = f"{args.dial} {twk[k]:+.2f}#sigma"
        marg = project_eavail_marginal(xs3d[k], EA)
        _, xpt = project_axis(xs3d[k], PT, PZ, EA, "pt")
        _, xpz = project_axis(xs3d[k], PT, PZ, EA, "pz")
        u3d.numpy_to_th3d(xs3d[k], None, "hXSec3D" + sfx,
                          f"GENIE {ttl} d^{{3}}#sigma;p_{{T}} (GeV/c);"
                          "p_{||} (GeV/c);E_{avail} (GeV)", PT, PZ, EA).Write()
        u3d.numpy_to_th2d(marg, None, "hXSec2D" + sfx,
                          f"GENIE {ttl} Eavail-marginal;p_{{T}} (GeV/c);"
                          "p_{||} (GeV/c)", PT, PZ).Write()
        u3d.numpy_to_th1d(PT, xpt, "hXSec_pt" + sfx, f"GENIE {ttl} d#sigma/dp_T").Write()
        u3d.numpy_to_th1d(PZ, xpz, "hXSec_pz" + sfx, f"GENIE {ttl} d#sigma/dp_||").Write()
        u3d.numpy_to_th1d(EA, xs_ea[k], "hXSec_eavail" + sfx,
                          f"GENIE {ttl} d#sigma/dE_avail").Write()
    # convenience CV / lo / hi aliases for band plotting
    for alias, k in (("cv", icv), ("lo", 0), ("hi", npts - 1)):
        u3d.numpy_to_th1d(EA, xs_ea[k], f"hXSec_eavail_{alias}",
                          f"GENIE {args.dial} {twk[k]:+.2f}#sigma d#sigma/dE_avail").Write()
    tv = ROOT.TVectorD(npts)
    for k in range(npts):
        tv[k] = float(twk[k])
    tv.Write("twkdials")
    ROOT.TNamed("dial", args.dial).Write()
    fo.Close()

    txt = os.path.splitext(out)[0] + "_summary.txt"
    with open(txt, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\n[fsi] wrote {out}\n[fsi] wrote {txt}")


if __name__ == "__main__":
    main()
