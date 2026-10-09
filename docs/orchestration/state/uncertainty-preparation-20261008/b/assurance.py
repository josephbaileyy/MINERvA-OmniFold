#!/usr/bin/env python3
"""Deterministic assurance arithmetic for the DRAFT 2D independent-population interval validation.

DRAFT -- NOT REGISTERED, NOT AUTHORIZED. Design arithmetic only: no event, toy, ROOT file or
cluster resource is read or used. Every operand is a literal below with its provenance, so the
output is a pure function of this file. Standard library only (``math``, ``json``, ``argparse``),
so an independent recomputation needs no third-party package.

Governing document: ``docs/orchestration/DESIGN-20261008-2d-independent-statistical-validation.md``.

What is computed
----------------
1. Nominal interval probabilities and the proposed sigma-scale tolerance, as coverage edges.
2. Coverage of ``U +- z * sigma_hat`` when ``sigma_hat`` comes from ``B`` inner replicas.
3. Exact-binomial acceptance hit counts per functional and level, the required number of
   experiments for the false-fail and power requirements, and the familywise assurance
   (union bound, valid under any within-experiment dependence between functionals).
4. Operating characteristic P(pass one functional | true sigma scale) near the boundaries.
5. Bias (accuracy) sizing, separately from coverage, including the finite-reference offset of the
   conditional held-out design.
6. The population frontier: what a split of the one available MC production can and cannot give.
7. The cost of every design option from measured per-run charges, against the measured allocation.

Run ``python3 assurance.py --self-test`` for the deterministic edge cases and
``python3 assurance.py --write assurance.json`` to regenerate the output.
"""

import argparse
import json
import math
import sys

# ---------------------------------------------------------------------------
# Operands (each with its provenance; re-measure the volatile ones before admission)
# ---------------------------------------------------------------------------

OPERANDS = {
    "data_pot": {
        "value": 1.057394261158926e21,
        "source": "dataPOTUsed of the production 2D omnifile, read 2026-10-09 (TParameter); equals "
                  "toy_metadata data_pot in docs/orchestration/state/coverage-2d-20261005/interim.npz.manifest.json",
    },
    "mc_pot": {
        "value": 4.978198462880827e21,
        "source": "mcPOTUsed of the production 2D omnifile, read 2026-10-09 (TParameter)",
    },
    "n_signal_rows": {
        "value": 32849103,
        "source": "mc_signal_reco entries, production 2D omnifile, read 2026-10-09",
    },
    "n_truth_only_misses": {
        "value": 8999007,
        "source": "nTruthOnlyMisses TParameter (sum over 12 playlists), read 2026-10-09",
    },
    "n_background_rows": {
        "value": 658227,
        "source": "mc_background entries, production 2D omnifile, read 2026-10-09",
    },
    "n_data_rows": {
        "value": 4119797,
        "source": "data tree entries, production 2D omnifile, read 2026-10-09",
    },
    "n_closure_events": {
        "value": 20404292,
        "source": "pass_reco & pass_truth, toy_metadata n_closure in docs/orchestration/state/coverage-2d-20261005/interim.npz.manifest.json",
    },
    "sum_w_reco_closure_data_equiv": {
        "value": 3533843.462254312,
        "source": "toy_metadata sum_w_reco_closure (POT-scaled) in docs/orchestration/state/coverage-2d-20261005/interim.npz.manifest.json",
    },
    "n_reported_bins": {
        "value": 205,
        "source": "mean_vl170 > 0 on the 14 x 16 grid in docs/orchestration/state/ki84-rebuild-20261006/vl170_band.json (populations.tsv mask row)",
    },
    "vl170_rebuild_node_h": {
        "value": 17.744,
        "source": "docs/orchestration/state/ki84-rebuild-20261006/budget.json job 59410433, 300 tasks, shared 64 CPU, "
                  "full MC, both bootstrap streams (sacct ElapsedRaw x billing/256)",
    },
    "vl170_rebuild_tasks": {"value": 300, "source": "same job"},
    "vl170_pilot_regular_node_h": {
        "value": 0.216,
        "source": "docs/orchestration/state/ki84-rebuild-20261006/budget.json job 59409026, 1 task, regular",
    },
    "ki85_node_h": {
        "value": 7.076,
        "source": "docs/orchestration/state/ki85-diag-20261006/budget.json, 100 shared runs, MC unresampled",
    },
    "ki85_runs": {"value": 100, "source": "same"},
    "prereg_toy_regular_node_h": {
        "value": 0.198,
        "source": "docs/orchestration/PREREG-20261005-2d-fixed-truth-coverage.md A1.7 P6: mean of three regular pilot toys",
    },
    "r0_cv_only_node_h_range": {
        "value": [0.4, 2.3],
        "source": "lane C reconciliation d07a3d33 (ASSESSMENT-20261008-2d-total-uncertainty-feasibility.md "
                  "setup notes): CV-only identity-carrying event-loop rebuild, 12 playlists, billing ASSUMED",
    },
    "m3246_allocated_node_h": {
        "value": 20000.0,
        "source": "iris on login05, 2026-10-09T06:15:10Z, project m3246 CPU",
    },
    "m3246_charged_node_h": {
        "value": 16959.4,
        "source": "iris on login05, 2026-10-09T06:15:10Z, project m3246 CPU (all users)",
    },
    "ki85_realboot_median_rel_pct": {
        "value": 0.4869623637052485,
        "source": "docs/orchestration/state/ki85-diag-20261006/ki85_result.json median_rel_spread_pct.realboot (200 data-only real-data replicas)",
    },
    "vl170_total_median_rel_pct": {
        "value": 6.8706583503726995,
        "source": "docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.json VL170.block_sum.median_pct",
    },
    "vl170_median_rel_pct": {
        "value": 0.6738150183177408,
        "source": "docs/orchestration/state/ki84-adopt-20261006/recompute_2d_budget.json VL170.boot.median_pct",
    },
}


def v(name):
    return OPERANDS[name]["value"]


# Proposed design constants (PROPOSED; require admission before any execution)
DESIGN = {
    "levels": {
        "I68": {"z": 1.0},
        "I95": {"z": None},  # filled with the exact 0.95 quantile below
    },
    "kappa_tolerance": [0.80, 1.25],
    "n_functionals": 206,          # 205 reported bins + the area-weighted integral
    "alpha_total": 0.05,           # familywise false-fail probability under exact calibration
    "alpha_split": {"coverage": 0.04, "bias": 0.01},
    "beta_per_functional": 0.10,   # P(pass) at a tolerance edge, for one functional
    "bias_tolerance_sigma": 0.20,  # |E(U - T)| / sigma at which a functional must fail
    "b_inner_production": 300,
    "stability_window": 100,       # the required N must keep the property for N..N+window
    "retry_allowance": 0.05,       # planning allowance for identical-seed infrastructure retries
}


# ---------------------------------------------------------------------------
# Numerics (pure, deterministic)
# ---------------------------------------------------------------------------

def norm_cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def norm_ppf(p):
    """Inverse standard-normal CDF by bisection (deterministic, ~1e-15 absolute)."""
    if not 0.0 < p < 1.0:
        raise ValueError(f"p must be in (0, 1), got {p!r}")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def binom_pmf_list(n, p):
    """All Binomial(n, p) probabilities, computed in log space."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if p <= 0.0:
        return [1.0] + [0.0] * n
    if p >= 1.0:
        return [0.0] * n + [1.0]
    lp, lq = math.log(p), math.log1p(-p)
    lgn = math.lgamma(n + 1)
    return [math.exp(lgn - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * lp + (n - k) * lq)
            for k in range(n + 1)]


def acceptance_region(n, p0, alpha_two_sided):
    """Hit-count acceptance ``[a, b]`` with each rejection tail at most ``alpha/2`` under ``p0``.

    Reject low iff ``H <= a - 1`` and high iff ``H >= b + 1``; each tail is the largest one whose
    probability under ``p0`` does not exceed ``alpha_two_sided / 2``.
    """
    pmf = binom_pmf_list(n, p0)
    half = alpha_two_sided / 2.0
    cum, a = 0.0, 0
    for k in range(n + 1):
        cum += pmf[k]
        if cum <= half:
            a = k + 1
        else:
            break
    cum, b = 0.0, n
    for k in range(n, -1, -1):
        cum += pmf[k]
        if cum <= half:
            b = k - 1
        else:
            break
    return a, b


def p_in(n, p, a, b):
    """P(a <= H <= b) for H ~ Binomial(n, p)."""
    if a > b:
        return 0.0
    pmf = binom_pmf_list(n, p)
    return min(1.0, sum(pmf[a:b + 1]))


def chi_scale_nodes(dof, n_nodes=2001):
    """Quadrature nodes/weights for s = sqrt(X / dof), X ~ chi^2_dof (Simpson on X).

    The chi-square density is singular or steep at 0 for dof < 3, where Simpson is inaccurate
    (the self-test measured P(|t_1| <= 1) as 0.0004 instead of 0.5), so those are refused.
    """
    if dof < 3:
        raise ValueError(f"dof must be >= 3 for this quadrature, got {dof}")
    m, sd = float(dof), math.sqrt(2.0 * dof)
    lo, hi = max(1e-12, m - 14.0 * sd), m + 14.0 * sd
    if n_nodes % 2 == 0:
        n_nodes += 1
    h = (hi - lo) / (n_nodes - 1)
    k2 = dof / 2.0
    logc = -k2 * math.log(2.0) - math.lgamma(k2)
    nodes, weights = [], []
    for i in range(n_nodes):
        x = lo + i * h
        w = 1.0 if i in (0, n_nodes - 1) else (4.0 if i % 2 else 2.0)
        dens = math.exp(logc + (k2 - 1.0) * math.log(x) - x / 2.0)
        nodes.append(math.sqrt(x / dof))
        weights.append(w * h / 3.0 * dens)
    tot = sum(weights)
    return nodes, [w / tot for w in weights]


def coverage(z, kappa, b_inner=None, offset=0.0):
    """P(|U - T| <= z * sigma_hat) for Gaussian U.

    ``kappa`` = true sd of (U - T) over experiments / the replica-population sigma.
    ``b_inner`` = number of inner replicas; ``None`` means sigma_hat equals that sigma exactly.
    ``offset`` = a fixed bias of (U - T), in units of the replica-population sigma.
    """
    if kappa <= 0:
        raise ValueError("kappa must be positive")

    def cov_s(s):
        return norm_cdf((z * s - offset) / kappa) - norm_cdf((-z * s - offset) / kappa)

    if b_inner is None:
        return cov_s(1.0)
    nodes, weights = chi_scale_nodes(b_inner - 1)
    return sum(w * cov_s(s) for s, w in zip(nodes, weights))


def normal_average(fn, tau, n_nodes=401):
    """E[fn(d)] for d ~ N(0, tau^2), Simpson over +-10 tau (fn(0) if tau == 0)."""
    if tau == 0.0:
        return fn(0.0)
    if n_nodes % 2 == 0:
        n_nodes += 1
    lo, hi = -10.0 * tau, 10.0 * tau
    h = (hi - lo) / (n_nodes - 1)
    acc = tot = 0.0
    for i in range(n_nodes):
        d = lo + i * h
        w = 1.0 if i in (0, n_nodes - 1) else (4.0 if i % 2 else 2.0)
        dens = math.exp(-0.5 * (d / tau) ** 2)
        acc += w * dens * fn(d)
        tot += w * dens
    return acc / tot


# ---------------------------------------------------------------------------
# Design calculations
# ---------------------------------------------------------------------------

def levels():
    out = {}
    for name, spec in DESIGN["levels"].items():
        z = spec["z"] if spec["z"] is not None else norm_ppf(0.975)
        out[name] = {"z": z, "nominal": 2.0 * norm_cdf(z) - 1.0}
    return out


def edges(lv, b_inner=None):
    k_lo, k_hi = DESIGN["kappa_tolerance"]
    return {name: {"p_low_edge": coverage(d["z"], k_hi, b_inner),
                   "p_high_edge": coverage(d["z"], k_lo, b_inner)}
            for name, d in lv.items()}


def per_test_alpha(n_levels):
    return DESIGN["alpha_split"]["coverage"] / (DESIGN["n_functionals"] * n_levels)


def check_n(n, lv, ed, alpha_t, beta):
    """Return (ok, details) for one N: power at both edges of every level."""
    det, ok = {}, True
    for name, d in lv.items():
        a, b = acceptance_region(n, d["nominal"], alpha_t)
        pl = p_in(n, ed[name]["p_low_edge"], a, b)
        ph = p_in(n, ed[name]["p_high_edge"], a, b)
        f0 = 1.0 - p_in(n, d["nominal"], a, b)
        det[name] = {"accept_hits": [a, b], "p_pass_at_low_edge": pl,
                     "p_pass_at_high_edge": ph, "p_fail_at_nominal": f0}
        ok = ok and pl <= beta and ph <= beta and f0 <= alpha_t
    return ok, det


def required_n(lv, ed, alpha_t, beta, n_max=6000, start=20):
    """Smallest N whose power/size requirements also hold for every N up to N + window."""
    win = DESIGN["stability_window"]
    run_start, n = None, start
    while n <= n_max:
        ok, _ = check_n(n, lv, ed, alpha_t, beta)
        if ok:
            if run_start is None:
                run_start = n
            if n - run_start >= win:
                return run_start
        else:
            run_start = None
        n += 1
    return None


def familywise(n, lv, alpha_t, true_p_by_level):
    """Union-bound P(all coverage tests pass) when every functional has the given true coverage."""
    j = DESIGN["n_functionals"]
    fail = 0.0
    det = {}
    for name, d in lv.items():
        a, b = acceptance_region(n, d["nominal"], alpha_t)
        f = 1.0 - p_in(n, true_p_by_level[name], a, b)
        det[name] = f
        fail += j * f
    return max(0.0, 1.0 - fail), det


def oc_curve(n, lv, alpha_t, b_inner, kappas):
    rows = []
    for k in kappas:
        row = {"kappa": k}
        for name, d in lv.items():
            a, b = acceptance_region(n, d["nominal"], alpha_t)
            p = coverage(d["z"], k, b_inner)
            row[name] = {"true_coverage": p, "p_pass_one_functional": p_in(n, p, a, b)}
        rows.append(row)
    return rows


def bias_sizing(kappa, delta, alpha_family, beta, j):
    """N for a two-sided z-test of mean pull per functional (Bonferroni over j)."""
    za = norm_ppf(1.0 - alpha_family / (2.0 * j))
    zb = norm_ppf(1.0 - beta)
    return math.ceil(((za + zb) * kappa / delta) ** 2), za


def bias_false_fail_with_reference(n, kappa, tau_ref, alpha_family, j):
    """P(one functional fails the bias test) when the fixed reference carries offset ~N(0, tau^2)."""
    za = norm_ppf(1.0 - alpha_family / (2.0 * j))
    c = za * kappa / math.sqrt(n)
    sd = math.sqrt(tau_ref ** 2 + kappa ** 2 / n)
    return 2.0 * (1.0 - norm_cdf(c / sd))


def coverage_false_fail_with_reference(n, lv, alpha_t, b_inner, tau_ref):
    """Expected P(fail) per functional at exact calibration when the reference has offset N(0,tau^2).

    The per-level fail probabilities are computed separately; the familywise bound adds them.
    """
    out = {}
    for name, d in lv.items():
        a, b = acceptance_region(n, d["nominal"], alpha_t)

        def fail_given(dlt, z=d["z"], a=a, b=b):
            return 1.0 - p_in(n, coverage(z, 1.0, None, offset=dlt), a, b)

        out[name] = normal_average(fail_given, tau_ref, n_nodes=121)
    return out


def population_frontier(r_mc):
    rows = []
    for rho in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        rows.append({
            "reservoir_fraction_rho": rho,
            "training_bank_mc_over_data": (1.0 - rho) * r_mc,
            "production_mc_over_data": r_mc,
            "mc_stat_variance_inflation_vs_production": 1.0 / (1.0 - rho),
            "reservoir_exposure_over_data": rho * r_mc,
            "tau2_ref_upper_bound_data_units": 1.0 / (rho * r_mc),
            "production_equivalent": False,
        })
    return rows


# Seed namespaces as closed integer ranges. The production driver seeds the MC stream with
# bootstrap_seed + 10_000_000, so every bootstrap-seed range implies a second, shifted range.
MC_OFFSET = 10_000_000
MAX_EXPERIMENT = 1999
MAX_REPLICA = 999
OUTER_DATA_BASE = 20_261_008_000_000          # outer pseudo-data draw: base + e
INNER_BASE = 20_261_008_200_000               # inner bootstrap_seed: base + 1000 e + r


def seed_ranges():
    """Existing and proposed seed ranges; the proposed ones must meet none of the others."""
    existing = {
        "production_data (VL162/VL170 bootstrap 1..300)": (1, 300),
        "production_mc": (1 + MC_OFFSET, 300 + MC_OFFSET),
        "old_toys_data (1001..1200)": (1001, 1200),
        "old_toys_mc": (10_001_001, 10_001_200),
        "prereg_20261005_data": (20_261_005_000_001, 20_261_005_099_999),
        "prereg_20261005_mc": (20_261_005_500_001, 20_261_005_599_999),
        "ki85_boot_data": (20_261_006_000_001, 20_261_006_009_999),
        "ki85_boot_mc_if_driver_seeded": (20_261_006_000_001 + MC_OFFSET,
                                          20_261_006_009_999 + MC_OFFSET),
    }
    proposed = {
        "outer_pseudo_data": (OUTER_DATA_BASE + 1, OUTER_DATA_BASE + MAX_EXPERIMENT),
        "inner_data_stream": (INNER_BASE + 1000 + 1,
                              INNER_BASE + 1000 * MAX_EXPERIMENT + MAX_REPLICA),
        "inner_mc_stream": (INNER_BASE + 1000 + 1 + MC_OFFSET,
                            INNER_BASE + 1000 * MAX_EXPERIMENT + MAX_REPLICA + MC_OFFSET),
    }
    return existing, proposed


def seed_collisions():
    existing, proposed = seed_ranges()
    allr = list(existing.items()) + list(proposed.items())
    bad = []
    for name, (lo, hi) in proposed.items():
        for other, (lo2, hi2) in allr:
            if other != name and lo <= hi2 and lo2 <= hi:
                bad.append([name, other])
    return bad


def cost(n_exp, b_inner, per_run, retry):
    return n_exp * (b_inner + 1) * per_run * (1.0 + retry)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compute():
    lv = levels()
    b_prod = DESIGN["b_inner_production"]
    alpha_t = per_test_alpha(len(lv))
    beta = DESIGN["beta_per_functional"]
    r_mc = v("mc_pot") / v("data_pot")

    ed_exact = edges(lv, None)
    ed_b300 = edges(lv, b_prod)
    n_req = required_n(lv, ed_b300, alpha_t, beta)
    ok, det = check_n(n_req, lv, ed_b300, alpha_t, beta)

    p_at_k1_b300 = {name: coverage(d["z"], 1.0, b_prod) for name, d in lv.items()}
    nominal = {name: d["nominal"] for name, d in lv.items()}
    fw_nominal, fw_nom_det = familywise(n_req, lv, alpha_t, nominal)
    fw_k1, fw_k1_det = familywise(n_req, lv, alpha_t, p_at_k1_b300)

    # Sensitivity of N to the tolerance and to the family
    sens = []
    for x in (1.15, 1.20, 1.25, 4.0 / 3.0, 1.50):
        tol = [1.0 / x, x]  # exact reciprocals (the design tolerance is [0.80, 1.25] = [1/1.25, 1.25])
        saved = DESIGN["kappa_tolerance"]
        DESIGN["kappa_tolerance"] = tol
        e = edges(lv, b_prod)
        n_both = required_n(lv, e, alpha_t, beta)
        lv68 = {"I68": lv["I68"]}
        n_68 = required_n(lv68, {"I68": e["I68"]}, per_test_alpha(1), beta)
        DESIGN["kappa_tolerance"] = saved
        sens.append({"kappa_tolerance": tol, "N_required_I68_and_I95": n_both,
                     "N_required_I68_only": n_68})

    # Bias sizing (separate from coverage)
    j = DESIGN["n_functionals"]
    a_b = DESIGN["alpha_split"]["bias"]
    dlt = DESIGN["bias_tolerance_sigma"]
    n_bias_k1, z_bias = bias_sizing(1.0, dlt, a_b, beta, j)
    n_bias_khi, _ = bias_sizing(DESIGN["kappa_tolerance"][1], dlt, a_b, beta, j)

    n_design = max(n_req, n_bias_khi)
    _, det_design = check_n(n_design, lv, ed_b300, alpha_t, beta)
    fw_design, _ = familywise(n_design, lv, alpha_t, nominal)
    za_b = norm_ppf(1.0 - a_b / (2.0 * j))
    zb = norm_ppf(1.0 - beta)

    def bias_power(n, kappa):
        m = dlt * math.sqrt(n) / kappa
        return (1.0 - norm_cdf(za_b - m)) + norm_cdf(-za_b - m)

    bias_cov_effect = {name: {"coverage_at_bias_tolerance": coverage(d["z"], 1.0, None, dlt),
                              "nominal": d["nominal"]} for name, d in lv.items()}

    # Effect of a tolerance-edge stat-sigma error on the median-bin total sigma (block sum)
    share = (v("vl170_median_rel_pct") / v("vl170_total_median_rel_pct")) ** 2
    total_effect = {str(k): math.sqrt(1.0 + (k * k - 1.0) * share) - 1.0
                    for k in DESIGN["kappa_tolerance"]}

    # Finite-reference offset of the conditional held-out design (N1)
    f_data = (v("ki85_realboot_median_rel_pct") / v("vl170_median_rel_pct")) ** 2
    ref_rows = []
    for rho in (0.3, 0.5, 0.7):
        for smear_share in (0.25, 0.5, 1.0):
            tau2 = (1.0 / (rho * r_mc)) * smear_share * f_data
            tau = math.sqrt(tau2)
            cov_fail = coverage_false_fail_with_reference(n_req, lv, alpha_t, b_prod, tau)
            bias_fail = bias_false_fail_with_reference(n_req, 1.0, tau, a_b, j)
            ref_rows.append({
                "rho": rho, "smearing_share": smear_share, "f_data": f_data,
                "tau_ref_pull_units": tau,
                "expected_coverage_failures_at_exact_calibration":
                    j * sum(cov_fail.values()),
                "expected_bias_failures_at_exact_calibration": j * bias_fail,
            })

    # Costs
    per_full_shared = v("vl170_rebuild_node_h") / v("vl170_rebuild_tasks")
    per_ki85_shared = v("ki85_node_h") / v("ki85_runs")
    remaining = v("m3246_allocated_node_h") - v("m3246_charged_node_h")
    retry = DESIGN["retry_allowance"]
    costs = {
        "per_run_node_h": {
            "full_mc_both_streams_shared_measured": per_full_shared,
            "pseudo_data_mc_unresampled_shared_measured": per_ki85_shared,
            "full_mc_regular_measured": v("vl170_pilot_regular_node_h"),
            "half_mc_shared_EXTRAPOLATED_linear_in_rows": 0.5 * per_full_shared,
        },
        "m3246_remaining_node_h_all_users": remaining,
        "options": [],
    }

    def add(label, n_exp, b_inner, per_run, measured):
        c = cost(n_exp, b_inner, per_run, retry)
        costs["options"].append({
            "option": label, "experiments": n_exp, "inner_replicas": b_inner,
            "runs": n_exp * (b_inner + 1), "per_run_node_h": per_run,
            "per_run_basis": measured, "node_h_with_retry_allowance": c,
            "fraction_of_remaining_allocation": c / remaining,
        })

    n_floor = min(r["N_required_I68_only"] for r in sens)
    add("P: primary, production-size bank, B=300", n_req, b_prod, per_full_shared, "measured")
    add("P-floor: primary at the loosest scanned tolerance [0.667, 1.5], I68 only, B=300",
        n_floor, b_prod, per_full_shared, "measured")
    add("P-B50: production-size bank, B=50 inner replicas (a separate procedure)", n_req, 50,
        per_full_shared, "measured")
    add("N1: conditional held-out, half-MC bank, B=300", n_req, b_prod,
        0.5 * per_full_shared, "extrapolated")
    add("N1-B50: conditional held-out, half-MC bank, B=50 (a separate procedure)", n_req, 50,
        0.5 * per_full_shared, "extrapolated")
    add("P at N_design (coverage + bias power at the tolerance edge), B=300", n_design, b_prod,
        per_full_shared, "measured")
    add("S: fixed-band transfer secondary, production-size bank, no inner bootstrap", n_req, 0,
        per_full_shared, "measured")
    add("N2: held-out data-stream variance calibration, arms T+B (50 + 50 runs)", 100, 0,
        per_ki85_shared, "measured (KI-85 arms, full MC; a half-MC bank is expected to be cheaper)")
    r0 = v("r0_cv_only_node_h_range")
    costs["r0_identity_rebuild_node_h_range"] = r0
    costs["n2_total_with_r0_node_h_range"] = [costs["options"][-1]["node_h_with_retry_allowance"] + r0[0],
                                              costs["options"][-1]["node_h_with_retry_allowance"] + r0[1]]
    reserve = 0.20
    costs["protected_reserve_fraction"] = reserve
    costs["n2_total_with_r0_and_reserve_node_h_range"] = [
        x / (1.0 - reserve) for x in costs["n2_total_with_r0_node_h_range"]]
    costs["m3246_annual_cpu_allocation_node_h"] = v("m3246_allocated_node_h")
    costs["primary_over_annual_allocation"] = [
        o["node_h_with_retry_allowance"] / v("m3246_allocated_node_h") for o in costs["options"]
        if o["option"].startswith("P: ") or o["option"].startswith("P at N_design")]
    costs["note"] = ("per-run charges are sacct ElapsedRaw x billing/256; option rows exclude the "
                     "identity-carrying rebuild R0, which every independent-population option needs "
                     "once (r0_identity_rebuild_node_h_range, priced by lane C with billing assumed)")

    out = {
        "schema": "uncertainty-preparation-20261008/b/assurance v1",
        "status": "DRAFT -- NOT REGISTERED, NOT AUTHORIZED; design arithmetic, no data",
        "operands": OPERANDS,
        "design_constants_PROPOSED": DESIGN,
        "levels": lv,
        "mc_over_data_exposure": r_mc,
        "coverage_edges_exact_sigma": ed_exact,
        "coverage_edges_b300": ed_b300,
        "coverage_at_kappa1_b300": p_at_k1_b300,
        "per_test_alpha_two_sided": alpha_t,
        "n_coverage_tests": j * len(lv),
        "N_required": n_req,
        "at_N_required": det,
        "familywise_pass_lower_bound_at_nominal": fw_nominal,
        "familywise_pass_lower_bound_at_kappa1_b300": fw_k1,
        "per_test_fail_at_nominal": fw_nom_det,
        "per_test_fail_at_kappa1_b300": fw_k1_det,
        "oc_curve_at_N_required": oc_curve(
            n_req, lv, alpha_t, b_prod,
            [0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4, 1.6]),
        "N_sensitivity": sens,
        "median_bin_stat_variance_share": share,
        "median_bin_total_sigma_change_at_tolerance_edges": total_effect,
        "N_design": n_design,
        "N_design_rule": "max(N_required for coverage, bias N at the high tolerance edge)",
        "at_N_design": det_design,
        "familywise_pass_lower_bound_at_nominal_N_design": fw_design,
        "bias": {
            "tolerance_sigma": dlt, "alpha_family": a_b, "z_critical": z_bias,
            "power_at_N_required_kappa1": bias_power(n_req, 1.0),
            "power_at_N_required_kappa_high": bias_power(n_req, DESIGN["kappa_tolerance"][1]),
            "power_at_N_design_kappa_high": bias_power(n_design, DESIGN["kappa_tolerance"][1]),
            "coverage_effect_of_a_tolerance_sized_bias": bias_cov_effect,
            "N_required_kappa1": n_bias_k1,
            "N_required_kappa_tolerance_high": n_bias_khi,
            "se_mean_pull_at_N_required_kappa1": 1.0 / math.sqrt(n_req),
        },
        "finite_reference_offset_N1": ref_rows,
        "population_frontier": population_frontier(r_mc),
        "max_disjoint_production_size_sets": math.floor(r_mc / (r_mc + 1.0)),
        "seed_namespaces": {"existing": seed_ranges()[0], "proposed": seed_ranges()[1],
                            "collisions": seed_collisions()},
        "costs": costs,
    }
    return out


def self_test():
    """Deterministic edge cases; raises AssertionError on the first failure."""
    t = []

    def chk(name, cond):
        t.append(name)
        assert cond, name

    chk("Phi(0)=0.5", abs(norm_cdf(0.0) - 0.5) < 1e-16)
    chk("ppf(0.975)=1.959963984540054", abs(norm_ppf(0.975) - 1.959963984540054) < 1e-12)
    chk("nominal I68 = 0.6826894921370859",
        abs(coverage(1.0, 1.0) - 0.6826894921370859) < 1e-14)
    chk("nominal z=2 is 0.9545, not 0.95",
        abs(coverage(2.0, 1.0) - 0.9544997361036416) < 1e-14)
    chk("z95 gives 0.95", abs(coverage(norm_ppf(0.975), 1.0) - 0.95) < 1e-12)
    chk("coverage decreases with kappa", coverage(1.0, 1.25) < coverage(1.0, 1.0) < coverage(1.0, 0.8))
    chk("coverage at huge kappa -> 0", coverage(1.0, 1e6) < 1e-5)
    chk("offset symmetric", abs(coverage(1.0, 1.0, None, 0.3) - coverage(1.0, 1.0, None, -0.3)) < 1e-15)
    chk("offset lowers coverage", coverage(1.0, 1.0, None, 0.3) < coverage(1.0, 1.0))
    # chi-scale quadrature: E[s^2] = 1 exactly for s^2 = X / dof
    nodes, w = chi_scale_nodes(299)
    chk("E[s^2]=1 (dof 299)", abs(sum(wi * s * s for s, wi in zip(nodes, w)) - 1.0) < 1e-9)
    # Student-t identity: P(|U| <= z s) with s^2 ~ chi2_d/d is P(|t_d| <= z). Literals from
    # scipy.stats.t 1.15.2: 2*t.cdf(1, 10) - 1 and 2*t.cdf(1.959963984540054, 299) - 1.
    chk("t_10 identity", abs(coverage(1.0, 1.0, b_inner=11) - 0.6591068676979399) < 1e-9)
    chk("t_299 identity", abs(coverage(norm_ppf(0.975), 1.0, b_inner=300) - 0.949071417754147) < 1e-9)
    try:
        coverage(1.0, 1.0, b_inner=2)
        chk("dof < 3 refused", False)
    except ValueError:
        chk("dof < 3 refused", True)
    chk("finite B lowers coverage", coverage(1.0, 1.0, 300) < coverage(1.0, 1.0))
    # binomial
    pm = binom_pmf_list(10, 0.3)
    chk("pmf sums to 1", abs(sum(pm) - 1.0) < 1e-13)
    chk("pmf n=0", binom_pmf_list(0, 0.4) == [1.0])
    chk("pmf p=0", binom_pmf_list(3, 0.0) == [1.0, 0.0, 0.0, 0.0])
    chk("pmf p=1", binom_pmf_list(3, 1.0) == [0.0, 0.0, 0.0, 1.0])
    chk("Bin(1,.5) exact", binom_pmf_list(1, 0.5) == [0.5, 0.5])
    a, b = acceptance_region(1, 0.5, 0.05)
    chk("n=1 cannot reject at alpha .05", (a, b) == (0, 1))
    a, b = acceptance_region(10, 0.5, 0.05)
    # P(H<=1)=11/1024=0.0107<=0.025, P(H<=2)=56/1024=0.0547>0.025 -> a=2, symmetric b=8
    chk("n=10 p=.5 region [2,8]", (a, b) == (2, 8))
    chk("p_in full range = 1", abs(p_in(10, 0.3, 0, 10) - 1.0) < 1e-13)
    chk("p_in empty = 0", p_in(10, 0.3, 5, 4) == 0.0)
    for n, p, al in ((50, 0.68, 0.01), (500, 0.95, 1e-4), (777, 0.6827, 9.7e-5)):
        a, b = acceptance_region(n, p, al)
        pm = binom_pmf_list(n, p)
        chk(f"lower tail <= alpha/2 (n={n})", sum(pm[:a]) <= al / 2 + 1e-15)
        chk(f"upper tail <= alpha/2 (n={n})", sum(pm[b + 1:]) <= al / 2 + 1e-15)
        chk(f"lower tail maximal (n={n})", a == n or sum(pm[:a + 1]) > al / 2)
        chk(f"upper tail maximal (n={n})", b == 0 or sum(pm[b:]) > al / 2)
    chk("normal_average of 1 = 1", abs(normal_average(lambda d: 1.0, 0.7) - 1.0) < 1e-12)
    chk("normal_average of d^2 = tau^2", abs(normal_average(lambda d: d * d, 0.7) - 0.49) < 1e-6)
    # averaged offset coverage equals coverage at kappa_eff = sqrt(1 + tau^2)
    tau = 0.4
    lhs = normal_average(lambda d: coverage(1.0, 1.0, None, d), tau)
    chk("offset average = kappa_eff", abs(lhs - coverage(1.0, math.sqrt(1 + tau * tau))) < 1e-7)
    n, za = bias_sizing(1.0, 0.2, 0.05, 0.1, 1)
    chk("bias N single test", n == math.ceil(((1.959963984540054 + norm_ppf(0.9)) / 0.2) ** 2))
    chk("frontier never production-equivalent",
        not any(r["production_equivalent"] for r in population_frontier(4.7)))
    chk("cost formula", abs(cost(2, 3, 0.5, 0.0) - 4.0) < 1e-15)
    chk("proposed seed ranges meet no other range", seed_collisions() == [])
    chk("experiment index range covers the design N", MAX_EXPERIMENT >= 1116)
    # negative control: a proposed range placed on the production MC stream must be caught
    global OUTER_DATA_BASE
    saved = OUTER_DATA_BASE
    OUTER_DATA_BASE = 10_000_000
    caught = seed_collisions() != []
    OUTER_DATA_BASE = saved
    chk("seed collision check fires on an overlapping range", caught)
    return t


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--write", metavar="PATH")
    args = ap.parse_args(argv)
    if args.self_test:
        names = self_test()
        print(f"self-test: {len(names)} checks passed")
        return 0
    out = compute()
    text = json.dumps(out, indent=1, sort_keys=False) + "\n"
    if args.write:
        with open(args.write, "w") as fh:
            fh.write(text)
        print(f"wrote {args.write}: N_required={out['N_required']}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
