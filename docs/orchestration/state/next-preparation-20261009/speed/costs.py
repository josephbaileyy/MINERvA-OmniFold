"""Full-procedure cost of the named uncertainty procedures under implementation speedups.

Reads ``results/profile.json`` (Perlmutter ``sacct`` reductions), the local
benchmark records in ``results/``, lane C's published ``costs.json`` (for the
reproduction check only) and the PET cost receipt. Writes ``results/costs.json``.
Standard library only; nothing is launched.

Conventions
-----------
* node-h = elapsed x billing / 256 / 3600 (Perlmutter CPU). A100-h for PET.
* Amdahl time factor ``A(f, s) = (1 - f) + f / s`` multiplies the elapsed time of
  one unit of work; billed node-h scale with it only when the allocation does
  not change. Packing changes are priced separately (``packing``).
* Admitted totals use lane C's formula (setup + development + production +
  verification + retry, then / 0.8 for the protected 20 % reserve), re-implemented
  here and checked against C's published values before any speedup is applied.
* Every operand carries a basis: MEASURED (Perlmutter receipt), LOCAL (this
  lane's laptop benchmark; never Perlmutter throughput), DOCUMENTED, ASSUMED or
  ANALYTICAL.
"""

import json
import math
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
C_COSTS = os.path.join(REPO, "docs/orchestration/state/uncertainty-preparation-20261008/c/costs.json")
PET_COST = os.path.join(REPO, "nd-unfolding/pet/final_design/resources/cost_fb_look1-20260930.json")
NODE_MEM_GB = 487802 * 2**20 / 1e9
RESERVE = 0.20
SPEEDUPS = (2, 5, 10, 100)
N_UNI, N_SEEDS = 187, 10

# Row counts of the production CV omnifile (read-only ROOT open on a login node, 2026-10-09).
ROWS = {"mc_signal_reco": 32849103, "mc_truth_denom": 32849103, "data": 4119797,
        "mc_background": 658227}
FILL_LOOPS_PURITY = 6       # hTruth2D, hUnfold2D, 2 in compute_efficiency_2d, 2 in completeness
# Comparators, not ceilings (B section 14, iris 2026-10-09T06:15Z).
CPU_REMAINING_NODE_H = 3040.6
CPU_ANNUAL_NODE_H = 20000.0
GPU_REMAINING_NODE_H = 55107.0   # m3246_g, 4 A100 per GPU node-hour


def amdahl(f, s):
    return (1.0 - f) + f / s


def load_bench():
    recs = []
    with open(os.path.join(HERE, "results", "bench_loader_fill.jsonl")) as fh:
        for ln in fh:
            d = json.loads(ln)
            if "seconds" in d:
                recs.append(d)
    get = {(d["variant"], d["tree"]): d["us_per_row_min"] for d in recs}
    return recs, get


# --------------------------------------------------------------------------------------
# Lane C's admitted-total formula, re-implemented (checked against C's costs.json).
# --------------------------------------------------------------------------------------
C_SC = {
    "optimistic": {"cv": 0.059147, "uni_ratio": 0.5 / (804 / 3600), "uni": None, "ovh": 1.0,
                   "ext": 0.01, "retry": 0.02, "verif": 0.05},
    "conservative": {"cv": 0.216111, "uni": 0.5, "ovh": 1.5, "ext": 0.05, "retry": 0.10,
                     "verif": 0.10},
}
C_SC["optimistic"]["uni"] = round(C_SC["optimistic"]["cv"] * C_SC["optimistic"]["uni_ratio"], 6)
DEV_NODE_H = 6.0


def c_setup(cv, uni, ovh, conservative):
    s_r = 12 * (24.0 if conservative else 2.5) * 24 / 256
    s_a = N_UNI * uni + cv                         # pairing not established
    s_b = (120 * 5 * 8 / 256 if conservative else 0.0) + 10 * uni
    s_d = 20.0 if conservative else 2.0
    s_e = 300 * cv if conservative else 0.0
    s_f = 200 * cv
    s_j = 3 * (200 + 2) * cv * ovh
    return {"S-r": s_r, "S-a": s_a, "S-b": s_b, "S-d": s_d, "S-e": s_e, "S-f": s_f, "S-j": s_j}


def c_per_experiment(proc, cv, uni, ovh, ext, n_inner):
    if proc == "P1_reconstructed_full":
        return cv * ovh + n_inner * cv + N_SEEDS * cv + N_UNI * uni + ext
    if proc == "P2_fixed_band":
        return cv * ovh + ext
    if proc == "P3_shortcut_S1_S2":
        return cv * ovh + n_inner * cv + ext
    raise KeyError(proc)


def c_total(proc, sc, cv, uni, conservative, n_exp=5000, n_inner=None):
    n_inner = n_inner if n_inner is not None else (300 if proc == "P1_reconstructed_full" else 50)
    setup = c_setup(cv, uni, sc["ovh"], conservative)
    setup_sum = sum(round(v, 4) for v in setup.values())
    prod = n_exp * round(c_per_experiment(proc, cv, uni, sc["ovh"], sc["ext"], n_inner), 6)
    verif = sc["verif"] * (prod + setup_sum)
    retry = sc["retry"] * (prod + setup_sum + DEV_NODE_H)
    sub = setup_sum + DEV_NODE_H + prod + verif + retry
    return {"admitted": sub / (1 - RESERVE), "production": prod, "setup": setup_sum,
            "per_experiment": c_per_experiment(proc, cv, uni, sc["ovh"], sc["ext"], n_inner)}


def reproduce_c():
    with open(C_COSTS) as fh:
        pub = json.load(fh)["totals"]
    out, ok = {}, True
    for name, sc in C_SC.items():
        for proc in ("P1_reconstructed_full", "P2_fixed_band", "P3_shortcut_S1_S2"):
            mine = round(c_total(proc, sc, sc["cv"], sc["uni"], name == "conservative")["admitted"], 3)
            theirs = pub[name][proc]["admitted_total_node_h"]
            out[f"{name}/{proc}"] = {"this_lane": mine, "lane_C_published": theirs}
            ok &= abs(mine - theirs) <= 0.01
    return out, ok


# --------------------------------------------------------------------------------------
def main():
    with open(os.path.join(HERE, "results", "profile.json")) as fh:
        prof = json.load(fh)
    recs, us = load_bench()
    res = {"schema": "speed-costs/1", "not_authorized": "prices only; no compute is requested"}

    # ---- measured unit operands ----------------------------------------------------------
    rep = prof["lgbm_cv_replica_shared64"]
    full = prof["lgbm_cv_replica_fullnode"]
    uni_sweep = prof["lgbm_universe_sweeps_fullnode"]["55677843"]          # purity_newomni
    ex = prof["universe_file_excess"]
    exact = prof["exact_gbt_cv_fullnode"]
    e_cv_shared = rep["elapsed_s"]["median"]
    e_cv_full = full["elapsed_s"]["median"]
    e_uni_full = uni_sweep["elapsed_s"]["median"]
    excess = ex["excess_s"]
    e_exact = exact["elapsed_s"]["median"]
    rss_exact = exact["max_rss_gb"]["median"]

    # ---- local loop costs (LOCAL: M1 Pro, ROOT 6.36, Python 3.13, 1 thread) -------------
    t = "synth_rows1000000_extra0.root"
    sig_us, truth_us = us[("pinned", t)], us[("truth", t)]
    col_us, fill_us, filln_us = us[("columnar", t)], us[("fill_loop", t)], us[("fill_n", t)]
    reads_local = (ROWS["mc_signal_reco"] * sig_us
                   + (ROWS["mc_truth_denom"] + ROWS["data"] + ROWS["mc_background"]) * truth_us) / 1e6
    fills_local = FILL_LOOPS_PURITY * ROWS["mc_signal_reco"] * fill_us / 1e6
    loops_local = reads_local + fills_local
    loops_local_after = (sum(ROWS.values()) * col_us
                         + FILL_LOOPS_PURITY * ROWS["mc_signal_reco"] * filln_us) / 1e6
    s_loop = loops_local / loops_local_after
    f_loop_lo = loops_local / e_cv_shared            # assumes Milan per-row cost >= M1 Pro's
    f_loop_hi = rep["serial_upper_fraction"]["median"]
    u192 = "synth_rows200000_extra192.root"
    u0 = "synth_rows200000_extra0.root"
    resid = (us[("status", u192)] - us[("pinned", u0)]) / (us[("pinned", u192)] - us[("pinned", u0)])
    s_io_local = 1.0 / resid
    bytes_ratio = 171.117087867 / 2.53                # bytes read: whole file vs needed columns
    res["operands"] = {
        "lgbm_cv_unfold_shared64_elapsed_s_median": [e_cv_shared, "MEASURED n=300"],
        "lgbm_cv_unfold_fullnode_elapsed_s": [e_cv_full, "MEASURED n=1"],
        "lgbm_universe_unfold_fullnode_elapsed_s_median": [e_uni_full, "MEASURED n=187"],
        "universe_file_excess_s": [excess, "MEASURED (CV unfold on universe file n=2 minus CV file n=1)"],
        "exact_unfold_elapsed_s": [e_exact, "MEASURED n=1"],
        "exact_unfold_max_rss_gb": [rss_exact, "MEASURED n=1"],
        "universe_unfold_max_rss_gb": [uni_sweep["max_rss_gb"], "MEASURED n=187"],
        "local_us_per_row": {"signal_loop": sig_us, "truth_loop": truth_us, "columnar": col_us,
                             "fill_loop": fill_us, "fill_n": filln_us, "basis": "LOCAL"},
        "loops_local_s": [loops_local, "LOCAL x production row counts"],
        "loops_local_after_s": [loops_local_after, "LOCAL"],
        "s_loop": [s_loop, "LOCAL"],
        "f_loop_range": [[f_loop_lo, f_loop_hi], "lower LOCAL/ASSUMED (Milan not faster per row "
                         "than an M1 Pro core); upper MEASURED sacct serial bound, median replica"],
        "f_io_universe": [ex["f_io_universe_task"], "MEASURED"],
        "s_io": [[s_io_local, bytes_ratio], "lower LOCAL (residual excess after prototype 1); "
                 "upper ANALYTICAL (bytes decompressed ratio)"],
        "residual_excess_fraction_after_p1": [resid, "LOCAL"],
    }

    # ---- 1. per-unit Amdahl table (category 1 candidates) -------------------------------
    unit = {}
    for f_name, f in (("loops_low", f_loop_lo), ("loops_high", f_loop_hi)):
        unit[f"lgbm_cv_unfold/{f_name}"] = {
            "f": f, "measured_s": s_loop, "speedup_at_measured_s": 1 / amdahl(f, s_loop),
            "speedup_at": {s: 1 / amdahl(f, s) for s in SPEEDUPS}, "ceiling": 1 / (1 - f)}
    f_io = ex["f_io_universe_task"]
    unit["lgbm_universe_unfold/io_excess"] = {
        "f": f_io, "measured_s": s_io_local, "speedup_at_measured_s": 1 / amdahl(f_io, s_io_local),
        "speedup_at": {s: 1 / amdahl(f_io, s) for s in SPEEDUPS}, "ceiling": 1 / (1 - f_io)}
    f_ex_loops = (f_loop_lo * e_cv_shared / e_exact, f_loop_hi * e_cv_shared / e_exact)
    unit["exact_cv_unfold/loops"] = {
        "f": list(f_ex_loops), "ceiling": [1 / (1 - f) for f in f_ex_loops],
        "note": "the remaining >= 99.4 % is sklearn's compiled single-threaded exact splitter"}
    unit["exact_universe_unfold/io_excess"] = {
        "f": excess / (e_exact + excess), "ceiling": (e_exact + excess) / e_exact,
        "note": "additive I/O (measured on LightGBM); no exact universe unfold has run"}
    res["unit_amdahl"] = unit

    # ---- 2. unit rates under each scenario (node-h per unfold) --------------------------
    a_lo, a_hi = amdahl(f_loop_lo, s_loop), amdahl(f_loop_hi, s_loop)
    e_uni_p1_full = e_cv_full + resid * excess
    e_uni_p1_shared = e_cv_shared + resid * excess
    rates = {
        "lgbm_cv_shared64": {"now": e_cv_shared * 64 / 256 / 3600,
                             "p2": [e_cv_shared * a_hi * 64 / 256 / 3600,
                                    e_cv_shared * a_lo * 64 / 256 / 3600]},
        "lgbm_universe": {
            "C_optimistic_assumed": C_SC["optimistic"]["uni"],
            "C_conservative_documented": C_SC["conservative"]["uni"],
            "now_fullnode_measured": e_uni_full / 3600,
            "now_shared64": None,
            "now_shared64_note": f"{uni_sweep['tasks_rss_over_shared64_alloc_gb']} of 187 tasks "
                                 "peaked above the 121.9 GB shared-64 allocation",
            "p1_fullnode": e_uni_p1_full / 3600,
            "p1_shared64": e_uni_p1_shared * 64 / 256 / 3600,
            "p1_p2_shared64": [(e_cv_shared * a_hi + resid * excess) * 64 / 256 / 3600,
                               (e_cv_shared * a_lo + resid * excess) * 64 / 256 / 3600]},
    }
    res["unit_rates_node_h"] = rates

    # ---- 3. exact backend: packing by memory -------------------------------------------
    def pack(rss):
        return max(1, min(128, math.floor(NODE_MEM_GB / rss)))
    lists_gb = (8 + 3) * ROWS["mc_signal_reco"] * 32 / 1e9     # CPython float + list slot
    arrays_gb = (8 + 3) * ROWS["mc_signal_reco"] * 8 / 1e9
    rss_p2 = rss_exact - lists_gb + arrays_gb
    uni_rss = uni_sweep["max_rss_gb"]
    exact_rates = {
        "cv_as_run": {"p": 1, "node_h": e_exact / 3600},
        "cv_packed_now": {"p": pack(rss_exact), "node_h": e_exact / 3600 / pack(rss_exact),
                          "basis": "MEASURED RSS; contention unmeasured"},
        "cv_packed_p2": {"p": pack(rss_p2), "node_h": e_exact / 3600 / pack(rss_p2),
                         "rss_gb": rss_p2, "basis": "ANALYTICAL RSS (lists -> arrays)"},
        "universe_now_safe": {"p": pack(uni_rss["max"]),
                              "node_h": (e_exact + excess) / 3600 / pack(uni_rss["max"]),
                              "basis": "RSS of the identical loader on the universe file "
                                       "(LightGBM tasks, max); packing must budget the max"},
        "universe_now_median": {"p": pack(uni_rss["median"]),
                                "node_h": (e_exact + excess) / 3600 / pack(uni_rss["median"]),
                                "basis": "median RSS; OOM risk for the high tasks"},
        "universe_p1": {"p": pack(rss_exact), "node_h": (e_exact + resid * excess) / 3600 / pack(rss_exact),
                        "basis": "RSS back to the CV-file level (LOCAL evidence only)"},
        "universe_p1_p2": {"p": pack(rss_p2), "node_h": (e_exact + resid * excess) / 3600 / pack(rss_p2),
                           "basis": "ANALYTICAL"},
        "lane_A_packed": 0.68, "lane_C_universe_ratio": 0.5 / (804 / 3600),
        "wall_per_exact_unfold_h": {"cv": e_exact / 3600, "universe_now": (e_exact + excess) / 3600,
                                    "universe_p1": (e_exact + resid * excess) / 3600},
    }
    res["exact_backend_unit_rates"] = exact_rates

    # ---- 4. named procedures ------------------------------------------------------------
    procs = {}
    # 4a. exact-backend transfer measurement (A's option (b)): P03 + P05 + P09b
    def transfer(cv_rate, uni_rate, n_boot):
        p03, p05, p09 = n_boot * cv_rate, N_UNI * uni_rate + cv_rate, N_SEEDS * cv_rate
        return {"P03": p03, "P05": p05, "P09b": p09, "sum": p03 + p05 + p09,
                "admitted_with_5pct_retry_10pct_verif_reserve": (p03 + p05 + p09) * 1.15 / 0.8}
    cvp = exact_rates["cv_packed_now"]["node_h"]
    procs["exact_transfer_measurement"] = {
        "estimator": "E_C (sklearn exact GBT, random_state=None)",
        "lane_A_forecast_N50": transfer(0.68, 0.68, 50),
        "lane_C_ratio_N50": transfer(0.68, 0.68 * 0.5 / (804 / 3600), 50),
        "now_safe_packing_N50": transfer(cvp, exact_rates["universe_now_safe"]["node_h"], 50),
        "now_median_packing_N50": transfer(cvp, exact_rates["universe_now_median"]["node_h"], 50),
        "p1_N50": transfer(cvp, exact_rates["universe_p1"]["node_h"], 50),
        "p1_p2_N50": transfer(exact_rates["cv_packed_p2"]["node_h"],
                              exact_rates["universe_p1_p2"]["node_h"], 50),
        "p1_N300": transfer(cvp, exact_rates["universe_p1"]["node_h"], 300),
        "now_safe_packing_N300": transfer(cvp, exact_rates["universe_now_safe"]["node_h"], 300),
        "wall_h_one_wave": exact_rates["wall_per_exact_unfold_h"],
        # P05's 188 tasks at C's 30-node concurrency cap: waves x ~19.5 h per exact unfold
        "P05_waves_at_30_nodes": {k: math.ceil(188 / (30 * exact_rates[k]["p"]))
                                  for k in ("universe_now_safe", "universe_now_median", "universe_p1")},
        # category 2 (a faster exact implementation is not bitwise E_C; needs P09b first)
        "p1_N50_native_s_category2": {s: transfer(cvp * amdahl(0.994, s),
                                                  exact_rates["universe_p1"]["node_h"] * amdahl(0.994, s),
                                                  50)["sum"] for s in SPEEDUPS},
    }
    # 4b. LightGBM matched sweep at the central's seed (C's S-a; option (c)'s seed-1 sweep)
    ru = rates["lgbm_universe"]
    procs["lgbm_matched_sweep_S-a"] = {
        "C_optimistic": N_UNI * ru["C_optimistic_assumed"] + C_SC["optimistic"]["cv"],
        "C_conservative": N_UNI * ru["C_conservative_documented"] + C_SC["conservative"]["cv"],
        "now_fullnode_measured": N_UNI * ru["now_fullnode_measured"] + full["node_h"]["median"],
        "p1_fullnode": N_UNI * ru["p1_fullnode"] + full["node_h"]["median"],
        "p1_shared64": N_UNI * ru["p1_shared64"] + rates["lgbm_cv_shared64"]["now"],
        "p1_p2_shared64": [N_UNI * r + rates["lgbm_cv_shared64"]["now"]
                           for r in ru["p1_p2_shared64"]],
        "wall_h_per_task": {"now": e_uni_full / 3600, "p1_fullnode": e_uni_p1_full / 3600,
                            "p1_shared64": e_uni_p1_shared / 3600},
    }
    # 4c. N2 (B 16.1): 100 LightGBM CV-file runs at the KI-85 rate + R0, 20 % reserve
    ki85 = 0.0708
    n2_runs = 100 * ki85 * 1.05
    procs["N2"] = {
        "now": [(n2_runs + 0.4) / 0.8, (n2_runs + 2.3) / 0.8],
        "p2": [(n2_runs * a_hi + 0.4) / 0.8, (n2_runs * a_lo + 2.3) / 0.8],
        "max_saving_node_h": n2_runs * (1 - a_hi) / 0.8,
        "share_of_remaining_cpu": (n2_runs + 2.3) / 0.8 / CPU_REMAINING_NODE_H,
    }
    # 4d. B primary (719 x 301 runs x 0.0591 x 1.05) and its design N (1,116)
    for label, n_exp in (("B_primary_N719", 719), ("B_primary_N1116", 1116)):
        base = n_exp * 301 * 0.059147 * 1.05
        procs[label] = {"now": base, "p2": [base * a_hi, base * a_lo],
                        "loops_infinitely_fast": [base * (1 - f_loop_hi), base * (1 - f_loop_lo)],
                        "x_remaining_cpu_p2_best": base * a_hi / CPU_REMAINING_NODE_H}
    # 4e. C's P1/P2/P3 at 4 x 1,250 with the accelerated unit rates
    rep_c, ok = reproduce_c()
    res["lane_C_reproduction"] = {"rows": rep_c, "all_within_0.01_node_h": ok}
    cc = {}
    for name, sc in C_SC.items():
        cons = name == "conservative"
        cv_now = sc["cv"]
        scen = {"C_as_published": (cv_now, sc["uni"])}
        if cons:
            scen["measured_universe_rate"] = (cv_now, ru["now_fullnode_measured"])
            scen["p1_fullnode"] = (cv_now, ru["p1_fullnode"])
            scen["p1_p2_fullnode"] = (cv_now * a_hi, (e_cv_full * a_hi + resid * excess) / 3600)
        else:
            scen["p1_shared64"] = (cv_now, ru["p1_shared64"])
            scen["p1_p2_shared64"] = (cv_now * a_hi, ru["p1_p2_shared64"][0])
        cc[name] = {k: {p: c_total(p, sc, cv, uni, cons)["admitted"]
                        for p in ("P1_reconstructed_full", "P2_fixed_band", "P3_shortcut_S1_S2")}
                    for k, (cv, uni) in scen.items()}
        # generic speedups applied to EVERY unfold (an upper bound on any implementation gain)
        cc[name]["all_unfolds_s"] = {s: {p: c_total(p, sc, sc["cv"] / s, sc["uni"] / s, cons)["admitted"]
                                         for p in ("P1_reconstructed_full", "P2_fixed_band",
                                                   "P3_shortcut_S1_S2")} for s in SPEEDUPS}
    procs["C_total_uncertainty_4x1250"] = cc
    # 4f. PET successor: the not-run section 11 repair (DEV 720 + RB 1,080 unfoldings)
    with open(PET_COST) as fh:
        pet = json.load(fh)["candidates"]["H2S1T24"]
    f_load = [r["load_seconds"] / (pet["k"] * r["mean_iteration_seconds"] + r["load_seconds"])
              for r in pet["runs"]]
    a100 = st.median(pet["gpu_hours_per_unfolding"])
    fl = st.median(f_load)
    pet_total = (720 + 1080) * a100
    procs["PET_repair_H2S1T24"] = {
        "a100_h_per_unfolding_median": a100, "n_runs": len(pet["runs"]),
        "f_load_median": fl, "f_load_max": max(f_load),
        "wrapper_io_ceiling": 1 / (1 - max(f_load)),
        "a100_h_total_now": pet_total,
        "share_of_remaining_gpu": pet_total / 4 / GPU_REMAINING_NODE_H,
        "training_s_hypothetical_category2": {s: pet_total * amdahl(1 - fl, s) for s in SPEEDUPS},
        "wall_days_now_record": 12.0,
    }
    res["procedures"] = procs

    # ---- 5. development / verification cost and payback ---------------------------------
    p1_verif = (2 * rates["lgbm_cv_shared64"]["now"] + 3 * ru["p1_fullnode"])
    p2_verif = 6 * rates["lgbm_cv_shared64"]["now"]
    sav_uni = ru["now_fullnode_measured"] - ru["p1_fullnode"]
    sav_cv = [rates["lgbm_cv_shared64"]["now"] - r for r in rates["lgbm_cv_shared64"]["p2"]]
    res["payback"] = {
        "p1": {"verification_node_h": p1_verif, "engineering": "ASSUMED 0.5-1 person-day incl. review",
               "saving_per_lgbm_universe_unfold_fullnode": sav_uni,
               "saving_per_lgbm_universe_unfold_shared": ru["now_fullnode_measured"] - ru["p1_shared64"],
               "saving_per_exact_universe_unfold_safe_packing":
                   exact_rates["universe_now_safe"]["node_h"] - exact_rates["universe_p1"]["node_h"],
               "payback_universe_unfolds": p1_verif / sav_uni},
        "p2": {"verification_node_h": p2_verif, "engineering": "ASSUMED 1-2 person-days incl. review",
               "saving_per_lgbm_cv_unfold": sav_cv,
               "payback_cv_unfolds": [p2_verif / sav_cv[0], p2_verif / sav_cv[1]]},
    }
    res["comparators"] = {"cpu_remaining_node_h": CPU_REMAINING_NODE_H,
                          "cpu_annual_node_h": CPU_ANNUAL_NODE_H,
                          "gpu_remaining_node_h": GPU_REMAINING_NODE_H,
                          "note": "point-in-time balances (B section 14); not ceilings or grants"}
    with open(os.path.join(HERE, "results", "costs.json"), "w") as fh:
        json.dump(res, fh, indent=1, sort_keys=True)
    return res


if __name__ == "__main__":
    r = main()
    print(json.dumps({"reproduction_ok": r["lane_C_reproduction"]["all_within_0.01_node_h"],
                      "f_loop": r["operands"]["f_loop_range"][0],
                      "s_loop": r["operands"]["s_loop"][0],
                      "s_io": r["operands"]["s_io"][0]}, indent=1))
