#!/usr/bin/env python3
"""OI-120(a), normalization axis: the TOTAL spread across Leg F draws at fixed data.

WHY THIS NEEDS NO PUSH STAGE, NO TF, NO ROOT AND NO GPU.
The extracted total cross section is

    sigma_tot = [ sum_i (counts_i * V_i) ] / (flux * data_POT * n_nucleons)

and the denominator is IDENTICAL across the Leg F draws -- same flux histogram, same POT, same
nucleon count. So the RELATIVE spread of sigma_tot across draws is independent of the whole
denominator, and equals the relative spread of the numerator:

    T_d = sum_j  w_truth[j] * push_d[j]     over pass_truth rows of the SHARED subsample

`weights_push` and `mc_indices` are already in each artifact, and all draws carry a bit-identical
`mc_indices` (verified), so `w_truth` and `pass_truth` are common factors read once from the dump.
The DataLoader's in-place rescale of `w_truth` is a per-run CONSTANT derived from the shared reco
leg, so it cancels in a ratio too.

This is what `central_vector` cannot give: it is normalized to unit sum, so its total is exactly 1
by construction. Read-only; no artifact is modified.
"""
import json
import os

import numpy as np

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet"
DUMP = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/g2_fullevent/input/G2_FPS_MEFHC_P12.npz"
FILES = [
    ("draw1_member1", f"{P}/fullevent_ml_ensemble/member_1/pet_fullevent_ml_member1_weights.npz"),
    ("draw2", f"{P}/fullevent_floor_42_0/draw_2/pet_fullevent_floor_draw2_weights.npz"),
    ("draw3", f"{P}/fullevent_floor_42_0/draw_3/pet_fullevent_floor_draw3_weights.npz"),
    ("draw4", f"{P}/fullevent_floor_42_0/draw_4/pet_fullevent_floor_draw4_weights.npz"),
    ("draw5", f"{P}/fullevent_floor_42_0/draw_5/pet_fullevent_floor_draw5_weights.npz"),
]

push, idx, meta = {}, {}, {}
for tag, path in FILES:
    if not os.path.exists(path):
        continue
    with np.load(path, allow_pickle=True) as z:
        push[tag] = np.asarray(z["weights_push"], np.float64)
        idx[tag] = np.asarray(z["mc_indices"], np.int64)
        meta[tag] = {"inputs_sha256": str(z["inputs_sha256"].item()),
                     "bootstrap_seed": int(z["bootstrap_seed"]),
                     "cap_saturation_frac": float(z["cap_saturation_frac"])}
tags = list(push)
ref = tags[0]

out = {"schema": "oi120a-normalization-axis-v1", "n_draws": len(tags), "draws": tags,
       "dump": DUMP, "dump_present": os.path.exists(DUMP)}

# premises
prem = {
    "all_mc_indices_bit_identical": all(np.array_equal(idx[t], idx[ref]) for t in tags),
    "all_push_same_length": len({push[t].size for t in tags}) == 1,
    "all_same_inputs_sha256": len({meta[t]["inputs_sha256"] for t in tags}) == 1,
    "all_bootstrap_seed_minus1": all(meta[t]["bootstrap_seed"] == -1 for t in tags),
    "all_push_finite": {t: bool(np.isfinite(push[t]).all()) for t in tags},
    "all_push_positive": {t: bool((push[t] > 0).all()) for t in tags},
}
out["premises"] = prem
if not (prem["all_mc_indices_bit_identical"] and prem["all_push_same_length"]):
    out["VOID"] = "subsamples are not identical; a common-factor cancellation is not available"
    print(json.dumps(out, indent=1, sort_keys=True))
    raise SystemExit(0)

with np.load(DUMP, allow_pickle=True) as d:
    keys = set(d.files)
    out["dump_has_keys"] = sorted(keys & {"w_truth", "pass_truth", "truth_scalars",
                                          "data_pot", "mc_pot", "pot_scale"})
    w_full = np.asarray(d["w_truth"], np.float64)
    pt_full = np.asarray(d["pass_truth"]).astype(bool)

sel = idx[ref]
w = w_full[sel]
ptr = pt_full[sel]
out["subsample"] = {
    "n_rows": int(sel.size),
    "n_pass_truth": int(ptr.sum()),
    "pass_truth_fraction": float(ptr.mean()),
    "sum_w_truth_pass": float(w[ptr].sum()),
}

# the numerator total per draw, and the prior (unpushed) total for reference
T = {t: float((w[ptr] * push[t][ptr]).sum()) for t in tags}
T_prior = float(w[ptr].sum())
vals = np.array([T[t] for t in tags], float)
out["totals"] = {
    "T_per_draw_arbitrary_units": T,
    "T_prior_unpushed": T_prior,
    "mean": float(vals.mean()),
    "sd_ddof1": float(vals.std(ddof=1)),
    "RELATIVE_SD": float(vals.std(ddof=1) / vals.mean()),
    "min": float(vals.min()), "max": float(vals.max()),
    "range_over_mean": float((vals.max() - vals.min()) / vals.mean()),
    "push_mean_per_draw": {t: float(push[t][ptr].mean()) for t in tags},
}

# comparison to CSTAT-O2 and to the Poisson prediction quoted there
o2_family_rel_sd = 0.04478
o2_poisson_pred = 0.000493
rel = out["totals"]["RELATIVE_SD"]
out["COMPARISON_TO_CSTAT_O2"] = {
    "this_floor_relative_sd_of_total": rel,
    "CSTAT_O2_family_relative_sd_of_total": o2_family_rel_sd,
    "CSTAT_O2_poisson_prediction": o2_poisson_pred,
    "floor_over_family": float(rel / o2_family_rel_sd),
    "floor_over_poisson": float(rel / o2_poisson_pred),
    "family_variance_accounted_for_by_this_floor": float((rel / o2_family_rel_sd) ** 2),
    "residual_if_quadrature": (float(np.sqrt(max(o2_family_rel_sd**2 - rel**2, 0.0)))),
    "CAVEATS": [
        "this floor is measured on the 2M SUBSAMPLE numerator; CSTAT-O2's 4.478% is the published "
        "full-inventory extracted total. They share a definition up to the common denominator and "
        "the subsample restriction, not exactly.",
        "this floor is at bootstrap_seed = -1 (NO Poisson); the family members each carry a draw. "
        "So family = Poisson (+) this floor, if the two are independent.",
        "n is small; the fractional uncertainty on this sd is 1/sqrt(2*(n-1)).",
    ],
}
out["fractional_uncertainty_on_this_sd"] = float(1.0 / np.sqrt(2 * (len(tags) - 1)))
out["cap_saturation_frac_per_draw"] = {t: meta[t]["cap_saturation_frac"] for t in tags}

print(json.dumps(out, indent=1, sort_keys=True))
