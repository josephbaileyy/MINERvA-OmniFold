import json, sys
from pathlib import Path
import numpy as np
from scipy.stats import norm
from scipy.optimize import least_squares
WT = Path(sys.argv[1]); OUT = Path(sys.argv[2])
sys.path.insert(0, str(WT / "nd-unfolding"))
import s5c_coverage as cov
S = WT / "docs/orchestration/state/s5c"
contract = json.loads((S / "contract.json").read_text())
U, names = cov.reported_functionals(contract)
rec = json.loads((S / "tier_s/interim_400.json").read_text())
assert rec["functional_names"] == names
bc = json.loads((S / "d1/bias_correction.json").read_text()); assert bc["functional_names"] == names
beta, se = np.array(bc["beta"]), np.array(bc["se"])
d2 = json.loads((S / "d2/d2_summary.json").read_text())
g2 = list(d2["groups"].values())[0] if "groups" in d2 else None
d2m = np.array(g2["mean_rel"]) if g2 and "mean_rel" in g2 else None
d2s = np.array(g2["se_rel"]) if g2 and "se_rel" in g2 else None
sigma = np.array(rec["sigma"])
P = {}
for tag in ("p3_nominal_s1", "p3_tilt20_s2"):
    z = np.load(S / f"p3/products/{tag}.npz", allow_pickle=False)
    P[tag] = (U @ z["xsec_flat"], U @ z["xtrue_flat"])
fh_n, ft_n = P["p3_nominal_s1"]; fh_t, ft_t = P["p3_tilt20_s2"]
inj = ft_t / ft_n - 1  # same split key 20260924 -> exact injected truth change
res_t_raw = fh_t / ft_t - 1
res_t_cor = fh_t / (1 + beta) / ft_t - 1
res_n_raw = fh_n / ft_n - 1
rec_change = fh_t / fh_n - 1  # recovered change (one experiment each, different Poisson draws)
grid = {g["truth"]: g for g in rec["grid"]}
def invert(c68, c95, h):
    # Gaussian model: f_corr - f_true ~ N(d, s^2); half-widths h (68) and 1.96h (95). Solve |d|/h, s/h.
    if c68 <= 0 or c95 >= 1 or c68 >= 1:
        return np.nan, np.nan
    def F(p):
        d, s = p
        cv = lambda k: norm.cdf((k - d) / s) - norm.cdf((-k - d) / s)
        return [cv(1.0) - c68, cv(1.96) - c95]
    best = None
    for d0 in (0.0, 0.5, 1.0, 2.0, 3.0):
        for s0 in (0.5, 1.0, 1.5):
            r = least_squares(F, [d0, s0], bounds=([0, 0.05], [10, 10]))
            if best is None or r.cost < best.cost:
                best = r
    return (best.x[0] * h, best.x[1] * h) if best.cost < 1e-6 else (np.nan, np.nan)
rows = []
for i, nm in enumerate(names):
    row = {"name": nm, "inj_pct": 100 * inj[i], "beta_pct": 100 * beta[i], "se_beta_pct": 100 * se[i],
           "sigma_rel_nom_pct": 100 * sigma[i] / ft_n[i], "sigma_rel_tilt_pct": 100 * sigma[i] / ft_t[i],
           "p3nom_raw_pct": 100 * res_n_raw[i], "p3tilt_raw_pct": 100 * res_t_raw[i],
           "p3tilt_cor_pct": 100 * res_t_cor[i], "p3tilt_cor_pull": res_t_cor[i] * ft_t[i] / sigma[i],
           "p3_recovered_change_pct": 100 * rec_change[i],
           "d2_signal_only_pct": None if d2m is None else 100 * d2m[i]}
    for t in ("nominal", "eavail_tilt"):
        g = grid[t]; n = g["n_present"]
        c68, c95 = g["hits68"][i] / n, g["hits95"][i] / n
        h = g["halfwidth68_over_sigma"][i]
        d, s = invert(c68, c95, h)
        row[t] = {"cov68": c68, "cov95": c95, "hw_over_sigma": h, "inferred_absbias_over_sigma": d,
                  "inferred_sd_over_sigma": s}
    rows.append(row)
OUT.write_text(json.dumps({"d2_keys": list(d2.keys()), "rows": rows}, indent=1))
def show(r):
    n, t = r["nominal"], r["eavail_tilt"]
    print(f"{r['name']:12s} inj {r['inj_pct']:+6.2f}  beta {r['beta_pct']:+6.2f}+-{r['se_beta_pct']:.2f}  sig/f {r['sigma_rel_nom_pct']:.2f}  "
          f"p3tilt raw {r['p3tilt_raw_pct']:+6.2f} cor {r['p3tilt_cor_pct']:+6.2f} ({r['p3tilt_cor_pull']:+5.1f}s) rec {r['p3_recovered_change_pct']:+6.2f} "
          f"d2 {r['d2_signal_only_pct'] if r['d2_signal_only_pct'] is None else round(r['d2_signal_only_pct'],2)} | "
          f"NOM c68 {n['cov68']:.3f} c95 {n['cov95']:.3f} hw {n['hw_over_sigma']:.2f} |d| {n['inferred_absbias_over_sigma']:.2f} sd {n['inferred_sd_over_sigma']:.2f} | "
          f"TILT c68 {t['cov68']:.3f} c95 {t['cov95']:.3f} hw {t['hw_over_sigma']:.2f} |d| {t['inferred_absbias_over_sigma']:.2f} sd {t['inferred_sd_over_sigma']:.2f}")
by = {r["name"]: r for r in rows}
tc = np.array([r["eavail_tilt"]["cov68"] for r in rows])
order = np.argsort(tc)
print("== worst 12 at tilt (68%)"); [show(rows[i]) for i in order[:12]]
print("== named"); [show(by[k]) for k in ("total_integrated", "EW_all_ones", "EW17", "EW7", "EW20", "EW0", "EW36", "J161") if k in by]
print("== median-ish"); [show(rows[i]) for i in order[70:76]]
inj_all = np.array([r["inj_pct"] for r in rows]); print("inj range", inj_all.min(), np.median(inj_all), inj_all.max())
