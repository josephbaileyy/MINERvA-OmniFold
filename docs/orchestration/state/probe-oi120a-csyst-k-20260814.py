#!/usr/bin/env python3
"""OI-120(a) robustness: is the median fractional noise driven by low-occupancy bins?

A normalized 259-bin shape vector puts ~0.39% of the total in an average bin, so a
fractional noise per bin can be large simply because the denominator is small. Reports
scale-free aggregates and an occupancy-stratified breakdown so the headline cannot be an
artefact of thin bins. Read-only.
"""
import json
import os

import numpy as np

P = "/pscratch/sd/j/josephrb/MINERvA-OmniFold/nd-unfolding/pet"
FILES = [
    ("draw1_member1", f"{P}/fullevent_ml_ensemble/member_1/pet_fullevent_ml_member1_weights.npz"),
    ("draw2", f"{P}/fullevent_floor_42_0/draw_2/pet_fullevent_floor_draw2_weights.npz"),
    ("draw3", f"{P}/fullevent_floor_42_0/draw_3/pet_fullevent_floor_draw3_weights.npz"),
    ("draw4", f"{P}/fullevent_floor_42_0/draw_4/pet_fullevent_floor_draw4_weights.npz"),
    ("draw5", f"{P}/fullevent_floor_42_0/draw_5/pet_fullevent_floor_draw5_weights.npz"),
]
D_REPORTED = sorted(set(range(0, 228)) | set(range(229, 247))
                    | set(range(254, 266)) | set(range(281, 285)))

vecs, masks = {}, {}
for tag, path in FILES:
    if os.path.exists(path):
        with np.load(path, allow_pickle=True) as z:
            vecs[tag] = np.asarray(z["central_vector"], np.float64)
            masks[tag] = np.asarray(z["reported_bin_mask"], bool)

tags = list(vecs)
X = np.vstack([vecs[t] for t in tags])
n = X.shape[0]
mean = X.mean(0)
sd = X.std(0, ddof=1)
m = masks[tags[0]]
dom = m & np.isin(np.arange(285), D_REPORTED) & (mean > 0.0)
f = np.zeros(285)
f[dom] = sd[dom] / mean[dom]

occ = mean[dom]
frac = f[dom]
order = np.argsort(occ)[::-1]                    # most-occupied first
cum = np.cumsum(occ[order]) / occ.sum()

out = {
    "schema": "oi120a-refine-v1",
    "n_draws": n,
    "n_domain": int(dom.sum()),
    "fractional_uncertainty_on_each_sd": float(1.0 / np.sqrt(2 * (n - 1))),

    "SCALE_FREE_AGGREGATES": {
        "L2_sd_over_L2_mean": float(np.linalg.norm(sd[dom]) / np.linalg.norm(mean[dom])),
        "L1_sd_over_L1_mean": float(np.abs(sd[dom]).sum() / np.abs(mean[dom]).sum()),
        "note": ("L2 ratio is the occupancy-weighted analogue of the per-bin median and is the "
                 "number to compare against a covariance sqrt-trace fraction"),
    },

    "OCCUPANCY_STRATIFIED": {},
    "BULK_ONLY": {},
    "correlation_frac_vs_log_occupancy": float(
        np.corrcoef(np.log10(occ), frac)[0, 1]),
    "bins_holding_90pct_of_spectrum": int(np.searchsorted(cum, 0.90) + 1),
    "bins_holding_99pct_of_spectrum": int(np.searchsorted(cum, 0.99) + 1),
}

# quartiles by occupancy
q = np.percentile(occ, [25, 50, 75])
for lab, sel in (("Q1_lowest_occupancy", occ <= q[0]),
                 ("Q2", (occ > q[0]) & (occ <= q[1])),
                 ("Q3", (occ > q[1]) & (occ <= q[2])),
                 ("Q4_highest_occupancy", occ > q[2])):
    out["OCCUPANCY_STRATIFIED"][lab] = {
        "n_bins": int(sel.sum()),
        "share_of_spectrum": float(occ[sel].sum() / occ.sum()),
        "median_frac_noise": float(np.median(frac[sel])),
        "max_frac_noise": float(frac[sel].max()),
    }

# restrict to the bins carrying the bulk
for pct in (0.90, 0.99):
    kk = int(np.searchsorted(cum, pct) + 1)
    sel = order[:kk]
    out["BULK_ONLY"][f"top_bins_to_{int(pct*100)}pct"] = {
        "n_bins": kk,
        "median_frac_noise": float(np.median(frac[sel])),
        "p90_frac_noise": float(np.percentile(frac[sel], 90)),
        "max_frac_noise": float(frac[sel].max()),
        "L2_sd_over_L2_mean": float(np.linalg.norm(sd[dom][sel]) / np.linalg.norm(mean[dom][sel])),
    }

# k table on the DEFENSIBLE aggregate (L2 ratio) and on the bulk median
agg = out["SCALE_FREE_AGGREGATES"]["L2_sd_over_L2_mean"]
bulk = out["BULK_ONLY"]["top_bins_to_90pct"]["median_frac_noise"]
ktab = {}
for name, fval in (("L2_aggregate", agg), ("bulk90_median", bulk)):
    ktab[name] = {"f_null": fval}
    for dphys in (0.02, 0.05, 0.0727, 0.10):
        ktab[name][f"delta_phys_{dphys}"] = {
            f"k_for_noise_le_{int(r*100)}pct": int(np.ceil((fval / (r * dphys)) ** 2))
            for r in (0.10, 0.20, 0.33)}
out["K_TABLE"] = ktab

print(json.dumps(out, indent=1, sort_keys=True))
