#!/usr/bin/env python3
"""s5p 2026-09-27: the negative-weight treatment's effect, the producer of state/s5p/stage3/negw/negative-weight-diagnostic.json.

For LowQ2_1, HighQ2_1 (and their partners LowQ2_0, HighQ2_0 as controls) of the bank, reco-level J cells (the MC
reco coordinates of reco-passing rows assigned to the J partition by fine-cell centre, s5p_truths.coarse_cells):
per cell the yield sum(w_reco r) with the negative ratios KEPT (the analysis's universe), CLIPPED to 0 (the
null-experiment treatment) and RESET to 1 (CV), against the band shift (kept minus CV) and the MC-statistics scale
sigma = sqrt(sum w_reco^2); the negative weight's share of the reco weight; rows negative in both LowQ2_1 and HighQ2_1.
Run in the analysis environment on a login node (this is the code that was run inline on 2026-09-27).

MEASURES: the per-cell effect of the treatment. CANNOT AUTHORIZE: a resubmission (the owner's exception and the
review do).
"""
import json
import sys

import numpy as np

import s5p_stage1_inspect as s1
import s5p_truths as st

B = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/bank_sweep_5d_bkgaware"
NPZ = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/of_inputs_5d.npz"


def main(out: str) -> int:
    z = np.load(NPZ, allow_pickle=True)
    wr = np.asarray(z["w_reco"], float)
    pr = np.asarray(z["pass_reco"], bool)
    edges = [np.asarray(z[f"edges_{i}"], float) for i in range(int(z["nedges"]))]
    ced = [np.asarray(s1.J_EDGES[a], float) for a in ("pt", "pz", "eavail", "q3", "W")]
    ok, cell = st.coarse_cells(np.asarray(z["MCreco"], float), edges, ced)
    c = np.full(len(wr), -1)
    c[ok] = cell
    sel = ok & pr
    cells = lambda w: np.bincount(c[sel], weights=w[sel], minlength=243)  # noqa: E731
    S_cv, stat = cells(wr), np.sqrt(cells(wr ** 2))
    res, R = {"n_rows": int(len(wr)), "n_reco": int(pr.sum())}, {}
    for u in ("LowQ2_1", "HighQ2_1", "LowQ2_0", "HighQ2_0"):
        w = np.asarray(np.load(f"{B}/{u}_wr.npy", mmap_mode="r"), float)
        r = np.where(wr > 0, w / np.where(wr > 0, wr, 1), 1.0)
        R[u] = r
        neg = r < 0
        keep, clip, tocv = cells(wr * r), cells(wr * np.maximum(r, 0)), cells(wr * np.where(neg, 1.0, r))
        shift, m = keep - S_cv, S_cv > 0
        rel = lambda a: np.abs(a)[m] / S_cv[m]  # noqa: E731
        res[u] = {"rows_negative": int(neg.sum()), "rows_negative_reco": int((neg & pr).sum()),
                  "nonfinite": int((~np.isfinite(w)).sum()),
                  "negative_weight_fraction_of_total_reco_weight": float(-(wr * r)[neg & pr].sum() / wr[pr].sum()),
                  "band_shift_rel_median": float(np.median(rel(shift))), "band_shift_rel_max": float(rel(shift).max()),
                  "clip_minus_keep_rel_median": float(np.median(rel(clip - keep))), "clip_minus_keep_rel_max": float(rel(clip - keep).max()),
                  "clip_minus_keep_over_band_shift_max": float(np.max(np.abs(clip - keep)[m] / np.maximum(np.abs(shift[m]), 1e-300))),
                  "clip_minus_keep_over_band_shift_median": float(np.median(np.abs(clip - keep)[m] / np.maximum(np.abs(shift[m]), 1e-300))),
                  "clip_minus_keep_over_stat_max": float(np.max(np.abs(clip - keep)[m] / stat[m])),
                  "tocv_minus_keep_over_stat_max": float(np.max(np.abs(tocv - keep)[m] / stat[m])),
                  "cells_touched": int(np.sum(np.abs(clip - keep) > 0))}
    res["rows_negative_in_both_LowQ2_1_and_HighQ2_1"] = int(((R["LowQ2_1"] < 0) & (R["HighQ2_1"] < 0)).sum())
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
