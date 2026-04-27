#!/usr/bin/env python3
"""
Step 2 of the MINOS-match acceptance investigation: denominator vs numerator.

Compare the shape of our truth-side denominator (`hTruth2D` from the 2D
unfold output, which is the MC truth event yield in our (p_T, p_||)
binning under truth phase-space mask) against the paper's published
MINERvA-Tune-v1 model prediction
(`minerva_paper_anc/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt`,
which is differential cross section dsigma/(dp_T dp_||) in
cm^2/(GeV/c)^2/nucleon).

Both objects represent the same underlying truth-level signal (CC
inclusive on tracker, FHC, in the paper's phase space) up to a global
normalization. So the *shape* (per-bin fraction inside the strict
interior) should agree if and only if our truth denominator is correct
in shape.

If shapes agree: the residual ours/paper xsec gradient is reco-side
(missing reco selection or misweighted reco efficiency).
If shapes disagree: the gradient is denominator-side (truth phase-space
acceptance modeling, e.g. MINOS geometric range-out).

Read-only diagnostic. Writes a JSON summary and a strip-ratio PNG.
"""

import argparse
import csv
import json
import math
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

from unfold_2d_omnifold_unbinned import PT_EDGES, PZ_EDGES

ANC_DIR = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/2d-unfolding/minerva_paper_anc"
DEFAULT_OURS = (
    "Documents/2d_crossSection_omnifold_1A_minos_fix_5iter.root"
)
DEFAULT_MODEL = (
    f"{ANC_DIR}/model_ptpl_minerva_inclusive_6GeV_MINERvA_Tune_v1.txt"
)
DEFAULT_OUT_PREFIX = "Documents/truth_shape_vs_paper_1A"

N_PT = 14
N_PZ = 16
TAN_THETA_MAX = math.tan(math.radians(20.0))


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ours", default=DEFAULT_OURS,
                   help="ROOT file with hTruth2D (and hXSec2D)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help="Paper Tune-v1 model CSV (P||bin, Ptbin, dsigma)")
    p.add_argument("--out-prefix", default=DEFAULT_OUT_PREFIX,
                   help="Output prefix for JSON/PNG")
    return p.parse_args()


def load_truth(path):
    f = ROOT.TFile.Open(path, "READ")
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open {path}")
    try:
        h = f.Get("hTruth2D")
        if not h:
            raise RuntimeError(f"hTruth2D missing in {path}")
        nx, ny = h.GetNbinsX(), h.GetNbinsY()
        if (nx, ny) != (N_PT, N_PZ):
            raise RuntimeError(
                f"hTruth2D shape {nx}x{ny}, expected {N_PT}x{N_PZ}")
        arr = np.zeros((N_PT, N_PZ), dtype=float)
        for ix in range(1, N_PT + 1):
            for iy in range(1, N_PZ + 1):
                arr[ix - 1, iy - 1] = float(h.GetBinContent(ix, iy))
        return arr
    finally:
        f.Close()


def load_model(path):
    """Returns dsigma/(dp_T dp_||) in cm^2/(GeV/c)^2/nucleon, shape (N_PT, N_PZ)."""
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
    """Returns d(p_T)*d(p_||) per bin in (GeV/c)^2."""
    pt_w = np.diff(PT_EDGES)  # length N_PT
    pz_w = np.diff(PZ_EDGES)  # length N_PZ
    return np.outer(pt_w, pz_w)  # (N_PT, N_PZ)


def main():
    args = parse_args()
    truth = load_truth(args.ours)              # event yield (MC truth)
    model = load_model(args.model)             # dsigma/(dp_T dp_||)
    interior = strict_interior_mask()
    areas = bin_areas()

    # Convert paper differential xsec -> per-bin integrated xsec
    # (cm^2/nucleon per bin), so it's directly comparable in shape to a
    # truth event count (which is also a per-bin integrated quantity).
    model_int = model * areas

    # Restrict both to the strict interior, then normalize to unit sum
    # so we are comparing pure shape (bin fractions).
    truth_in = np.where(interior, truth, 0.0)
    model_in = np.where(interior, model_int, 0.0)

    truth_norm = truth_in / max(truth_in.sum(), 1e-300)
    model_norm = model_in / max(model_in.sum(), 1e-300)

    # Per-bin model/ours shape ratio. >1 means ours is shape-deficient
    # in that bin relative to paper Tune-v1.
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(truth_norm > 0.0, model_norm / truth_norm, np.nan)

    # Strip sums (over p_T, fixed p_|| bin) — same projection as the
    # audit JSON, so the two are directly comparable.
    strip_truth = truth_in.sum(axis=0)
    strip_model = model_in.sum(axis=0)
    strip_truth_norm = strip_truth / max(strip_truth.sum(), 1e-300)
    strip_model_norm = strip_model / max(strip_model.sum(), 1e-300)
    with np.errstate(divide="ignore", invalid="ignore"):
        strip_ratio = np.where(
            strip_truth_norm > 0.0,
            strip_model_norm / strip_truth_norm,
            np.nan,
        )

    # Reference plateau (p_|| >= 20 GeV/c): take the average shape
    # ratio there; if denominator shape is fine, strip_ratio should be
    # ~constant (== 1 by construction of unit normalization).
    pz_lo = np.array(PZ_EDGES[:-1])
    plateau = pz_lo >= 20.0
    plateau_avg = float(np.nanmean(strip_ratio[plateau]))

    summary = {
        "ours": args.ours,
        "model": args.model,
        "n_pt_bins": N_PT,
        "n_pz_bins": N_PZ,
        "interior_bin_count": int(interior.sum()),
        "plateau_strip_ratio_avg_pz_ge_20": plateau_avg,
        "interpretation": (
            "Both shape-normalized inside strict interior. strip_ratio "
            "= model/ours over strict interior, sum-normalized. "
            "If strip_ratio is approximately flat with p_||, the truth "
            "denominator shape is correct and the residual xsec gradient "
            "is reco-side. If strip_ratio rises toward low p_||, the "
            "truth denominator is shape-deficient at low p_|| (i.e. our "
            "denominator over-counts low-p_|| truth events), and the "
            "gradient is denominator-side (MINOS geometric acceptance)."
        ),
        "pz_strips": [
            {
                "pz_low": float(PZ_EDGES[i]),
                "pz_high": float(PZ_EDGES[i + 1]),
                "ours_truth_fraction": float(strip_truth_norm[i]),
                "paper_model_fraction": float(strip_model_norm[i]),
                "model_over_ours": float(strip_ratio[i])
                if np.isfinite(strip_ratio[i])
                else None,
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

    fig, axs = plt.subplots(2, 1, figsize=(9.0, 8.0), sharex=True)
    axs[0].step(PZ_EDGES[:-1], strip_truth_norm, where="post",
                label="ours hTruth2D (shape)", color="#1f77b4")
    axs[0].step(PZ_EDGES[:-1], strip_model_norm, where="post",
                label="paper MnvTune-v1 (shape)", color="#d62728")
    axs[0].set_ylabel("strip fraction (interior)")
    axs[0].set_yscale("log")
    axs[0].legend(frameon=False)
    axs[0].grid(True, alpha=0.25)

    axs[1].axhline(1.0, color="#555555", lw=1.0, ls="--")
    axs[1].errorbar(pz_mid, strip_ratio, xerr=pz_w / 2.0, fmt="s-",
                    color="#2ca02c", capsize=2,
                    label="paper-model / ours (shape)")
    axs[1].set_xlabel(r"$p_{\parallel}$ (GeV/c)")
    axs[1].set_ylabel("shape ratio")
    axs[1].grid(True, alpha=0.25)
    axs[1].legend(frameon=False)
    fig.suptitle(
        r"Low-$p_{\parallel}$ Shape Check: Paper Tune-v1 Model / Local MC Truth")
    fig.tight_layout()
    fig.savefig(png_path, dpi=160)
    plt.close(fig)

    print(f"[INFO] ours: {args.ours}")
    print(f"[INFO] model: {args.model}")
    print(f"[INFO] interior bins: {summary['interior_bin_count']}")
    print(f"[INFO] plateau (p||>=20) shape ratio avg: {plateau_avg:.4f}")
    print("[INFO] strip shape ratios (paper/ours):")
    for s in summary["pz_strips"]:
        r = s["model_over_ours"]
        rs = "nan" if r is None else f"{r:.4f}"
        print(f"  {s['pz_low']:5.1f}-{s['pz_high']:5.1f}: "
              f"ours={s['ours_truth_fraction']:.4e}  "
              f"paper={s['paper_model_fraction']:.4e}  "
              f"ratio={rs}")
    print(f"[INFO] wrote {json_path}")
    print(f"[INFO] wrote {png_path}")


if __name__ == "__main__":
    main()
