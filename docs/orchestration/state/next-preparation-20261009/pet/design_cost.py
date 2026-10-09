"""Precision, event budget and price of candidate PET interval experiments (no runs launched).

Everything here is arithmetic or a seeded synthetic Gaussian simulation; nothing trains, nothing
reads final-bank or reserve rows. Inputs are labelled MEASURED (a committed receipt), FORECAST (a
committed scaled estimate) or ASSUMPTION (declared here). Component ratios come from
`results/saved_reductions.json` (study scale, development tilt, aggregate E_avail).

Sections of the output:

1. ``bias_tolerance``: the largest |bias| / sd at which a normal interval with exactly calibrated
   variance still reaches the proposed lower bounds 0.63 (68 %) and 0.92 (95 %).
2. ``validation_sizing``: replicates per case so that a calibrated procedure passes "pooled coverage
   LB >= tolerance" with assurance 0.9 per decision, one-sided Bonferroni over m decisions, with the
   measured within-replicate design effect.
3. ``pilot_precision``: the spread of the component estimates each candidate design would deliver,
   simulated under the measured study-scale ratios (and a data-scale scenario).
4. ``events``: rows needed per data-size experiment against the banks.
5. ``costs``: A100-hours with the 20 %-of-total reserve (T / 0.8), GPU node-hours, elapsed days,
   prior-size and speed-up sensitivity.

    python design_cost.py --reductions results/saved_reductions.json --out results/design_cost.json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

B = 6
SIM_N = 4000
SIM_SEED = 20261009

# ---- inputs, each with its label and source ------------------------------------------------- #
INPUTS = {
    "u_study_a100h": {"value": 1.768, "label": "MEASURED",
                      "source": "nd-unfolding/pet/final_design/resources/cost_fb_look1-20260930.json "
                                "(H2S1T24 K5 FB median, packing 2, n = 352)"},
    "u_study_realized_a100h": {"value": 1290.0 / 720, "label": "MEASURED (realized, includes scoring "
                               "and 24 stopped D4c members)",
                               "source": "final_design/resources/README.md 2026-10-05 snapshot: coverage stage "
                                         "~1.29 k A100-h for 720 complete members"},
    "u_data_2M_a100h": {"value": 7.3, "low": 3.7, "high": 14.6, "label": "FORECAST",
                        "source": "nd-unfolding/pet/gbdt_comparison/REPORT-20261005.md section 7.2 (scaled; "
                                  "0.5-2x band)"},
    "u_data_10M_a100h": {"value": 29.0, "low": 15.0, "high": 58.0, "label": "FORECAST",
                         "source": "gbdt_comparison/REPORT-20261005.md section 7.2"},
    "throughput_a100h_per_day": {"value": 288.0, "label": "MEASURED (study average, ~12 concurrent A100)",
                                 "source": "gbdt_comparison/REPORT-20261005.md section 7.2"},
    "a100h_per_gpu_node_hour": {"value": 4.0, "label": "MEASURED (iris charging)",
                                "source": "final_design/resources/README.md"},
    "allocation_remaining_gpu_node_h": {"value": 56132.0, "label": "MEASURED 2026-10-05, NOT re-measured",
                                        "source": "final_design/resources/README.md (2026-10-05 13:26Z)"},
    "train_share_of_unfolding": {"value": 1.734 / 1.768, "label": "MEASURED (fit time / receipt median)",
                                 "source": "gbdt_comparison/REPORT-20261005.md section 7.2"},
    "failed_member_allowance": {"value": 0.05, "label": "ASSUMPTION (study excluded none; 622 runs needed "
                                "bit-exact resume across jobs)", "source": "DECISION_RECORD look-1 row"},
    "dev_bank_truth_rows": {"value": 45087969, "label": "MEASURED", "source": "q3 quartile provenance n_used"},
    "fb_rows": {"value": 2646891, "label": "MEASURED", "source": "PROTOCOL section 3"},
    "rb_rows_sealed": {"value": 1414846, "label": "MEASURED", "source": "PROTOCOL section 3"},
    "never_drawn_rows": {"value": 4061737, "label": "MEASURED", "source": "PROTOCOL section 2"},
    "inventory_rows": {"value": 49152885, "label": "MEASURED", "source": "PROTOCOL section 2"},
    "data_size_pseudo_truth_rows": {"value": 9.6e6, "label": "FORECAST (matches 4.0 M reco-passing data)",
                                    "source": "gbdt_comparison/REPORT-20261005.md section 8"},
    "prior_rows_2M": {"value": 2.0e6, "label": "ASSUMPTION (historical full-event practice)",
                      "source": "gbdt_comparison/REPORT-20261005.md section 7.2"},
    "r3_systematics_units": {"low": 121, "high": 308, "label": "FORECAST (unit counts are pricing assumptions)",
                             "source": "gbdt_comparison/REPORT-20261005.md section 7.3 R3"},
    "reserve_fraction_of_total": {"value": 0.2, "label": "RULE (T / 0.8)", "source": "Goal 6 / shared contract"},
}


def v(key: str, which: str = "value") -> float:
    return float(INPUTS[key][which])


# ---- 1. bias tolerance ------------------------------------------------------------------------ #
def normal_coverage(b: float, level: float) -> float:
    z = stats.norm.ppf(0.5 + level / 2)
    return float(stats.norm.cdf(z - b) - stats.norm.cdf(-z - b))


def bias_tolerance() -> dict:
    out = {}
    for level, lb in ((0.68, 0.63), (0.95, 0.92)):
        lo, hi = 0.0, 3.0
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if normal_coverage(mid, level) >= lb else (lo, mid)
        out[f"{level:.2f}"] = {"proposed_lower_bound": lb, "max_abs_bias_over_sd": lo,
                               "coverage_at_bias_0.5sd": normal_coverage(0.5, level),
                               "coverage_at_bias_1sd": normal_coverage(1.0, level),
                               "coverage_at_bias_2sd": normal_coverage(2.0, level)}
    return out


# ---- 2. validation sizing --------------------------------------------------------------------- #
def assurance(n_rep: int, true_p: float, lb_req: float, m: int, deff: float, nbins: int = 7,
              alpha: float = 0.05) -> float:
    """P(Wilson lower bound >= lb_req) for pooled coverage, normal approximation on n_eff."""
    n_eff = n_rep * nbins / deff
    z = stats.norm.ppf(1 - alpha / m)
    # Wilson LB is increasing in p_hat: find the p_hat at which LB == lb_req
    lo, hi = 0.0, 1.0
    for _ in range(80):
        ph = (lo + hi) / 2
        c = ph + z * z / (2 * n_eff)
        lbw = (c - z * math.sqrt(ph * (1 - ph) / n_eff + z * z / (4 * n_eff ** 2))) / (1 + z * z / n_eff)
        lo, hi = (lo, ph) if lbw >= lb_req else (ph, hi)
    p_crit = hi
    sd = math.sqrt(true_p * (1 - true_p) / n_eff)
    return float(1 - stats.norm.cdf((p_crit - true_p) / sd))


def n_for_assurance(true_p: float, lb_req: float, m: int, deff: float, target: float = 0.9) -> int:
    n = 10
    while assurance(n, true_p, lb_req, m, deff) < target:
        n += 1
        if n > 100000:
            return -1
    return n


def validation_sizing(deff: float) -> dict:
    out = {"design_effect": deff, "nbins": 7, "alpha_familywise": 0.05, "assurance_target_per_decision": 0.9,
           "rows": []}
    for tol_label, tols in (("proposed 0.63/0.92", ((0.68, 0.63), (0.95, 0.92))),
                            ("study C1 form 0.60/0.90", ((0.68, 0.60), (0.95, 0.90)))):
        for m, label in ((2, "one case, aggregate only, both levels"),
                         (8, "one case, aggregate + 3 regions, both levels"),
                         (32, "four cases x four regions x two levels")):
            for level, lb in tols:
                n = n_for_assurance(level, lb, m, deff)
                out["rows"].append({"tolerances": tol_label, "m": m, "family": label, "level": level,
                                    "lower_bound": lb, "replicates_per_case": n,
                                    "check_assurance_at_n": assurance(n, level, lb, m, deff)})
    return out


def wilson_ub(k: float, n: float, z: float) -> float:
    ph = k / n
    c = ph + z * z / (2 * n)
    return (c + z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def futility_power(E: int, true_p: float, deff: float, rng, tol: float = 0.63, m: int = 4,
                   nbins: int = 7) -> float:
    """P(no-go) for the rule "Wilson UB (one-sided alpha 0.05/m, on n_eff = E nbins / deff) of the
    pooled 68 % coverage of the FROZEN section-9 interval < tol". Hits are simulated as a
    beta-binomial per experiment with the intra-experiment correlation implied by `deff`."""
    rho = (deff - 1) / (nbins - 1)
    a = true_p * (1 / rho - 1)
    b = (1 - true_p) * (1 / rho - 1)
    z = stats.norm.ppf(1 - 0.05 / m)
    n_eff = E * nbins / deff
    p = rng.beta(a, b, (SIM_N, E))
    k = rng.binomial(nbins, p).sum(axis=1)
    ub = np.array([wilson_ub(x / (E * nbins) * n_eff, n_eff, z) for x in k])
    return float((ub < tol).mean())


# ---- 3. pilot precision ----------------------------------------------------------------------- #
def simulate(design: dict, fT: float, g: float, rng: np.random.Generator) -> dict:
    """Gaussian model with W = 1: s_T^2 = fT, s_P^2 = 1 - fT, s_D^2 = g / B (g = s_D^2 / (W / B)).
    `design`: E experiments x B members; `pairs`: experiments whose B members are refit with the SAME
    Poisson weights and new seeds; `singles`: separate unbootstrapped single fits (other draws)."""
    E, pairs, singles = design["E"], design.get("pairs", 0), design.get("singles", 0)
    sT, sP, sD = math.sqrt(fT), math.sqrt(1 - fT), math.sqrt(g / B)
    est = {"fT": [], "g": [], "bias_se_over_sde": []}
    for _ in range(SIM_N):
        D = rng.normal(0, sD, E)
        P = rng.normal(0, sP, (E, B))
        m = D[:, None] + P + rng.normal(0, sT, (E, B))
        W = m.var(axis=1, ddof=1).mean()
        V = m.mean(axis=1).var(ddof=1)
        sD2 = V - W / B
        if pairs:
            m2 = D[:pairs, None] + P[:pairs] + rng.normal(0, sT, (pairs, B))
            sT2 = ((m[:pairs] - m2) ** 2).mean() / 2
        elif singles:
            s = rng.normal(0, sD, singles) + rng.normal(0, sT, singles)
            sT2 = s.var(ddof=1) - sD2
        else:
            sT2 = float("nan")
        est["fT"].append(sT2 / W)
        est["g"].append(sD2 / (W / B))
        est["bias_se_over_sde"].append(1 / math.sqrt(E))
    q = lambda a: {f"p{p}": float(np.nanpercentile(a, p)) for p in (2.5, 16, 50, 84, 97.5)}  # noqa: E731
    return {"fT_hat": q(np.asarray(est["fT"])), "g_hat": q(np.asarray(est["g"])),
            "bias_se_over_member_mean_error_sd": 1 / math.sqrt(E)}


DESIGNS = {
    "saved_120x6_plus_60_single": {"E": 120, "singles": 60, "units": 0,
                                   "note": "already exists (S5 + S4F); study scale only"},
    "dispatch_192_24x6_plus_8_repeats": {"E": 24, "pairs": 8, "units": 24 * B + 8 * B,
                                         "note": "24 six-member experiments + 8 repeated ensembles (same events and "
                                                 "Poisson weights, new seeds)"},
    "E1_look1_4x6_two_cases_plus_2_partner_sets": {"E": 4, "pairs": 2, "units": 2 * 4 * B + 2 * B,
                                                   "note": "per case; two cases (dev tilt, D5 NuWro) on the same four "
                                                           "draws; partners only on dev tilt"},
    "E1_look2_8x6_two_cases": {"E": 8, "pairs": 2, "units": 2 * 8 * B + 2 * B, "note": "cumulative"},
    "E1_look3_24x6_two_cases": {"E": 24, "pairs": 4, "units": 2 * 24 * B + 4 * B, "note": "cumulative; optional bias-estimation extension beyond E1"},
}


def bias_decisions(E: int, true_z: float, tol: float, alpha_one_sided: float, rng) -> dict:
    """With the member-mean error sd known from the within-experiment members, the bias of one bin is
    estimated with SE sd / sqrt(E); t(E-1) bounds. Returns P(declare inadequate: LB > tol) and
    P(declare adequate: UB < tol)."""
    tq = stats.t.ppf(1 - alpha_one_sided, E - 1)
    e = rng.normal(true_z, 1, (SIM_N, E))
    m, s = e.mean(axis=1), e.std(axis=1, ddof=1) / math.sqrt(E)
    return {"P_inadequate": float(((np.abs(m) - tq * s) > tol).mean()),
            "P_adequate": float(((np.abs(m) + tq * s) < tol).mean())}


# ---- 5. costs --------------------------------------------------------------------------------- #
def price(units: float, u: float) -> dict:
    t = units * (1 + v("failed_member_allowance")) * u
    total = t / (1 - v("reserve_fraction_of_total"))
    return {"units": units, "a100h_subtotal_incl_failures": t, "a100h_total_with_reserve": total,
            "gpu_node_h": total / v("a100h_per_gpu_node_hour"),
            "gpu_days_at_study_throughput": total / v("throughput_a100h_per_day"),
            "share_of_recorded_allocation": total / v("a100h_per_gpu_node_hour") / v("allocation_remaining_gpu_node_h")}


def priced(units: float) -> dict:
    return {"study_scale": price(units, v("u_study_a100h")),
            "data_2M_forecast": {w: price(units, v("u_data_2M_a100h", w)) for w in ("low", "value", "high")},
            "data_10M_forecast": {w: price(units, v("u_data_10M_a100h", w)) for w in ("low", "value", "high")}}


def amdahl(f: float, s: float) -> float:
    return 1 / ((1 - f) + f / s)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reductions", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    red = json.loads(a.reductions.read_text())
    agg = red["histograms"]["eavail"]
    c = {k: np.asarray(x) for k, x in agg["components"].items()}
    bins = slice(1, 6)                     # interior bins 1-5; bin 0 and the open top bin reported apart
    fT_meas = float(np.median(c["sT2"][bins] / c["W"][bins]))
    g_meas = float(np.median(c["sD2"][bins] / (c["W"][bins] / B)))
    deff = max(agg["coverage_section9_own"][L]["design_effect"] for L in ("0.68", "0.95"))
    rng = np.random.default_rng(SIM_SEED)

    out = {"schema": "next-prep-pet/design-cost/1", "inputs": INPUTS, "sim": {"n": SIM_N, "seed": SIM_SEED},
           "measured_ratios_study_scale": {"fT_median_bins1_5": fT_meas, "g_median_bins1_5": g_meas,
                                           "fT_definition": "s_T^2 / W (nominal-seed training variance / member variance)",
                                           "g_definition": "s_D^2 / (W / B) (event-sample variance / internal-randomness "
                                                           "variance of the member mean)"},
           "bias_tolerance": bias_tolerance(),
           "validation_sizing": validation_sizing(deff)}

    scen = {"study_scale_measured": (fT_meas, g_meas),
            "data_scale_sD2_over_16": (fT_meas, g_meas / 16),
            "data_scale_g_unchanged": (fT_meas, g_meas)}
    out["pilot_precision"] = {s: {d: simulate(DESIGNS[d], fT, g, rng) for d in DESIGNS}
                              for s, (fT, g) in scen.items()}
    out["designs"] = DESIGNS
    tol = out["bias_tolerance"]["0.68"]["max_abs_bias_over_sd"]
    alpha = 0.05 / (7 * 4 * 2)            # bins x regions x cases, one-sided
    out["bias_decision_power"] = {
        "tolerance_abs_bias_over_sd": tol, "alpha_one_sided_per_bin": alpha,
        "rows": [{"E": E, "true_abs_bias_over_sd": z, **bias_decisions(E, z, tol, alpha, rng)}
                 for E in (4, 8, 12, 24, 48) for z in (0.0, 0.3, 1.0, 2.0, 3.0)]}

    out["futility_rule"] = {
        "statistic": "pooled 68 % coverage of the frozen section-9 interval in the low-acceptance region, per case "
                     "(dev tilt, D5 NuWro), Wilson UB at one-sided 0.05/4 (two cases x two looks) on n_eff = 7 E / deff",
        "no_go_if": "UB < 0.63 in either case",
        "logic": "for a fixed centre, coverage is monotone in half-width; the section-9 interval is the widest "
                 "member-based construction considered, so a narrower repair cannot cover more",
        "study_scale_value": red["histograms"]["eavail@low_acceptance"]["coverage_section9_own"]["0.68"]["pooled"],
        "deff_low_acceptance": red["histograms"]["eavail@low_acceptance"]["coverage_section9_own"]["0.68"]["design_effect"],
        "rows": [{"E": E, "true_coverage": tp,
                  "P_no_go": futility_power(E, tp, red["histograms"]["eavail@low_acceptance"]
                                            ["coverage_section9_own"]["0.68"]["design_effect"], rng)}
                 for E in (4, 8) for tp in (0.26, 0.45, 0.68, 0.8)]}

    # 4. events
    per_exp = v("data_size_pseudo_truth_rows") + v("prior_rows_2M")
    out["events"] = {
        "rows_per_data_size_experiment_2M_prior": per_exp,
        "disjoint_data_size_experiments_in_DEV": math.floor(v("dev_bank_truth_rows") / per_exp),
        "never_drawn_rows_over_one_experiment": v("never_drawn_rows") / per_exp,
        "pseudodata_sampling_fraction_in_DEV": v("data_size_pseudo_truth_rows") / v("dev_bank_truth_rows"),
        "finite_population_variance_factor": 1 - v("data_size_pseudo_truth_rows") / v("dev_bank_truth_rows"),
        "rows_for_independent_validation": {str(n): n * per_exp for n in (24, 120, 300, 500)},
        "inventory_multiples_for_independent_validation": {str(n): n * per_exp / v("inventory_rows")
                                                           for n in (24, 120, 300, 500)},
    }

    # 5. costs
    n_val = {r["level"]: r["replicates_per_case"] for r in out["validation_sizing"]["rows"]
             if r["m"] == 32 and r["tolerances"].startswith("proposed")}
    nv = max(n_val.values())
    stages = {
        "dispatch_192_pilot": 192,
        "E1_look1": DESIGNS["E1_look1_4x6_two_cases_plus_2_partner_sets"]["units"],
        "E1_through_look2": DESIGNS["E1_look2_8x6_two_cases"]["units"],
        "E1_through_look3": DESIGNS["E1_look3_24x6_two_cases"]["units"],
        "strategyA_whole_bootstrap_per_experiment_O50": B * (1 + 50),
        "strategyA_whole_bootstrap_per_experiment_O200": B * (1 + 200),
        "strategyA_validation_120_experiments_O50": 120 * B * (1 + 50),
        "strategyB_calibration_60x6_three_cases": 60 * B * 3,
        "strategyB_final_validation_four_cases": nv * B * 4,
        "physical_systematics_R3_low": v("r3_systematics_units", "low"),
        "physical_systematics_R3_high": v("r3_systematics_units", "high"),
    }
    stages["full_procedure_strategyB_low"] = (stages["E1_through_look2"] + stages["strategyB_calibration_60x6_three_cases"]
                                              + stages["strategyB_final_validation_four_cases"]
                                              + stages["physical_systematics_R3_low"])
    stages["full_procedure_strategyB_high"] = (stages["E1_through_look2"] + stages["strategyB_calibration_60x6_three_cases"]
                                               + stages["strategyB_final_validation_four_cases"]
                                               + stages["physical_systematics_R3_high"])
    out["validation_replicates_per_case_used"] = nv
    out["costs"] = {k: priced(u) for k, u in stages.items()}
    f = v("train_share_of_unfolding")
    out["speedup_sensitivity"] = {
        "accelerated_fraction_f": f, "label": "f = training share of one unfolding (measured at study scale); "
        "speed-ups are hypothetical (no Session-4 result pushed)",
        "rows": [{"s": s, "amdahl_end_to_end": amdahl(f, s),
                  "full_procedure_strategyB_low_data_2M_a100h": out["costs"]["full_procedure_strategyB_low"]
                  ["data_2M_forecast"]["value"]["a100h_total_with_reserve"] / amdahl(f, s),
                  "E1_look1_data_2M_a100h": out["costs"]["E1_look1"]["data_2M_forecast"]["value"]
                  ["a100h_total_with_reserve"] / amdahl(f, s)}
                 for s in (2, 5, 10, 100)]}
    a.out.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({"fT": fT_meas, "g": g_meas, "deff": deff, "n_val": n_val}, indent=0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
