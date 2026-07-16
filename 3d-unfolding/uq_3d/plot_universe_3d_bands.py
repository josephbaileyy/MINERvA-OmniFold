#!/usr/bin/env python3
"""Grouped per-axis 3D uncertainty bands from the SAVED universe covariance.

analyze_universes_3d.py builds these band figures while it computes the
covariance from the per-universe banks; those banks were removed in the disk
cleanup, but every per-band matrix was kept inside the distilled covariance
file (hCov_universe3d_<band>).  This script reproduces the band figures from
that saved product, reusing the exact category grouping and axis projection of
analyze_universes_3d, so the figures match -- just title-free and with the
shared technote colour cycle.

  python plot_universe_3d_bands.py \
      --cv ../xsec_3d_MEFHC_5iter_lgbm.root \
      --cov universe_stage2_3d/uq_universe_3d_covariance.root \
      --outdir universe_stage2_3d
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
import ROOT  # noqa: E402

import analyze_universes_3d as au  # noqa: E402  (category grouping + CV loader)

ROOT.gROOT.SetBatch(True)

# band-cov hists that are not individual error bands
_SKIP = {"hCov_universe3d_total", "hCov_combined3d_total"}


def th2_to_np(h):
    n = h.GetNbinsX()
    return np.array([[h.GetBinContent(i + 1, j + 1) for j in range(n)]
                     for i in range(n)])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cv", default="../xsec_3d_MEFHC_5iter_lgbm.root")
    ap.add_argument("--cov", default="universe_stage2_3d/uq_universe_3d_covariance.root")
    ap.add_argument("--outdir", default="universe_stage2_3d")
    args = ap.parse_args()

    cv, (pt_e, pz_e, ea_e) = au.load_xsec3d(args.cv, want_edges=True)
    NX, NY, NZ = cv.shape
    reported_flat = (cv > 0).ravel(order="C")
    n_reported = int(reported_flat.sum())

    f = ROOT.TFile.Open(args.cov)
    band_cov = {}
    for k in f.GetListOfKeys():
        name = k.GetName()
        if not name.startswith("hCov_universe3d_") or name in _SKIP:
            continue
        band = name[len("hCov_universe3d_"):]
        mat = th2_to_np(f.Get(name))
        if mat.shape != (n_reported, n_reported):
            print(f"  [skip] {name}: shape {mat.shape} != reported {n_reported}")
            continue
        band_cov[band] = mat
    f.Close()
    print(f"[INFO] {len(band_cov)} per-band covariances over {n_reported} reported 3D bins")

    def project_axis_sigma(cov_mat, axis):
        full = np.zeros(NX * NY * NZ)
        full[reported_flat] = np.sqrt(np.maximum(np.diag(cov_mat), 0))
        full3d = full.reshape(NX, NY, NZ, order="C")
        keep = tuple(a for a in (0, 1, 2) if a != axis)
        return np.sqrt(np.sum(full3d ** 2, axis=keep))

    group_cov = {cat: np.zeros((n_reported, n_reported)) for cat in au.CATEGORY_ORDER}
    for band, cov in band_cov.items():
        group_cov[au.category_for_band(band)] += cov
    active = [(c, group_cov[c]) for c in au.CATEGORY_ORDER if np.trace(group_cov[c]) > 0]
    grouped_total = sum((cov for _, cov in active), np.zeros((n_reported, n_reported)))

    AXES = [(0, pt_e, r"$p_T$ (GeV/c)", "pt"),
            (1, pz_e, r"$p_{||}$ (GeV/c)", "pz"),
            (2, ea_e, r"$E_{avail}$ (GeV)", "eavail")]
    for axis, edges, xlabel, tag in AXES:
        centers = 0.5 * (edges[:-1] + edges[1:])
        fig, ax = plt.subplots(figsize=(8, 5))
        for category, cov in active:
            ax.step(centers, project_axis_sigma(cov, axis), where="mid",
                    label=category, lw=1.5)
        ax.step(centers, project_axis_sigma(grouped_total, axis), where="mid",
                color="k", lw=2, label="TOTAL")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"grouped 1D $\sigma$ (cm$^2$/nucleon, per-axis)")
        ax.legend(fontsize=8, loc="best", ncol=2)
        ax.grid(True, alpha=0.3)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        technote_style.minerva_tag(ax)
        outp = os.path.join(args.outdir, f"uq_universe_3d_band_{tag}.png")
        fig.savefig(outp, dpi=140)
        plt.close(fig)
        print(f"[wrote] {outp}")


if __name__ == "__main__":
    main()
