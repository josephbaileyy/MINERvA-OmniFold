#!/usr/bin/env python3
"""Unfolded available-energy spectrum d(sigma)/d(Eavail) -- the 1D projection of
the 3D measurement (hXSec_eavail in the 3D cross-section file).

The wide [3,100] GeV catch bin is dropped from the axis (its value is annotated)
so it does not stretch the physical 0-3 GeV range.  Title-free with the shared
technote style.

  python plot_eavail_spectrum.py --infile xsec_3d_MEFHC_5iter_lgbm.root --out eavail_spectrum.png

Opt-in (note figure style, group C family 4): --dump-arrays FILE.npz writes every drawn value after the read;
--from-arrays FILE.npz draws from such a dump with no ROOT. With neither, the figure is drawn as before.
"""
import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse  # noqa: E402
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402


def fill(infile):
    """Read hXSec_eavail: its edges, values and errors (everything the figure draws)."""
    import ROOT
    ROOT.gROOT.SetBatch(True)
    f = ROOT.TFile.Open(infile)
    h = f.Get("hXSec_eavail")
    n = h.GetNbinsX()
    edges = np.array([h.GetXaxis().GetBinLowEdge(i + 1) for i in range(n)]
                     + [h.GetXaxis().GetBinUpEdge(n)])
    vals = np.array([h.GetBinContent(i + 1) for i in range(n)])
    errs = np.array([h.GetBinError(i + 1) for i in range(n)])
    f.Close()
    return {"edges": edges, "vals": vals, "errs": errs}


def draw(arr, out):
    edges, vals, errs = arr["edges"], arr["vals"], arr["errs"]
    # drop the wide catch bin (last) from the axis, annotate its value
    catch_lo, catch_val = edges[-2], vals[-1]
    e, v, dv = edges[:-1], vals[:-1], errs[:-1]
    centers = 0.5 * (e[:-1] + e[1:])

    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    ax.stairs(v, e, color="k", lw=1.6, label="unfolded data")
    ax.errorbar(centers, v, yerr=dv, fmt="none", ecolor="k", elinewidth=1, capsize=2)
    ax.set_xlabel(r"$E_{\mathrm{avail}}$ (GeV)")
    ax.set_ylabel(r"$d\sigma/dE_{\mathrm{avail}}$ (cm$^2$/nucleon/GeV)")
    ax.set_xlim(e[0], e[-1])
    ax.set_ylim(bottom=0)
    ax.annotate(rf"catch bin $[{catch_lo:.0f},100]$ GeV: {catch_val:.2e}",
                xy=(0.97, 0.82), xycoords="axes fraction", ha="right", va="top",
                fontsize=8)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    technote_style.minerva_tag(ax)
    fig.savefig(out, dpi=130)
    print(f"[eavail-spectrum] wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--infile", default="xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--out", default="eavail_spectrum.png")
    ap.add_argument("--dump-arrays", default=None, help="write every drawn value to this .npz after the read")
    ap.add_argument("--from-arrays", default=None, help="draw from this .npz (no ROOT)")
    args = ap.parse_args()
    if args.from_arrays:
        with np.load(args.from_arrays) as z:
            arr = {k: z[k] for k in z.files}
    else:
        arr = fill(args.infile)
        if args.dump_arrays:
            np.savez(args.dump_arrays, **arr)
    draw(arr, args.out)


if __name__ == "__main__":
    main()
