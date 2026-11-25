"""Plot the directly measured signed-curvature control and report both-sign totals."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MOMENTA = ["20–40", "40–60", "60–80", "≥80"]


def make_plot(path: Path) -> None:
    """Show data and the all-selected fold in the same signed bins."""
    hist = pd.read_csv(path / "signed-qp.csv")
    fig, panels = plt.subplots(
        2, 3, figsize=(11.5, 5.3), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    groups = [(0,), (1,), (2, 3)]
    for col, (group, title) in enumerate(zip(groups, ["20–40", "40–60", "≥60"])):
        ax, ratios = panels[:, col]
        sub = hist[hist.band.isin(group) & hist.sign.isin(["-", "+"])]
        totals = sub.groupby(["sample", "qbin"])[
            ["tune_weight", "fold", "fold_w2"]
        ].sum()
        edges = np.array(
            [-50, -25, -1000 / 60, -12.5, -10, -5, 0, 5, 10, 12.5, 1000 / 60, 25, 50]
        )
        qbins = np.arange(1, 13)
        observed = (
            totals.loc["Data", "tune_weight"].reindex(qbins, fill_value=0).to_numpy()
        )
        pred = totals.loc["MC", "fold"].reindex(qbins, fill_value=0).to_numpy()
        mcvar = totals.loc["MC", "fold_w2"].reindex(qbins, fill_value=0).to_numpy()
        mids = (edges[1:] + edges[:-1]) / 2
        widths = np.diff(edges)
        ax.stairs(
            pred / widths,
            edges,
            color="#24648a",
            linewidth=1.8,
            label="All-selected fold",
        )
        ax.errorbar(
            mids,
            observed / widths,
            yerr=np.sqrt(observed) / widths,
            color="#171717",
            fmt="o",
            ms=3,
            linewidth=0.9,
            label="Data",
        )
        valid = (pred > 0) & (observed > 0)
        ratio = observed[valid] / pred[valid]
        err = ratio * np.sqrt(1 / observed[valid] + mcvar[valid] / pred[valid] ** 2)
        ratios.axhline(1.0, color="#24648a", lw=1.2)
        ratios.errorbar(
            mids[valid], ratio, yerr=err, fmt="o", color="#171717", ms=3, linewidth=0.9
        )
        for panel in (ax, ratios):
            panel.axvline(0, color="0.55", linestyle="--", linewidth=0.8)
            panel.spines[["top", "right"]].set_visible(False)
        ax.set_yscale("log")
        ax.set_title(rf"$p_\parallel^{{\rm reco}}$ {title} GeV/$c$")
        ratios.set_xticks([-50, -25, 0, 25, 50])
        ratios.set_ylim(bottom=0)
        if col == 0:
            ax.set_ylabel("Events per axis unit")
            ratios.set_ylabel("Data / fold")
        if col == 2:
            ax.legend(loc="best", fontsize=8)
    fig.supxlabel(
        r"Reconstructed MINOS $q/p$ [$10^{-3}$ (GeV/$c$)$^{-1}$]", y=0.075, fontsize=11
    )
    fig.text(
        0.5,
        0.015,
        "Error bars show counting statistics. Outer curvature bins are included in the CSV.",
        ha="center",
        fontsize=8,
    )
    fig.subplots_adjust(
        left=0.09, right=0.98, bottom=0.20, top=0.92, hspace=0.14, wspace=0.26
    )
    fig.savefig(path / "signed-curvature.pdf")
    plt.close(fig)


def make_tables(path: Path) -> None:
    for scope in ("merged", "validation"):
        raw = pd.read_csv(path / f"{scope}-all.csv")
        totals = raw.set_index(["band", "sign", "sample"])
        rows = []
        for band, momentum in enumerate(MOMENTA):
            for sign in ["-", "+"]:
                data = totals.loc[(band, sign, "Data"), "tune_weight"]
                mc = totals.loc[(band, sign, "MC")]
                rows.append(
                    {
                        "reco_p_parallel_GeV_c": momentum,
                        "sign": sign,
                        "data": int(data),
                        "tune_v1": mc.tune_weight,
                        "all_selected": mc.fold,
                        "data_minus_all_selected": data - mc.fold,
                        "data_minus_fold_stat_error": np.sqrt(data + mc.fold_w2),
                        "extra_true_tail": mc.extra_true_tail,
                        "extra_upward_migrants": mc.extra_upward_migrants,
                    }
                )
        pd.DataFrame(rows).to_csv(path / f"{scope}-comparison.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path", type=Path, default=Path(__file__).resolve().parent, nargs="?"
    )
    args = parser.parse_args()
    make_tables(args.path)
    make_plot(args.path)
