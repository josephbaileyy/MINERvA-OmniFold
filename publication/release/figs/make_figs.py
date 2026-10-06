#!/usr/bin/env python3
"""Regenerate the article's Figs. 1-3 from the released arrays (numpy + matplotlib only).

Same quantities as the committed producers (2d-unfolding/compare_to_models.py, compare_to_paper_fullcov.py,
nd-unfolding/excess_eavail_W.py, 3d-unfolding/genie/overlay_eavailW_band.py); not pixel-identical.
The 2D uncertainty-band number in Fig. 1's inset ("This work" median) is NOT drawn: the 2D statistical band is
being rebuilt (VL170 adopted 2026-10-06; rollup pending), so it is printed as "pending VL170".

  python3 make_figs.py --npz fig_arrays.npz --outdir figs_out
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

GENS = ("GENIE-CV", "GENIE+MEC", "NuWro", "GiBUU")


def grid(vec, mask, n_pt=14, n_pz=16):
    g = np.full((n_pt, n_pz), np.nan)
    idx = np.where(mask)[0]
    g[idx // n_pz, idx % n_pz] = vec[idx]
    return g


def projections(vec, mask, pt_e, pz_e):
    g = np.nan_to_num(grid(vec, mask))
    return (g * np.diff(pz_e)[None, :]).sum(1), (g * np.diff(pt_e)[:, None]).sum(0)


def fig1(z, out: Path):
    m = z["mask_reported"].astype(bool)
    pt_e, pz_e = z["pt_edges"], z["pz_edges"]
    fig = plt.figure(figsize=(11, 8))
    for k, (ax_i, edges, lab) in enumerate(((0, pt_e, r"$p_T$ (GeV/c)"), (1, pz_e, r"$p_\parallel$ (GeV/c)"))):
        ax = fig.add_subplot(2, 2, k + 1)
        for vec, lbl, style in ((z["paper_v"], "Published", dict(color="k", lw=2)),
                                (z["ours_v"], "This work (OmniFold)", dict(color="C0", ls="--")),
                                (z["tune_v1_v"], "MINERvA Tune v1", dict(color="C1"))):
            y = projections(vec, m, pt_e, pz_e)[ax_i]
            ax.stairs(y, edges, label=lbl, **style)
        ax.set_xlabel(lab); ax.set_ylabel(r"$d\sigma/dx$ (cm$^2$/(GeV/c)/nucleon)"); ax.set_xscale("log")
        ax.legend(fontsize=8)
    ax = fig.add_subplot(2, 2, 3)
    pull = (z["ours_v"] - z["paper_v"]) / np.sqrt(np.where(np.diag(z["cov_total"]) > 0, np.diag(z["cov_total"]), np.nan))
    im = ax.imshow(grid(pull, m).T, origin="lower", aspect="auto", cmap="RdBu_r", vmin=-3, vmax=3,
                   extent=[0, 14, 0, 16])
    ax.set_xlabel(r"$p_T$ bin"); ax.set_ylabel(r"$p_\parallel$ bin"); fig.colorbar(im, ax=ax, label="(OmniFold - published)/sigma_pub")
    ax = fig.add_subplot(2, 2, 4); ax.axis("off")
    p = pull[m]
    ax.text(0.05, 0.6, "Median relative uncertainty\n  This work: pending VL170\n"
            f"Published-sigma standardized residuals\n  mean = {p.mean():.3f}, RMS = {p.std():.3f}", fontsize=10)
    fig.tight_layout(); fig.savefig(out / "fig1_validation.pdf"); plt.close(fig)


def fig2(z, out: Path):
    ee, we = z["eavail_edges"], z["W_edges"]
    area = np.outer(np.diff(ee), np.diff(we))
    ratio = z["hData2D"] / np.where(z["hGenCV2D"] > 0, z["hGenCV2D"], np.nan)
    diff = (z["hData2D"] - z["hGenCV2D"]) * area
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    im = axs[0].imshow(ratio, origin="lower", aspect="auto", cmap="RdBu_r", vmin=0.5, vmax=1.5)
    axs[0].set_title("unfolded / MINERvA Tune v1"); fig.colorbar(im, ax=axs[0])
    vmax = np.nanmax(np.abs(diff))
    im = axs[1].imshow(diff, origin="lower", aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    axs[1].set_title("unfolded - Tune v1, cell-integrated (cm$^2$/nucleon)"); fig.colorbar(im, ax=axs[1])
    for ax in axs:
        ax.set_xlabel("W bin index"); ax.set_ylabel(r"$E_{avail}$ bin index")
    fig.tight_layout(); fig.savefig(out / "fig2_joint_localization.pdf"); plt.close(fig)


def fig3(z, out: Path):
    ee, we = z["eavail_edges"], z["W_edges"]
    dea, dw = np.diff(ee)[:, None], np.diff(we)[None, :]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, edges, proj, lab in ((axs[0], ee, lambda a: (a * dw).sum(1), r"$E_{avail}$ (GeV)"),
                                 (axs[1], we, lambda a: (a * dea).sum(0), "W (GeV)")):
        e = edges[:-1]
        c = 0.5 * (e[:-1] + e[1:])
        ax.plot(c, proj(z["hData2D"])[:-1], "ko", label="data (unfolded)")
        for g in GENS:
            ax.step(c, proj(z[f"gen_{g}"])[:-1], where="mid", label=g)
        ax.set_yscale("log"); ax.set_xlabel(lab); ax.legend(fontsize=8)
    axs[0].set_ylabel(r"$d\sigma/dE_{avail}$"); axs[1].set_ylabel(r"$d\sigma/dW$")
    fig.tight_layout(); fig.savefig(out / "fig3_generator_context.pdf"); plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    a = ap.parse_args(argv)
    a.outdir.mkdir(parents=True, exist_ok=True)
    z = np.load(a.npz, allow_pickle=False)
    fig1(z, a.outdir); fig2(z, a.outdir); fig3(z, a.outdir)
    print("wrote", sorted(p.name for p in a.outdir.glob("fig*.pdf")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
