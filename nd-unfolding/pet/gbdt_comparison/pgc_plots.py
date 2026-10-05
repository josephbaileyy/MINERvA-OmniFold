"""Figures of the PET-vs-GBDT comparison, drawn only from `results/comparison.json`.

    pgc_plots.py --comparison results/comparison.json --out results/figures

Every plotted number is a field of `comparison.json`, which is the figures' machine-readable plot
data; written as PDF and SVG (committed) and PNG. Colours: categorical slots 1-3 of the validated reference palette (H2S1T24K5 blue,
L128S1T24K4 orange, GBDT aqua), with marker shape and direct labels as the second encoding.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

COL = {"H2S1T24K5": "#2a78d6", "L128S1T24K4": "#eb6834", "GBDT": "#1baf7a"}
MARK = {"H2S1T24K5": "o", "L128S1T24K4": "s", "GBDT": "D"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
LABEL = {"H2S1T24K5": "PET H2S1T24 (k=5)", "L128S1T24K4": "PET L128S1T24 (k=4)",
         "GBDT": "GBDT scalar OmniFold (k=7)"}
EP_LABEL = {"E0": "E0 dev tilt", "E1_low_acceptance": "E1 low acc.", "E1_moderate": "E1 moderate",
            "E1_good": "E1 good", "E3": "E3 opposite tilt", "E4": "E4 E_avail×p class",
            "E5": "E5 E_avail×q3"}
FOOT = ("Simulation only; final-bank (FB) look-1 draws, inference conditional on the banks; "
        "exploratory, unadjusted 95% t intervals.")


def _save(fig, stem: Path) -> None:
    """PDF and SVG are the committed formats (the repository ignores *.png); PNG for quick viewing."""
    for ext in ("pdf", "svg", "png"):
        fig.savefig(stem.with_suffix(f".{ext}"), dpi=160)


def _style(ax):
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelcolor=INK)


def _ci(s):
    return s["mean"] - s["ci95"][0], s["ci95"][1] - s["mean"]


def fig_endpoints(c, out: Path) -> None:
    eps = [e for e in EP_LABEL if "summary" in c["endpoints"].get(e, {})]
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    x = np.arange(len(eps))
    for i, (m, key) in enumerate((("H2S1T24K5", "H2S1T24K5"), ("L128S1T24K4", "L128S1T24K4"),
                                  ("GBDT", "GBDT@k7"))):
        s = [c["endpoints"][e]["summary"][key] for e in eps]
        lo, hi = zip(*[_ci(v) for v in s])
        ax.errorbar(x + (i - 1) * 0.22, [v["mean"] for v in s], yerr=[lo, hi], fmt=MARK[m],
                    ms=8, color=COL[m], mec="#fcfcfb", mew=1.5, elinewidth=2, capsize=0,
                    label=LABEL[m])
    for e_i, e in enumerate(eps):
        for k, mk in ((3, "_"), (10, "_")):
            v = c["endpoints"][e]["summary"][f"GBDT@k{k}"]["mean"]
            ax.plot(e_i + 0.22, v, mk, color=COL["GBDT"], ms=10, mew=2, alpha=0.6)
    ax.set_xticks(x, [EP_LABEL[e] for e in eps], rotation=0, fontsize=9)
    ax.set_ylabel("recovery R (fraction of injected L1 removed)", color=INK)
    ax.set_ylim(0, 1.0)
    ax.set_title("Designated endpoints on identical FB draws: mean R ± 95% CI "
                 "(GBDT dashes: k = 3 and 10)", color=INK, fontsize=11, loc="left")
    _style(ax)
    ax.legend(frameon=False, loc="lower left", fontsize=9)
    fig.text(0.01, 0.01, FOOT, fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, out / "fig1_endpoints")
    plt.close(fig)


def fig_paired(c, out: Path) -> None:
    eps = [e for e in EP_LABEL if "paired" in c["endpoints"].get(e, {})]
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    x = np.arange(len(eps))
    for i, d in enumerate(("H2S1T24K5", "L128S1T24K4")):
        s = [c["endpoints"][e]["paired"][f"{d} - GBDT@k7"] for e in eps]
        lo, hi = zip(*[_ci(v) for v in s])
        ax.errorbar(x + (i - 0.5) * 0.25, [v["mean"] for v in s], yerr=[lo, hi], fmt=MARK[d],
                    ms=8, color=COL[d], mec="#fcfcfb", mew=1.5, elinewidth=2, capsize=0,
                    label=f"{LABEL[d]} − GBDT (k=7)")
        for xi, v in zip(x, s):
            ax.annotate(f"{v['mean']:+.3f}", (xi + (i - 0.5) * 0.25, v["ci95"][1]),
                        textcoords="offset points", xytext=(0, 4), ha="center", fontsize=7.5,
                        color=INK)
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xticks(x, [EP_LABEL[e] for e in eps], fontsize=9)
    ax.set_ylabel("paired ΔR = R_PET − R_GBDT (same draw)", color=INK)
    ax.set_title("Paired differences per FB draw, mean ± 95% t interval", color=INK,
                 fontsize=11, loc="left")
    _style(ax)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.text(0.01, 0.01, FOOT, fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, out / "fig2_paired_differences")
    plt.close(fig)


def fig_per_bin(c, out: Path, ep: str, xlabel: str) -> None:
    pb = c["per_bin"].get(ep)
    if pb is None:
        return
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    meths = (("H2S1T24K5", "H2S1T24K5"), ("L128S1T24K4", "L128S1T24K4"), ("GBDT", "GBDT@k7"))
    nb = len(pb["methods"]["GBDT@k7"]["mean_signed_residual"])
    x = np.arange(nb)
    for i, (m, key) in enumerate(meths):
        v = pb["methods"][key]
        ax.errorbar(x + (i - 1) * 0.25, v["mean_signed_residual"], yerr=v["se_mean"],
                    fmt=MARK[m], ms=6 if nb > 10 else 8, color=COL[m], mec="#fcfcfb", mew=1.2,
                    elinewidth=1.5, capsize=0,
                    label=f"{LABEL[m]}: L1(mean) {v['l1_of_mean_residual']:.4f}, "
                          f"mean L1 {v['mean_per_draw_l1']:.4f}")
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xlabel(xlabel, color=INK)
    ax.set_ylabel("mean (unfolded − own target), unit-normalized", color=INK)
    ax.set_title(f"{EP_LABEL[ep]}: per-bin signed residual, mean ± s.e. over "
                 f"{pb['methods']['GBDT@k7']['n']} draws", color=INK, fontsize=11, loc="left")
    _style(ax)
    ax.legend(frameon=False, fontsize=8, loc="best")
    fig.text(0.01, 0.01, FOOT + " Target moves with the draw.", fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    _save(fig, out / f"fig_{ep}_per_bin_residual")
    plt.close(fig)


def fig_k(c, out: Path) -> None:
    eps = [e for e in ("E0", "E3", "E4", "E5") if e in c["k_trajectory"]]
    fig, axes = plt.subplots(1, len(eps), figsize=(3.1 * len(eps), 3.6), sharey=False)
    axes = np.atleast_1d(axes)
    for ax, e in zip(axes, eps):
        t = c["k_trajectory"][e]
        ks = list(range(1, 11))
        rec = [t[str(k)] if str(k) in t else t[k] for k in ks]
        m = [x["mean"] for x in rec]
        lo = [x["mean"] - x["ci95"][0] for x in rec]
        hi = [x["ci95"][1] - x["mean"] for x in rec]
        ax.errorbar(ks, m, yerr=[lo, hi], fmt="-" + MARK["GBDT"], color=COL["GBDT"], ms=5, lw=2,
                    label="GBDT")
        for d in ("H2S1T24K5", "L128S1T24K4"):
            p = t["pet"][d]
            ax.axhspan(p["ci95"][0], p["ci95"][1], color=COL[d], alpha=0.18, lw=0)
            ax.axhline(p["mean"], color=COL[d], lw=2, label=LABEL[d])
        ax.axvline(7, color=MUTED, lw=0.8, ls=":")
        ax.set_title(EP_LABEL[e], color=INK, fontsize=10, loc="left")
        ax.set_xlabel("GBDT iteration k", color=INK)
        _style(ax)
    axes[0].set_ylabel("mean R with 95% t interval (GBDT bars, PET bands)", color=INK)
    axes[0].legend(frameon=False, fontsize=7, loc="lower right")
    fig.text(0.01, 0.01, FOOT + " Dotted: primary k = 7 (fixed on DEV beforehand).",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    _save(fig, out / "fig3_gbdt_k_trajectory")
    plt.close(fig)


def fig_library(c, out: Path) -> None:
    cases = [k for k, v in sorted(c["library"].items()) if v.get("paired")]
    order = sorted(cases, key=lambda k: c["library"][k]["paired"]["H2S1T24K5 - GBDT@k7"]["mean"])
    fig, ax = plt.subplots(figsize=(8.5, 0.34 * len(order) + 1.6))
    y = np.arange(len(order))
    for i, d in enumerate(("H2S1T24K5", "L128S1T24K4")):
        s = [c["library"][k]["paired"][f"{d} - GBDT@k7"] for k in order]
        lo, hi = zip(*[_ci(v) for v in s])
        ax.errorbar([v["mean"] for v in s], y + (i - 0.5) * 0.3, xerr=[lo, hi], fmt=MARK[d], ms=6,
                    color=COL[d], mec="#fcfcfb", mew=1.2, elinewidth=1.6, capsize=0,
                    label=f"{LABEL[d]} − GBDT (k=7)")
    ax.axvline(0, color=MUTED, lw=1)
    ax.set_yticks(y, [f"{k} ({c['library'][k]['draws']}; {c['library'][k]['natural_histogram']})"
                      for k in order], fontsize=8)
    ax.set_xlabel("paired ΔR on the case's natural histogram (PET better →)", color=INK)
    ax.set_title("Final library: paired differences per case, mean ± 95% t interval", color=INK,
                 fontsize=11, loc="left")
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.text(0.01, 0.005, FOOT, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    _save(fig, out / "fig4_library_paired")
    plt.close(fig)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--comparison", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    c = json.loads(a.comparison.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    fig_endpoints(c, a.out)
    fig_paired(c, a.out)
    fig_k(c, a.out)
    fig_library(c, a.out)
    fig_per_bin(c, a.out, "E0", "truth E_avail bin (7 historical bins)")
    fig_per_bin(c, a.out, "E4", "E_avail bin × proton class (0,1,2,3+), E_avail-major")
    fig_per_bin(c, a.out, "E5", "E_avail bin × true-q3 quartile, E_avail-major")
    print(sorted(p.name for p in a.out.glob("*.pdf")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
