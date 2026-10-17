#!/usr/bin/env python3
"""Compare recompute result.json with the committed combination.json. Usage: compare_comb.py result.json combination.json"""
import json, sys
import numpy as np
me = json.load(open(sys.argv[1])); P = json.load(open(sys.argv[2])); R = P["report"]
def rel(a, b):
    a, b = np.atleast_1d(np.asarray(a, float)), np.atleast_1d(np.asarray(b, float))
    return float(np.max(np.abs(a / b - 1)))
g = {}
# checks (values vs values; both tiny)
mc, pc = me["checks"], P["checks"]
pairs = [("total_minus_sum_over_max", "s5_total_equals_universe_stat_c08"), ("total_asym_over_max", "s5_total_symmetry_rel"),
         ("total_mineig_over_max", "s5_total_min_eig_over_max"), ("Q_asym_over_max", "combined_symmetry_rel"),
         ("Q_mineig_over_max", "combined_min_eig_over_max"), ("x_vs_cells_x_EU_maxrel", "cells_x_s5_vs_playlist_rel"),
         ("x_vs_workcov_EU_maxrel", "cells_x_playlist_vs_work_cov_rel"), ("functionals_vs_npz_F_over_max", "functionals_s5_vs_playlist_rel"),
         ("area_vs_npz_F0_over_max", "area_s5_vs_playlist_rel"), ("cells_npz_eq_workcov", "cells_npz_equal_work_cov"),
         ("cells_eq_nonzero_EU", "cells_work_cov_equal_E_U_nonzero")]
g["checks_side_by_side"] = {a: [mc[a], pc[b]] for a, b in pairs}
g["checks_side_by_side"]["r_vs_npz_max"] = [max(mc[f"r_{X}_vs_npz_maxrel"] for X in ("PA", "PB", "PC")), pc["r_npz_vs_reloaded_rel"]]
# budget
names = {"VL175": "VL175", "S5_universe": "S5_universe", "S5_stat": "S5_stat", "S5_c08": "S5_c08", "S5_total": "S5_total",
         "C_PL": "C_PL", "S5_plus_C_PL": "S5_total_plus_C_PL"}
cs, ig, fr, fa, ra = 0.0, 0.0, 0.0, 0.0, 0.0
for m, p in names.items():
    b, q = me["budget"][m], R["budget"][p]
    cs = max(cs, rel([b["cell_median"], b["cell_p84"], b["cell_max"]], [q["cell_rel_sigma_pct"][k] for k in ("median", "p84", "max")]))
    ig = max(ig, rel(b["integral"], q["integral_rel_sigma_pct"]))
    fr = max(fr, rel(np.round(b["pt"] + b["pz"], 4), q["pt_rel_sigma_pct"] + q["pz_rel_sigma_pct"]))
    fa = max(fa, float(np.max(np.abs(np.array(b["pt"] + b["pz"]) - np.array(q["pt_rel_sigma_pct"] + q["pz_rel_sigma_pct"])))))
    ra = max(ra, rel(b["median_sigma_ratio_to_VL175"], q["median_cell_sigma_ratio_to_VL175"]))
g["budget_cell_stats_maxrel"] = cs; g["budget_integral_maxrel"] = ig
g["budget_30proj_rounded4_maxrel"] = fr; g["budget_30proj_unrounded_absdiff_pctpts"] = fa; g["budget_ratioVL_maxrel"] = ra
g["S5_total_vs_VL175_ratio_rel"] = rel(me["budget"]["S5_total"]["median_sigma_ratio_to_VL175"], R["S5_total_vs_VL175"]["median_cell_sigma_ratio"])
e, pe = me["effect"], R["effect_of_C_PL_on_S5"]
g["effect_maxrel"] = rel([100 * e["cell_sigma_increase_median"], 100 * e["cell_sigma_increase_max"], 100 * e["integral_sigma_increase"],
                          100 * e["max_functional_increase"], e["cpl_variance_share_cell_median"], e["cpl_variance_share_integral"]],
                         [pe["cell_sigma_increase_pct"]["median"], pe["cell_sigma_increase_pct"]["max"], pe["integral_sigma_increase_pct"],
                          pe["functional_sigma_increase_pct_max"], pe["block_share_of_cell_variance_median"], pe["block_share_of_integral_variance"]])
vm = {"b_PB_dr": "b_PB_dr", "b_PC_dr": "b_PC_dr", "bias_PB": "bias_PB_raw_frozen", "bias_PC": "bias_PC_raw_frozen"}
mm = {"VL175": "VL175", "VL175_plus_C_PL": "VL175_plus_C_PL", "S5_total": "S5", "S5_plus_C_PL": "S5_plus_C_PL"}
c2 = {}
for v, pv in vm.items():
    for pk in ("pz", "pt"):
        for m, pm in mm.items():
            c2[f"{v}/{pk}_vs_{m}"] = rel(me["chi2"][v][f"{pk}_vs_{m}"], R["reference_scenario_algebraic"][pv][f"{pk}_vs_{pm}"])
g["chi2_32_maxrel"] = max(c2.values()); g["chi2_worst"] = max(c2, key=c2.get)
g["chi2_control_vs_checks"] = rel([me["chi2"]["b_PB_dr"]["pz_vs_VL175"], me["chi2"]["b_PB_dr"]["pz_vs_VL175_plus_C_PL"],
                                   me["chi2"]["bias_PB"]["pz_vs_VL175"], me["chi2"]["bias_PB"]["pz_vs_VL175_plus_C_PL"]],
                                  [pc["control_chi2"]["b_PB_dr"]["pz_vs_VL175"]["committed"], pc["control_chi2"]["b_PB_dr"]["pz_vs_VL175_plus_C_PL"]["committed"],
                                   pc["control_chi2"]["bias_PB_raw_frozen"]["pz_vs_VL175"]["committed"], pc["control_chi2"]["bias_PB_raw_frozen"]["pz_vs_VL175_plus_C_PL"]["committed"]])
g["ranks"] = {"mine": me["ranks_rcond1e-10"], "producer": R["ranks_rcond_1e-10"]}
print(json.dumps(g, indent=1))
