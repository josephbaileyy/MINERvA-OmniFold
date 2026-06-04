#!/usr/bin/env python3
"""Bin-identical comparison of the 4D OmniFold result to MINERvA's low-q3 release.

This is the q3 analogue of ../3d-unfolding/genie/compare_ascencio_eavail.py and the
payoff of adding q3 as the 4th axis (docs/HIGHER_DIM_OMNIFOLD_DESIGN.md, Phase 1).
Ascencio et al. (arXiv:2110.13372, PRD 106 032001) published the double-differential
CC-inclusive cross section d2sigma/(dq3 dEavail) for numu on hydrocarbon at
<E_nu> ~ 6 GeV with q3 < 1.2 GeV. With q3 now an unfolded axis, the comparison can be
made on Ascencio's OWN q3 / E_avail binning -- a true bin-identical overlay and chi2,
not the area-normalized shape-only cross-check the E_avail script was limited to.

Phase-space note. Our 4D unfold spans the full muon acceptance (pt < 4.5, 1.5 < pz < 60
GeV); restricting to q3 < 1.2 GeV via the q3 axis selects the SAME low-recoil region
Ascencio measured. The remaining acceptance difference is the muon (pt,pz) gate, which is
marginalized out in d2sigma/(dq3 dEavail). The comparison is therefore meaningful in
absolute normalization once both are on the shared (q3, Eavail) grid -- modulo any
residual phase-space/flux differences, which is exactly what the chi2 quantifies.

Our side is read from the frozen 4D xsec product (hXSecND_flat reshaped with the per-axis
edges read back from the 1D/2D projection hists -- the canonical N-D recovery path, see
unfold_nd_omnifold_unbinned.py::write_thnd). The Ascencio side is a plain text release you
drop in (MINERvA member access / HepData ins... -- not public in-session, same as the
E_avail script). Two accepted formats:

  --ascencio-q3 FILE         1D dsigma/dq3:        q3_lo q3_hi dsigma err
  --ascencio-2d FILE         2D dsigma/dq3dEavail: q3_lo q3_hi ea_lo ea_hi dsigma err

Run from nd-unfolding/ after `source ../setup_salloc_env.sh`:
  python compare_ascencio_q3.py                              # our spectra only (self-test)
  python compare_ascencio_q3.py --ascencio-q3 ascencio_q3.txt
  python compare_ascencio_q3.py --ascencio-2d ascencio_q3_eavail.txt
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ROOT
import xsec_nd

ROOT.gROOT.SetBatch(True)

# Ascencio q3 < 1.2 GeV: the low-recoil region. Our q3 axis edges include this exactly
# as a prefix (driver EXTRA_AXES["q3"]: 0,0.2,0.4,0.6,0.8,1.2,2.0,100). The bin-identical
# region is the q3 bins with high edge <= LOW_Q3_MAX.
LOW_Q3_MAX = 1.2


def _axis_edges(ax):
    return np.array([ax.GetBinLowEdge(i) for i in range(1, ax.GetNbins() + 2)])


def load_xsec4d(path):
    """Return (xsec4d array (pt,pz,ea,q3), [pt_e, pz_e, ea_e, q3_e]).

    Reshapes hXSecND_flat (C-order ravel) using the per-axis edges read from the
    stored projection hists (hXSec2D for pt/pz, hXSec_eavail, hXSec_q3).
    """
    f = ROOT.TFile.Open(path)
    if not f or f.IsZombie():
        raise SystemExit(f"[FAIL] cannot open {path}")
    ndim = int(f.Get("ndim").GetVal())
    if ndim != 4:
        raise SystemExit(f"[FAIL] {path} is ndim={ndim}, expected 4 (pt,pz,eavail,q3)")
    h2 = f.Get("hXSec2D")
    pt_e = _axis_edges(h2.GetXaxis())
    pz_e = _axis_edges(h2.GetYaxis())
    ea_e = _axis_edges(f.Get("hXSec_eavail").GetXaxis())
    q3_e = _axis_edges(f.Get("hXSec_q3").GetXaxis())
    shape = (len(pt_e) - 1, len(pz_e) - 1, len(ea_e) - 1, len(q3_e) - 1)
    flat = f.Get("hXSecND_flat")
    n = flat.GetNbinsX()
    if n != int(np.prod(shape)):
        raise SystemExit(f"[FAIL] flat nbins {n} != prod(shape) {np.prod(shape)}")
    arr = np.array([flat.GetBinContent(i + 1) for i in range(n)]).reshape(shape, order="C")
    f.Close()
    return arr, [pt_e, pz_e, ea_e, q3_e]


def area_norm(edges, y):
    w = np.diff(edges)
    integral = float(np.sum(y * w))
    return (y / integral) if integral > 0 else y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xsec4d", default="xsec_4d_MEFHC_5iter_lgbm.root",
                    help="4D xsec product (hXSecND_flat + projection hists).")
    ap.add_argument("--ascencio-q3", default="",
                    help="text: q3_lo q3_hi dsigma err  (1D dsigma/dq3, arXiv:2110.13372)")
    ap.add_argument("--ascencio-2d", default="",
                    help="text: q3_lo q3_hi ea_lo ea_hi dsigma err  (d2sigma/dq3dEavail)")
    ap.add_argument("--out-prefix", default="ascencio_vs_unfolded_q3")
    args = ap.parse_args()

    xsec4d, edges = load_xsec4d(args.xsec4d)
    pt_e, pz_e, ea_e, q3_e = edges
    print(f"[ours] 4D xsec {args.xsec4d} shape={xsec4d.shape}, "
          f"total={xsec_nd.total_xsec(xsec4d, edges):.4e} cm^2/nucleon")

    # 1D dsigma/dq3 (axis 3) over the full q3 range.
    q3_edges, dsig_dq3 = xsec_nd.project_axis(xsec4d, edges, keep_axis=3)
    q3_c = 0.5 * (q3_edges[:-1] + q3_edges[1:])
    low_mask = q3_edges[1:] <= LOW_Q3_MAX + 1e-9    # bins fully inside q3<1.2
    print(f"[ours] dsigma/dq3: {len(dsig_dq3)} bins; "
          f"{int(low_mask.sum())} bins in the Ascencio q3<{LOW_Q3_MAX} region "
          f"(edges {q3_edges[:int(low_mask.sum())+1]})")

    # 2D d2sigma/(dEavail dq3): marginalize pt,pz (axes 0,1) -> (eavail, q3).
    d2_ea_q3 = xsec_nd.project_marginal(xsec4d, edges, drop_axes=[0, 1])  # (n_ea, n_q3)

    # ---------- plot 1: dsigma/dq3 (full + low-q3), overlay Ascencio 1D ----------
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.step(q3_c, dsig_dq3, where="mid", color="k", lw=2,
            label="This work (4D OmniFold, full muon acceptance)")
    ax.axvspan(q3_edges[0], LOW_Q3_MAX, color="C0", alpha=0.08,
               label=f"Ascencio region q3<{LOW_Q3_MAX} GeV")
    chi2_msg = ""
    if args.ascencio_q3 and os.path.exists(args.ascencio_q3):
        d = np.loadtxt(args.ascencio_q3)
        a_lo, a_hi, a_y, a_e = d[:, 0], d[:, 1], d[:, 2], d[:, 3]
        a_c = 0.5 * (a_lo + a_hi)
        ax.errorbar(a_c, a_y, yerr=a_e, fmt="s", color="C3", capsize=2,
                    label="Ascencio 2110.13372 (q3<1.2 GeV)")
        # bin-identical chi2 on the shared low-q3 bins (requires matching edges)
        chi2_msg = _binwise_chi2(q3_edges, dsig_dq3, a_lo, a_hi, a_y, a_e)
        print(f"[chi2 dsigma/dq3] {chi2_msg}")
    else:
        print("[note] no --ascencio-q3 file: plotting our dsigma/dq3 only. Obtain the "
              "2110.13372 release\n       (q3_lo q3_hi dsigma err) for the bin-identical "
              "overlay + chi2.")
    ax.set_xlabel(r"$q_3$ (GeV)")
    ax.set_ylabel(r"$d\sigma/dq_3$ (cm$^2$/nucleon/GeV)")
    ax.set_title("q3 spectrum: 4D OmniFold vs MINERvA low-q3 (2110.13372)" +
                 (f"\n{chi2_msg}" if chi2_msg else ""))
    ax.set_xlim(0, 2.0)
    ax.legend(fontsize=8)
    fig.tight_layout()
    p1 = f"{args.out_prefix}_dq3.png"
    fig.savefig(p1, dpi=130)
    plt.close(fig)
    print(f"[OK] wrote {p1}")

    # ---------- plot 2: Eavail spectra in low-q3 slices (the Ascencio observable) ----------
    ea_c = 0.5 * (ea_e[:-1] + ea_e[1:])
    n_low = int(low_mask.sum())
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for j in range(n_low):
        # d2sigma/dq3dEavail is per-(eavail,q3); the Eavail spectrum at q3 slice j
        # is d2_ea_q3[:, j] (already a density in eavail and q3).
        ax.step(ea_c, d2_ea_q3[:, j], where="mid", lw=1.6,
                label=fr"$q_3\in[{q3_e[j]:.1f},{q3_e[j+1]:.1f}]$ GeV")
    ax.set_xlabel(r"$E_{\rm avail}$ (GeV)")
    ax.set_ylabel(r"$d^2\sigma/(dq_3\,dE_{\rm avail})$ (cm$^2$/nucleon/GeV$^2$)")
    ax.set_title("E_avail in low-q3 slices (bin-identical to Ascencio 2110.13372)")
    ax.set_xlim(0, 1.5)
    ax.legend(fontsize=8, ncol=2)
    if args.ascencio_2d and os.path.exists(args.ascencio_2d):
        _overlay_ascencio_2d(ax, args.ascencio_2d, q3_e, n_low)
        print(f"[overlay] added Ascencio 2D points from {args.ascencio_2d}")
    else:
        print("[note] no --ascencio-2d file: our d2sigma/dq3dEavail slices only. Obtain "
              "the 2110.13372\n       2D release (q3_lo q3_hi ea_lo ea_hi dsigma err) for "
              "the bin-identical overlay.")
    fig.tight_layout()
    p2 = f"{args.out_prefix}_eavail_in_q3slices.png"
    fig.savefig(p2, dpi=130)
    plt.close(fig)
    print(f"[OK] wrote {p2}")


def _binwise_chi2(our_edges, our_y, a_lo, a_hi, a_y, a_e):
    """Diagonal chi2 on bins where our edges match the Ascencio edges exactly.

    (A full-covariance chi2 needs the q3-projected combined covariance, which is a
    follow-on once the q3 systematic campaign lands -- see ND_OMNIFOLD_STATUS.md.)
    """
    a_edges = np.append(a_lo, a_hi[-1])
    matched = []
    for k in range(len(a_y)):
        # find our bin with the same [lo,hi)
        for i in range(len(our_y)):
            if (abs(our_edges[i] - a_lo[k]) < 1e-6 and
                    abs(our_edges[i + 1] - a_hi[k]) < 1e-6):
                matched.append((our_y[i], a_y[k], a_e[k]))
                break
    if not matched:
        return ("no exactly-matching q3 bins (edges differ) -- rebin the release onto "
                "the driver q3 edges or vice versa for a bin-identical chi2")
    m = np.array(matched)
    with np.errstate(divide="ignore", invalid="ignore"):
        chi2 = float(np.sum(((m[:, 0] - m[:, 1]) / m[:, 2]) ** 2))
    ndf = len(matched)
    return f"diagonal chi2/ndf = {chi2:.2f}/{ndf} = {chi2/ndf:.2f} on {ndf} matched q3 bins"


def _overlay_ascencio_2d(ax, path, q3_e, n_low):
    d = np.loadtxt(path)
    q3lo, q3hi, ealo, eahi, y, e = (d[:, i] for i in range(6))
    eac = 0.5 * (ealo + eahi)
    for j in range(n_low):
        sel = (np.abs(q3lo - q3_e[j]) < 1e-6) & (np.abs(q3hi - q3_e[j + 1]) < 1e-6)
        if sel.any():
            ax.errorbar(eac[sel], y[sel], yerr=e[sel], fmt="s", ms=4, capsize=2,
                        color=f"C{j}", alpha=0.8)


if __name__ == "__main__":
    main()
