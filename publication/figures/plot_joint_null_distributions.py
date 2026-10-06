#!/usr/bin/env python3
"""Article figure: each null's calibrated distribution of the joint statistics with the observed value marked.

Plotting only. Reads the frozen sufficient-inputs extract (``publication/release/extract_inference_sufficient.py``;
receipt docs/publication/release/RECEIPT-20261006-inference-sufficient-frozen.json) and recomputes the null
statistics with the frozen-rule replay. Per null and statistic, it shows the declared claim variant whose null
distribution has the largest median (the most conservative), with the observed statistic and k/B.

Usage: python3 plot_joint_null_distributions.py --npz <inference_sufficient.npz> --out <pdf>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "release"))
import replay_inference as rp  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import ticker  # noqa: E402

SERIES_1 = "#2a78d6"   # reference palette categorical slot 1 (null distribution)
INK = "#0b0b0b"        # text-primary (observed statistic, labels)
INK_2 = "#52514e"      # text-secondary (annotations)
LABELS = {"MnvTune_v1": "MINERvA Tune v1", "GENIE_2_12_10_CV": "GENIE 2.12.10 CV",
          "GENIE_2_12_10_MEC": "GENIE 2.12.10 + MEC", "NuWro_21_09": "NuWro 21.09", "GiBUU_2019": "GiBUU 2019"}


def null_sets(z, man):
    out = {}
    V, f_data, coefs = z["V"], z["f_data"], man["shift_coefficients"]
    for key, nm in man["nulls"].items():
        F, seeds = z[f"F__{key}"], z[f"seeds__{key}"]
        mu, var, dom = z[f"mu__{key}"], z[f"var__{key}"], z[f"dom__{key}"].astype(bool)
        S = z[f"S__{key}"] if f"S__{key}" in z.files else None
        variants = [(str(c), (c * S if S is not None else None)) for c in (coefs if S is not None else [0.0])]
        if nm["m1"] is not None:
            d1, ka = z[f"d1__{key}"], nm["m1"]["kappa"]
            variants += [(f"m1+{ka}", ka * d1), (f"m1-{ka}", -ka * d1)]
        tt_o, ts_o = rp.statistics(f_data[None, :], mu, var, V, dom, 0, draw=False)
        res = {"total": {"obs": float(tt_o[0])}, "shape": {"obs": float(ts_o[0])}}
        for s, i in (("total", 0), ("shape", 1)):
            best = None
            for name, sv in variants:
                t = rp.statistics(F + (sv if sv is not None else 0.0), mu, var, V, dom, nm["surrogate_seed0"], seeds=seeds)[i]
                if best is None or np.median(t) > np.median(best[1]):
                    best = (name, t)
            res[s].update(variant=best[0], null=best[1], k=int(np.sum(best[1] >= res[s]["obs"])), B=int(best[1].size))
        out[key] = res
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--npz", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    z = np.load(a.npz, allow_pickle=False)
    man = json.loads(Path(str(a.npz) + ".manifest.json").read_text())
    ns = null_sets(z, man)
    order = ["MnvTune_v1", "GENIE_2_12_10_CV", "GENIE_2_12_10_MEC", "NuWro_21_09", "GiBUU_2019"]
    plt.rcParams.update({"font.size": 7, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
                         "axes.edgecolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2})
    fig, axes = plt.subplots(2, 5, figsize=(7.0, 3.1), constrained_layout=True)
    for j, key in enumerate(order):
        for i, s in enumerate(("total", "shape")):
            ax = axes[i, j]
            d = ns[key][s]
            lo = max(min(d["null"].min(), d["obs"]) * 0.8, 1e-3)
            hi = max(d["null"].max(), d["obs"]) * 1.25
            bins = np.geomspace(lo, hi, 60)
            h, _, _ = ax.hist(d["null"], bins=bins, color=SERIES_1, alpha=0.8, histtype="stepfilled", linewidth=0)
            ax.axvline(d["obs"], color=INK, linewidth=1.2)
            ax.set_xscale("log")
            if hi / lo >= 20:
                ax.xaxis.set_major_locator(ticker.LogLocator(base=10, numticks=6))
            else:  # less than ~1.3 decades: a few round linear ticks read better than log subs
                ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=3, steps=[1, 2, 5, 10]))
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:g}"))
            ax.xaxis.set_minor_formatter(ticker.NullFormatter())
            ax.set_ylim(0, h.max() * 1.45)
            ax.set_yticks([])
            for sp in ("top", "right", "left"):
                ax.spines[sp].set_visible(False)
            ax.text(0.97, 0.97, f"k/B = {d['k']}/{d['B']}", transform=ax.transAxes, ha="right", va="top", color=INK_2,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
            if i == 0:
                ax.set_title(LABELS[key], color=INK, fontsize=7)
            if j == 0:
                ax.set_ylabel(f"{s}", color=INK)
            ax.set_xlabel(r"$T_{\mathrm{%s}}$" % ("tot" if s == "total" else "sh"), color=INK_2, labelpad=1)
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=SERIES_1, alpha=0.8),
                        plt.Line2D([0], [0], color=INK, linewidth=1.2)],
               labels=["null pseudo-experiments (most conservative claim variant)", "data"],
               loc="outside lower center", ncol=2, frameon=False, fontsize=6.5)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out)
    summary = {k: {s: {kk: (v if not isinstance(v, np.ndarray) else None) for kk, v in d.items() if kk != "null"}
                   for s, d in r.items()} for k, r in ns.items()}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
