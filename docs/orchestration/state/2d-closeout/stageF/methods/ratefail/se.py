import json, numpy as np
from scipy.stats import norm
from scipy.optimize import least_squares
D = {r["name"]: r for r in json.load(open("diag_out.json"))["rows"]}
def inv(c68, c95):
    if not (0 < c68 < 1 and c95 < 1): return np.nan, np.nan
    F = lambda p: [norm.cdf((k - p[0]) / p[1]) - norm.cdf((-k - p[0]) / p[1]) - c for k, c in ((1, c68), (1.96, c95))]
    best = min((least_squares(F, [d0, s0], bounds=([0, .05], [10, 10])) for d0 in (0, 1, 2, 3) for s0 in (.5, 1, 1.5)), key=lambda r: r.cost)
    return tuple(best.x) if best.cost < 1e-6 else (np.nan, np.nan)
rng = np.random.default_rng(0)
for nm in ("J224", "EW17", "J233", "EW23", "EW11", "EW29", "EW16", "EW10", "J116", "EW9", "EW15", "EW_all_ones", "total_integrated", "EW7", "EW0"):
    r = D[nm]; t = r["eavail_tilt"]; h = t["hw_over_sigma"]
    d, s = t["inferred_absbias_over_sigma"], t["inferred_sd_over_sigma"]
    sig_t = r["sigma_rel_tilt_pct"]
    if np.isnan(d):
        print(f"{nm:16s} not invertible (c68 {t['cov68']:.3f} c95 {t['cov95']:.3f})"); continue
    bs = []
    for _ in range(300):
        x = rng.normal(d / h, s / h, 400)  # in half-width units
        bs.append(inv(np.mean(np.abs(x) <= 1), np.mean(np.abs(x) <= 1.96))[0] * h)
    bs = np.array(bs); bs = bs[np.isfinite(bs)]
    sign = np.sign(r["p3tilt_cor_pct"])
    dp = sign * d * sig_t
    raw_t = (1 + r["beta_pct"] / 100) * (1 + dp / 100) - 1
    rec = (1 + r["inj_pct"] / 100) * (1 + raw_t) / (1 + r["beta_pct"] / 100) - 1
    print(f"{nm:16s} inj {r['inj_pct']:+.2f}% | inferred corrected mean {dp:+.2f}% ({sign*d:+.2f}+-{bs.std():.2f} sigma; sign from p3) "
          f"SD/sigma {s:.2f} hw/sigma {h:.2f} | implied raw tilt bias {100*raw_t:+.2f}% vs beta {r['beta_pct']:+.2f}+-{r['se_beta_pct']:.2f}% | implied mean recovered change {100*rec:+.2f}%")
