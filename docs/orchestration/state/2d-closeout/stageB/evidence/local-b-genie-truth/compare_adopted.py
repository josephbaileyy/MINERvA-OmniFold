"""Compare the adopted C_U (62590df7) with covariances rebuilt from saved May universe vectors; KI-92 effect."""
import json, re, sys
from collections import defaultdict
import numpy as np
A = np.load("sweeps.npz"); M = json.load(open("sweeps.json")); C = np.load("adopted_cov.npz")
ref = A["ref/E_U|hXSec2D"][1:-1, 1:-1].ravel(); rep = ref > 0
vec = lambda t: A[f"{t}|hXSec2D"][1:-1, 1:-1].ravel()[rep]
c0 = vec("may/CV")
bands = defaultdict(dict)
for t in M:
    if t.startswith("may/") and t != "may/CV":
        b, i = re.match(r"may/(.+)_(\d+)$", t).groups(); bands[b][int(i)] = t
out = {"band": {}}
mine_tot = np.zeros((205, 205))
for b, d in bands.items():
    D = np.stack([vec(d[i]) - c0 for i in sorted(d)]); Z = D - D.mean(0)
    cv_ = Z.T @ Z / len(d); mine_tot += cv_
    ad = C[f"hCov_universe_full_{b}"]
    out["band"][b] = float(np.max(np.abs(cv_ - ad)) / np.max(np.abs(ad)))
norm = C["hCov_universe___Normalization_flat"]
tot = C["hCov_universe_total"]; comb = C["hCov_combined"]
out["max_band_rel_diff_mine_vs_adopted"] = max(out["band"].values())
out["total_mine_plus_norm_vs_adopted"] = float(np.max(np.abs(mine_tot + norm - tot)) / np.max(np.abs(tot)))
out["norm_rel_sigma"] = float(np.median(np.sqrt(np.diag(norm)) / c0))
rvp = C["hCov_universe_full_Rvp1pi"]; rvn = C["hCov_universe_full_Rvn1pi"]
out["adopted_Rvn_vs_Rvp_maxdiff_over_max"] = float(np.max(np.abs(rvn - rvp)) / np.max(np.abs(rvn)))
for name, T in (("C_U_total", tot), ("combined_U_plus_stat", comb)):
    s = np.sqrt(np.diag(T)); s1 = np.sqrt(np.diag(T - rvp))
    r = s1 / s
    out[name] = {"median_rel_sigma": float(np.median(s / c0)), "sigma_ratio_count_once_median": float(np.median(r)),
                 "sigma_ratio_min": float(r.min()), "argmin_reported_index": int(r.argmin()),
                 "median_rel_sigma_count_once": float(np.median(s1 / c0)),
                 "trace_frac": float(np.trace(rvp) / np.trace(T)),
                 "rank_before": int(np.linalg.matrix_rank(T, tol=np.linalg.eigvalsh(T).max() * 1e-12)),
                 "rank_after": int(np.linalg.matrix_rank(T - rvp, tol=np.linalg.eigvalsh(T - rvp).max() * 1e-12))}
    # integral functional (area-weighted)
xe = np.array([0, .07, .15, .25, .33, .4, .47, .55, .7, .85, 1., 1.25, 1.5, 2.5, 4.5])
ye = np.array([1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, 15, 20, 40, 60])
area = np.outer(np.diff(xe), np.diff(ye)).ravel()[rep]
I = area @ c0
out["integral"] = {"sigma_rel_before": float(np.sqrt(area @ tot @ area) / I),
                   "sigma_rel_after": float(np.sqrt(area @ (tot - rvp) @ area) / I),
                   "Rvn1pi_band_rel": float(np.sqrt(area @ rvn @ area) / I)}
json.dump(out, open("compare_adopted.json", "w"), indent=1, sort_keys=True)
o = dict(out); o.pop("band"); print(json.dumps(o, indent=1))
