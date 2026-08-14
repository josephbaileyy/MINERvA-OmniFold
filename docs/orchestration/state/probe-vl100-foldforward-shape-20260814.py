"""Is the fold-forward deficit a pure overall SCALE, or does it vary across the 285-cell grid?

Lane D, falsification test for the VL100 quotability ruling. READ-ONLY.

WHY THIS MATTERS. VL100 = 0.512603276 is computed on UNIT-NORMALIZED 285-cell spectra. The
quotability argument is that the fold-forward normalization deficit divides out under that
normalization. THAT HOLDS IF AND ONLY IF THE DEFICIT IS SCALE-ONLY. If it varies across the grid
it contaminates the normalized shapes and the argument fails.

THE RECORDED QUANTITY CANNOT ANSWER THIS, and that is the first result. The gate
(pet_diagnostic_quarantine.measured_fold_forward_dev) reads two SCALARS:

    fold_forward_sum_w_push_reco   scalar
    fold_forward_sum_w_reco        scalar
    dev = |(num/den)/R - 1|

Both are sums over the whole reco leg, so the shape information is integrated away BEFORE the
number is formed. No amount of reading that field can distinguish scale from shape.

WHAT CAN. The per-event pieces survive in the same artifact -- `weights_push` (2,000,000,) and
`mc_indices` -- so the recorded scalars can be DECOMPOSED per cell using the producer's exact
definition (train_fullevent_nominal.py:576-577):

    sum_w_push_reco = (w_reco[pass_reco] * push[pass_reco]).sum()
    sum_w_reco      =  w_reco[pass_reco].sum()

Per cell:  ratio[c] = sum_c(w_reco*push) / sum_c(w_reco)   -- the w_reco-weighted mean push in c.
A pure scale deficit makes ratio[c] constant. Anything else is shape.

CONTROL, and it is not optional: summing the per-cell numerators and denominators MUST reproduce
the recorded scalars. If it does not, the decomposition is not of the quantity the gate measures
and nothing below means anything.

NOISE, defined rather than asserted (BEN-025 -- do not let a small-sample spread settle this).
Each ratio[c] is a weighted mean of push over the events in c, so its sampling standard error is
estimated per cell from the within-cell weighted variance of push. The observed dispersion is then
compared against the dispersion EXPECTED from that sampling error alone. Reporting only "the
spread is X" would invite exactly the error BEN-025 names.
"""
import json
import os

import numpy as np

REPO = "/pscratch/sd/j/josephrb/MINERvA-OmniFold"
W = os.path.join(REPO, "nd-unfolding/pet/fullevent_nominal/pet_fullevent_nominal_weights.npz")
NPZ = os.path.join(REPO, "nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz")
PT = np.array([0, 0.07, 0.15, 0.25, 0.33, 0.4, 0.47, 0.55, 0.7, 0.85, 1.0, 1.25, 1.5, 2.5, 4.5,
               30.0], float)
PP = np.array([0.0, 0.75, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0,
               20.0, 40.0, 60.0, 120.0], float)
NPT, NPP = len(PT) - 1, len(PP) - 1
NC = NPT * NPP
DEAD = ([12 * NPP + 0] + [13 * NPP + j for j in range(7)] + [14 * NPP + j for j in range(15)])

print("=== fold-forward deficit: SCALE or SHAPE? ===\n")
z = np.load(W, allow_pickle=True)
push = np.asarray(z["weights_push"], np.float64)
imc = np.asarray(z["mc_indices"], np.int64)
rec_num = float(np.asarray(z["fold_forward_sum_w_push_reco"]))
rec_den = float(np.asarray(z["fold_forward_sum_w_reco"]))
tgt = z["target"]
try:
    tgt = tgt.item()
except Exception:
    pass
R = float(tgt["step1_class_ratio"])
z.close()
print(f"recorded  sum_w_push_reco = {rec_num!r}")
print(f"recorded  sum_w_reco      = {rec_den!r}")
print(f"recorded  ratio           = {rec_num / rec_den:.12f}")
print(f"target R (step1_class_ratio) = {R:.12f}")
print(f"dev = |ratio/R - 1|       = {abs((rec_num / rec_den) / R - 1):.6f}")
print(f"subsample rows            = {push.size}\n")

src = np.load(NPZ, allow_pickle=False)
w_reco = np.asarray(src["w_reco"], np.float64)[imc]
pass_reco = np.asarray(src["pass_reco"], bool)[imc]
ts = np.asarray(src["truth_scalars"], np.float64)
rs = np.asarray(src["reco_scalars"], np.float64)
t_pt, t_pp = ts[imc, 0], ts[imc, 1]
r_pt, r_pp = rs[imc, 0], rs[imc, 1]
del ts, rs
src.close()

m = pass_reco
print(f"pass_reco in subsample    = {int(m.sum())} / {m.size}")


def cells(a_pt, a_pp):
    i = np.clip(np.digitize(a_pt, PT) - 1, 0, NPT - 1)
    j = np.clip(np.digitize(a_pp, PP) - 1, 0, NPP - 1)
    return i * NPP + j


def analyse(label, c):
    num = np.bincount(c, weights=(w_reco * push)[m], minlength=NC)
    den = np.bincount(c, weights=w_reco[m], minlength=NC)
    # CONTROL. The trainer uses the LOADER's mc.weight_reco (train_fullevent_nominal.py:564-565),
    # not the NPZ's raw w_reco, so the absolute sums differ. What must hold for the per-cell
    # RATIOS to be the gate's quantity is that the two weights differ by a GLOBAL SCALE k, under
    # which num/den per cell is invariant. Tested, not assumed: k is fixed from the DENOMINATOR
    # alone, then the NUMERATOR must reproduce under that same k. It need not -- num weights each
    # event by push and den does not, so a per-event discrepancy would break this and not the
    # other.
    k = rec_den / den.sum()
    num_pred = num.sum() * k
    resid = abs(num_pred - rec_num) / abs(rec_num)
    print(f"\n--- {label} ---")
    print(f"  k from denominator alone      : {k:.15f}")
    print(f"  numerator predicted under k   : {num_pred!r}")
    print(f"  numerator recorded            : {rec_num!r}")
    print(f"  residual                      : {resid:.3e}")
    ok = resid < 1e-9
    print(f"  weights differ by a GLOBAL SCALE (so per-cell ratios are the gate's): {ok}")
    if not ok:
        print("  *** not a global scale: the per-cell ratios below are NOT the gate's quantity ***")

    live = den > 0
    ratio = np.full(NC, np.nan)
    ratio[live] = num[live] / den[live]
    # per-cell sampling error of the weighted mean of push
    n_eff = np.zeros(NC)
    sw = np.bincount(c, weights=w_reco[m], minlength=NC)
    sw2 = np.bincount(c, weights=(w_reco[m] ** 2), minlength=NC)
    n_eff[live] = sw[live] ** 2 / np.maximum(sw2[live], 1e-300)
    mean_b = np.zeros(NC)
    mean_b[live] = ratio[live]
    # `c` is already masked to pass_reco, so every weight array here must be masked too.
    var_num = np.bincount(c, weights=w_reco[m] * (push[m] - mean_b[c]) ** 2, minlength=NC)
    var = np.zeros(NC)
    var[live] = var_num[live] / np.maximum(den[live], 1e-300)
    se = np.zeros(NC)
    se[live] = np.sqrt(np.maximum(var[live], 0) / np.maximum(n_eff[live], 1))

    good = live & (n_eff >= 50)
    r = ratio[good]
    print(f"  live cells {int(live.sum())}, with n_eff>=50: {int(good.sum())}")
    print(f"  ratio  min {r.min():.6f}  max {r.max():.6f}  mean {r.mean():.6f}  "
          f"sd {r.std(ddof=1):.6f}")
    print(f"  spread  (max-min)/mean = {(r.max() - r.min()) / r.mean():.4%}")
    print(f"  rel sd  sd/mean        = {r.std(ddof=1) / r.mean():.4%}")
    exp_sd = np.sqrt((se[good] ** 2).mean())
    print(f"  sd EXPECTED from sampling noise alone = {exp_sd:.6f}  "
          f"({exp_sd / r.mean():.4%} of mean)")
    excess = r.std(ddof=1) / exp_sd if exp_sd > 0 else float("inf")
    print(f"  observed sd / noise-expected sd = {excess:.2f}x")
    # marginals
    ii, jj = np.divmod(np.flatnonzero(good), NPP)
    for name, idx, n in (("pT", ii, NPT), ("p_parallel", jj, NPP)):
        prof = [float(r[idx == k].mean()) if (idx == k).any() else float("nan") for k in range(n)]
        fin = [x for x in prof if np.isfinite(x)]
        print(f"  {name} marginal: min {min(fin):.4f} max {max(fin):.4f} "
              f"range/mean {(max(fin) - min(fin)) / np.mean(fin):.3%}")
        print(f"    {[round(x, 4) for x in prof]}")
    near = [c_ for c_ in np.flatnonzero(good) if c_ // NPP >= 12]
    if near:
        print(f"  cells on the pT>=1.5 staircase rows with n_eff>=50: {len(near)}, "
              f"ratio mean {np.nanmean(ratio[near]):.6f} vs global {r.mean():.6f}")
    return {"label": label, "global_scale_k": float(k),
            "global_scale_residual": float(resid),
            "control_ok": bool(ok), "n_live": int(live.sum()), "n_good": int(good.sum()),
            "ratio_min": float(r.min()), "ratio_max": float(r.max()),
            "ratio_mean": float(r.mean()), "ratio_sd": float(r.std(ddof=1)),
            "spread_frac": float((r.max() - r.min()) / r.mean()),
            "rel_sd": float(r.std(ddof=1) / r.mean()),
            "noise_expected_sd": float(exp_sd),
            "observed_over_noise": float(excess),
            # BEN-077: publish the operands the SUMMARY was reduced from, not just the array.
            # Shipping per_cell_ratio alone let the mediator recompute a different mean and max
            # from it -- correctly, because the n_eff>=50 cut was not derivable from what was
            # published. n_eff and the good mask close that.
            "reduction": ("summary statistics are UNWEIGHTED over cells with den>0 AND "
                          "n_eff>=50; n_eff is the Kish effective count sum(w)^2/sum(w^2) of "
                          "w_reco within the cell"),
            "n_eff_threshold": 50,
            "n_eff_threshold_provenance": (
                "present in the first version of this probe, before any run; the three "
                "subsequent patches (global-scale control, a broadcast fix, a return-dict fix) "
                "did not touch it. Intermediate versions were not committed, so this rests on "
                "that account rather than on the commit graph."),
            "naive_all_live_cells": {
                "n": int(live.sum()),
                "min": float(np.nanmin(ratio[live])), "max": float(np.nanmax(ratio[live])),
                "mean": float(np.nanmean(ratio[live])),
                "rel_sd": float(np.nanstd(ratio[live], ddof=1) / np.nanmean(ratio[live])),
                "note": "the unweighted reduction over ALL live cells, published so both "
                        "reductions are on the record and the verdict can be seen to survive "
                        "either"},
            "per_cell_ratio": [None if not np.isfinite(x) else float(x) for x in ratio],
            "per_cell_n_eff": [float(x) for x in n_eff],
            "per_cell_in_summary": [bool(x) for x in good]}


out = {"recorded": {"sum_w_push_reco": rec_num, "sum_w_reco": rec_den,
                    "ratio": rec_num / rec_den, "R": R,
                    "dev_abs": abs((rec_num / rec_den) / R - 1)},
       "n_subsample": int(push.size), "n_pass_reco": int(m.sum())}
out["truth_grid"] = analyse("binned on TRUTH (pT, p_par) -- the grid VL100 lives on",
                            cells(t_pt, t_pp)[m])
out["reco_grid"] = analyse("binned on RECO (pT, p_par) -- the leg the sums are taken over",
                           cells(r_pt, r_pp)[m])
print("\n<<<RECEIPT_JSON>>>")
print(json.dumps(out, indent=1, sort_keys=True))
