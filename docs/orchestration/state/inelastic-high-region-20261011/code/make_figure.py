"""Figure for the memo: normalization-removed contrast by W bin with the +-4% recoil band, and the corner split.

Plots committed results only (results/R4b_recorded_and_profiles.json, results/R3R4_decomposition.json).
Usage: python3 -I make_figure.py <results_dir> <out_png>
"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

PRED = [("TuneV1", "Tune v1 (prior)", "#6b6b6b"), ("GENIE_CV", "GENIE 2.12.10 CV", "#1f6fb4"),
        ("GENIE_MEC", "GENIE + MEC", "#7fb2e0"), ("NuWro", "NuWro 21.09", "#c4542d")]
WLAB = ["<1.1", "1.1–1.4", "1.4–1.8", "1.8–2.2", "2.2–3", "≥3"]
STEPS = [("muon_shape", "muon shape"), ("transfer_given_muon", "transfer | muon"),
         ("partition_given_transfer", "E_avail | transfer")]


def main(rdir, out):
    prof = json.load(open(os.path.join(rdir, "R4b_recorded_and_profiles.json")))["profiles"]
    dec = json.load(open(os.path.join(rdir, "R3R4_decomposition.json")))["results"]["production"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(6)
    lo = np.array([prof["GENIE_CV"][f"W{j}"]["recoil_minus4_shift_ln_rho"] for j in range(6)])
    hi = np.array([prof["GENIE_CV"][f"W{j}"]["recoil_plus4_shift_ln_rho"] for j in range(6)])
    band = np.maximum(np.abs(lo), np.abs(hi))
    ax[0].bar(x, 2 * band, bottom=-band, width=0.8, color="#e8e2c8", label="±4% recoil-scale shift (data side)")
    for k, (key, lab, c) in enumerate(PRED):
        y = [prof[key][f"W{j}"]["ln_rho"] for j in range(6)]
        ax[0].plot(x + (k - 1.5) * 0.12, y, "o", color=c, label=lab)
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].axvspan(2.5, 5.5, color="#f3d9d9", alpha=0.35, lw=0)
    ax[0].set_xticks(x, WLAB)
    ax[0].set_xlabel("analysis W bin (GeV), all E_avail")
    ax[0].set_ylabel("ln ρ  (data/prediction ÷ total ratio)")
    ax[0].set_title("Normalization-removed contrast by W (shaded: W ≥ 1.8)")
    ax[0].legend(fontsize=8, loc="upper center")
    regs = [("C_no_overflow", "C, no overflow"), ("C_overflow", "C, overflow cells"), ("C", "C (all)")]
    width = 0.2
    for i, (key, lab, c) in enumerate(PRED[1:]):
        for r, (reg, rl) in enumerate(regs):
            s = dec[key]["inclusive_first"][reg]["steps"]
            bottom_p = bottom_n = 0.0
            for si, (sk, sl) in enumerate(STEPS):
                v = s[sk]
                b = bottom_p if v >= 0 else bottom_n
                ax[1].bar(r + (i - 1) * width, v, width, bottom=b, color=c,
                          alpha=[1.0, 0.6, 0.3][si], edgecolor="k", lw=0.3,
                          label=f"{lab}: {sl}" if r == 0 else None)
                if v >= 0:
                    bottom_p += v
                else:
                    bottom_n += v
            ax[1].plot(r + (i - 1) * width, dec[key]["inclusive_first"][reg]["ln_rho"], "k_", ms=12)
    ax[1].axhline(0, color="k", lw=0.8)
    ax[1].set_xticks(range(3), [rl for _, rl in regs])
    ax[1].set_ylabel("ln ρ_C split into steps (bar marks the sum)")
    ax[1].set_title("Corner decomposition, inclusive-first order")
    ax[1].legend(fontsize=6.5, ncol=1, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
