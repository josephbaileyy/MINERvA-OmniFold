#!/usr/bin/env python3
"""Bootstrap correlation + relative-spread figures from a SAVED covariance file.

The per-replica bootstrap ROOT files for the 300-replica MEFHC set were removed
in the disk cleanup, but the distilled product (uq_covariance_boot300.root) was
kept.  Everything the two note figures need is already in it:

  hRel2D            -- per-bin relative spread on the pT x pz grid  -> spread map
  hCov2D_reported   -- 205 x 205 reported-bin covariance            -> corr matrix

so we plot straight from the saved product rather than re-running the bootstrap.
Output is title-free with the shared technote colormaps (viridis sequential for
the spread, RdBu_r diverging for the correlation).

  python plot_bootstrap_figs.py \
      --cov bootstrap_MEFHC_300/uq_covariance_boot300.root \
      --outdir bootstrap_MEFHC_300

Opt-in (note figure style, group C family 3): --dump-arrays FILE.npz writes every drawn value after the read;
--from-arrays FILE.npz draws from such a dump with no ROOT; --print-style draws in the note's print style
(note_print_style, at the printed width). With none of them, the figures are drawn as before.
"""
import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse  # noqa: E402
import os  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

# physical paper edges, so the spread map matches the seedscan map (Fig.~13):
# real GeV/c axes with unpopulated bins masked white, not bin-index with empties
# painted as 0%.
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])


def _print_style(depth):
    """note_print_style from the repository root, applied (the paper's rcParams); returned for its figsize()."""
    import sys as _s
    from pathlib import Path as _P
    _r = _P(__file__).resolve().parents[depth]
    if str(_r) not in _s.path:
        _s.path.insert(0, str(_r))
    import note_print_style as _nps
    _nps.apply()
    return _nps


def th2_to_np(h):
    nx, ny = h.GetNbinsX(), h.GetNbinsY()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(ny)]
                     for i in range(nx)])


def fill(path):
    """Read hRel2D (percent) and hCov2D_reported: everything the two figures draw."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(path)
    rel = th2_to_np(f.Get("hRel2D")) * 100.0           # percent
    cov = th2_to_np(f.Get("hCov2D_reported"))          # 205 x 205
    f.Close()
    return {"rel": rel, "cov": cov}


def draw(arr, outdir, print_style=False):
    rel, cov = arr["rel"], arr["cov"]
    nps = _print_style(2) if print_style else None

    d = np.sqrt(np.clip(np.diag(cov), 0, None))
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = cov / np.outer(d, d)
    corr[~np.isfinite(corr)] = 0.0

    # --- relative-spread map on the physical pT x pz grid ----------------
    # mask unpopulated bins (hRel2D stores them as 0) so they render white,
    # not as a 0% spread; physical GeV/c axes to match the seedscan map.
    fig, ax = plt.subplots(figsize=nps.figsize(0.49, 0.8) if print_style else (8, 6))
    Z = np.where(rel > 0, rel, np.nan)
    vmax = min(20.0, np.nanmax(Z)) if np.isfinite(np.nanmax(Z)) else 5.0
    pc = ax.pcolormesh(PT_EDGES, PZ_EDGES, Z.T, cmap=technote_style.SEQ_CMAP,
                       shading="flat", vmin=0, vmax=vmax)
    ax.set_xlabel(r"$p_T$ (GeV/c)"); ax.set_ylabel(r"$p_{||}$ (GeV/c)")
    cb = fig.colorbar(pc, ax=ax); cb.set_label("per-bin rel spread std/mean (%)")
    fig.tight_layout()
    out_spread = os.path.join(outdir, "uq_spread_2d.png")
    fig.savefig(out_spread, dpi=130); plt.close(fig)

    # --- 205 x 205 correlation matrix ------------------------------------
    fig, ax = plt.subplots(figsize=nps.figsize(0.49, 0.88) if print_style else (5.0, 4.4))
    im = ax.imshow(corr, origin="lower", cmap=technote_style.DIV_CMAP, vmin=-1, vmax=1)
    ax.set_xlabel("reported-bin index\n(row-major pT,pz)" if print_style else "reported-bin index (row-major pT,pz)")
    ax.set_ylabel("reported-bin index")
    cb = fig.colorbar(im, ax=ax); cb.set_label("correlation")
    fig.tight_layout()
    out_corr = os.path.join(outdir, "uq_corr_2d.png")
    fig.savefig(out_corr, dpi=130); plt.close(fig)

    print(f"[boot] wrote {out_spread} and {out_corr}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cov", default="bootstrap_MEFHC_300/uq_covariance_boot300.root")
    ap.add_argument("--outdir", default="bootstrap_MEFHC_300")
    ap.add_argument("--dump-arrays", default=None, help="write every drawn value to this .npz after the read")
    ap.add_argument("--from-arrays", default=None, help="draw from this .npz (no ROOT)")
    ap.add_argument("--print-style", action="store_true", help="draw in the note's print style")
    args = ap.parse_args()
    if args.from_arrays:
        with np.load(args.from_arrays) as z:
            arr = {k: z[k] for k in z.files}
    else:
        arr = fill(args.cov)
        if args.dump_arrays:
            np.savez(args.dump_arrays, **arr)
    draw(arr, args.outdir, args.print_style)


if __name__ == "__main__":
    main()
