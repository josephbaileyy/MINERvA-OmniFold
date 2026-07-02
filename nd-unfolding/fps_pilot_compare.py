#!/usr/bin/env python3
"""FPS pilot honesty battery: anchor + prior-swap comparison (1A).

Inputs (TH2D hXSecND from unfold_nd_omnifold_unbinned.py):
  --fps-tune   FPS omnifile unfold, MnvTune-v1 prior (extended grid)
  --fps-genie  FPS omnifile unfold, bare-GENIE prior (no --use-weights)
  --ctrl       standard omnifile unfold, MnvTune prior (paper grid) = anchor ref

Checks:
  1. ANCHOR: FPS(tune) restricted to the published-phase-space sub-block must
     reproduce the control unfold (same data, same settings, the only change
     being the enlarged truth denominator + grid). Reported on the 205
     paper-reported cells (the 19 diagonal cells with pT_hi/pz_lo > tan20 are
     excluded -- in FPS they contain real new signal).
  2. PRIOR SWAP: FPS(tune) vs FPS(genie) per-cell ratio = direct prior-
     dependence metric, summarised separately inside the published phase
     space and in the new (extrapolated) cells.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import math
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d
from fps_acceptance import PT_EXT, PZ_EXT, TAN20


def th2_np(fn, name="hXSecND"):
    import ROOT
    ROOT.gErrorIgnoreLevel = ROOT.kError
    f = ROOT.TFile.Open(fn)
    h = f.Get(name)
    if not h:
        raise RuntimeError(f"{name} missing in {fn}")
    a = np.array([[h.GetBinContent(i + 1, j + 1) for j in range(h.GetNbinsY())]
                  for i in range(h.GetNbinsX())])
    f.Close()
    return a


def reported_mask(pt_e, pz_e):
    """True for paper-reported cells: NOT (pT_hi/pz_lo > tan20)."""
    m = np.ones((len(pt_e) - 1, len(pz_e) - 1), bool)
    for i in range(len(pt_e) - 1):
        for j in range(len(pz_e) - 1):
            if pz_e[j] <= 0 or pt_e[i + 1] / max(pz_e[j], 1e-9) > TAN20:
                m[i, j] = False
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps-tune", default="products/5d/xsec_2d_FPS_1A_tune.root")
    ap.add_argument("--fps-genie", default="products/5d/xsec_2d_FPS_1A_genie.root")
    ap.add_argument("--ctrl", default="products/5d/xsec_2d_CTRL_1A.root")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_FPS_1A.root",
                    help="unused since the 2026-06-10 driver normalization fix; "
                         "kept for caller compatibility")
    ap.add_argument("--out-png", default="products/5d/fps_pilot_compare_1A.png")
    args = ap.parse_args()

    pt_ext, pz_ext = np.asarray(PT_EXT), np.asarray(PZ_EXT)
    pt_pap, pz_pap = np.asarray(u2d.PT_EDGES, float), np.asarray(u2d.PZ_EDGES, float)
    # paper sub-block inside the extended grid
    i0 = int(np.searchsorted(pt_ext, pt_pap[0]))
    j0 = int(np.searchsorted(pz_ext, pz_pap[0]))
    npt, npz = len(pt_pap) - 1, len(pz_pap) - 1
    assert np.allclose(pt_ext[i0:i0 + npt + 1], pt_pap), "pT edges not nested"
    assert np.allclose(pz_ext[j0:j0 + npz + 1], pz_pap), "pz edges not nested"

    A_t = th2_np(args.fps_tune)
    A_g = th2_np(args.fps_genie)
    C = th2_np(args.ctrl)

    # No 1/pot_scale correction here: the driver fix of 2026-06-10
    # (KNOWN_ISSUES #1, RESOLVED) passes the POT-scaled weights to OmniFold in
    # no --use-weights mode, so bare-GENIE outputs are absolutely normalized.
    # Outputs produced by the pre-fix driver need A_g / pot_scale.
    wid_ext = np.diff(pt_ext)[:, None] * np.diff(pz_ext)[None, :]
    print(f"[prior] totals: tune={np.sum(A_t*wid_ext):.4g} "
          f"genie={np.sum(A_g*wid_ext):.4g} "
          f"ratio={np.sum(A_t*wid_ext)/np.sum(A_g*wid_ext):.4f}")
    # shape-only comparison as well (normalization-independent)
    A_ts = A_t / np.sum(A_t * wid_ext)
    A_gs = A_g / np.sum(A_g * wid_ext)

    rep = reported_mask(pt_pap, pz_pap)

    # ---------- 1. anchor ----------
    sub = A_t[i0:i0 + npt, j0:j0 + npz]
    ok = rep & (C > 0) & (sub > 0)
    r = sub[ok] / C[ok]
    wid = np.diff(pt_pap)[:, None] * np.diff(pz_pap)[None, :]
    int_fps = (sub * wid)[rep].sum()
    int_ctl = (C * wid)[rep].sum()
    print(f"[anchor] reported cells compared: {ok.sum()}/{rep.sum()}")
    print(f"[anchor] integral FPS(old-PS block)/CTRL = {int_fps/int_ctl:.4f}")
    print(f"[anchor] per-cell ratio median={np.median(r):.4f} "
          f"mean={r.mean():.4f} std={r.std():.4f} "
          f"|ratio-1| median={np.median(np.abs(r-1))*100:.2f}%")

    # ---------- 2. prior swap ----------
    okp = (A_t > 0) & (A_g > 0)
    R = np.full(A_t.shape, np.nan)
    R[okp] = A_t[okp] / A_g[okp]
    old_block = np.zeros(A_t.shape, bool)
    old_block[i0:i0 + npt, j0:j0 + npz] = rep
    new_cells = okp & ~old_block
    old_cells = okp & old_block
    Rs = np.full(A_t.shape, np.nan)
    Rs[okp] = A_ts[okp] / A_gs[okp]
    for nm, m in [("published-PS cells", old_cells), ("new/extrapolated cells", new_cells)]:
        d = np.abs(R[m] - 1)
        ds = np.abs(Rs[m] - 1)
        print(f"[prior] {nm:24s} n={m.sum():4d} |tune/genie - 1|: "
              f"median={np.median(d)*100:.2f}%  p90={np.percentile(d,90)*100:.2f}%  "
              f"max={d.max()*100:.1f}%   (shape-only: median={np.median(ds)*100:.2f}% "
              f"p90={np.percentile(ds,90)*100:.2f}%)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 3, figsize=(19, 5))
    X, Y = np.arange(len(pt_ext)), np.arange(len(pz_ext))
    sub_full = np.full(A_t.shape, np.nan)
    sub_full[i0:i0 + npt, j0:j0 + npz] = np.where(ok, sub / np.where(C > 0, C, np.nan), np.nan)
    # panels (a),(b) are RATIOS -> diverging RdBu_r centred at 1.0; panel (c) is an
    # absolute MAGNITUDE -> sequential viridis (the two-colour-scheme question)
    im0 = axs[0].pcolormesh(X, Y, sub_full.T, cmap="RdBu_r", vmin=0.8, vmax=1.2)
    im1 = axs[1].pcolormesh(X, Y, R.T, cmap="RdBu_r", vmin=0.8, vmax=1.2)
    im2 = axs[2].pcolormesh(X, Y, np.log10(np.maximum(A_t, 1e-44)).T, cmap="viridis")
    labels = ["(a) anchor ratio", "(b) prior-swap ratio", r"(c) abs. xsec (log$_{10}$)"]
    ipt45 = np.searchsorted(pt_ext, 4.5)
    ipz15, ipz60 = np.searchsorted(pz_ext, 1.5), np.searchsorted(pz_ext, 60.0)
    for A, im, lab in zip(axs, [im0, im1, im2], labels):
        A.axvline(ipt45, color="k", lw=1.0)
        A.axhline(ipz15, color="k", lw=1.0)
        A.axhline(ipz60, color="k", lw=1.0)
        A.set_xlabel("p_T bin (extended)")
        A.set_ylabel("p_|| bin (extended)")
        fig.colorbar(im, ax=A, fraction=0.046, pad=0.04)
        technote_style.panel_label(A, lab)
    fig.subplots_adjust(wspace=0.55)  # keep each colorbar clear of the next panel's y-label
    os.makedirs(os.path.dirname(args.out_png), exist_ok=True)
    fig.savefig(args.out_png, dpi=140, bbox_inches="tight")
    print(f"[cmp] wrote {args.out_png}")


if __name__ == "__main__":
    main()
