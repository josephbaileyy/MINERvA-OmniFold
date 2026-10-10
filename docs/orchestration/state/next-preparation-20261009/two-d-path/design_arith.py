"""Design arithmetic for the 2D publication-path report (REPORT.md in this directory).

Deterministic; numpy and the standard library only; no cluster access. Operands are read from
committed files in `operands()`. Every number REPORT.md quotes from §3.6 onward is a field of the
JSON this script writes, unless the report names another committed source.

    python3 design_arith.py --self-test      # arithmetic and internal-consistency checks only
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
RESERVE = 0.8      # admitted = subtotal / 0.8 (a protected 20 % reserve of the admitted total)
RETRY, VERIF = 0.05, 0.10
LO, HI = 0.8, 1.25  # proposed width tolerance on kappa = true / claimed sd (B §9)
N_FUNCTIONALS = 205 + 1 + 14 + 16  # cells, reported-domain integral, p_T and p_parallel projections


def operands():
    def load(*p):
        with open(os.path.join(*p)) as f:
            return json.load(f)
    rr = load(HERE, "operands", "remote_reduce.json")
    pn = load(HERE, "operands", "remote_reduce_pn.json")
    pairs = load(HERE, "operands", "remote_reduce_pairs.json")
    speed = load(REPO, "docs/orchestration/state/next-preparation-20261009/speed/results/costs.json")
    toys = np.load(os.path.join(REPO, "docs/orchestration/state/coverage-2d-20261005/interim.npz"))
    return rr, pn, pairs, speed, toys


def coverage(z, kappa):
    """Coverage of [U - z s, U + z s] when the true sd is kappa * s (Gaussian U)."""
    return 2.0 * N01.cdf(z / kappa) - 1.0


def kappa_for_coverage(z, cov):
    return z / N01.inv_cdf((1.0 + cov) / 2.0)


def total_sigma_ratio(f_s, kappa_s):
    """Total-width ratio when only the statistical block is off by kappa_s; f_s = stat share of variance."""
    return math.sqrt(1.0 + f_s * (kappa_s ** 2 - 1.0))


def admitted(subtotal):
    return subtotal / RESERVE


# --------------------------------------------------------------------------- per-cell operands
def blocks(rr, pn):
    sS = np.array(rr["sigma_abs"]["boot_vl170"])
    sM = np.array(rr["sigma_abs"]["ml"])
    sU = np.array(rr["sigma_abs"]["universe"])
    sUp = np.array(pn["sigma_universe_total_abs"])
    return sS, sM, sU, sUp


def per_cell_operands(rr, pn):
    sS, sM, sU, sUp = blocks(rr, pn)
    x1 = np.array(rr["central"]["seed1"])
    x42 = np.array(rr["central"]["CV42_universe_file"])
    xc = np.array(rr["central"]["E_C"])
    xpn = np.array(pn["pn_cv_xsec"])
    tot = np.sqrt(sS ** 2 + sU ** 2 + sM ** 2)
    totp = np.sqrt(sS ** 2 + sUp ** 2 + sM ** 2)
    f_s = sS ** 2 / tot ** 2
    f_s_pn = sS ** 2 / totp ** 2
    seeds = np.array([rr["central"][f"seed{i}"] for i in range(1, 11)])
    cells = rr["cells"]
    q = lambda a: {p: float(np.percentile(a, p)) for p in (0, 16, 50, 84, 90, 100)}
    fam = [i * 16 + j for (i, j), f in zip(cells, f_s_pn) if f >= 0.05]  # paper GlobalID, 0-based bins
    z = (x42 - seeds.mean(axis=0)) / (seeds.std(axis=0, ddof=1) * math.sqrt(1 + 1 / 10))
    return {
        "n_cells": int(len(sS)),
        "f_s_percentiles": q(f_s),
        "n_cells_f_s_ge": {str(t): int((f_s >= t).sum()) for t in (0.02, 0.05, 0.1, 0.25, 0.5)},
        "f_s_pn_percentiles": q(f_s_pn),
        "frozen_family_F": {"rule": "f_s >= 0.05 with VL170 C_S, purity_newomni C_U and C_ML",
                            "globalid_0based": fam, "size": len(fam)},
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
        "E_C_minus_CV42_median_rel_pct": float(np.median(np.abs(xc / x42 - 1)) * 100),
        "central_diffs_in_sigma_stat": {
            "E_C_minus_seed1_median": float(np.median(np.abs(xc - x1) / sS)),
            "seed1_minus_CV42_median": float(np.median(np.abs(x1 - x42) / sS)),
        },
        "ml_over_stat_percentiles": q(sM / sS),
        "seedscan_sd_matches_ml_block_max_rel": float(np.max(np.abs(seeds.std(axis=0, ddof=1) / sM - 1))),
        "CV42_vs_seedscan_z": {"rms": float(np.sqrt(np.mean(z ** 2))), "max_abs": float(np.max(np.abs(z))),
                               "t9_rms_expected": math.sqrt(9 / 7)},
    }


def toy_kurtosis(toys):
    """Development operand: per-cell excess kurtosis of the 100 VL169 closure-toy centrals."""
    U = toys["U"][:, toys["reported"]]
    m = U.mean(axis=0)
    g = ((U - m) ** 4).mean(axis=0) / ((U - m) ** 2).mean(axis=0) ** 2 - 3.0
    return {"n_toys": int(U.shape[0]), "median": float(np.median(g)), "p84": float(np.percentile(g, 84)),
            "max": float(np.max(g))}


# --------------------------------------------------------------------------- split-sample assurance
def log_ratio_se(R, M, gamma):
    """SE of ln(kappa_hat), kappa_hat^2 = v_split / s_boot^2.

    v_split = mean over R random half-splits of (U_A - U_B)^2 / 2; each split contributes one
    degree of freedom. The half-difference has excess kurtosis gamma/2, so its variance-of-variance
    factor is (1 + gamma/4); the bootstrap variance over M replicas has (1 + gamma/2). Random splits
    are treated as independent draws, which holds for a linear statistic and is an assumption here.
    """
    var_ln_v = (2.0 / R) * (1.0 + gamma / 4.0)
    var_ln_s2 = (2.0 / (M - 1)) * (1.0 + gamma / 2.0)
    return 0.5 * math.sqrt(var_ln_v + var_ln_s2)


def per_functional_design(m_tests, alpha=0.05, beta=0.10, gamma=0.0):
    """Smallest R = M such that a per-functional width test (accept |ln kappa_hat| <= c) passes an
    exactly calibrated functional with prob >= 1 - alpha/m and either tolerance edge with prob <= beta."""
    z_a = N01.inv_cdf(1 - alpha / (2 * m_tests))
    z_b = N01.inv_cdf(1 - beta)
    edge = min(math.log(HI), -math.log(LO))
    for R in range(10, 20001):
        se = log_ratio_se(R, R, gamma)
        if (z_a + z_b) * se <= edge:
            return {"R": R, "M": R, "se_log": se, "accept_abs_log_le": z_a * se, "z_alpha": z_a, "m_tests": m_tests}
    return None


def regional_probs(se_med, z, kappa):
    """Verdict probabilities of the regional rule for a median estimate ~ N(ln kappa, se_med):
    FAITHFUL iff the interval est +/- z se_med lies inside [ln LO, ln HI]; FAIL-low / FAIL-high iff
    it lies entirely below / above that range; otherwise INCONCLUSIVE."""
    lk = math.log(kappa)
    lo, hi = math.log(LO), math.log(HI)
    p_f = max(0.0, N01.cdf((hi - z * se_med - lk) / se_med) - N01.cdf((lo + z * se_med - lk) / se_med))
    p_low = N01.cdf((lo - z * se_med - lk) / se_med)
    p_high = 1 - N01.cdf((hi + z * se_med - lk) / se_med)
    return {"faithful": p_f, "fail_low": p_low, "fail_high": p_high, "inconclusive": max(0.0, 1 - p_f - p_low - p_high)}


def regional_tier(gamma, regions, n_tests=4, alpha=0.05, target=0.95, R_fixed=None):
    """Size R = M for the regional rule at its declared Bonferroni level. `regions` maps a region
    name to the assumed effective number of independent cells (capped at the region size)."""
    z = N01.inv_cdf(1 - alpha / (2 * n_tests))

    def probs(R):
        out = {}
        for name, n_eff in regions.items():
            se_med = log_ratio_se(R, R, gamma) * math.sqrt(math.pi / 2) / math.sqrt(n_eff)
            out[name] = {"n_eff_assumed": n_eff, "se_median_log": se_med,
                         **{f"kappa_{k}": regional_probs(se_med, z, k) for k in (1.0, LO, HI, 0.63)}}
        return out

    if R_fixed is None:
        R = 10
        while True:
            p = probs(R)
            all4 = math.prod(v["kappa_1.0"]["faithful"] for v in p.values()) ** 2  # two streams
            if all4 >= target:
                break
            R += 1
    else:
        R = R_fixed
        p = probs(R)
        all4 = math.prod(v["kappa_1.0"]["faithful"] for v in p.values()) ** 2
    return {"R": R, "M": R, "z_bonferroni": z, "P_all_four_faithful_at_kappa_1": all4, "regions": p}


# --------------------------------------------------------------------------- prices
def costs(speed):
    u = speed["exact_backend_unit_rates"]
    rate = {
        "lgbm_cv_shared64_measured": 0.0591,         # 300 VL170 replicas, array 59410433 (mean)
        "lgbm_cv_fullnode_measured": 0.216,          # 59409026_1, one regular full-node replica
        "lgbm_universe_fullnode_measured": 0.7075,   # median of 374 universe tasks (speed §3)
        "lgbm_universe_p1_fullnode_forecast": speed["unit_rates_node_h"]["lgbm_universe"]["p1_fullnode"],
        "exact_cv_as_run": u["cv_as_run"]["node_h"],
        "exact_cv_shared_mem24G": u["cv_as_run"]["node_h"] * 12 / 256,  # XR: --mem 24G of 512 GB
        "exact_cv_packed_forecast": u["cv_packed_now"]["node_h"],
        "exact_universe_now_median_forecast": u["universe_now_median"]["node_h"],
        "exact_universe_now_p90_forecast": u["universe_now_p90"]["node_h"],
        "exact_universe_now_safe_forecast": u["universe_now_safe"]["node_h"],
        "exact_universe_p1_forecast": u["universe_p1"]["node_h"],
    }
    ov = 1 + RETRY + VERIF
    out = {"rates_node_h": rate, "retry": RETRY, "verification_rerun_fraction": VERIF, "reserve_divisor": RESERVE,
           "convention": "admitted = runs x rate x 1.15 / 0.8 unless stated", "core_h_per_node_h": 128}

    def stage(runs, r):
        sub = runs * r * ov
        return {"runs": runs, "rate": r, "subtotal": sub, "admitted": admitted(sub)}

    # XR: five single runs, no fractional retry; one rerun of each kind inside the hard cap.
    exact_job_cap = 30 * 12 / 256   # 30 h limit at 12/256 billing
    lgbm_job_cap = 1 * 64 / 256     # 1 h limit at 64/256 billing
    exp_sub = 3 * rate["exact_cv_shared_mem24G"] + 2 * rate["lgbm_cv_shared64_measured"]
    out["XR"] = {
        "runs": {"exact": 3, "lgbm": 2},
        "expected_subtotal": exp_sub,
        "expected_over_0.8": admitted(exp_sub),
        "expected_if_exact_on_full_nodes": 3 * rate["exact_cv_as_run"] + 2 * rate["lgbm_cv_shared64_measured"],
        "cap_by_job_limits_incl_one_rerun_each_kind": 4 * exact_job_cap + 3 * lgbm_job_cap,
        "exact_job_cap": exact_job_cap, "lgbm_job_cap": lgbm_job_cap,
        "wall_h_measured_full_node": u["wall_per_exact_unfold_h"]["cv"],
    }

    m_band = {"opt": stage(300, rate["lgbm_cv_shared64_measured"]), "cons": stage(300, rate["lgbm_cv_fullnode_measured"])}
    out["L42"] = {"M_band": m_band, "V_Bpm": stage(6, rate["lgbm_cv_fullnode_measured"]),
                  "S_b_lane_C_subtotal": {"opt": 1.3, "cons": 23.8, "note": "includes its 10 lateral unfolds"}}
    out["L42_band_on_universe_file"] = stage(300, rate["lgbm_universe_fullnode_measured"])
    out["exact_10_seed_scan"] = {"packed": stage(10, rate["exact_cv_packed_forecast"]),
                                 "mem24G": stage(10, rate["exact_cv_shared_mem24G"])}
    out["L1"] = {"S_a_now": stage(188, rate["lgbm_universe_fullnode_measured"]),
                 "S_a_p1_forecast": stage(188, rate["lgbm_universe_p1_fullnode_forecast"])}

    xb = {"opt": stage(300, rate["exact_cv_packed_forecast"]), "cons": stage(300, rate["exact_cv_as_run"])}
    xs = {"opt": stage(188, rate["exact_universe_p1_forecast"]),
          "median": stage(188, rate["exact_universe_now_median_forecast"]),
          "cons": stage(188, rate["exact_universe_now_safe_forecast"])}
    out["X_matched"] = {"boot300": xb, "sweep": xs,
                        "admitted_range": [xb["opt"]["admitted"] + xs["opt"]["admitted"],
                                           xb["cons"]["admitted"] + xs["cons"]["admitted"]],
                        "admitted_packed_replicas_today_driver": [xb["opt"]["admitted"] + xs["median"]["admitted"],
                                                                  xb["opt"]["admitted"] + xs["cons"]["admitted"]]}
    t_univ = {"opt": stage(16, rate["exact_universe_p1_forecast"]), "cons": stage(16, rate["exact_universe_now_safe_forecast"])}
    # Stage T is the systematic arm only (16 universe unfolds); the 50-replica statistical arm was
    # dropped because it cannot resolve a width transfer (stage_T_assurance), so it is not priced.
    out["XR_stage_T"] = {"universes": t_univ,
                         "admitted_range": [t_univ["opt"]["admitted"], t_univ["cons"]["admitted"]]}
    return out


def stage_T_assurance(per_cell, gamma):
    """XR stage T. T-syst replaces the tested bands' widths by exact ones. Only if the two
    estimators' deltas were identical universe by universe would eta be exactly 0; under the
    decision-relevant null (widths transfer within tolerance) eta carries between-estimator scatter
    from 10 throws and 3 pairs, and its false-fail rate is not quantified. T-stat (50 exact against
    300 LightGBM replicas, regional rule) is shown only to explain why it was dropped."""
    z = N01.inv_cdf(1 - 0.05 / (2 * 2))  # two regions, one stream (both streams together)
    out = {"T_syst_false_fail_if_deltas_identical_universe_by_universe": 0.0,
           "T_syst_false_fail_under_width_equivalence_null": "not quantified"}
    se_cell = 0.5 * math.sqrt((2 / 49) * (1 + gamma / 2) + (2 / 299) * (1 + gamma / 2))
    out["T_stat_se_cell_log"] = se_cell
    for name, n_eff in (("F", 3), ("rest", 5)):
        se_med = se_cell * math.sqrt(math.pi / 2) / math.sqrt(n_eff)
        out[f"T_stat_{name}"] = {"n_eff_assumed": n_eff,
                                 **{f"kappa_{k}": regional_probs(se_med, z, k) for k in (1.0, LO, HI)}}
    return out


def mappings(per_cell):
    z68, z95 = 1.0, 1.959963984540054
    f_s = np.array(per_cell["f_s"])
    out = {
        "kappa_at_0.63_I68": kappa_for_coverage(z68, 0.63),
        "kappa_at_0.92_I95": kappa_for_coverage(z95, 0.92),
        **{f"coverage_at_kappa_{k}": {"I68": coverage(z68, k), "I95": coverage(z95, k)} for k in (0.8, 0.95, 1.05, 1.25)},
    }
    for ks in (0.63, 0.8, 1.25, 1.6):
        r = np.array([total_sigma_ratio(f, ks) for f in f_s])
        out[f"total_sigma_ratio_if_stat_kappa_{ks}"] = {
            "median": float(np.median(r)), "min": float(r.min()), "max": float(r.max()),
            "n_cells_change_gt_5pct": int((np.abs(r - 1) > 0.05).sum())}
    return out


def pair_structure(rr, pn, pairs):
    """Zero-compute comparison of the +/-1 sigma pair bands of the two seed-42 sweeps.

    The sweeps share one CV realization (1.4e-11) but differ in background treatment, in the
    universe omnifile (regenerated 2026-07-08 after the adopted sweep ran; its universe-weight
    columns were not compared) and in the driver revision. So A_adopted - A_pn has the CV term
    cancelled, and its square measures cross-sweep non-reproducibility of a band's delta, of
    unknown mechanism. It is NOT an estimate of seed noise.
    """
    sS, sM, _, sUp = blocks(rr, pn)
    tot = np.sqrt(sS ** 2 + sUp ** 2 + sM ** 2)
    a = pairs["sweeps"]["adopted_fluxfix"]["pairs"]
    b = pairs["sweeps"]["purity_newomni"]["pairs"]
    corr, hcorr, nonrep, det_A2 = {}, {}, np.zeros_like(tot), np.zeros_like(tot)
    for k in sorted(a):
        A1, A2 = np.array(a[k]["A_signed"]), np.array(b[k]["A_signed"])
        if np.allclose(A1, 0, atol=1e-50) and np.allclose(A2, 0, atol=1e-50):
            continue
        corr[k] = float(np.corrcoef(A1, A2)[0, 1])
        hcorr[k] = float(np.corrcoef(np.array(a[k]["h_abs"]), np.array(b[k]["h_abs"]))[0, 1])
        if corr[k] >= 0.75:
            det_A2 += A2 ** 2
        else:
            nonrep += (A1 - A2) ** 2 / 2
    s = nonrep / tot ** 2
    ok = s < 1
    q = lambda v: {"median": float(np.median(v)), "p84": float(np.percentile(v, 84)), "max": float(np.max(v))}
    noise_like = [k for k, v in corr.items() if v < 0.75]
    bs = pn["band_sigma_abs"]
    tested = ["Flux", "Muon_Energy_MINOS", "MinosEfficiency", "Muon_Energy_MINERvA"]
    share = sum(np.array(bs[t]) ** 2 for t in tested) / tot ** 2
    x = np.array(pn["pn_cv_xsec"])
    rv = {k: float(np.max(np.abs(np.array(sw["pairs"]["Rvn1pi"]["h_abs"]) / np.array(sw["pairs"]["Rvp1pi"]["h_abs"]) - 1)))
          for k, sw in pairs["sweeps"].items()}
    infl = 1 / np.sqrt(1 - s[ok]) - 1
    return {
        "corr_signed_A_by_band": corr,
        "corr_h_by_band": hcorr,
        "n_bands_reproducible_A_ge_0.75": int(sum(1 for v in corr.values() if v >= 0.75)),
        "n_bands_nonreproducible_lt_0.75": len(noise_like),
        "corr_signed_A_range_nonreproducible": [min(corr[k] for k in noise_like), max(corr[k] for k in noise_like)],
        "corr_h_median_nonreproducible": float(np.median([hcorr[k] for k in noise_like])),
        "nonrep_share_of_total_variance": {"median": float(np.median(s)), "p84": float(np.percentile(s, 84)),
                                           "n_cells_ge_1": int((~ok).sum()),
                                           "cells_ge_1_reported_index_and_bins": [[int(i)] + list(rr["cells"][i]) for i in np.where(~ok)[0]]},
        "total_sigma_inflation_if_nonrep_is_additive_inside_total": {
            "formula": "1/sqrt(1-s) - 1, cells with s < 1", "median": float(np.median(infl)),
            "p84": float(np.percentile(infl, 84))},
        "omitted_reproducible_displacement_over_tot": q(np.sqrt(det_A2) / tot),
        "total_sigma_change_if_displacement_added_in_quadrature": q(np.sqrt(1 + det_A2 / tot ** 2) - 1),
        "xr_stage_T_tested_bands": tested,
        "xr_stage_T_tested_share_of_total_variance": {"median": float(np.median(share)), "min": float(share.min())},
        "Rvn1pi_vs_Rvp1pi_max_rel_h_diff_by_sweep": rv,
        "Rvn1pi_median_rel_sigma_pct_pn": float(np.median(np.array(bs["Rvn1pi"]) / x) * 100),
    }


def self_test():
    """Arithmetic and internal-consistency checks. They do not test the modelling premises
    (e.g. that random half-splits behave as independent draws)."""
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
    check("se shrinks with R", log_ratio_se(1000, 1000, 0.0) < log_ratio_se(100, 100, 0.0))
    check("kurtosis inflates se", log_ratio_se(100, 100, 2.0) > log_ratio_se(100, 100, 0.0))
    d = per_functional_design(10)
    check("design meets power", d["accept_abs_log_le"] + N01.inv_cdf(0.9) * d["se_log"] <= math.log(HI) + 1e-12)
    check("more tests need more R", per_functional_design(410)["R"] > d["R"])
    p1 = regional_probs(0.05, 2.5, 1.0)
    check("regional probs sum to 1", abs(sum(p1.values()) - 1) < 1e-12)
    check("regional: KI-85 size mostly fails low", regional_probs(0.03, 2.5, 0.63)["fail_low"] > 0.9)
    check("regional: more precision, more faithful", regional_probs(0.03, 2.5, 1.0)["faithful"] > p1["faithful"])
    rng = np.random.default_rng(7)
    R, M, reps = 60, 60, 4000
    v = rng.chisquare(1, size=(reps, R)).mean(axis=1)
    s2 = rng.chisquare(M - 1, size=reps) / (M - 1)
    check("se formula vs simulation of its own model (10%)", abs((0.5 * np.log(v / s2)).std() / log_ratio_se(R, M, 0.0) - 1) < 0.10)
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
    gam = max(0.0, kt["median"])
    F = pc["frozen_family_F"]["size"]
    regions = {"F": min(3, F), "rest": min(5, 205 - F)}
    split = {
        "gamma_used": gam,
        "declared_family_per_functional": per_functional_design(2 * N_FUNCTIONALS, gamma=gam),
        "stat_relevant_per_cell_F": per_functional_design(2 * F, gamma=gam),
        "regional_sized": regional_tier(gam, regions),
        "regional_at_R100": regional_tier(gam, regions, R_fixed=100),
        "regional_at_R100_optimistic_neff": regional_tier(gam, {"F": min(10, F), "rest": 20}, R_fixed=100),
    }
    c = costs(speed)
    r = c["rates_node_h"]
    ov = 1 + RETRY + VERIF
    tiers = {"declared_family": split["declared_family_per_functional"]["R"],
             "regional": split["regional_sized"]["R"]}
    c["SD_SM_runs"] = {t: 2 * (2 * R + R) for t, R in tiers.items()}  # 2 streams x (2R halves + M = R replicas)
    full = {}
    for route in ("L42", "X"):
        for tier, runs in c["SD_SM_runs"].items():
            for case in ("opt", "cons"):
                if route == "L42":
                    unit = r["lgbm_cv_shared64_measured"] if case == "opt" else r["lgbm_cv_fullnode_measured"]
                    match = c["L42"]["M_band"][case]["subtotal"]
                else:
                    unit = r["exact_cv_packed_forecast"] if case == "opt" else r["exact_cv_as_run"]
                    match = c["X_matched"]["boot300"][case]["subtotal"] + c["X_matched"]["sweep"][case]["subtotal"]
                s_b = c["L42"]["S_b_lane_C_subtotal"][case]  # includes the lateral unfolds
                sub = match + s_b + (6 + runs) * unit * ov    # + 6 B± unfolds + split-sample runs
                full[f"{route}|{tier}|{case}"] = {"subtotal": sub, "admitted": admitted(sub)}
    c["full_route_admitted"] = full
    out = {
        "per_cell": {k: v for k, v in pc.items() if k != "f_s"},
        "toy_kurtosis_dev": kt,
        "mappings": mappings(pc),
        "split_sample": split,
        "stage_T": stage_T_assurance(pc, gam),
        "costs": c,
        "pair_structure": pair_structure(rr, pn, pairs),
    }
    if a.write:
        with open(a.write, "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
            f.write("\n")
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
