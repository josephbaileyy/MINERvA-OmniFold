#!/usr/bin/env python3
"""FPS 3-prior envelope: per-cell spread across {MnvTune, bare-GENIE, NuWro-shaped}
priors, summarised inside the published phase space vs the extension cells.

The bare-GENIE input must come from the 2026-06-10-fixed driver (KNOWN_ISSUES
#1 RESOLVED: no-weights mode is now absolutely normalized); pre-fix outputs
would need an extra 1/pot_scale.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os
import sys

import numpy as np

_REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
for _p in (f"{_REPO}/2d-unfolding", f"{_REPO}/nd-unfolding"):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import unfold_2d_omnifold_unbinned as u2d
from fps_acceptance import PT_EXT, PZ_EXT
from fps_pilot_compare import th2_np, reported_mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune", default="products/5d/xsec_2d_FPS_MEFHC_tune.root")
    ap.add_argument("--genie", default="products/5d/xsec_2d_FPS_MEFHC_genie.root")
    ap.add_argument("--nuwro", default="products/5d/xsec_2d_FPS_MEFHC_nuwroprior.root")
    ap.add_argument("--omnifile", default="runEventLoopOmniFold_5D_FPS_MEFHC.root")
    ap.add_argument("--out-png", default="products/5d/fps_prior_envelope_MEFHC.png")
    args = ap.parse_args()

    A = {"tune": th2_np(args.tune),
         "genie": th2_np(args.genie),
         "nuwro": th2_np(args.nuwro)}
    pt_ext, pz_ext = np.asarray(PT_EXT), np.asarray(PZ_EXT)
    pt_pap, pz_pap = np.asarray(u2d.PT_EDGES, float), np.asarray(u2d.PZ_EDGES, float)
    i0 = int(np.searchsorted(pt_ext, pt_pap[0]))
    j0 = int(np.searchsorted(pz_ext, pz_pap[0]))
    npt, npz = len(pt_pap) - 1, len(pz_pap) - 1
    rep = reported_mask(pt_pap, pz_pap)
    old_block = np.zeros(A["tune"].shape, bool)
    old_block[i0:i0 + npt, j0:j0 + npz] = rep

    wid = np.diff(pt_ext)[:, None] * np.diff(pz_ext)[None, :]
    for k, a in A.items():
        print(f"[env] total sigma ({k:5s}) = {np.sum(a*wid):.4g}")

    stack = np.stack([A["tune"], A["genie"], A["nuwro"]])
    ok = np.all(stack > 0, axis=0)
    mean = stack.mean(axis=0)
    half = 0.5 * (stack.max(axis=0) - stack.min(axis=0))
    env = np.full(mean.shape, np.nan)
    env[ok] = half[ok] / mean[ok]
    for nm, m in [("published-PS cells", ok & old_block),
                  ("extension cells", ok & ~old_block)]:
        d = env[m]
        print(f"[env] {nm:20s} n={m.sum():4d} half-spread/mean: "
              f"median={np.median(d)*100:.2f}%  p90={np.percentile(d,90)*100:.2f}%  "
              f"max={d.max()*100:.1f}%")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 6))
    X, Y = np.arange(len(pt_ext)), np.arange(len(pz_ext))
    im = ax.pcolormesh(X, Y, (100 * env).T, cmap="viridis", vmin=0, vmax=30)
    ax.axvline(np.searchsorted(pt_ext, 4.5), color="cyan", lw=1.2)
    ax.axhline(np.searchsorted(pz_ext, 1.5), color="cyan", lw=1.2)
    ax.axhline(np.searchsorted(pz_ext, 60.0), color="cyan", lw=1.2)
    ax.set_xlabel("p_T bin (extended)")
    ax.set_ylabel("p_|| bin (extended)")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("3-prior half-spread/mean (%)")
    os.makedirs(os.path.dirname(args.out_png), exist_ok=True)
    fig.savefig(args.out_png, dpi=140, bbox_inches="tight")
    print(f"[env] wrote {args.out_png}")


if __name__ == "__main__":
    main()
