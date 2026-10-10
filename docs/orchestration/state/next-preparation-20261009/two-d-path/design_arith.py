"""Design arithmetic for the 2D publication-path report (REPORT.md in this directory).

Deterministic; numpy and the standard library only; no cluster access. Operands are read from
committed files and named at the top of `operands()`. Every printed figure in REPORT.md §6–§8 is
a field of the JSON this script writes.

    python3 design_arith.py --self-test
    python3 design_arith.py --write design_arith.json
"""
import argparse
import json
import math
import os
import sys
from statistics import NormalDist

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
N01 = NormalDist()
RESERVE = 0.8  # admitted = subtotal / 0.8 (a protected 20 % reserve of the admitted total)


def operands():
    with open(os.path.join(HERE, "operands", "remote_reduce.json")) as f:
        rr = json.load(f)
    with open(os.path.join(HERE, "operands", "remote_reduce_pn.json")) as f:
        pn = json.load(f)
    with open(os.path.join(HERE, "operands", "remote_reduce_pairs.json")) as f:
        pairs = json.load(f)
    with open(os.path.join(REPO, "docs/orchestration/state/next-preparation-20261009/speed/results/costs.json")) as f:
        speed = json.load(f)
    toys = np.load(os.path.join(REPO, "docs/orchestration/state/coverage-2d-20261005/interim.npz"))
    return rr, pn, pairs, speed, toys


def coverage(z, kappa):
    """Coverage of [U - z s, U + z s] when the true sd is kappa * s (Gaussian U)."""
    return 2.0 * N01.cdf(z / kappa) - 1.0


def kappa_for_coverage(z, cov):
    """Inverse of coverage(): the true/claimed sd ratio at which the interval covers `cov`."""
    return z / N01.inv_cdf((1.0 + cov) / 2.0)


def total_sigma_ratio(f_s, kappa_s):
    """Total-width ratio when only the statistical block is off by kappa_s; f_s = stat share of variance."""
    return math.sqrt(1.0 + f_s * (kappa_s ** 2 - 1.0))


def admitted(subtotal):
    return subtotal / RESERVE


def per_cell_operands(rr, pn):
    sS = np.array(rr["sigma_abs"]["boot_vl170"])
    sU = np.array(rr["sigma_abs"]["universe"])
    sM = np.array(rr["sigma_abs"]["ml"])
    sUp = np.array(pn["sigma_universe_total_abs"])
    x1 = np.array(rr["central"]["seed1"])
    x42 = np.array(rr["central"]["CV42_universe_file"])
    xc = np.array(rr["central"]["E_C"])
    xpn = np.array(pn["pn_cv_xsec"])
    tot = np.sqrt(sS ** 2 + sU ** 2 + sM ** 2)
    totp = np.sqrt(sS ** 2 + sUp ** 2 + sM ** 2)
    f_s = sS ** 2 / tot ** 2
    seeds = np.array([rr["central"][f"seed{i}"] for i in range(1, 11)])
    q = lambda a: {p: float(np.percentile(a, p)) for p in (0, 16, 50, 84, 90, 100)}
    return {
        "n_cells": int(len(sS)),
        "f_s_percentiles": q(f_s),
        "n_cells_f_s_ge": {str(t): int((f_s >= t).sum()) for t in (0.02, 0.05, 0.1, 0.25, 0.5)},
        "f_s": f_s.tolist(),
        "rel_tot_pct_percentiles_adopted": q(100 * tot / x42),
        "rel_tot_pct_percentiles_pn": q(100 * totp / xpn),
        "rel_stat_pct_percentiles": q(100 * sS / x1),
        "sigmaU_pn_over_adopted_percentiles": q(sUp / sU),
        "ml_share_percentiles": q(sM ** 2 / tot ** 2),
        "central_diffs_in_sigma_tot": {
            "E_C_minus_CV42": {"median": float(np.median(np.abs(xc - x42) / tot)), "max": float(np.max(np.abs(xc - x42) / tot))},
            "seed1_minus_CV42": {"median": float(np.median(np.abs(x1 - x42) / tot)), "max": float(np.max(np.abs(x1 - x42) / tot))},
            "pn_CV_minus_CV42_max_rel": float(np.max(np.abs(xpn / x42 - 1))),
        },
        "central_diffs_in_sigma_stat": {
            "E_C_minus_seed1_median": float(np.median(np.abs(xc - x1) / sS)),
            "seed1_minus_CV42_median": float(np.median(np.abs(x1 - x42) / sS)),
        },
        "seedscan_sd_matches_ml_block_max_rel": float(np.max(np.abs(seeds.std(axis=0, ddof=1) / sM - 1))),
        "CV42_vs_seedscan_z": (lambda z: {"rms": float(np.sqrt(np.mean(z ** 2))), "max_abs": float(np.max(np.abs(z)))})(
            (x42 - seeds.mean(axis=0)) / (seeds.std(axis=0, ddof=1) * math.sqrt(1 + 1 / 10))),
    }


def toy_kurtosis(toys):
    """Development operand: per-cell excess kurtosis of the 100 VL169 closure-toy centrals."""
    U = toys["U"][:, toys["reported"]]
    m = U.mean(axis=0)
    c2 = ((U - m) ** 2).mean(axis=0)
    c4 = ((U - m) ** 4).mean(axis=0)
    g = c4 / c2 ** 2 - 3.0
    return {"n_toys": int(U.shape[0]), "median": float(np.median(g)), "p84": float(np.percentile(g, 84)),
            "max": float(np.max(g))}


def log_ratio_se(R, M, gamma):
    """SE of ln(kappa_hat) for the split-sample width test.

    kappa_hat^2 = v_split / s_boot^2; v_split = mean over R random half-splits of (U_A - U_B)^2 / 2;
    s_boot^2 from M bootstrap replicas on one half. Under Gaussian U each split contributes one
    chi^2_1 degree of freedom; excess kurtosis gamma inflates the variance of a variance estimate
    by (1 + gamma/2) per degree of freedom. Random splits are treated as independent draws,
    which holds for a linear statistic (signs independent across splits, given the data).
    """
    var_ln_v = (2.0 / R) * (1.0 + gamma / 2.0)
    var_ln_s2 = (2.0 / (M - 1)) * (1.0 + gamma / 2.0)
    return 0.5 * math.sqrt(var_ln_v + var_ln_s2)


def per_cell_design(m_tests, lo=0.8, hi=1.25, alpha=0.05, beta=0.10, gamma=0.0, R_eq_M=True):
    """Smallest R (= M) such that a per-cell two-sided width test at familywise alpha over m_tests
    passes an exactly calibrated cell with prob >= 1 - alpha/m (Bonferroni) and passes a cell at
    either tolerance edge with prob <= beta. Acceptance: |ln kappa_hat| <= c."""
    z_a = N01.inv_cdf(1 - alpha / (2 * m_tests))
    z_b = N01.inv_cdf(1 - beta)
    edge = min(math.log(hi), -math.log(lo))
    for R in range(10, 20001):
        se = log_ratio_se(R, R, gamma)
        c = z_a * se
        if c + z_b * se <= edge:
            return {"R": R, "M": R, "se_log": se, "accept_abs_log_le": c, "z_alpha": z_a, "m_tests": m_tests}
    return None


def global_tier(R, M, gamma, n_eff):
    """95 % interval half-width of the median ln kappa over cells, treating the cells as n_eff
    independent values (a proposed, conservative stand-in for the unmeasured cell correlation)."""
    se = log_ratio_se(R, M, gamma) * 1.2533 / math.sqrt(n_eff)  # median of normals: sqrt(pi/2)
    return {"R": R, "M": M, "n_eff_assumed": n_eff, "half_width_95_log": 1.96 * se,
            "inside_[0.8,1.25]_if_true_kappa_1": 1.96 * se < math.log(1.25)}


def costs(speed):
    u = speed["exact_backend_unit_rates"]
    rate = {
        "lgbm_cv_shared64_measured": 0.0591,       # 300 VL170 replicas, array 59410433 (mean)
        "lgbm_cv_fullnode_measured": 0.216,        # 59409026_1, one regular full-node replica
        "lgbm_universe_fullnode_measured": 0.7075,  # median of 374 universe tasks (speed §3)
        "lgbm_universe_p1_fullnode_forecast": speed["unit_rates_node_h"]["lgbm_universe"]["p1_fullnode"],
        "exact_cv_as_run": u["cv_as_run"]["node_h"],
        "exact_cv_shared_mem24G": u["cv_as_run"]["node_h"] * 12 / 256,  # XR request: --mem 24G of 512 GB
        "exact_cv_packed_forecast": u["cv_packed_now"]["node_h"],
        "exact_universe_now_median_forecast": u["universe_now_median"]["node_h"],
        "exact_universe_now_p90_forecast": u["universe_now_p90"]["node_h"],
        "exact_universe_now_safe_forecast": u["universe_now_safe"]["node_h"],
        "exact_universe_p1_forecast": u["universe_p1"]["node_h"],
    }
    retry, verif = 0.05, 0.10
    out = {"rates_node_h": rate, "retry": retry, "verification_rerun_fraction": verif, "reserve_divisor": RESERVE}

    def stage(runs, r):
        sub = runs * r * (1 + retry + verif)
        return {"runs": runs, "rate": r, "subtotal": sub, "admitted": admitted(sub)}

    # Next experiment XR (§8): reproduction of both candidate centrals.
    xr_runs_exact, xr_runs_lgbm = 2, 2
    xr = {
        "exact_shared_mem24G": stage(xr_runs_exact, rate["exact_cv_shared_mem24G"]),
        "exact_packed": stage(xr_runs_exact, rate["exact_cv_packed_forecast"]),
        "exact_unpacked": stage(xr_runs_exact, rate["exact_cv_as_run"]),
        "lgbm": stage(xr_runs_lgbm, rate["lgbm_cv_shared64_measured"]),
    }
    xr["admitted_mem24G_total"] = xr["exact_shared_mem24G"]["admitted"] + xr["lgbm"]["admitted"]
    xr["admitted_packed_total"] = xr["exact_packed"]["admitted"] + xr["lgbm"]["admitted"]
    # hard per-job limits: exact 26 h x 12/256; LightGBM 1 h x 64/256
    xr["cap_by_job_limits"] = 2 * 26 * 12 / 256 + 2 * 1 * 64 / 256
    xr["admitted_unpacked_total"] = xr["exact_unpacked"]["admitted"] + xr["lgbm"]["admitted"]
    xr["cap_node_h"] = 3.0
    xr["wall_h"] = u["wall_per_exact_unfold_h"]["cv"]
    out["XR"] = xr

    # Route L42 (§6): matched seed-42 statistical band; laterals; split-sample validation; B±.
    m_band = stage(300, rate["lgbm_cv_shared64_measured"])
    m_band_cons = stage(300, rate["lgbm_cv_fullnode_measured"])
    lat = {"setup_S_b_lane_C": [1.3, 23.8], "lateral_unfolds": stage(10, rate["lgbm_cv_fullnode_measured"])}
    bpm = stage(6, rate["lgbm_cv_fullnode_measured"])
    out["L42"] = {"M_band_opt": m_band, "M_band_cons": m_band_cons, "V_lat": lat, "V_Bpm": bpm}

    # Route L1 (alternative): seed-1 sweep on the universe file (lane C's S-a), VL170 reused.
    out["L1"] = {"S_a_now": stage(188, rate["lgbm_universe_fullnode_measured"]),
                 "S_a_p1_forecast": stage(188, rate["lgbm_universe_p1_fullnode_forecast"])}

    # Route X, matched exact construction (§6): 300 exact replicas + 188 exact universe-file unfolds.
    xb = stage(300, rate["exact_cv_packed_forecast"])
    xs = {k: stage(188, rate[k]) for k in ("exact_universe_p1_forecast", "exact_universe_now_median_forecast",
                                           "exact_universe_now_p90_forecast", "exact_universe_now_safe_forecast")}
    out["X_matched"] = {"boot300": xb, "sweep": xs,
                        "admitted_range": [xb["admitted"] + xs["exact_universe_p1_forecast"]["admitted"],
                                           xb["admitted"] + xs["exact_universe_now_safe_forecast"]["admitted"]]}
    # Route X via a demonstrated transfer (XR stage T): 10 Flux throws + 3 pair bands (6) exact, 50 exact replicas.
    t_univ = {k: stage(16, rate[k]) for k in ("exact_universe_p1_forecast", "exact_universe_now_median_forecast",
                                              "exact_universe_now_safe_forecast")}
    t_boot = stage(50, rate["exact_cv_packed_forecast"])
    out["XR_stage_T"] = {"universes": t_univ, "boot50": t_boot,
                         "admitted_range": [t_boot["admitted"] + t_univ["exact_universe_p1_forecast"]["admitted"],
                                            t_boot["admitted"] + t_univ["exact_universe_now_safe_forecast"]["admitted"]]}
    return out


def split_sample(per_cell, gamma_dev):
    f_s = np.array(per_cell["f_s"])
    fam = {str(t): int((f_s >= t).sum()) for t in (0.05, 0.1)}
    gam = max(0.0, gamma_dev)
    res = {"gamma_used": gam, "family_sizes": fam}
    for t, n in fam.items():
        res[f"per_cell_f_s_ge_{t}"] = per_cell_design(m_tests=2 * n, gamma=gam)  # two streams
    res["per_cell_all_205"] = per_cell_design(m_tests=2 * 205, gamma=gam)
    res["global_R100_M100_neff20"] = global_tier(100, 100, gam, 20)
    res["global_R100_M100_neff5"] = global_tier(100, 100, gam, 5)
    return res


def mappings(per_cell):
    z68, z95 = 1.0, 1.959963984540054
    f_s = np.array(per_cell["f_s"])
    out = {
        "kappa_at_0.63_I68": kappa_for_coverage(z68, 0.63),
        "kappa_at_0.92_I95": kappa_for_coverage(z95, 0.92),
        "coverage_at_kappa_1.25": {"I68": coverage(z68, 1.25), "I95": coverage(z95, 1.25)},
        "coverage_at_kappa_0.8": {"I68": coverage(z68, 0.8), "I95": coverage(z95, 0.8)},
        "coverage_at_kappa_1.05": {"I68": coverage(z68, 1.05), "I95": coverage(z95, 1.05)},
        "coverage_at_kappa_0.95": {"I68": coverage(z68, 0.95), "I95": coverage(z95, 0.95)},
    }
    for ks in (0.63, 0.8, 1.25, 1.6):
        r = np.array([total_sigma_ratio(f, ks) for f in f_s])
        out[f"total_sigma_ratio_if_stat_kappa_{ks}"] = {
            "median": float(np.median(r)), "min": float(r.min()), "max": float(r.max()),
            "n_cells_change_gt_5pct": int((np.abs(r - 1) > 0.05).sum())}
    return out


def self_test():
    fails = []

    def check(name, ok):
        if not ok:
            fails.append(name)

    check("coverage nominal I68", abs(coverage(1.0, 1.0) - 0.682689492) < 1e-8)
    check("coverage nominal I95", abs(coverage(1.959963984540054, 1.0) - 0.95) < 1e-9)
    check("kappa inverse", abs(kappa_for_coverage(1.0, coverage(1.0, 1.17)) - 1.17) < 1e-9)
    check("B edge I68 at 1.25", abs(coverage(1.0, 1.25) - 0.5763) < 1e-3)
    check("total ratio f_s=0", total_sigma_ratio(0.0, 3.0) == 1.0)
    check("total ratio f_s=1", abs(total_sigma_ratio(1.0, 1.3) - 1.3) < 1e-12)
    check("reserve", abs(admitted(80.0) - 100.0) < 1e-12)
    check("reserve is not x1.2", abs(admitted(80.0) - 96.0) > 1)
    se_small = log_ratio_se(1000, 1000, 0.0)
    se_big = log_ratio_se(100, 100, 0.0)
    check("se shrinks with R", se_small < se_big)
    check("kurtosis inflates se", log_ratio_se(100, 100, 2.0) > se_big)
    d = per_cell_design(10)
    check("design meets power", d is not None and d["accept_abs_log_le"] + N01.inv_cdf(0.9) * d["se_log"] <= math.log(1.25) + 1e-12)
    d_more = per_cell_design(410)
    check("more tests need more R", d_more["R"] > d["R"])
    # negative control: a looser tolerance must need fewer splits
    check("looser tolerance fewer R", per_cell_design(10, lo=2 / 3, hi=1.5)["R"] < d["R"])
    # simulation check of log_ratio_se on Gaussian linear statistic (seeded)
    rng = np.random.default_rng(7)
    R, M, reps = 60, 60, 4000
    v = rng.chisquare(1, size=(reps, R)).mean(axis=1)            # split part, true variance 1
    s2 = rng.chisquare(M - 1, size=reps) / (M - 1)              # bootstrap part
    k = 0.5 * np.log(v / s2)
    check("se formula vs simulation (10%)", abs(k.std() / log_ratio_se(R, M, 0.0) - 1) < 0.10)
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write")
    a = ap.parse_args()
    if a.self_test:
        fails = self_test()
        print("self-test:", "PASS" if not fails else f"FAIL {fails}")
        sys.exit(1 if fails else 0)
    rr, pn, pairs, speed, toys = operands()
    pc = per_cell_operands(rr, pn)
    kt = toy_kurtosis(toys)
    out = {
        "per_cell": {k: v for k, v in pc.items() if k != "f_s"},
        "toy_kurtosis_dev": kt,
        "mappings": mappings(pc),
        "split_sample": split_sample(pc, kt["median"]),
        "costs": costs(speed),
        "pair_structure": pair_structure(rr, pn, pairs),
    }
    c = out["costs"]
    r = c["rates_node_h"]
    ov = 1 + c["retry"] + c["verification_rerun_fraction"]
    tiers = {"regional_R100": 100, "per_cell_fs_ge_0.05": out["split_sample"]["per_cell_f_s_ge_0.05"]["R"]}
    # Two streams; each needs 2R half-sample unfolds and M = R bootstrap replicas on one half.
    sdsm_runs = {t: 2 * (2 * R + R) for t, R in tiers.items()}
    c["SD_SM_runs"] = sdsm_runs
    s_b = {"opt": 1.3, "cons": 23.8}  # lane C setup item S-b (selection-complete laterals), node-h
    full = {}
    for route in ("L42", "X"):
        for tier, runs in sdsm_runs.items():
            for case in ("opt", "cons"):
                if route == "L42":
                    unit = r["lgbm_cv_shared64_measured"] if case == "opt" else r["lgbm_cv_fullnode_measured"]
                    match = c["L42"]["M_band_opt" if case == "opt" else "M_band_cons"]["subtotal"]
                else:
                    unit = r["exact_cv_packed_forecast"] if case == "opt" else r["exact_cv_as_run"]
                    sweep = "exact_universe_p1_forecast" if case == "opt" else "exact_universe_now_safe_forecast"
                    boot = c["X_matched"]["boot300"]["subtotal"] if case == "opt" else 300 * r["exact_cv_as_run"] * ov
                    match = boot + c["X_matched"]["sweep"][sweep]["subtotal"]
                sub = match + s_b[case] + (10 + 6 + runs) * unit * ov  # laterals, B±, split-sample
                full[f"{route}|{tier}|{case}"] = {"subtotal": sub, "admitted": admitted(sub)}
    c["full_route_admitted"] = full
    c["core_h_per_node_h"] = 128  # Perlmutter CPU node: 2 x 64-core EPYC 7763; billing 256 threads
    if a.write:
        with open(a.write, "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
    print(json.dumps(out, indent=1, sort_keys=True))


def pair_structure(rr, pn, pairs):
    """Zero-compute decomposition of the +/-1 sigma pair bands of the two seed-42 sweeps.

    The two sweeps share one CV realization (pn CV = CV42 to 1.4e-11) and differ only in the
    background treatment, so for a band the difference of the signed common displacements,
    A_adopted - A_pn, has the CV term cancelled; its square estimates the per-run estimator
    perturbation variance sigma_eps^2 (an upper bound where the background treatment matters).
    Under a noise reading each pair's MAT variance term h^2 carries sigma_eps^2 / 2.
    """
    sS = np.array(rr["sigma_abs"]["boot_vl170"])
    sM = np.array(rr["sigma_abs"]["ml"])
    tot = np.sqrt(sS ** 2 + np.array(pn["sigma_universe_total_abs"]) ** 2 + sM ** 2)
    a = pairs["sweeps"]["adopted_fluxfix"]["pairs"]
    b = pairs["sweeps"]["purity_newomni"]["pairs"]
    corr, hcorr, noise_var, det_A2 = {}, {}, np.zeros_like(tot), np.zeros_like(tot)
    for k in sorted(a):
        A1, A2 = np.array(a[k]["A_signed"]), np.array(b[k]["A_signed"])
        if np.allclose(A1, 0, atol=1e-50) and np.allclose(A2, 0, atol=1e-50):
            continue
        r = float(np.corrcoef(A1, A2)[0, 1])
        corr[k] = r
        hcorr[k] = float(np.corrcoef(np.array(a[k]["h_abs"]), np.array(b[k]["h_abs"]))[0, 1])
        if r >= 0.75:
            det_A2 += A2 ** 2          # reproducible displacement omitted by the pair convention
        else:
            noise_var += (A1 - A2) ** 2 / 2  # sigma_eps^2 / 2 per pair, the noise in h^2
    q = lambda v: {"median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "max": float(np.max(v))}
    noise_like = [k for k, v in corr.items() if v < 0.75]
    x = np.array(pn["pn_cv_xsec"])
    bs = pn["band_sigma_abs"]
    tested = ["Flux", "Muon_Energy_MINOS", "MinosEfficiency", "Muon_Energy_MINERvA"]
    share = sum(np.array(bs[t]) ** 2 for t in tested) / tot ** 2
    return {
        "corr_signed_A_by_band": corr,
        "corr_h_by_band": hcorr,
        "corr_signed_A_range_noise_like": [min(corr[k] for k in noise_like), max(corr[k] for k in noise_like)],
        "corr_h_median_noise_like": float(np.median([hcorr[k] for k in noise_like])),
        "xr_stage_T_tested_bands": tested,
        "xr_stage_T_tested_share_of_total_variance": {"median": float(np.median(share)), "min": float(share.min())},
        "n_bands_reproducible_A_ge_0.75": int(sum(1 for v in corr.values() if v >= 0.75)),
        "n_bands_noise_like_lt_0.75": int(sum(1 for v in corr.values() if v < 0.75)),
        "noise_share_of_total_variance": q(noise_var / tot ** 2),
        "total_sigma_inflation_from_noise": q(np.sqrt(1 + noise_var / tot ** 2) - 1),
        "omitted_reproducible_displacement_over_tot": q(np.sqrt(det_A2) / tot),
        "total_sigma_change_if_displacement_added_in_quadrature": q(np.sqrt(1 + det_A2 / tot ** 2) - 1),
    }


if __name__ == "__main__":
    main()
