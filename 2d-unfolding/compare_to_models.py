#!/usr/bin/env python3
"""Three-way comparison: our 2D OmniFold unfolded result vs the published
MINERvA data (arXiv:2106.16210) vs the MINERvA Tune v1 model prediction.

The paper ancillary ships one generator prediction,
`model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt` (GENIE MINERvA Tune v1
d^2sigma/(dpT dp||), bin-index format) -- the same tune the C++ event loop
reweights to. This script overlays the three, computes per-bin ratios and the
chi^2 of each measurement against the model in the paper TotalCov, and makes
1D projections. It is the simulator-comparison companion to
`compare_to_paper_fullcov.py` (data-vs-ours) and reuses its loaders.

The model loader is kept generic (`load_model_csv`): drop in additional
generator CSVs (GENIE vN / NuWro / GiBUU / NEUT) with the same bin-index format
and pass repeated `--model NAME:PATH` to extend the comparison.
"""

import sys as _sys, pathlib as _pathlib
for _a in _pathlib.Path(__file__).resolve().parents:
    if (_a / 'technote_style.py').exists():
        _sys.path.insert(0, str(_a)); break
import technote_style  # noqa: E402  (no titles + consistent colours)

import argparse
import os
import numpy as np
import ROOT
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from compare_to_paper_fullcov import (
    ANC_DIR, DEFAULT_OURS, N, N_PT, N_PZ,
    tmatrix_to_numpy, flatten_th2d, flatten_ours, chi2_with_cov,
)

# Paper binning (STATUS / bin_mapping.txt); widths drive the 1D projections.
PT_EDGES = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.40, 0.47, 0.55,
                     0.70, 0.85, 1.00, 1.25, 1.50, 2.50, 4.50])
PZ_EDGES = np.array([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0,
                     6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0, 40.0, 60.0])
DEFAULT_MODEL = os.path.join(
    ANC_DIR, "model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt")
DEFAULT_OUT_PREFIX = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/model_comp"


def load_model_csv(path):
    """Generic loader for an ancillary model CSV in bin-index format
    `P||bin,Ptbin,model_cross_section`. Returns a length-N (224) vector on the
    global grid (gid = (ptbin-1)*16 + (pzbin-1)), matching flatten_th2d."""
    v = np.zeros(N)
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.lower().startswith(("p||", "p|")):
                continue
            pzb, ptb, xs = line.split(",")
            v[(int(ptb) - 1) * N_PZ + (int(pzb) - 1)] = float(xs)
    return v


def project(vec_red, mask, axis):
    """Marginalize a length-n_reported differential xsec to 1D by integrating
    over the other axis: dsigma/dpT = sum_j d2sigma * dpz_j (axis='pt')."""
    g = np.full((N_PT, N_PZ), 0.0)
    idx = np.where(mask)[0]
    for k, gid in enumerate(idx):
        g[gid // N_PZ, gid % N_PZ] = vec_red[k]
    dpt = np.diff(PT_EDGES)
    dpz = np.diff(PZ_EDGES)
    if axis == "pt":
        return PT_EDGES, (g * dpz[None, :]).sum(axis=1)       # length N_PT
    return PZ_EDGES, (g * dpt[:, None]).sum(axis=0)           # length N_PZ


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ours", default=DEFAULT_OURS)
    ap.add_argument("--model", action="append", default=[], metavar="NAME:PATH",
                    help="Model CSV as NAME:PATH (repeatable). Default: MINERvA "
                         "Tune v1 from the ancillary.")
    ap.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX)
    args = ap.parse_args()
    models = args.model or [f"MINERvA_Tune_v1:{DEFAULT_MODEL}"]

    lines = []

    def emit(s=""):
        print(s); lines.append(s)

    # ---- load paper cov + data, ours, model(s) -----------------------------
    fp = ROOT.TFile.Open(f"{ANC_DIR}/cov_ptpl_minerva_inclusive_6GeV.root")
    cov_total = tmatrix_to_numpy(fp.Get("TotalCovariance"))
    cov_stat = tmatrix_to_numpy(fp.Get("StatOnlyCovariance"))
    data_v = flatten_th2d(fp.Get("pt_pl_cross_section"))
    fo = ROOT.TFile.Open(args.ours)
    ours_v = flatten_ours(fo.Get("hXSec2D"))

    mask = np.diag(cov_stat) > 0
    n = int(mask.sum())

    emit("=" * 72)
    emit("THREE-WAY COMPARISON  -  ours / published data / generator model")
    emit("=" * 72)
    emit(f"reported bins: {n}")
    emit(f"sigma_tot: ours/data = {ours_v[mask].sum()/data_v[mask].sum():.4f}")

    model_vs = {}
    for spec in models:
        name, path = spec.split(":", 1)
        mv = load_model_csv(path)
        model_vs[name] = mv
        emit(f"model {name}: sigma_tot/data = {mv[mask].sum()/data_v[mask].sum():.4f}")

    # ---- chi^2 of each measurement / model against each other (paper cov) --
    emit("")
    emit("--- chi^2 in paper TotalCov (ndf = 205) ---")
    chi2_with_cov(ours_v - data_v, cov_total, "ours vs data (sanity ~3.66)")
    for name, mv in model_vs.items():
        chi2_with_cov(data_v - mv, cov_total, f"data vs {name}")
        chi2_with_cov(ours_v - mv, cov_total, f"ours vs {name}")

    # ---- 1D projections overlay --------------------------------------------
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    for axis, ax, xlabel in [("pt", axs[0], "p_T (GeV/c)"),
                             ("pz", axs[1], "p_|| (GeV/c)")]:
        edges, y_ours = project(ours_v[mask], mask, axis)
        _, y_data = project(data_v[mask], mask, axis)
        ctr = 0.5 * (edges[:-1] + edges[1:])
        ax.step(ctr, y_data, where="mid", color="k", lw=2, label="Published (PRD 104, 092007)",
                marker=technote_style.gen_marker("data"), markersize=4)
        ax.step(ctr, y_ours, where="mid", color="C0", lw=1.5, ls="--",
                label="This work (OmniFold)")
        for j, (name, mv) in enumerate(model_vs.items()):
            _, y_m = project(mv[mask], mask, axis)
            ax.step(ctr, y_m, where="mid", color=f"C{j+1}", lw=1.5, label=name,
                    marker=technote_style.gen_marker(name), markersize=4)
        ax.set_xlabel(xlabel); ax.set_ylabel(rf"$d\sigma/d{axis}$ (cm$^2$/(GeV/c)/nucleon)")
        ax.set_title(f"Projection onto {xlabel}"); ax.legend(); ax.grid(alpha=0.3)
    fig.suptitle("2D OmniFold vs data vs MINERvA Tune v1 - 1D projections")
    technote_style.minerva_tag(fig)
    fig.tight_layout(); fig.savefig(f"{args.out_prefix}_projections.png", dpi=130)
    plt.close(fig)

    # ---- per-bin ratio heatmaps (ours/model, data/model) -------------------
    name0 = next(iter(model_vs))
    mv0 = model_vs[name0]
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    for ax, num, tag in [(axs[0], ours_v, "ours"), (axs[1], data_v, "data")]:
        g = np.full((N_PT, N_PZ), np.nan)
        for gid in np.where(mask)[0]:
            if mv0[gid] > 0:
                g[gid // N_PZ, gid % N_PZ] = num[gid] / mv0[gid]
        im = ax.imshow(g.T, aspect="auto", origin="lower", cmap="RdBu_r",
                       vmin=0.7, vmax=1.3, extent=[0, N_PT, 0, N_PZ])
        ax.set_xlabel("p_T bin"); ax.set_ylabel("p_|| bin")
        ax.set_title(f"{tag} / {name0}")
        plt.colorbar(im, ax=ax, label="ratio")
    fig.suptitle(f"Ratio to {name0}")
    fig.tight_layout(); fig.savefig(f"{args.out_prefix}_ratio_maps.png", dpi=130)
    plt.close(fig)

    rpt = f"{args.out_prefix}_report.txt"
    with open(rpt, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    emit(""); emit(f"wrote {rpt}, {args.out_prefix}_projections.png, "
                   f"{args.out_prefix}_ratio_maps.png")


if __name__ == "__main__":
    main()
