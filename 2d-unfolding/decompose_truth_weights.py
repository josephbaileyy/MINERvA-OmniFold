#!/usr/bin/env python3
"""
Option 1 — per-reweighter decomposition of the MnvTune-v1 truth weight.

Reads the truth-denom tree from a component-dumped event-loop output
(produced by a build with the per-reweighter branches added), and shows
per-truth-p_|| strip how each of the five reweighters contributes to the
combined `w_truth`. Identifies which reweighter is responsible for the
low-p_|| weight suppression observed in `diagnose_weights_vs_pz.py`.
"""

import argparse
import json
import os
import tempfile

os.environ.setdefault(
    "MPLCONFIGDIR",
    os.path.join(tempfile.gettempdir(), "minerva101-mplconfig"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)

from unfold_2d_omnifold_unbinned import PZ_EDGES

DEFAULT_INPUT = (
    "Documents/component_dump_1A/runEventLoopOmniFold.root"
)
DEFAULT_OUT_PREFIX = "Documents/component_dump_1A/decompose_truth"
COMPONENTS = [
    "w_FluxAndCV",
    "w_GENIE",
    "w_LowRecoil2p2hTune",
    "w_MINOSEfficiency",
    "w_RPA",
]


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=DEFAULT_INPUT)
    p.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX)
    return p.parse_args()


def load_tree(path):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"cannot open {path}")
    t = f.Get("mc_truth_denom")
    if not t:
        raise RuntimeError("mc_truth_denom missing")
    branches = ["MC", "MC_pz", "w_truth"] + COMPONENTS
    rdf = ROOT.RDataFrame(t)
    out = {}
    for b in branches:
        col = rdf.AsNumpy([b])[b]
        out[b] = np.asarray(col, dtype=float)
    f.Close()
    return out


def in_phase(pt, pz):
    return (pt >= 0.0) & (pt <= 4.5) & (pz >= 1.5) & (pz <= 60.0)


def strip_means(pz, w, edges):
    means = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (pz >= lo) & (pz < hi)
        means.append(float(w[m].mean()) if m.any() else float("nan"))
    return np.asarray(means)


def main():
    args = parse_args()
    arrs = load_tree(args.input)
    pt = arrs["MC"]
    pz = arrs["MC_pz"]
    w_total = arrs["w_truth"]
    mask = in_phase(pt, pz)
    pz, w_total = pz[mask], w_total[mask]
    comps = {c: arrs[c][mask] for c in COMPONENTS}

    edges = np.asarray(PZ_EDGES)
    strip_total = strip_means(pz, w_total, edges)
    strip_comps = {c: strip_means(pz, comps[c], edges) for c in COMPONENTS}

    plateau_mask = edges[:-1] >= 20.0

    def plateau(arr):
        return float(np.nanmean(arr[plateau_mask]))

    rel_total = strip_total / plateau(strip_total)
    rel_comps = {c: strip_comps[c] / plateau(strip_comps[c]) for c in COMPONENTS}

    summary = {
        "input": args.input,
        "n_truth_in_phase": int(mask.sum()),
        "components": COMPONENTS,
        "plateau_means_pz_ge_20": {
            "w_truth": plateau(strip_total),
            **{c: plateau(strip_comps[c]) for c in COMPONENTS},
        },
        "pz_strips": [
            {
                "pz_low": float(edges[i]),
                "pz_high": float(edges[i + 1]),
                "rel_w_truth": float(rel_total[i]),
                **{f"rel_{c}": float(rel_comps[c][i]) for c in COMPONENTS},
                "abs_w_truth": float(strip_total[i]),
                **{f"abs_{c}": float(strip_comps[c][i]) for c in COMPONENTS},
            }
            for i in range(len(edges) - 1)
        ],
    }

    out_json = f"{args.out_prefix}_summary.json"
    out_png = f"{args.out_prefix}_strips.png"
    with open(out_json, "w") as fout:
        json.dump(summary, fout, indent=2, sort_keys=True)
        fout.write("\n")

    pz_mid = 0.5 * (edges[:-1] + edges[1:])

    fig, axs = plt.subplots(2, 1, figsize=(9.0, 9.0), sharex=True)
    axs[0].plot(pz_mid, rel_total, "o-", color="black", lw=2.0,
                label="combined w_truth")
    for c in COMPONENTS:
        axs[0].plot(pz_mid, rel_comps[c], ".-", label=c, alpha=0.85)
    axs[0].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[0].set_ylabel("strip mean / plateau (p_||>=20)")
    axs[0].set_xscale("log")
    axs[0].grid(True, alpha=0.25)
    axs[0].legend(frameon=False, fontsize=9, loc="lower right")

    axs[1].plot(pz_mid, strip_total, "o-", color="black", lw=2.0,
                label="combined w_truth")
    for c in COMPONENTS:
        axs[1].plot(pz_mid, strip_comps[c], ".-", label=c, alpha=0.85)
    axs[1].axhline(1.0, color="#555555", lw=0.7, ls=":")
    axs[1].set_xlabel(r"$p_{\parallel}$ (GeV/c)")
    axs[1].set_ylabel("strip mean (absolute)")
    axs[1].set_xscale("log")
    axs[1].grid(True, alpha=0.25)
    axs[1].legend(frameon=False, fontsize=9, loc="lower right")
    fig.suptitle(
        "Per-reweighter decomposition of MnvTune-v1 truth weight (1A)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)

    print(f"[INFO] entries: {summary['n_truth_in_phase']}")
    print(f"[INFO] plateau (p||>=20) means: "
          f"{summary['plateau_means_pz_ge_20']}")
    print()
    h_cols = ["pz", "wtruth"] + [c.replace("w_", "") for c in COMPONENTS]
    print("rel-to-plateau (each component normalized to its own p||>=20 mean):")
    print(f"{'pz':>11}  " + "  ".join(f"{c:>10}" for c in h_cols[1:]))
    for i, s in enumerate(summary["pz_strips"]):
        line = f"  {s['pz_low']:4.1f}-{s['pz_high']:4.1f}  "
        line += f"{s['rel_w_truth']:10.4f}  "
        for c in COMPONENTS:
            line += f"{s[f'rel_{c}']:10.4f}  "
        print(line)
    print(f"[INFO] wrote {out_json}")
    print(f"[INFO] wrote {out_png}")


if __name__ == "__main__":
    main()
