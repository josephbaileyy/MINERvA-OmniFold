"""Synthetic, non-training controls with known answers for the split-sample (SD/SM) design.

No MINERvA input and no classifier training. The toy estimator keeps the structure the
two-d-path SD/SM proposal depends on:
  * bin edges are quantiles of a SEEDED 2,000-row sample of all retained rows (MC reco then data),
    computed from row values only, as LightGBM's binning sample is (two-d-path §3.3);
  * a ratio reweight (data / MC per reco bin) pulled to truth, a one-step unfold;
  * zero-weight rows are retained under masks and bootstrap weights, so they still enter binning;
  * the output is invariant to the MC weight scale, as an odds reweight is.

The known answers are Monte Carlo variances over independent productions of data and MC drawn
from the generating law, with the estimator's seed fixed. Every random draw is seeded.

    python3 synthetic_controls.py --out synthetic_controls.json [--productions 300]
"""
import argparse
import json
import math
import time

import numpy as np

N_EXP = 20_000          # expected data events
MC_OVER_DATA = 4.7      # bank exposure ratio, as production (4.708)
K_BINS = 16
N_BINSAMPLE = 400       # deliberately binning-sensitive (production: 200,000 of ~3e7 rows)
REGION = (1.5, 3.0)     # truth functional: yield in this truth interval


def draw_truth(rng, n, tilt):
    """Gamma(2, 1) truth, optionally tilted by (1 + tilt (t - 2)) via rejection."""
    out = []
    need = n
    while need > 0:
        t = rng.gamma(2.0, 1.0, size=int(need * 1.6) + 16)
        if tilt:
            acc = rng.random(t.size) < np.clip(1 + tilt * (t - 2), 0, None) / (1 + tilt * 8)
            t = t[acc]
        out.append(t[:need])
        need -= out[-1].size
    return np.concatenate(out)


def smear(rng, t):
    return t * (1 + 0.15 * rng.standard_normal(t.size)) + 0.05 * rng.standard_normal(t.size)


def production(rng, data_scale=1.0, mc_scale=1.0):
    nd = rng.poisson(N_EXP * data_scale)
    d = smear(rng, draw_truth(rng, nd, 0.2))          # data: tilted truth, reco only
    nm = rng.poisson(N_EXP * MC_OVER_DATA * mc_scale)
    t = draw_truth(rng, nm, 0.0)
    return {"d": d, "dw": np.ones(nd), "t": t, "y": smear(rng, t), "mw": np.ones(nm)}


def estimate(p, seed, dw=None, mw=None):
    """The toy estimator. Edges: quantiles of a seeded sample of ALL rows (weights ignored)."""
    dw = p["dw"] if dw is None else dw
    mw = p["mw"] if mw is None else mw
    rows = np.concatenate([p["y"], p["d"]])
    idx = np.random.default_rng(seed).choice(rows.size, size=min(N_BINSAMPLE, rows.size), replace=False)
    edges = np.quantile(rows[idx], np.linspace(0, 1, K_BINS + 1)[1:-1])
    by = np.searchsorted(edges, p["y"])
    bd = np.searchsorted(edges, p["d"])
    num = np.bincount(bd, weights=dw, minlength=K_BINS)
    den = np.bincount(by, weights=mw, minlength=K_BINS)
    r = np.divide(num, den, out=np.zeros(K_BINS), where=den > 0)
    w = mw * r[by]                      # invariant to the MC weight scale
    sel = (p["t"] >= REGION[0]) & (p["t"] < REGION[1])
    return float(np.sum(w[sel]))


def run(P, R, M, S_SEEDS, seed0=20261010):
    master = np.random.default_rng(seed0)
    FIX = 1  # the estimator's fixed seed
    rec = {k: [] for k in ("U", "boot_d", "boot_m", "seed", "split_d", "split_m", "bootd_half", "bootm_half",
                           "cov_split_d", "U_half_data_fresh", "U_half_mc_fresh")}
    for _ in range(P):
        rng = np.random.default_rng(master.integers(2**63))
        p = production(rng)
        U = estimate(p, FIX)
        rec["U"].append(U)
        bd = [estimate(p, FIX, dw=p["dw"] * rng.poisson(1.0, p["dw"].size)) for _ in range(M)]
        bm = [estimate(p, FIX, mw=p["mw"] * rng.poisson(1.0, p["mw"].size)) for _ in range(M)]
        rec["boot_d"].append(np.var(bd, ddof=1))
        rec["boot_m"].append(np.var(bm, ddof=1))
        rec["seed"].append(np.var([estimate(p, 1000 + s) for s in range(S_SEEDS)], ddof=1))
        # SD: complementary 0/1 data masks; rows retained; x2 restores the half exposure
        diffs, ua, ub = [], [], []
        mask1 = None
        for _r in range(R):
            m = (rng.random(p["dw"].size) < 0.5).astype(float)
            mask1 = m if mask1 is None else mask1
            a = 2 * estimate(p, FIX, dw=p["dw"] * m)
            b = 2 * estimate(p, FIX, dw=p["dw"] * (1 - m))
            diffs.append((a - b) ** 2 / 2)
            ua.append(a)
            ub.append(b)
        rec["split_d"].append(np.mean(diffs))
        rec["cov_split_d"].append(np.cov(ua, ub, ddof=1)[0, 1] / np.sqrt(np.var(ua, ddof=1) * np.var(ub, ddof=1)))
        rec["bootd_half"].append(np.var([2 * estimate(p, FIX, dw=p["dw"] * mask1 * rng.poisson(1.0, p["dw"].size))
                                         for _ in range(M)], ddof=1))
        # SM: complementary 0/1 MC masks (the output is MC-scale invariant)
        diffs, mm1 = [], None
        for _r in range(R):
            m = (rng.random(p["mw"].size) < 0.5).astype(float)
            mm1 = m if mm1 is None else mm1
            diffs.append((estimate(p, FIX, mw=p["mw"] * m) - estimate(p, FIX, mw=p["mw"] * (1 - m))) ** 2 / 2)
        rec["split_m"].append(np.mean(diffs))
        rec["bootm_half"].append(np.var([estimate(p, FIX, mw=p["mw"] * mm1 * rng.poisson(1.0, p["mw"].size))
                                         for _ in range(M)], ddof=1))
        # genuinely new half-size productions (rows dropped, so binning sees only them)
        ph = production(rng, data_scale=0.5)
        ph = dict(ph, t=p["t"], y=p["y"], mw=p["mw"])
        rec["U_half_data_fresh"].append(2 * estimate(ph, FIX))
        pm = production(rng, mc_scale=0.5)
        pm = dict(pm, d=p["d"], dw=p["dw"])
        rec["U_half_mc_fresh"].append(estimate(pm, FIX))
    return {k: np.array(v) for k, v in rec.items()}


def stream_only(P, seed0, which):
    """Repeated-sampling variance of one stream with the other held at one realization."""
    master = np.random.default_rng(seed0)
    base = production(np.random.default_rng(seed0 + 1))
    full, half = [], []
    for _ in range(P):
        rng = np.random.default_rng(master.integers(2**63))
        if which == "data":
            p = production(rng)
            q = dict(p, t=base["t"], y=base["y"], mw=base["mw"])
            h = production(rng, data_scale=0.5)
            h = dict(h, t=base["t"], y=base["y"], mw=base["mw"])
            full.append(estimate(q, 1))
            half.append(2 * estimate(h, 1))
        else:
            p = production(rng)
            q = dict(p, d=base["d"], dw=base["dw"])
            h = production(rng, mc_scale=0.5)
            h = dict(h, d=base["d"], dw=base["dw"])
            full.append(estimate(q, 1))
            half.append(estimate(h, 1))
    # the bootstrap of the same fixed other stream, for comparison
    rng = np.random.default_rng(seed0 + 2)
    if which == "data":
        boot = [estimate(base, 1, dw=base["dw"] * rng.poisson(1.0, base["dw"].size)) for _ in range(400)]
    else:
        boot = [estimate(base, 1, mw=base["mw"] * rng.poisson(1.0, base["mw"].size)) for _ in range(400)]
    return {"var_full": float(np.var(full, ddof=1)), "var_half": float(np.var(half, ddof=1)),
            "half_over_full": float(np.var(half, ddof=1) / np.var(full, ddof=1)),
            "boot_var_at_one_realization": float(np.var(boot, ddof=1)),
            "n": P, "se_rel_var": math.sqrt(2 / (P - 1))}


def log_ratio_se_formula(R, M, gamma=0.0):
    return 0.5 * math.sqrt((2 / R) * (1 + gamma / 4) + (2 / (M - 1)) * (1 + gamma / 2))


def main():  # noqa: C901 - one flat report
    global N_BINSAMPLE, K_BINS
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--productions", type=int, default=300)
    ap.add_argument("--bin-sample", type=int, default=N_BINSAMPLE)
    ap.add_argument("--bins", type=int, default=K_BINS)
    a = ap.parse_args()
    N_BINSAMPLE, K_BINS = a.bin_sample, a.bins
    t0 = time.time()
    R, M, S = 40, 60, 30
    rec = run(a.productions, R, M, S)
    var_true = float(np.var(rec["U"], ddof=1))
    E = lambda k: float(np.mean(rec[k]))
    lk_d = 0.5 * np.log(rec["split_d"] / rec["bootd_half"])
    lk_m = 0.5 * np.log(rec["split_m"] / rec["bootm_half"])
    out = {
        "settings": {"productions": a.productions, "R_splits": R, "M_boot": M, "seeds": S, "N_EXP": N_EXP,
                     "MC_OVER_DATA": MC_OVER_DATA, "K_BINS": K_BINS, "N_BINSAMPLE": N_BINSAMPLE},
        "C1_full_variance_decomposition": {
            "var_true_fixed_seed_new_productions": var_true,
            "mean_boot_data": E("boot_d"), "mean_boot_mc": E("boot_m"), "mean_seed": E("seed"),
            "ratio_boot_both_over_true": (E("boot_d") + E("boot_m")) / var_true,
            "ratio_boot_both_plus_seed_over_true": (E("boot_d") + E("boot_m") + E("seed")) / var_true,
            "se_rel_var_true": math.sqrt(2 / (a.productions - 1))},
        "C3_split_targets": {
            "data": {"mean_split": E("split_d"), "mean_boot_half": E("bootd_half"),
                     "var_half_fresh_rows_both_streams_vary": float(np.var(rec["U_half_data_fresh"], ddof=1)),
                     "kappa_mean_split_vs_boot_half": math.sqrt(E("split_d") / E("bootd_half"))},
            "mc": {"mean_split": E("split_m"), "mean_boot_half": E("bootm_half"),
                   "var_half_fresh_rows_both_streams_vary": float(np.var(rec["U_half_mc_fresh"], ddof=1)),
                   "kappa_mean_split_vs_boot_half": math.sqrt(E("split_m") / E("bootm_half"))}},
        "C5_ln_kappa_hat_spread": {
            "data": {"mean": float(lk_d.mean()), "sd_over_productions": float(lk_d.std(ddof=1))},
            "mc": {"mean": float(lk_m.mean()), "sd_over_productions": float(lk_m.std(ddof=1))},
            "formula_se_R_M": log_ratio_se_formula(R, M)},
        "C6_corr_of_halves_over_splits_given_production": {"median": float(np.median(rec["cov_split_d"])),
                                                           "p16": float(np.percentile(rec["cov_split_d"], 16)),
                                                           "p84": float(np.percentile(rec["cov_split_d"], 84))},
        "C4_scaling_data_stream": stream_only(a.productions, 777, "data"),
        "C4_scaling_mc_stream": stream_only(a.productions, 888, "mc"),
        "wall_s": time.time() - t0,
    }
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
