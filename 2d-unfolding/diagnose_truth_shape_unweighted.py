#!/usr/bin/env python3
"""
Step 1 of the truth-shape attribution: unweighted vs weighted vs paper.

The existing diagnose_truth_shape_vs_paper.py compared local *weighted*
truth (full MnvTune-v1 reweighter product) to the paper's MnvTune-v1
ancillary and found a 1.43x low-p_|| shape excess in the paper. That
result by itself does not separate (a) base AnaTuple GENIE production
differing from the paper's, (b) the local reweighter chain differing
from the paper's, or (c) a truth-side selection mismatch.

This script removes one degree of freedom: it reads the canonical truth
denominator (`mc_truth_denom` from runEventLoopOmniFold output, which is
already filtered by `isEfficiencyDenom`, i.e. the local truth-side
phase-space cuts) and projects it onto the paper (p_T, p_||) grid both
unweighted (w_truth = 1) and weighted (w_truth = MnvTune-v1 product).
Both are shape-normalized inside the strict interior and compared to
the paper MnvTune-v1 ancillary on the same grid.

Reading off the result:
- If unweighted shape is close to paper and weighted shape is the one
  that disagrees, the local reweighter chain is the culprit.
- If unweighted shape already disagrees with paper at low p_||, then
  the disagreement is upstream of the reweighters (base GENIE
  generation, or a truth-selection mismatch).
- The (weighted/unweighted) strip ratio quantifies how strongly the
  local MnvTune-v1 chain reshapes the prior in p_||.

Note: the unfold script's hTruth2D is currently filled from
`mc_signal_reco` (24.5M entries) rather than `mc_truth_denom` (32.8M),
so its truth shape is the reco-tree subset, not the canonical
denominator. This script uses `mc_truth_denom` so the comparison is
against the proper denominator.
"""
import argparse
import csv
import json
import math
import os
import sys
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

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding"
sys.path.insert(0, REPO)
from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES  # noqa: E402

ANC_DIR = f"{REPO}/minerva_paper_anc"
DEFAULT_INPUT = f"{REPO}/runEventLoopOmniFold_MEHFC.root"
DEFAULT_MODEL = f"{ANC_DIR}/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"
DEFAULT_OUT_PREFIX = f"{REPO}/truth_shape_unweighted_MEHFC"

N_PT = len(PT_EDGES) - 1  # 14
N_PZ = len(PZ_EDGES) - 1  # 16
TAN_THETA_MAX = math.tan(math.radians(20.0))


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default=DEFAULT_INPUT,
                   help="runEventLoopOmniFold output ROOT file")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX)
    p.add_argument("--max-entries", type=int, default=-1,
                   help="limit entries for quick debug")
    return p.parse_args()


def fill_truth_hists(path, max_entries):
    """Use TTree::Project to fill (unweighted, weighted) 2D histograms in C++.

    Returns (unweighted_yields, weighted_yields) as (N_PT, N_PZ) numpy arrays.
    Note: TTree::Draw fills bin (ix, iy) for X in [edge[ix], edge[ix+1]).
    Underflow/overflow are not retained.
    """
    from array import array as carray
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open {path}")
    t = f.Get("mc_truth_denom")
    if not t:
        raise RuntimeError(f"mc_truth_denom missing in {path}")

    pt_edges_c = carray("d", PT_EDGES)
    pz_edges_c = carray("d", PZ_EDGES)

    # Project resolves histograms by name from gDirectory; leave attached.
    ROOT.gROOT.cd()
    if ROOT.gDirectory.Get("h_unw"): ROOT.gDirectory.Delete("h_unw;*")
    if ROOT.gDirectory.Get("h_wt"): ROOT.gDirectory.Delete("h_wt;*")
    h_unw = ROOT.TH2D("h_unw", "unweighted truth yield",
                       N_PT, pt_edges_c, N_PZ, pz_edges_c)
    h_wt = ROOT.TH2D("h_wt", "MnvTune-v1 weighted truth yield",
                      N_PT, pt_edges_c, N_PZ, pz_edges_c)

    sel_unw = "1.0"
    sel_wt = "w_truth"
    nopt = ""

    nmax = t.GetEntries() if max_entries <= 0 else max_entries

    print(f"[INFO] Project unweighted (n={nmax})...", flush=True)
    n_unw = t.Project("h_unw", "MC_pz:MC", sel_unw, nopt, nmax)
    print(f"[INFO]   filled {n_unw} entries, integral={h_unw.Integral():.6g}",
          flush=True)
    print(f"[INFO] Project weighted (n={nmax})...", flush=True)
    n_wt = t.Project("h_wt", "MC_pz:MC", sel_wt, nopt, nmax)
    print(f"[INFO]   filled {n_wt} entries, integral={h_wt.Integral():.6g}",
          flush=True)

    unw = np.zeros((N_PT, N_PZ), dtype=float)
    wt = np.zeros((N_PT, N_PZ), dtype=float)
    for ix in range(1, N_PT + 1):
        for iy in range(1, N_PZ + 1):
            unw[ix - 1, iy - 1] = h_unw.GetBinContent(ix, iy)
            wt[ix - 1, iy - 1] = h_wt.GetBinContent(ix, iy)

    f.Close()
    return unw, wt


def load_model(path):
    arr = np.zeros((N_PT, N_PZ), dtype=float)
    with open(path, encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            pzb = int(row["P||bin"]) - 1
            ptb = int(row["Ptbin"]) - 1
            arr[ptb, pzb] = float(row["model_cross_section"])
    return arr


def strict_interior_mask():
    mask = np.zeros((N_PT, N_PZ), dtype=bool)
    for ptb in range(N_PT):
        pt_hi = PT_EDGES[ptb + 1]
        for pzb in range(N_PZ):
            pz_lo = PZ_EDGES[pzb]
            mask[ptb, pzb] = (pt_hi / pz_lo) <= TAN_THETA_MAX
    return mask


def bin_areas():
    pt_w = np.diff(PT_EDGES)
    pz_w = np.diff(PZ_EDGES)
    return np.outer(pt_w, pz_w)


def shape_strip(arr2d, mask):
    masked = np.where(mask, arr2d, 0.0)
    norm = masked / max(masked.sum(), 1e-300)
    return norm.sum(axis=0), norm  # strip in p_||, full 2D normalized


def main():
    args = parse_args()
    interior = strict_interior_mask()
    areas = bin_areas()

    print("[INFO] reading", args.input)
    unw_yield, wt_yield = fill_truth_hists(args.input, args.max_entries)

    model = load_model(args.model)            # dsigma/(dpT dp||)
    model_int = model * areas                 # per-bin integrated xsec

    strip_unw, _ = shape_strip(unw_yield, interior)
    strip_wt, _ = shape_strip(wt_yield, interior)
    strip_mod, _ = shape_strip(model_int, interior)

    pz_lo_arr = np.array(PZ_EDGES[:-1])
    plateau_mask = pz_lo_arr >= 20.0

    def safe_ratio(num, den):
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(den > 0, num / den, np.nan)

    r_paper_over_unw = safe_ratio(strip_mod, strip_unw)
    r_paper_over_wt = safe_ratio(strip_mod, strip_wt)
    r_wt_over_unw = safe_ratio(strip_wt, strip_unw)

    summary = {
        "input": args.input,
        "model": args.model,
        "interior_bin_count": int(interior.sum()),
        "n_pt_bins": N_PT,
        "n_pz_bins": N_PZ,
        "plateau_paper_over_unweighted_pz_ge_20":
            float(np.nanmean(r_paper_over_unw[plateau_mask])),
        "plateau_paper_over_weighted_pz_ge_20":
            float(np.nanmean(r_paper_over_wt[plateau_mask])),
        "plateau_weighted_over_unweighted_pz_ge_20":
            float(np.nanmean(r_wt_over_unw[plateau_mask])),
        "interpretation": (
            "unweighted = w_truth set to 1 on mc_truth_denom (raw GENIE prior, "
            "with local truth-side phase-space cuts already applied). weighted "
            "= w_truth from the local MnvTune-v1 chain. Both shape-normalized "
            "over the 185-bin strict interior, then strip-summed in p_T per "
            "p_|| bin. paper/weighted reproduces the existing 1.43x low-p_|| "
            "feature; if paper/unweighted is closer to flat than paper/weighted, "
            "the local reweighter chain is moving the prior in the wrong "
            "direction; if paper/unweighted is also non-flat at low p_||, the "
            "disagreement is upstream of the reweighters (base GENIE or "
            "truth-side selection)."
        ),
        "pz_strips": [
            {
                "pz_low": float(PZ_EDGES[i]),
                "pz_high": float(PZ_EDGES[i + 1]),
                "unweighted_fraction": float(strip_unw[i]),
                "weighted_fraction": float(strip_wt[i]),
                "paper_fraction": float(strip_mod[i]),
                "paper_over_unweighted":
                    float(r_paper_over_unw[i])
                    if np.isfinite(r_paper_over_unw[i]) else None,
                "paper_over_weighted":
                    float(r_paper_over_wt[i])
                    if np.isfinite(r_paper_over_wt[i]) else None,
                "weighted_over_unweighted":
                    float(r_wt_over_unw[i])
                    if np.isfinite(r_wt_over_unw[i]) else None,
            }
            for i in range(N_PZ)
        ],
    }

    json_path = f"{args.out_prefix}_summary.json"
    png_path = f"{args.out_prefix}_strips.png"
    with open(json_path, "w", encoding="utf-8") as fout:
        json.dump(summary, fout, indent=2, sort_keys=True)
        fout.write("\n")

    pz_mid = 0.5 * (np.array(PZ_EDGES[:-1]) + np.array(PZ_EDGES[1:]))
    pz_w = np.diff(PZ_EDGES)

    fig, axs = plt.subplots(2, 1, figsize=(9.5, 9.0), sharex=True)

    axs[0].step(PZ_EDGES[:-1], strip_unw, where="post",
                label="local truth, unweighted (w=1)", color="#1f77b4")
    axs[0].step(PZ_EDGES[:-1], strip_wt, where="post",
                label="local truth, MnvTune-v1 weighted", color="#ff7f0e")
    axs[0].step(PZ_EDGES[:-1], strip_mod, where="post",
                label="paper MnvTune-v1 ancillary", color="#d62728")
    axs[0].set_ylabel("strip fraction (interior)")
    axs[0].set_yscale("log")
    axs[0].legend(frameon=False, fontsize=9)
    axs[0].grid(True, alpha=0.25)

    axs[1].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[1].errorbar(pz_mid, r_paper_over_unw, xerr=pz_w / 2.0, fmt="o-",
                    color="#1f77b4", capsize=2,
                    label="paper / unweighted")
    axs[1].errorbar(pz_mid, r_paper_over_wt, xerr=pz_w / 2.0, fmt="s-",
                    color="#ff7f0e", capsize=2,
                    label="paper / weighted")
    axs[1].errorbar(pz_mid, r_wt_over_unw, xerr=pz_w / 2.0, fmt="^-",
                    color="#2ca02c", capsize=2,
                    label="weighted / unweighted (= local MnvTune-v1 effect)")
    axs[1].set_xlabel(r"$p_{\parallel}$ (GeV/c)")
    axs[1].set_ylabel("shape ratio")
    axs[1].grid(True, alpha=0.25)
    axs[1].legend(frameon=False, fontsize=9)
    fig.suptitle("MEHFC truth shape: unweighted vs MnvTune-v1 vs paper "
                 "(strict interior, sum-normalized)")
    fig.tight_layout()
    fig.savefig(png_path, dpi=160)
    plt.close(fig)

    # Console table
    print(f"\n[INFO] interior bins (strict 20°): {summary['interior_bin_count']}")
    print(f"[INFO] plateau (p|| >= 20) avg ratios:")
    print(f"       paper/unweighted = "
          f"{summary['plateau_paper_over_unweighted_pz_ge_20']:.4f}")
    print(f"       paper/weighted   = "
          f"{summary['plateau_paper_over_weighted_pz_ge_20']:.4f}")
    print(f"       weighted/unwght  = "
          f"{summary['plateau_weighted_over_unweighted_pz_ge_20']:.4f}")
    print(f"\n{'pz_lo':>5} {'pz_hi':>5} {'unwgt':>9} {'wgt':>9} "
          f"{'paper':>9} {'p/uw':>7} {'p/w':>7} {'w/uw':>7}")
    for s in summary["pz_strips"]:
        def fmt(x): return "  nan " if x is None else f"{x:7.4f}"
        print(f"{s['pz_low']:5.1f} {s['pz_high']:5.1f} "
              f"{s['unweighted_fraction']:9.3e} "
              f"{s['weighted_fraction']:9.3e} "
              f"{s['paper_fraction']:9.3e} "
              f"{fmt(s['paper_over_unweighted'])} "
              f"{fmt(s['paper_over_weighted'])} "
              f"{fmt(s['weighted_over_unweighted'])}")
    print(f"\n[INFO] wrote {json_path}")
    print(f"[INFO] wrote {png_path}")


if __name__ == "__main__":
    main()
