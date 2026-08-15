"""Per-cell fold-forward ratio for VL100's OWN run (job 56552326), and its relation to the
unfolding's own per-cell correction. READ-ONLY: reads two files, writes nothing.

WHY THIS PROBE EXISTS. Lane D's shape test decomposed
`fullevent_nominal/pet_fullevent_nominal_weights.npz` -- the NOMINAL Gate-4 training run. VL100
comes from the annealed powered closure, job 56552326, a different run with a different subsample,
a different loader population and an injected truth tilt. D's n_pass_reco is 837671; the closure
records n_step1_a=837494 and n_step1_b=836975, so D's decomposition is of neither closure half.
This probe runs D's own quantity on the closure's own artifact.

CONTROL, and nothing below means anything without it: `weights_push` is aligned to half B, whose
global row ids are `dump_rows_b` (deterministic_halves returns SORTED index sets and mc_indices is
sorted, so the pairing push[j] <-> dump_rows_b[j] is determined, not guessed). If that pairing is
right, rebuilding h_prior and h_unfolded from the NPZ must reproduce the PUBLISHED 285-cell arrays.
The loader rescales both weight legs by a global factor; unit normalization removes it, so raw
NPZ weights must reproduce to float noise. If they do not, the alignment is wrong.

THE QUESTION THE COMPARISON ANSWERS. D's per-cell quantity is, by D's own definition, the
w_reco-weighted MEAN OF push inside cell c. The unfolding's per-cell correction is
h_unfolded[c]/h_prior[c], the w_truth-weighted mean of push inside the same cell over the
pass_truth population. If those two track each other, then the dispersion D measured is the
unfolding's learned reweighting, and "68x sampling noise" is the expected signature of any real
shape correction rather than evidence of a contaminating deficit.
"""
import json
import os
import sys

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
CLO = os.path.join(REPO, "nd-unfolding/pet/annealed_shape_validation",
                   "NONQUOTABLE-DIAGNOSTIC.POWERED_CLOSURE_ANNEALED.slurm-56552326.npz")
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5,
               30.0], float)
PP = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
               20.0, 40.0, 60.0, 120.0], float)
NPT, NPP = len(PT) - 1, len(PP) - 1
NC = NPT * NPP

out = {"probe": "vl100-own-run-foldforward-percell", "reads": [CLO, NPZ], "writes": None}

z = np.load(CLO, allow_pickle=True)
push = np.asarray(z["weights_push"], np.float64)
rows_b = np.asarray(z["dump_rows_b"], np.int64)
rows_a = np.asarray(z["dump_rows_a"], np.int64)
z.close()
assert push.shape == rows_b.shape, (push.shape, rows_b.shape)
out["n_half_b"] = int(rows_b.size)
out["push_stats"] = {"min": float(push.min()), "max": float(push.max()),
                     "mean": float(push.mean()), "sd": float(push.std(ddof=1))}

src = np.load(NPZ, allow_pickle=False)
ts = np.asarray(src["truth_scalars"])
t_pt_b = ts[rows_b, 0].astype(np.float64)
t_pp_b = ts[rows_b, 1].astype(np.float64)
t_pt_a = ts[rows_a, 0].astype(np.float64)
t_pp_a = ts[rows_a, 1].astype(np.float64)
del ts
w_truth_all = np.asarray(src["w_truth"], np.float64)
w_reco_all = np.asarray(src["w_reco"], np.float64)
pass_reco_all = np.asarray(src["pass_reco"]).astype(bool)
pass_truth_all = np.asarray(src["pass_truth"]).astype(bool)
src.close()

wt_b = w_truth_all[rows_b]
wr_b = w_reco_all[rows_b]
pr_b = pass_reco_all[rows_b]
pg_b = pass_truth_all[rows_b]
pr_a = pass_reco_all[rows_a]
pg_a = pass_truth_all[rows_a]
out["counts"] = {"pass_truth_b": int(pg_b.sum()), "pass_reco_b": int(pr_b.sum()),
                 "step1_b_pass_reco_and_truth": int((pr_b & pg_b).sum()),
                 "step1_a_pass_reco_and_truth": int((pr_a & pg_a).sum())}


def cells(a_pt, a_pp):
    i = np.clip(np.digitize(a_pt, PT) - 1, 0, NPT - 1)
    j = np.clip(np.digitize(a_pp, PP) - 1, 0, NPP - 1)
    return i * NPP + j


def unit_spectrum(pt, pp, w):
    h, _, _ = np.histogram2d(pt, pp, [PT, PP], weights=w)
    return (h / float(h.sum())).ravel()


# ---- CONTROL: rebuild the published spectra ----
h_prior_re = unit_spectrum(t_pt_b[pg_b], t_pp_b[pg_b], wt_b[pg_b])
h_unfold_re = unit_spectrum(t_pt_b[pg_b], t_pp_b[pg_b], (wt_b * push)[pg_b])
out["rebuilt"] = {"h_prior": [float(x) for x in h_prior_re],
                  "h_unfolded": [float(x) for x in h_unfold_re]}

# ---- D's quantity, on the closure's own run ----
c_truth_b = cells(t_pt_b, t_pp_b)
m = pr_b  # the gate's population: pass_reco rows of the training subsample
num = np.bincount(c_truth_b[m], weights=(wr_b * push)[m], minlength=NC)
den = np.bincount(c_truth_b[m], weights=wr_b[m], minlength=NC)
live = den > 0
ratio = np.full(NC, np.nan)
ratio[live] = num[live] / den[live]

sw = den
sw2 = np.bincount(c_truth_b[m], weights=wr_b[m] ** 2, minlength=NC)
n_eff = np.zeros(NC)
n_eff[live] = sw[live] ** 2 / np.maximum(sw2[live], 1e-300)
mean_b = np.zeros(NC)
mean_b[live] = ratio[live]
var_num = np.bincount(c_truth_b[m], weights=wr_b[m] * (push[m] - mean_b[c_truth_b[m]]) ** 2,
                      minlength=NC)
var = np.zeros(NC)
var[live] = var_num[live] / np.maximum(den[live], 1e-300)
se = np.zeros(NC)
se[live] = np.sqrt(np.maximum(var[live], 0) / np.maximum(n_eff[live], 1))

good = live & (n_eff >= 50)
r = ratio[good]
exp_sd = float(np.sqrt((se[good] ** 2).mean()))
out["own_run_truth_grid"] = {
    "reduction": ("UNWEIGHTED over cells with den>0 AND n_eff>=50; n_eff is the Kish effective "
                  "count sum(w)^2/sum(w^2) of w_reco within the cell -- D's reduction, copied so "
                  "the two runs are compared like-for-like"),
    "n_eff_threshold": 50,
    "population": "pass_reco rows of half B (the leg the gate's sums are taken over)",
    "n_live": int(live.sum()), "n_good": int(good.sum()),
    "global_ratio_all_pass_reco": float(num.sum() / den.sum()),
    "ratio_min": float(r.min()), "ratio_max": float(r.max()), "ratio_mean": float(r.mean()),
    "ratio_sd": float(r.std(ddof=1)),
    "spread_frac": float((r.max() - r.min()) / r.mean()),
    "rel_sd": float(r.std(ddof=1) / r.mean()),
    "noise_expected_sd": exp_sd,
    "observed_over_noise": float(r.std(ddof=1) / exp_sd) if exp_sd > 0 else None,
    "per_cell_ratio": [None if not np.isfinite(x) else float(x) for x in ratio],
    "per_cell_n_eff": [float(x) for x in n_eff],
    "per_cell_in_summary": [bool(x) for x in good],
}

# marginals, same reduction as D
ii, jj = np.divmod(np.flatnonzero(good), NPP)
marg = {}
for name, idx, n in (("pT", ii, NPT), ("p_parallel", jj, NPP)):
    prof = [float(r[idx == k].mean()) if (idx == k).any() else None for k in range(n)]
    fin = [x for x in prof if x is not None]
    marg[name] = {"profile": prof, "min": min(fin), "max": max(fin),
                  "range_over_mean": (max(fin) - min(fin)) / float(np.mean(fin))}
out["own_run_truth_grid"]["marginals"] = marg

# ---- the comparison that matters: D's quantity vs the unfolding's own per-cell correction ----
u = np.full(NC, np.nan)
ok = h_prior_re > 0
u[ok] = h_unfold_re[ok] / h_prior_re[ok]
both = good & np.isfinite(u)
x, y = ratio[both], u[both]
xs, ys = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
out["ratio_vs_unfolding_correction"] = {
    "what": ("x = per-cell fold-forward ratio (w_reco-weighted mean push over pass_reco); "
             "y = h_unfolded[c]/h_prior[c] (w_truth-weighted mean push over pass_truth). Same "
             "push array, same cells, different population and weight leg."),
    "n_cells": int(both.sum()),
    "pearson_r": float(np.corrcoef(x, y)[0, 1]),
    "spearman_r": float(np.corrcoef(xs, ys)[0, 1]),
    "x_rel_sd": float(x.std(ddof=1) / x.mean()),
    "y_rel_sd": float(y.std(ddof=1) / y.mean()),
    "ratio_x_over_y": {"min": float((x / y).min()), "max": float((x / y).max()),
                       "mean": float((x / y).mean()),
                       "rel_sd": float((x / y).std(ddof=1) / (x / y).mean())},
}

print("<<<RECEIPT_JSON>>>")
json.dump(out, sys.stdout, indent=1, sort_keys=True)
print()
